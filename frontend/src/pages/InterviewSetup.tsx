import { useState, useCallback } from 'react'
import {
  Box,
  Typography,
  Paper,
  Button,
  LinearProgress,
  Alert,
  Chip,
  Grid,
  Card,
  CardContent,
  Fade,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Stepper,
  Step,
  StepLabel,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
} from '@mui/material'
import {
  CloudUpload as UploadIcon,
  CheckCircle as SuccessIcon,
  Delete as DeleteIcon,
  AttachFile as AttachIcon,
  Person as PersonIcon,
  Work as WorkIcon,
  Code as CodeIcon,
  ArrowBack as BackIcon,
  ArrowForward as NextIcon,
  Edit as EditIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material'
import { useDropzone } from 'react-dropzone'
import { useApp } from '../App'
import MDEditor from '@uiw/react-md-editor'
import './InterviewSetup.css'

// 文件大小限制（MB）
const MAX_RESUME_SIZE = 10
const MAX_SUPPORTING_SIZE = 50
const MAX_SUPPORTING_FILES = 3

// 模拟API调用 - 根据文件名动态生成解析结果
const mockParseResume = async (file: File): Promise<any> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // 从文件名提取候选人姓名（去掉扩展名和常见前缀）
      let candidateName = '候选人'
      const fileName = file.name.replace(/\.[^/.]+$/, '') // 去掉扩展名
      
      // 尝试提取中文名（2-4个汉字）
      const chineseNameMatch = fileName.match(/[\u4e00-\u9fa5]{2,4}/)
      if (chineseNameMatch) {
        candidateName = chineseNameMatch[0]
      } else {
        // 尝试提取英文名（假设是英文名）
        const englishNameMatch = fileName.match(/^[a-zA-Z\s]+/)
        if (englishNameMatch && englishNameMatch[0].length > 1) {
          candidateName = englishNameMatch[0].trim()
        }
      }
      
      // 随机生成经验年限（1-8年）
      const years = Math.floor(Math.random() * 8) + 1
      
      // 根据经验年限确定职级
      let level = '初级'
      if (years >= 3 && years < 5) level = '中级'
      else if (years >= 5) level = '高级'
      
      // 随机生成手机号（隐藏中间4位）
      const phonePrefix = ['138', '139', '150', '186', '188'][Math.floor(Math.random() * 5)]
      const phoneSuffix = Math.floor(Math.random() * 9000 + 1000).toString()
      
      // 生成邮箱
      const emailDomains = ['gmail.com', 'qq.com', '163.com', 'outlook.com']
      const randomDomain = emailDomains[Math.floor(Math.random() * emailDomains.length)]
      const emailPrefix = Math.random().toString(36).substring(2, 8)
      
      // 技能栈组合
      const skillSets = [
        {
          programming_languages: ['Go', 'Java'],
          databases: ['MySQL', 'Redis'],
          frameworks: ['Gin', 'Spring Boot'],
          middleware: ['Kafka'],
        },
        {
          programming_languages: ['Python', 'Go'],
          databases: ['PostgreSQL', 'MongoDB'],
          frameworks: ['Django', 'Gin'],
          middleware: ['RabbitMQ'],
        },
        {
          programming_languages: ['Java', 'Kotlin'],
          databases: ['MySQL', 'Oracle'],
          frameworks: ['Spring Cloud', 'MyBatis'],
          middleware: ['RocketMQ', 'Nacos'],
        },
        {
          programming_languages: ['Go', 'Rust'],
          databases: ['Redis', 'TiDB'],
          frameworks: ['Gin', 'gRPC'],
          middleware: ['Kafka', 'Etcd'],
        },
      ]
      
      const randomSkillSet = skillSets[Math.floor(Math.random() * skillSets.length)]
      
      resolve({
        name: candidateName,
        phone: `${phonePrefix}****${phoneSuffix}`,
        email: `${emailPrefix}@${randomDomain}`,
        education: [
          {
            school: ['清华大学', '北京大学', '复旦大学', '上海交通大学', '浙江大学'][Math.floor(Math.random() * 5)],
            major: ['计算机科学与技术', '软件工程', '信息安全', '数据科学'][Math.floor(Math.random() * 4)],
            degree: ['本科', '硕士'][Math.floor(Math.random() * 2)],
            graduation_year: (2024 - years - Math.floor(Math.random() * 3)).toString(),
          },
        ],
        work_experience: [
          {
            company: ['字节跳动', '阿里巴巴', '腾讯', '美团', '京东'][Math.floor(Math.random() * 5)],
            position: '后端开发工程师',
            duration: `${2024 - years}.0${Math.floor(Math.random() * 9 + 1)}-至今`,
          },
        ],
        skills: randomSkillSet,
        estimated_level: level,
        years_of_experience: years,
        interview_strategy: {
          focus_areas: [
            `${randomSkillSet.programming_languages[0]}语言核心特性`,
            `${randomSkillSet.databases[0]}性能优化`,
            `${randomSkillSet.middleware[0]}高级应用`,
          ],
          difficulty_adjustment: '正常',
          scenario_design: '微服务架构下的订单系统',
        },
      })
    }, 2000)
  })
}

export default function InterviewSetup() {
  const { 
    selectedInterviewType, 
    setCurrentPage, 
    setResumeData, 
    resumeData,
    supportingMaterials,
    setSupportingMaterials,
    setSessionId,
  } = useApp()

  const [activeStep, setActiveStep] = useState(0)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  
  // 编辑状态
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [editTab, setEditTab] = useState(0)
  const [editFormData, setEditFormData] = useState({
    name: '',
    phone: '',
    email: '',
    estimated_level: '',
    years_of_experience: 0,
    work_experience_md: '',
  })

  const steps = ['上传简历', '上传辅助材料', '确认信息']

  // 简历上传
  const onResumeDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    // 验证文件类型
    const validTypes = ['.pdf', '.docx', '.doc', '.txt']
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
    if (!validTypes.includes(fileExtension)) {
      setError('请上传 PDF、DOCX 或 TXT 格式的文件')
      return
    }

    // 验证文件大小
    if (file.size > MAX_RESUME_SIZE * 1024 * 1024) {
      setError(`简历文件大小不能超过 ${MAX_RESUME_SIZE}MB`)
      return
    }

    setUploading(true)
    setError(null)
    setUploadProgress(0)

    try {
      // 模拟上传进度
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 200)

      // 调用解析API
      const result = await mockParseResume(file)
      
      clearInterval(progressInterval)
      setUploadProgress(100)
      setResumeData(result)
      setActiveStep(1) // 自动进入下一步
    } catch (err) {
      setError('简历解析失败，请重试')
    } finally {
      setUploading(false)
    }
  }, [setResumeData])

  const { getRootProps: getResumeRootProps, getInputProps: getResumeInputProps, isDragActive: isResumeDragActive } = useDropzone({
    onDrop: onResumeDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
    disabled: uploading || !!resumeData,
  })

  // 辅助材料上传
  const onSupportingDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.filter(file => {
      // 验证文件大小
      if (file.size > MAX_SUPPORTING_SIZE * 1024 * 1024) {
        setError(`辅助材料单个文件不能超过 ${MAX_SUPPORTING_SIZE}MB`)
        return false
      }
      return true
    })

    if (supportingMaterials.length + newFiles.length > MAX_SUPPORTING_FILES) {
      setError(`最多只能上传 ${MAX_SUPPORTING_FILES} 个辅助材料文件`)
      return
    }

    setSupportingMaterials([...supportingMaterials, ...newFiles])
    setError(null)
  }, [supportingMaterials, setSupportingMaterials])

  const { getRootProps: getSupportingRootProps, getInputProps: getSupportingInputProps, isDragActive: isSupportingDragActive } = useDropzone({
    onDrop: onSupportingDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'image/*': ['.png', '.jpg', '.jpeg'],
    },
    disabled: supportingMaterials.length >= MAX_SUPPORTING_FILES,
  })

  const removeSupportingFile = (index: number) => {
    const newFiles = [...supportingMaterials]
    newFiles.splice(index, 1)
    setSupportingMaterials(newFiles)
  }

  // 打开编辑对话框
  const handleOpenEdit = () => {
    if (resumeData) {
      // 将工作经验数组转换为 Markdown 格式
      const workExpMd = resumeData.work_experience
        ?.map((exp: any) => 
          `### ${exp.company} - ${exp.position}\n\n**时间：** ${exp.duration}\n\n**工作内容：**\n\n- `)
        .join('\n\n---\n\n') || ''
      
      setEditFormData({
        name: resumeData.name || '',
        phone: resumeData.phone || '',
        email: resumeData.email || '',
        estimated_level: resumeData.estimated_level || '',
        years_of_experience: resumeData.years_of_experience || 0,
        work_experience_md: workExpMd,
      })
      setEditDialogOpen(true)
    }
  }

  // 保存编辑
  const handleSaveEdit = () => {
    if (resumeData) {
      setResumeData({
        ...resumeData,
        name: editFormData.name,
        phone: editFormData.phone,
        email: editFormData.email,
        estimated_level: editFormData.estimated_level,
        years_of_experience: editFormData.years_of_experience,
        work_experience_md: editFormData.work_experience_md,
      })
    }
    setEditDialogOpen(false)
  }

  const handleBack = () => {
    if (activeStep === 0) {
      setCurrentPage('home')
    } else {
      setActiveStep(activeStep - 1)
    }
  }

  // 重新上传简历
  const handleReuploadResume = () => {
    setResumeData(null)
    setActiveStep(0)
    setError(null)
    setUploadProgress(0)
  }

  // 清除所有辅助材料
  const handleClearAllSupporting = () => {
    if (confirm('确定要删除所有已上传的辅助材料吗？')) {
      setSupportingMaterials([])
    }
  }

  const handleNext = () => {
    if (activeStep === steps.length - 1) {
      // 开始面试
      startInterview()
    } else {
      setActiveStep(activeStep + 1)
    }
  }

  const startInterview = async () => {
    try {
      // 模拟创建面试会话
      await new Promise(resolve => setTimeout(resolve, 1000))
      setSessionId('session_' + Date.now())
      setCurrentPage('interview')
    } catch (err) {
      setError('创建面试会话失败，请重试')
    }
  }

  // 渲染步骤内容
  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return renderResumeUpload()
      case 1:
        return renderSupportingMaterials()
      case 2:
        return renderConfirmation()
      default:
        return renderResumeUpload()
    }
  }

  const renderResumeUpload = () => (
    <Box>
      {!resumeData ? (
        <Paper
          elevation={3}
          sx={{
            p: 4,
            textAlign: 'center',
            background: isResumeDragActive
              ? 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)'
              : 'linear-gradient(135deg, #f5f5f5 0%, #eeeeee 100%)',
            border: '2px dashed',
            borderColor: isResumeDragActive ? 'primary.main' : 'grey.300',
            transition: 'all 0.3s ease',
            cursor: uploading ? 'not-allowed' : 'pointer',
          }}
          {...getResumeRootProps()}
        >
          <input {...getResumeInputProps()} />
          
          <UploadIcon
            sx={{
              fontSize: 64,
              color: isResumeDragActive ? 'primary.main' : 'grey.400',
              mb: 2,
            }}
          />
          
          <Typography variant="h5" gutterBottom>
            {isResumeDragActive ? '释放文件以上传' : '拖拽简历到这里'}
          </Typography>
          
          <Typography variant="body1" color="text.secondary" gutterBottom>
            或点击选择文件
          </Typography>
          
          <Typography variant="caption" color="text.secondary">
            支持 PDF、DOCX、TXT 格式，文件大小不超过 {MAX_RESUME_SIZE}MB
          </Typography>

          {uploading && (
            <Box sx={{ mt: 3 }}>
              <LinearProgress
                variant="determinate"
                value={uploadProgress}
                sx={{ height: 8, borderRadius: 4 }}
              />
              <Typography variant="body2" sx={{ mt: 1 }}>
                {uploadProgress < 100 ? '正在解析简历...' : '解析完成！'}
              </Typography>
            </Box>
          )}
        </Paper>
      ) : (
        <Fade in={true}>
          <Box>
            <Alert 
              severity="success" 
              icon={<SuccessIcon />} 
              sx={{ mb: 2 }}
              action={
                <Button
                  color="inherit"
                  size="small"
                  startIcon={<RefreshIcon />}
                  onClick={handleReuploadResume}
                >
                  重新上传
                </Button>
              }
            >
              简历解析成功！已提取 {resumeData.name} 的信息
            </Alert>
            
            <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.50' }}>
              <Typography variant="body2" color="text.secondary">
                <strong>姓名：</strong>{resumeData.name}<br/>
                <strong>电话：</strong>{resumeData.phone}<br/>
                <strong>邮箱：</strong>{resumeData.email}<br/>
                <strong>经验：</strong>{resumeData.years_of_experience}年 | {resumeData.estimated_level}工程师
              </Typography>
            </Paper>
          </Box>
        </Fade>
      )}

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  )

  const renderSupportingMaterials = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        上传辅助材料（可选）
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        可以上传项目文档、技术博客、论文等辅助材料，帮助AI更好地了解你的技术背景
      </Typography>

      {/* 辅助材料上传区域 */}
      {supportingMaterials.length < MAX_SUPPORTING_FILES && (
        <Paper
          elevation={2}
          sx={{
            p: 3,
            mb: 3,
            textAlign: 'center',
            background: isSupportingDragActive
              ? 'linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%)'
              : '#fafafa',
            border: '2px dashed',
            borderColor: isSupportingDragActive ? 'secondary.main' : 'grey.300',
            transition: 'all 0.3s ease',
            cursor: 'pointer',
          }}
          {...getSupportingRootProps()}
        >
          <input {...getSupportingInputProps()} />
          
          <AttachIcon sx={{ fontSize: 48, color: 'secondary.main', mb: 1 }} />
          
          <Typography variant="body1" gutterBottom>
            {isSupportingDragActive ? '释放文件以上传' : '拖拽辅助材料到这里'}
          </Typography>
          
          <Typography variant="caption" color="text.secondary">
            支持 PDF、DOCX、图片等，单个文件不超过 {MAX_SUPPORTING_SIZE}MB
          </Typography>
          
          <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
            已上传 {supportingMaterials.length}/{MAX_SUPPORTING_FILES} 个文件
          </Typography>
        </Paper>
      )}

      {/* 已上传文件列表 */}
      {supportingMaterials.length > 0 && (
        <Paper elevation={2} sx={{ p: 2 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="subtitle2">
              已上传的辅助材料：
            </Typography>
            <Button
              size="small"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={handleClearAllSupporting}
            >
              全部删除
            </Button>
          </Box>
          <List dense>
            {supportingMaterials.map((file, index) => (
              <ListItem
                key={index}
                secondaryAction={
                  <IconButton edge="end" onClick={() => removeSupportingFile(index)}>
                    <DeleteIcon />
                  </IconButton>
                }
              >
                <ListItemIcon>
                  <AttachIcon />
                </ListItemIcon>
                <ListItemText
                  primary={file.name}
                  secondary={`${(file.size / 1024 / 1024).toFixed(2)} MB`}
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  )

  const renderConfirmation = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">
          确认面试信息
        </Typography>
        {resumeData && (
          <Button
            variant="outlined"
            size="small"
            startIcon={<EditIcon />}
            onClick={handleOpenEdit}
          >
            编辑信息
          </Button>
        )}
      </Box>

      {/* 面试类型 */}
      <Card variant="outlined" sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            面试类型
          </Typography>
          <Typography variant="h6">
            {selectedInterviewType?.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {selectedInterviewType?.description}
          </Typography>
          <Box sx={{ mt: 1 }}>
            <Chip 
              label={`${selectedInterviewType?.duration}分钟`} 
              size="small" 
              sx={{ mr: 1 }}
            />
            <Chip 
              label={selectedInterviewType?.style === 'strict' ? '严格模式' : selectedInterviewType?.style === 'friendly' ? '友好模式' : '标准模式'} 
              size="small" 
              color="primary"
            />
          </Box>
        </CardContent>
      </Card>

      {/* 简历信息 */}
      {resumeData && (
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <PersonIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="subtitle2">基本信息</Typography>
                </Box>
                <Typography variant="body1">{resumeData.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {resumeData.phone} · {resumeData.email}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card variant="outlined">
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <WorkIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="subtitle2">工作经验</Typography>
                </Box>
                <Typography variant="body1">{resumeData.estimated_level}开发工程师</Typography>
                <Typography variant="body2" color="text.secondary">
                  {resumeData.years_of_experience}年经验
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* 详细工作经验 Markdown */}
          <Grid item xs={12}>
            <Card variant="outlined">
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <WorkIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="subtitle2">详细工作经历</Typography>
                </Box>
                {resumeData.work_experience_md ? (
                  <Box className="markdown-preview" data-color-mode="light">
                    <MDEditor.Markdown source={resumeData.work_experience_md} />
                  </Box>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    暂无详细工作经历描述，点击"编辑信息"添加
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Card variant="outlined">
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <CodeIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="subtitle2">技能栈</Typography>
                </Box>
                <Box display="flex" flexWrap="wrap" gap={0.5}>
                  {Object.values(resumeData.skills || {}).flat().map((skill: any, index: number) => (
                    <Chip key={index} label={skill} size="small" variant="outlined" />
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* 辅助材料 */}
      {supportingMaterials.length > 0 && (
        <Card variant="outlined" sx={{ mt: 2 }}>
          <CardContent>
            <Box display="flex" alignItems="center" mb={1}>
              <AttachIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="subtitle2">辅助材料</Typography>
            </Box>
            <Typography variant="body2">
              已上传 {supportingMaterials.length} 个文件
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* 编辑对话框 */}
      <Dialog 
        open={editDialogOpen} 
        onClose={() => setEditDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>编辑面试信息</DialogTitle>
        <DialogContent>
          <Tabs
            value={editTab}
            onChange={(_, newValue) => setEditTab(newValue)}
            sx={{ mb: 2 }}
          >
            <Tab label="基本信息" />
            <Tab label="工作经验" />
          </Tabs>
          
          {editTab === 0 && (
            <Box sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="姓名"
                value={editFormData.name}
                onChange={(e) => setEditFormData({ ...editFormData, name: e.target.value })}
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="电话"
                value={editFormData.phone}
                onChange={(e) => setEditFormData({ ...editFormData, phone: e.target.value })}
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="邮箱"
                value={editFormData.email}
                onChange={(e) => setEditFormData({ ...editFormData, email: e.target.value })}
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="职级"
                value={editFormData.estimated_level}
                onChange={(e) => setEditFormData({ ...editFormData, estimated_level: e.target.value })}
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="工作年限"
                type="number"
                value={editFormData.years_of_experience}
                onChange={(e) => setEditFormData({ ...editFormData, years_of_experience: parseFloat(e.target.value) || 0 })}
              />
            </Box>
          )}
          
          {editTab === 1 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                使用 Markdown 格式编辑你的工作经历
              </Typography>
              <MDEditor
                value={editFormData.work_experience_md}
                onChange={(value) => setEditFormData({ ...editFormData, work_experience_md: value || '' })}
                height={400}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>取消</Button>
          <Button onClick={handleSaveEdit} variant="contained">保存</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )

  return (
    <Box>
      {/* 面试类型信息 */}
      {selectedInterviewType && (
        <Paper elevation={2} sx={{ p: 3, mb: 3, bgcolor: 'primary.light', color: 'white' }}>
          <Typography variant="h5" fontWeight={600} gutterBottom>
            {selectedInterviewType.name}
          </Typography>
          <Typography variant="body1" sx={{ opacity: 0.9 }}>
            {selectedInterviewType.description}
          </Typography>
          <Box sx={{ mt: 2 }}>
            {selectedInterviewType.focusAreas.map((area, index) => (
              <Chip
                key={index}
                label={area}
                size="small"
                sx={{ 
                  mr: 1, 
                  mb: 1, 
                  bgcolor: 'white', 
                  color: 'primary.main',
                  fontWeight: 500,
                }}
              />
            ))}
          </Box>
        </Paper>
      )}

      {/* 步骤条 */}
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {/* 步骤内容 */}
      <Paper elevation={3} sx={{ p: 4, mb: 3 }}>
        {renderStepContent()}
      </Paper>

      {/* 导航按钮 */}
      <Box display="flex" justifyContent="space-between">
        <Button
          variant="outlined"
          startIcon={<BackIcon />}
          onClick={handleBack}
          disabled={uploading}
        >
          {activeStep === 0 ? '返回选择' : '上一步'}
        </Button>
        
        <Button
          variant="contained"
          endIcon={activeStep === steps.length - 1 ? undefined : <NextIcon />}
          onClick={handleNext}
          disabled={activeStep === 0 && !resumeData}
        >
          {activeStep === steps.length - 1 ? '开始面试' : '下一步'}
        </Button>
      </Box>
    </Box>
  )
}
