import { useState } from 'react'
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Slider,
  Chip,
  Grid,
  Card,
  CardContent,
  Alert,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material'
import {
  Build as BuildIcon,
  ArrowBack as BackIcon,
  Save as SaveIcon,
  PlayArrow as StartIcon,
} from '@mui/icons-material'
import { useApp, DIYInterviewerConfig } from '../App'

// 可选的题库范围
const KNOWLEDGE_BASE_OPTIONS = [
  { id: 'go', name: 'Go语言', description: 'Go基础、并发、标准库' },
  { id: 'java', name: 'Java', description: 'Java核心、JVM、Spring' },
  { id: 'python', name: 'Python', description: 'Python基础、框架' },
  { id: 'mysql', name: 'MySQL', description: '数据库、SQL优化' },
  { id: 'redis', name: 'Redis', description: '缓存、数据结构' },
  { id: 'network', name: '计算机网络', description: 'TCP/IP、HTTP' },
  { id: 'system', name: '操作系统', description: 'Linux、进程线程' },
  { id: 'algorithm', name: '算法', description: '数据结构、算法题' },
  { id: 'system-design', name: '系统设计', description: '架构、分布式' },
  { id: 'cs-basic', name: '计算机基础', description: '组成原理、编译原理' },
]

// 面试风格选项
const STYLE_OPTIONS = [
  { value: 'strict', label: '严格模式', description: '直接指出问题，高标准要求，适合正式面试' },
  { value: 'standard', label: '标准模式', description: '循序渐进，平衡追问，适合大多数场景' },
  { value: 'friendly', label: '友好模式', description: '鼓励为主，耐心引导，适合初学者和校招' },
]

// 关注领域选项
const FOCUS_AREA_OPTIONS = [
  '基础知识', '项目经验', '算法能力', '系统设计', 
  '沟通能力', '学习能力', '问题解决', '团队协作'
]

export default function DIYInterviewer() {
  const { setCurrentPage, setDiyConfig, setSelectedInterviewType } = useApp()
  const [activeStep, setActiveStep] = useState(0)
  const [config, setConfig] = useState<DIYInterviewerConfig>({
    name: '',
    style: 'standard',
    focusAreas: ['基础知识', '项目经验'],
    knowledgeBase: ['go', 'mysql', 'redis'],
    duration: 45,
    maxFollowups: 8,
    customPrompt: '',
  })
  const [saved, setSaved] = useState(false)

  const steps = ['基本设置', '题库选择', '高级配置']

  const handleConfigChange = (field: keyof DIYInterviewerConfig, value: any) => {
    setConfig({ ...config, [field]: value })
    setSaved(false)
  }

  const handleKnowledgeBaseToggle = (id: string) => {
    const current = config.knowledgeBase
    const updated = current.includes(id)
      ? current.filter(k => k !== id)
      : [...current, id]
    handleConfigChange('knowledgeBase', updated)
  }

  const handleFocusAreaToggle = (area: string) => {
    const current = config.focusAreas
    const updated = current.includes(area)
      ? current.filter(a => a !== area)
      : [...current, area]
    handleConfigChange('focusAreas', updated)
  }

  const handleSave = () => {
    setDiyConfig(config)
    setSaved(true)
  }

  const handleStart = () => {
    // 将DIY配置转换为InterviewType格式
    const customInterview = {
      id: 'custom_' + Date.now(),
      name: config.name || '自定义面试',
      description: `DIY面试官 - ${config.style === 'strict' ? '严格' : config.style === 'friendly' ? '友好' : '标准'}模式`,
      icon: 'Build',
      knowledgeBase: config.knowledgeBase,
      style: config.style,
      duration: config.duration,
      focusAreas: config.focusAreas,
    }
    
    setSelectedInterviewType(customInterview)
    setCurrentPage('setup')
  }

  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return renderBasicSettings()
      case 1:
        return renderKnowledgeBaseSelection()
      case 2:
        return renderAdvancedSettings()
      default:
        return renderBasicSettings()
    }
  }

  const renderBasicSettings = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        基本设置
      </Typography>

      <TextField
        fullWidth
        label="面试官名称"
        placeholder="例如：考研复试面试官"
        value={config.name}
        onChange={(e) => handleConfigChange('name', e.target.value)}
        sx={{ mb: 3 }}
        helperText="给你的面试官起个名字，方便识别"
      />

      <Typography variant="subtitle2" gutterBottom>
        面试风格
      </Typography>
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {STYLE_OPTIONS.map((style) => (
          <Grid item xs={12} md={4} key={style.value}>
            <Card
              variant={config.style === style.value ? 'elevation' : 'outlined'}
              elevation={config.style === style.value ? 4 : 0}
              sx={{
                cursor: 'pointer',
                borderColor: config.style === style.value ? 'primary.main' : undefined,
                bgcolor: config.style === style.value ? 'primary.light' : undefined,
                color: config.style === style.value ? 'white' : undefined,
              }}
              onClick={() => handleConfigChange('style', style.value)}
            >
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {style.label}
                </Typography>
                <Typography variant="body2" sx={{ opacity: config.style === style.value ? 0.9 : 0.7 }}>
                  {style.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Typography variant="subtitle2" gutterBottom>
        关注领域
      </Typography>
      <Box sx={{ mb: 3 }}>
        {FOCUS_AREA_OPTIONS.map((area) => (
          <Chip
            key={area}
            label={area}
            onClick={() => handleFocusAreaToggle(area)}
            color={config.focusAreas.includes(area) ? 'primary' : 'default'}
            variant={config.focusAreas.includes(area) ? 'filled' : 'outlined'}
            sx={{ m: 0.5 }}
          />
        ))}
      </Box>

      <Typography variant="subtitle2" gutterBottom>
        面试时长: {config.duration} 分钟
      </Typography>
      <Slider
        value={config.duration}
        onChange={(_, value) => handleConfigChange('duration', value)}
        min={15}
        max={90}
        step={5}
        marks={[
          { value: 15, label: '15分' },
          { value: 30, label: '30分' },
          { value: 45, label: '45分' },
          { value: 60, label: '60分' },
          { value: 90, label: '90分' },
        ]}
        valueLabelDisplay="auto"
        sx={{ mb: 3 }}
      />
    </Box>
  )

  const renderKnowledgeBaseSelection = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        选择题库范围
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        选择要考察的技术领域，AI将从这些题库中抽取问题
      </Typography>

      <Grid container spacing={2}>
        {KNOWLEDGE_BASE_OPTIONS.map((kb) => (
          <Grid item xs={12} sm={6} md={4} key={kb.id}>
            <Card
              variant={config.knowledgeBase.includes(kb.id) ? 'elevation' : 'outlined'}
              elevation={config.knowledgeBase.includes(kb.id) ? 2 : 0}
              sx={{
                cursor: 'pointer',
                borderColor: config.knowledgeBase.includes(kb.id) ? 'primary.main' : undefined,
              }}
              onClick={() => handleKnowledgeBaseToggle(kb.id)}
            >
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Typography variant="h6" fontSize="1.1rem">
                    {kb.name}
                  </Typography>
                  {config.knowledgeBase.includes(kb.id) && (
                    <Chip label="已选" size="small" color="primary" />
                  )}
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  {kb.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Alert severity="info" sx={{ mt: 3 }}>
        <Typography variant="body2">
          已选择 {config.knowledgeBase.length} 个题库领域，面试将覆盖这些技术栈
        </Typography>
      </Alert>
    </Box>
  )

  const renderAdvancedSettings = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        高级配置
      </Typography>

      <Typography variant="subtitle2" gutterBottom>
        最大追问次数: {config.maxFollowups} 次
      </Typography>
      <Slider
        value={config.maxFollowups}
        onChange={(_, value) => handleConfigChange('maxFollowups', value)}
        min={0}
        max={15}
        step={1}
        marks={[
          { value: 0, label: '0' },
          { value: 5, label: '5' },
          { value: 8, label: '8' },
          { value: 10, label: '10' },
          { value: 15, label: '15' },
        ]}
        valueLabelDisplay="auto"
        sx={{ mb: 3 }}
      />

      <Typography variant="subtitle2" gutterBottom>
        自定义系统提示词（可选）
      </Typography>
      <TextField
        fullWidth
        multiline
        rows={4}
        placeholder="例如：你是一位考研复试面试官，重点关注学生的基础知识掌握程度和学习潜力..."
        value={config.customPrompt}
        onChange={(e) => handleConfigChange('customPrompt', e.target.value)}
        sx={{ mb: 2 }}
        helperText="自定义AI面试官的人设和行为准则，可以创建更个性化的面试体验"
      />

      {saved && (
        <Alert severity="success" sx={{ mt: 2 }}>
          配置已保存！现在可以开始面试了
        </Alert>
      )}
    </Box>
  )

  return (
    <Box>
      {/* 标题 */}
      <Paper elevation={3} sx={{ p: 4, mb: 4, textAlign: 'center', bgcolor: 'secondary.main', color: 'white' }}>
        <BuildIcon sx={{ fontSize: 48, mb: 2 }} />
        <Typography variant="h4" gutterBottom fontWeight={700}>
          DIY 面试官
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.9 }}>
          打造专属于你的面试官
        </Typography>
      </Paper>

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
        <Box>
          <Button
            variant="outlined"
            startIcon={<BackIcon />}
            onClick={() => activeStep === 0 ? setCurrentPage('home') : setActiveStep(activeStep - 1)}
            sx={{ mr: 2 }}
          >
            {activeStep === 0 ? '返回首页' : '上一步'}
          </Button>
          
          {activeStep === steps.length - 1 && (
            <Button
              variant="outlined"
              startIcon={<SaveIcon />}
              onClick={handleSave}
              color="success"
            >
              保存配置
            </Button>
          )}
        </Box>

        <Box>
          {activeStep < steps.length - 1 ? (
            <Button
              variant="contained"
              onClick={() => setActiveStep(activeStep + 1)}
            >
              下一步
            </Button>
          ) : (
            <Button
              variant="contained"
              color="secondary"
              startIcon={<StartIcon />}
              onClick={handleStart}
              disabled={config.knowledgeBase.length === 0}
            >
              开始面试
            </Button>
          )}
        </Box>
      </Box>

      {/* 提示 */}
      {activeStep === steps.length - 1 && config.knowledgeBase.length === 0 && (
        <Alert severity="warning" sx={{ mt: 2 }}>
          请至少选择一个题库领域
        </Alert>
      )}
    </Box>
  )
}
