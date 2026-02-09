import React, { useState, useEffect, useCallback } from 'react'
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Divider,
} from '@mui/material'
import {
  Delete as DeleteIcon,
  UploadFile as UploadIcon,
  PlayArrow as StartIcon,
} from '@mui/icons-material'
import { documentApi, interviewApi } from '../services/api'

interface Document {
  id: string
  title: string
  description?: string
  file_type: string
  status: string
  created_at: string
  chunk_count: number
}

interface DocumentUploadProps {
  onSessionStart: (sessionId: string) => void
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ onSessionStart }) => {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false)
  const [startDialogOpen, setStartDialogOpen] = useState(false)
  const [selectedDocs, setSelectedDocs] = useState<string[]>([])
  const [interviewMode, setInterviewMode] = useState<'structured' | 'open'>('structured')
  const [candidateInfo, setCandidateInfo] = useState('')
  const [duration, setDuration] = useState(30)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)

  // Form state for upload
  const [uploadForm, setUploadForm] = useState({
    title: '',
    description: '',
    file: null as File | null,
  })

  const fetchDocuments = useCallback(async () => {
    console.log('=== fetchDocuments 开始 ===')
    try {
      setLoading(true)
      const response = await documentApi.getAll()
      console.log('API 响应:', response)
      console.log('响应数据:', response.data)
      console.log('数据类型:', typeof response.data)
      console.log('是否为数组:', Array.isArray(response.data))
      
      // 确保返回的是数组
      const data = Array.isArray(response.data) ? response.data : []
      console.log('处理后的文档数量:', data.length)
      setDocuments(data)
    } catch (err: any) {
      console.error('获取文档列表失败:', err)
      console.error('错误详情:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status
      })
      setError('获取文档列表失败')
      setDocuments([])
    } finally {
      console.log('=== fetchDocuments 结束 ===')
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    console.log('=== 组件挂载，开始加载文档列表 ===')
    fetchDocuments()
  }, [fetchDocuments])

  useEffect(() => {
    console.log('文档列表变化:', {
      count: documents.length,
      documents: documents.map(d => ({ id: d.id, title: d.title }))
    })
  }, [documents])

  // 文件大小限制 5MB
  const MAX_FILE_SIZE = 5 * 1024 * 1024

  const handleUpload = async () => {
    console.log('=== handleUpload 开始 ===')
    console.log('表单数据:', {
      title: uploadForm.title,
      description: uploadForm.description,
      fileName: uploadForm.file?.name,
      fileSize: uploadForm.file?.size
    })
    
    if (!uploadForm.file || !uploadForm.title) {
      console.log('验证失败: 缺少文件或标题')
      setError('请填写标题并选择文件')
      return
    }

    // 检查文件大小
    if (uploadForm.file.size > MAX_FILE_SIZE) {
      setError(`文件大小超过限制（最大 ${MAX_FILE_SIZE / 1024 / 1024}MB）`)
      return
    }

    try {
      setIsUploading(true)
      setUploadProgress(0)
      setError(null)
      
      const formData = new FormData()
      formData.append('file', uploadForm.file)
      formData.append('title', uploadForm.title)
      if (uploadForm.description) {
        formData.append('description', uploadForm.description)
      }

      console.log('准备发送上传请求...')
      const response = await documentApi.upload(formData, (progress) => {
        setUploadProgress(progress)
      })
      console.log('上传响应:', response.data)
      
      console.log('关闭对话框...')
      setUploadDialogOpen(false)
      
      console.log('重置表单...')
      setUploadForm({ title: '', description: '', file: null })
      
      console.log('准备刷新文档列表...')
      await fetchDocuments()
      console.log('文档列表刷新完成')
    } catch (err: any) {
      console.error('上传错误:', err)
      console.error('错误详情:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status
      })
      setError(err.response?.data?.detail || '上传失败')
    } finally {
      console.log('=== handleUpload 结束 ===')
      setIsUploading(false)
      setUploadProgress(0)
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await documentApi.delete(id)
      fetchDocuments()
    } catch (err) {
      setError('删除失败')
    }
  }

  const handleStartInterview = async () => {
    if (selectedDocs.length === 0) {
      setError('请至少选择一个知识库')
      return
    }

    try {
      setLoading(true)
      const response = await interviewApi.start({
        mode: interviewMode,
        knowledge_base_ids: selectedDocs,
        candidate_info: candidateInfo || undefined,
        duration_minutes: duration,
      })
      
      setStartDialogOpen(false)
      setSelectedDocs([])
      setCandidateInfo('')
      onSessionStart(response.data.session_id)
    } catch (err: any) {
      setError(err.response?.data?.detail || '启动面试失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Button
          variant="contained"
          startIcon={<UploadIcon />}
          onClick={() => setUploadDialogOpen(true)}
        >
          上传文档
        </Button>
        
        {documents.length > 0 && (
          <Button
            variant="outlined"
            startIcon={<StartIcon />}
            onClick={() => setStartDialogOpen(true)}
          >
            开始面试
          </Button>
        )}
      </Box>

      <Typography variant="h6" gutterBottom>
        已上传的知识库
      </Typography>

      {documents.length === 0 ? (
        <Card>
          <CardContent>
            <Typography color="text.secondary" align="center">
              暂无文档，请先上传面试相关的资料
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <List>
          {documents.map((doc) => (
            <Card key={doc.id} sx={{ mb: 1 }}>
              <ListItem>
                <ListItemText
                  primary={doc.title}
                  secondary={
                    <Box sx={{ mt: 0.5 }}>
                      <Typography variant="body2" color="text.secondary">
                        {doc.description || '无描述'}
                      </Typography>
                      <Box sx={{ mt: 1 }}>
                        <Chip
                          label={doc.file_type.toUpperCase()}
                          size="small"
                          color="primary"
                          sx={{ mr: 1 }}
                        />
                        <Chip
                          label={`${doc.chunk_count} 个片段`}
                          size="small"
                          variant="outlined"
                        />
                      </Box>
                    </Box>
                  }
                />
                <ListItemSecondaryAction>
                  <IconButton
                    edge="end"
                    aria-label="delete"
                    onClick={() => handleDelete(doc.id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            </Card>
          ))}
        </List>
      )}

      {/* Upload Dialog */}
      <Dialog 
        open={uploadDialogOpen} 
        onClose={() => {
          if (!isUploading) {
            setUploadDialogOpen(false)
            setUploadForm({ title: '', description: '', file: null })
            setUploadProgress(0)
          }
        }} 
        maxWidth="sm" 
        fullWidth
      >
        <DialogTitle>上传知识库文档</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="文档标题"
            fullWidth
            variant="outlined"
            value={uploadForm.title}
            disabled={isUploading}
            onChange={(e) => setUploadForm({ ...uploadForm, title: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="文档描述（可选）"
            fullWidth
            variant="outlined"
            multiline
            rows={2}
            value={uploadForm.description}
            disabled={isUploading}
            onChange={(e) => setUploadForm({ ...uploadForm, description: e.target.value })}
            sx={{ mb: 2 }}
          />
          <Button
            variant="outlined"
            component="label"
            fullWidth
            disabled={isUploading}
            color={uploadForm.file && uploadForm.file.size > MAX_FILE_SIZE ? "error" : "primary"}
          >
            {uploadForm.file ? uploadForm.file.name : '选择文件'}
            <input
              type="file"
              hidden
              accept=".pdf,.docx,.md,.txt"
              disabled={isUploading}
              onChange={(e) => {
                const file = e.target.files?.[0] || null
                if (file && file.size > MAX_FILE_SIZE) {
                  setError(`文件大小超过限制（最大 ${MAX_FILE_SIZE / 1024 / 1024}MB），当前 ${(file.size / 1024 / 1024).toFixed(2)}MB`)
                } else {
                  setError(null)
                }
                setUploadForm({ ...uploadForm, file })
              }}
            />
          </Button>
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            支持 PDF、Word、Markdown、TXT 格式（最大 5MB）
          </Typography>
          {uploadForm.file && (
            <Typography variant="caption" color={uploadForm.file.size > MAX_FILE_SIZE ? "error" : "success"} sx={{ display: 'block' }}>
              文件大小: {(uploadForm.file.size / 1024).toFixed(2)} KB {uploadForm.file.size > MAX_FILE_SIZE && '(超过限制)'}
            </Typography>
          )}
          
          {/* 上传进度条 */}
          {isUploading && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                上传进度: {uploadProgress}%
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={uploadProgress} 
                sx={{ 
                  height: 8, 
                  borderRadius: 4,
                  backgroundColor: 'grey.200',
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 4,
                  }
                }}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)} disabled={isUploading}>取消</Button>
          <Button onClick={handleUpload} variant="contained" disabled={loading || isUploading || !uploadForm.file || !uploadForm.title}>
            {isUploading ? '上传中...' : '上传'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Start Interview Dialog */}
      <Dialog open={startDialogOpen} onClose={() => setStartDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>开始面试</DialogTitle>
        <DialogContent>
          <Typography variant="subtitle1" gutterBottom>
            选择要使用的知识库：
          </Typography>
          <Box sx={{ mb: 2 }}>
            {documents.map((doc) => (
              <FormControlLabel
                key={doc.id}
                control={
                  <Checkbox
                    checked={selectedDocs.includes(doc.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedDocs([...selectedDocs, doc.id])
                      } else {
                        setSelectedDocs(selectedDocs.filter((id) => id !== doc.id))
                      }
                    }}
                  />
                }
                label={doc.title}
              />
            ))}
          </Box>

          <Divider sx={{ my: 2 }} />

          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>面试模式</InputLabel>
            <Select
              value={interviewMode}
              label="面试模式"
              onChange={(e) => setInterviewMode(e.target.value as 'structured' | 'open')}
            >
              <MenuItem value="structured">结构化面试（基于知识库）</MenuItem>
              <MenuItem value="open">开放式面试（自由对话）</MenuItem>
            </Select>
          </FormControl>

          {interviewMode === 'open' && (
            <TextField
              label="候选人背景信息（可选）"
              fullWidth
              multiline
              rows={3}
              value={candidateInfo}
              onChange={(e) => setCandidateInfo(e.target.value)}
              sx={{ mb: 2 }}
              placeholder="请简要介绍您的背景、经验或期望面试的方向"
            />
          )}

          <FormControl fullWidth>
            <InputLabel>面试时长</InputLabel>
            <Select
              value={duration}
              label="面试时长"
              onChange={(e) => setDuration(e.target.value as number)}
            >
              <MenuItem value={15}>15分钟</MenuItem>
              <MenuItem value={30}>30分钟</MenuItem>
              <MenuItem value={45}>45分钟</MenuItem>
              <MenuItem value={60}>60分钟</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setStartDialogOpen(false)}>取消</Button>
          <Button onClick={handleStartInterview} variant="contained" disabled={loading}>
            开始
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default DocumentUpload
