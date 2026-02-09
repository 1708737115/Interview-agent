import os
import uuid
from typing import List, Optional
from datetime import datetime
import aiofiles

try:
    from llama_parse import LlamaParse
    LLAMAPARSE_AVAILABLE = True
except ImportError:
    LLAMAPARSE_AVAILABLE = False

from app.core.config import get_settings
from app.models.schemas import DocumentType

settings = get_settings()


class DocumentParser:
    """文档解析服务"""
    
    def __init__(self):
        self.upload_dir = "uploads"
        os.makedirs(self.upload_dir, exist_ok=True)
        
        # Initialize LlamaParse if API key available
        self.llama_parser = None
        if settings.LLAMAPARSE_API_KEY and LLAMAPARSE_AVAILABLE:
            self.llama_parser = LlamaParse(
                api_key=settings.LLAMAPARSE_API_KEY,
                result_type="markdown",
                use_vendor_multimodal_model=True,
                verbose=True
            )
    
    def get_document_type(self, filename: str) -> DocumentType:
        """根据文件名判断文档类型"""
        ext = filename.lower().split('.')[-1]
        type_map = {
            'pdf': DocumentType.PDF,
            'docx': DocumentType.DOCX,
            'doc': DocumentType.DOCX,
            'md': DocumentType.MARKDOWN,
            'markdown': DocumentType.MARKDOWN,
            'txt': DocumentType.TXT,
            'text': DocumentType.TXT
        }
        return type_map.get(ext, DocumentType.TXT)
    
    async def save_upload(self, file) -> tuple:
        """保存上传的文件"""
        file_id = str(uuid.uuid4())
        original_name = file.filename
        file_type = self.get_document_type(original_name)
        
        # Create safe filename
        safe_name = f"{file_id}_{original_name}"
        file_path = os.path.join(self.upload_dir, safe_name)
        
        # Save file
        content = await file.read()
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        return file_id, file_path, file_type, original_name
    
    async def parse_document(self, file_path: str, file_type: DocumentType) -> str:
        """解析文档内容"""
        if file_type == DocumentType.PDF and self.llama_parser:
            # Use LlamaParse for PDF
            try:
                documents = await self.llama_parser.aload_data(file_path)
                return "\n\n".join([doc.text for doc in documents])
            except Exception as e:
                print(f"LlamaParse failed: {e}, falling back to basic parser")
                return await self._basic_parse(file_path, file_type)
        else:
            return await self._basic_parse(file_path, file_type)
    
    async def _basic_parse(self, file_path: str, file_type: DocumentType) -> str:
        """基础文档解析"""
        try:
            if file_type == DocumentType.PDF:
                return await self._parse_pdf(file_path)
            elif file_type == DocumentType.DOCX:
                return await self._parse_docx(file_path)
            elif file_type in [DocumentType.MARKDOWN, DocumentType.TXT]:
                return await self._parse_text(file_path)
            else:
                return await self._parse_text(file_path)
        except Exception as e:
            raise Exception(f"文档解析失败: {str(e)}")
    
    async def _parse_pdf(self, file_path: str) -> str:
        """解析PDF（基础版，使用PyPDF2或pdfplumber）"""
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
                    text += "\n\n"
            return text
        except ImportError:
            raise Exception("请安装pdfplumber: pip install pdfplumber")
    
    async def _parse_docx(self, file_path: str) -> str:
        """解析Word文档"""
        try:
            from docx import Document
            doc = Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except ImportError:
            raise Exception("请安装python-docx: pip install python-docx")
    
    async def _parse_text(self, file_path: str) -> str:
        """解析文本文件"""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            return await f.read()
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 200,  # 减小到 200 字符以确保不超出 API 限制
        overlap: int = 30
    ) -> List[dict]:
        """
        智能文本分块 - 确保每个块不超过 API 限制
        
        策略：
        1. 优先按段落分割
        2. 如果段落太长，按句子分割
        3. 如果句子还太长，强制按字符数分割
        4. 保持上下文连贯性
        """
        chunks = []
        max_api_length = 250  # GLM-4 embedding API 安全限制
        
        def split_long_text(text: str, max_length: int) -> List[str]:
            """将长文本强制分割成小块"""
            if len(text) <= max_length:
                return [text]
            
            result = []
            # 尝试按句子分割
            sentences = text.replace('。', '\n').replace('！', '\n').replace('？', '\n').replace('.', '\n').replace('!', '\n').replace('?', '\n').split('\n')
            
            current = ""
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                if len(current) + len(sentence) + 1 <= max_length:
                    if current:
                        current += " "
                    current += sentence
                else:
                    if current:
                        result.append(current)
                    # 如果单句太长，强制分割
                    if len(sentence) > max_length:
                        for i in range(0, len(sentence), max_length):
                            result.append(sentence[i:i+max_length])
                    else:
                        current = sentence
            
            if current:
                result.append(current)
            
            return result if result else [text[:max_length]]
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # 如果段落太长，先分割段落
            if len(paragraph) > max_api_length:
                # 先保存当前块
                if current_chunk:
                    chunks.append({
                        'text': current_chunk.strip(),
                        'size': len(current_chunk)
                    })
                    current_chunk = ""
                
                # 分割长段落
                sub_paragraphs = split_long_text(paragraph, max_api_length)
                for sub in sub_paragraphs:
                    chunks.append({
                        'text': sub.strip(),
                        'size': len(sub)
                    })
                continue
            
            # 检查添加这个段落后是否会超出限制
            new_chunk = current_chunk + ("\n\n" if current_chunk else "") + paragraph
            if len(new_chunk) > max_api_length and current_chunk:
                # 保存当前块
                chunks.append({
                    'text': current_chunk.strip(),
                    'size': len(current_chunk)
                })
                # 开始新块（带重叠）
                if len(current_chunk) > overlap:
                    current_chunk = current_chunk[-overlap:] + "\n\n" + paragraph
                else:
                    current_chunk = paragraph
            else:
                current_chunk = new_chunk
        
        # 保存最后一个块
        if current_chunk:
            chunks.append({
                'text': current_chunk.strip()[:max_api_length],  # 确保不超出限制
                'size': min(len(current_chunk), max_api_length)
            })
        
        return chunks


# Global instance
document_parser = DocumentParser()
