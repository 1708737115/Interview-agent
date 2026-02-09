import { useState, useCallback } from 'react'
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  Alert,
  Chip,
  Grid,
  Card,
  CardContent,
  Divider,
  Fade,
  Zoom,
} from '@mui/material'
import {
  CloudUpload as UploadIcon,
  CheckCircle as SuccessIcon,
  Person as PersonIcon,
  School as SchoolIcon,
  Work as WorkIcon,
  Code as CodeIcon,
  Psychology as StrategyIcon,
} from '@mui/icons-material'
import { useDropzone } from 'react-dropzone'
import { useApp } from '../App'
import './ResumeUpload.css'

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
        // 尝试提取英文名
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

export default function ResumeUpload() {
  const { setResumeData, setCurrentStep } = useApp()
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [parsedData, setParsedData] = useState<any | null>(null)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    // 验证文件类型
    const validTypes = ['.pdf', '.docx', '.doc', '.txt']
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
    if (!validTypes.includes(fileExtension)) {
      setError('请上传 PDF、DOCX 或 TXT 格式的文件')
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
      setParsedData(result)
      setResumeData(result)
    } catch (err) {
      setError('简历解析失败，请重试')
    } finally {
      setUploading(false)
    }
  }, [setResumeData])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
    disabled: uploading,
  })

  const handleStartInterview = () => {
    setCurrentStep(1)
  }

  return (
    <Box>
      {/* 上传区域 */}
      {!parsedData && (
        <Paper
          elevation={3}
          sx={{
            p: 4,
            mb: 3,
            textAlign: 'center',
            background: isDragActive
              ? 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)'
              : 'linear-gradient(135deg, #f5f5f5 0%, #eeeeee 100%)',
            border: '2px dashed',
            borderColor: isDragActive ? 'primary.main' : 'grey.300',
            transition: 'all 0.3s ease',
            cursor: uploading ? 'not-allowed' : 'pointer',
          }}
          {...getRootProps()}
        >
          <input {...getInputProps()} />
          
          <UploadIcon
            sx={{
              fontSize: 64,
              color: isDragActive ? 'primary.main' : 'grey.400',
              mb: 2,
            }}
          />
          
          <Typography variant="h5" gutterBottom>
            {isDragActive ? '释放文件以上传' : '拖拽简历到这里'}
          </Typography>
          
          <Typography variant="body1" color="text.secondary" gutterBottom>
            或点击选择文件
          </Typography>
          
          <Typography variant="caption" color="text.secondary">
            支持 PDF、DOCX、TXT 格式，文件大小不超过 10MB
          </Typography>

          {uploading && (
            <Box sx={{ mt: 3 }}>
              <LinearProgress
                variant="determinate"
                value={uploadProgress}
                sx={{ height: 8, borderRadius: 4 }}
              />
              <Typography variant="body2" sx={{ mt: 1 }}>
                {uploadProgress < 100 ? '正在上传...' : '正在解析简历...'}
              </Typography>
            </Box>
          )}
        </Paper>
      )}

      {/* 错误提示 */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* 解析结果展示 */}
      {parsedData && (
        <Fade in={true} timeout={500}>
          <Box>
            <Alert severity="success" sx={{ mb: 3 }} icon={<SuccessIcon />}>
              简历解析成功！AI已为您生成个性化面试方案
            </Alert>

            <Grid container spacing={3}>
              {/* 基本信息 */}
              <Grid item xs={12} md={4}>
                <Card elevation={2}>
                  <CardContent>
                    <Box display="flex" alignItems="center" mb={2}>
                      <PersonIcon color="primary" sx={{ mr: 1 }} />
                      <Typography variant="h6">基本信息</Typography>
                    </Box>
                    <Divider sx={{ mb: 2 }} />
                    <Typography variant="body1" gutterBottom>
                      <strong>姓名：</strong>
                      {parsedData.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {parsedData.phone}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {parsedData.email}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              {/* 能力评估 */}
              <Grid item xs={12} md={4}>
                <Card elevation={2}>
                  <CardContent>
                    <Box display="flex" alignItems="center" mb={2}>
                      <WorkIcon color="primary" sx={{ mr: 1 }} />
                      <Typography variant="h6">能力评估</Typography>
                    </Box>
                    <Divider sx={{ mb: 2 }} />
                    <Typography variant="body1" gutterBottom>
                      <strong>预估等级：</strong>
                      <Chip
                        label={parsedData.estimated_level}
                        color="primary"
                        size="small"
                        sx={{ ml: 1 }}
                      />
                    </Typography>
                    <Typography variant="body2" gutterBottom>
                      <strong>工作经验：</strong>
                      {parsedData.years_of_experience} 年
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              {/* 面试策略 */}
              <Grid item xs={12} md={4}>
                <Card elevation={2}>
                  <CardContent>
                    <Box display="flex" alignItems="center" mb={2}>
                      <StrategyIcon color="primary" sx={{ mr: 1 }} />
                      <Typography variant="h6">面试策略</Typography>
                    </Box>
                    <Divider sx={{ mb: 2 }} />
                    <Typography variant="body2" gutterBottom>
                      <strong>难度调整：</strong>
                      {parsedData.interview_strategy.difficulty_adjustment}
                    </Typography>
                    <Typography variant="body2">
                      <strong>场景设计题：</strong>
                      {parsedData.interview_strategy.scenario_design}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              {/* 教育背景 */}
              <Grid item xs={12} md={6}>
                <Card elevation={2}>
                  <CardContent>
                    <Box display="flex" alignItems="center" mb={2}>
                      <SchoolIcon color="primary" sx={{ mr: 1 }} />
                      <Typography variant="h6">教育背景</Typography>
                    </Box>
                    <Divider sx={{ mb: 2 }} />
                    {parsedData.education.map((edu: any, index: number) => (
                      <Box key={index} mb={1}>
                        <Typography variant="body1">
                          <strong>{edu.school}</strong>
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {edu.major} · {edu.degree} · {edu.graduation_year}年毕业
                        </Typography>
                      </Box>
                    ))}
                  </CardContent>
                </Card>
              </Grid>

              {/* 工作经历 */}
              <Grid item xs={12} md={6}>
                <Card elevation={2}>
                  <CardContent>
                    <Box display="flex" alignItems="center" mb={2}>
                      <WorkIcon color="primary" sx={{ mr: 1 }} />
                      <Typography variant="h6">工作经历</Typography>
                    </Box>
                    <Divider sx={{ mb: 2 }} />
                    {parsedData.work_experience.map((work: any, index: number) => (
                      <Box key={index} mb={1}>
                        <Typography variant="body1">
                          <strong>{work.company}</strong>
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {work.position} · {work.duration}
                        </Typography>
                      </Box>
                    ))}
                  </CardContent>
                </Card>
              </Grid>

              {/* 技能栈 */}
              <Grid item xs={12}>
                <Card elevation={2}>
                  <CardContent>
                    <Box display="flex" alignItems="center" mb={2}>
                      <CodeIcon color="primary" sx={{ mr: 1 }} />
                      <Typography variant="h6">技能栈</Typography>
                    </Box>
                    <Divider sx={{ mb: 2 }} />
                    
                    {Object.entries(parsedData.skills).map(([category, skills]: [string, any]) => (
                      <Box key={category} mb={2}>
                        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                          {category === 'programming_languages' && '编程语言'}
                          {category === 'databases' && '数据库'}
                          {category === 'frameworks' && '框架'}
                          {category === 'middleware' && '中间件'}
                          {category === 'tools' && '工具'}
                        </Typography>
                        <Box display="flex" flexWrap="wrap" gap={1}>
                          {skills.map((skill: string, index: number) => (
                            <Chip
                              key={index}
                              label={skill}
                              variant="outlined"
                              size="small"
                              color="primary"
                            />
                          ))}
                        </Box>
                      </Box>
                    ))}
                  </CardContent>
                </Card>
              </Grid>

              {/* 重点考察领域 */}
              <Grid item xs={12}>
                <Card elevation={2} sx={{ bgcolor: 'primary.light', color: 'white' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      🎯 重点考察领域
                    </Typography>
                    <Typography variant="body1">
                      根据您的简历，AI面试官将重点考察以下领域：
                    </Typography>
                    <Box display="flex" flexWrap="wrap" gap={1} mt={2}>
                      {parsedData.interview_strategy.focus_areas.map(
                        (area: string, index: number) => (
                          <Chip
                            key={index}
                            label={area}
                            sx={{
                              bgcolor: 'white',
                              color: 'primary.main',
                              fontWeight: 600,
                            }}
                          />
                        )
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* 开始面试按钮 */}
            <Zoom in={true} timeout={500}>
              <Box display="flex" justifyContent="center" mt={4}>
                <Button
                  variant="contained"
                  size="large"
                  onClick={handleStartInterview}
                  sx={{
                    px: 6,
                    py: 2,
                    fontSize: '1.2rem',
                    borderRadius: 3,
                    boxShadow: 4,
                  }}
                >
                  开始面试
                </Button>
              </Box>
            </Zoom>
          </Box>
        </Fade>
      )}
    </Box>
  )
}
