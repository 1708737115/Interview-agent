import { useState, createContext, useContext, useEffect } from 'react'
import { BrowserRouter, Routes, Route, useNavigate, useLocation, Navigate } from 'react-router-dom'
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Box,
  Typography,
  Paper,
  Breadcrumbs,
  Link,
  Fade,
  BottomNavigation,
  BottomNavigationAction,
  Container,
  AppBar,
  Toolbar,
  Stepper,
  Step,
  StepLabel,
  Button,
} from '@mui/material'
import {
  Home as HomeIcon,
  Upload as UploadIcon,
  Chat as ChatIcon,
  Assessment as ReportIcon,
  SmartToy as AIIcon,
  Build as BuildIcon,
  NavigateBefore as BackIcon,
} from '@mui/icons-material'
import Home from './pages/Home'
import InterviewSetup from './pages/InterviewSetup'
import Interview from './pages/Interview'
import Report from './pages/Report'
import DIYInterviewer from './pages/DIYInterviewer'
import './App.css'

// 创建主题
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
})

// 面试类型定义
export interface InterviewType {
  id: string
  name: string
  description: string
  icon: string
  knowledgeBase: string[]
  style: 'standard' | 'strict' | 'friendly'
  duration: number
  focusAreas: string[]
}

// 预设面试类型
export const PRESET_INTERVIEWS: InterviewType[] = [
  {
    id: 'backend',
    name: '后端开发面试',
    description: '针对Go/Java/Python后端开发岗位的全栈面试',
    icon: 'Code',
    knowledgeBase: ['go', 'java', 'mysql', 'redis', 'system-design'],
    style: 'standard',
    duration: 45,
    focusAreas: ['Go语言', 'MySQL', 'Redis', '系统设计'],
  },
  {
    id: 'go-backend',
    name: 'Go后端专项',
    description: '专注Go语言后端开发的深度面试',
    icon: 'GTranslate',
    knowledgeBase: ['go', 'mysql', 'redis'],
    style: 'strict',
    duration: 40,
    focusAreas: ['Go语言核心', 'GMP调度', 'GC机制'],
  },
  {
    id: 'java-backend',
    name: 'Java后端专项',
    description: 'Java生态后端技术深度考察',
    icon: 'Coffee',
    knowledgeBase: ['java', 'spring', 'mysql', 'redis'],
    style: 'standard',
    duration: 45,
    focusAreas: ['Java核心', 'Spring', 'JVM'],
  },
  {
    id: 'postgraduate',
    name: '考研复试面试',
    description: '计算机专业考研复试面试，侧重基础和项目',
    icon: 'School',
    knowledgeBase: ['cs-basic', 'algorithm', 'project'],
    style: 'friendly',
    duration: 30,
    focusAreas: ['计算机基础', '算法', '项目经历'],
  },
  {
    id: 'campus',
    name: '校招面试',
    description: '针对应届生的校招面试，基础+潜力考察',
    icon: 'EmojiPeople',
    knowledgeBase: ['cs-basic', 'algorithm'],
    style: 'friendly',
    duration: 35,
    focusAreas: ['基础概念', '算法', '学习能力'],
  },
]

// DIY面试官配置
export interface DIYInterviewerConfig {
  name: string
  style: 'strict' | 'standard' | 'friendly'
  focusAreas: string[]
  knowledgeBase: string[]
  duration: number
  maxFollowups: number
  customPrompt?: string
}

// 全局状态上下文
interface AppState {
  // 导航
  currentPage: string
  setCurrentPage: (page: string) => void
  
  // 面试类型选择
  selectedInterviewType: InterviewType | null
  setSelectedInterviewType: (type: InterviewType | null) => void
  
  // DIY配置
  diyConfig: DIYInterviewerConfig | null
  setDiyConfig: (config: DIYInterviewerConfig | null) => void
  
  // 简历和材料
  resumeData: any | null
  setResumeData: (data: any) => void
  supportingMaterials: File[]
  setSupportingMaterials: (files: File[]) => void
  
  // 面试会话
  sessionId: string | null
  setSessionId: (id: string | null) => void
  interviewData: any | null
  setInterviewData: (data: any) => void
  
  // 步骤控制
  setCurrentStep: (step: number) => void
}

const AppContext = createContext<AppState | undefined>(undefined)

export const useApp = () => {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useApp must be used within AppProvider')
  }
  return context
}

// localStorage key
const STORAGE_KEY = 'interview-agent-state'

// 应用内容组件
function AppContent() {
  const navigate = useNavigate()
  const location = useLocation()
  
  // 从 localStorage 加载初始状态
  const loadSavedState = () => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved) {
        return JSON.parse(saved)
      }
    } catch (e) {
      console.error('Failed to load state from localStorage:', e)
    }
    return null
  }
  
  const savedState = loadSavedState()
  
  // 从 URL 或 localStorage 确定当前页面
  const getInitialPage = () => {
    const path = location.pathname.slice(1) || 'home'
    return path
  }
  
  // 导航状态
  const [currentPage, setCurrentPageState] = useState<string>(getInitialPage())
  
  // 面试类型
  const [selectedInterviewType, setSelectedInterviewType] = useState<InterviewType | null>(savedState?.selectedInterviewType || null)
  
  // DIY配置
  const [diyConfig, setDiyConfig] = useState<DIYInterviewerConfig | null>(savedState?.diyConfig || null)
  
  // 简历和材料
  const [resumeData, setResumeData] = useState<any | null>(savedState?.resumeData || null)
  const [supportingMaterials, setSupportingMaterials] = useState<File[]>([])
  
  // 会话
  const [sessionId, setSessionId] = useState<string | null>(savedState?.sessionId || null)
  const [interviewData, setInterviewData] = useState<any | null>(savedState?.interviewData || null)

  // 设置当前页面（同时更新 URL）
  const setCurrentPage = (page: string) => {
    setCurrentPageState(page)
    navigate(`/${page === 'home' ? '' : page}`)
  }

  // URL 变化时同步状态
  useEffect(() => {
    const path = location.pathname.slice(1) || 'home'
    if (path !== currentPage) {
      setCurrentPageState(path)
    }
  }, [location.pathname])

  // 保存状态到 localStorage
  useEffect(() => {
    const stateToSave = {
      selectedInterviewType,
      diyConfig,
      resumeData,
      sessionId,
      interviewData,
    }
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(stateToSave))
    } catch (e) {
      console.error('Failed to save state to localStorage:', e)
    }
  }, [selectedInterviewType, diyConfig, resumeData, sessionId, interviewData])

  // 设置当前步骤（用于页面跳转）
  const setCurrentStep = (step: number) => {
    switch (step) {
      case 0:
        setCurrentPage('home')
        break
      case 1:
        setCurrentPage('setup')
        break
      case 2:
        setCurrentPage('interview')
        break
      case 3:
        setCurrentPage('report')
        break
      default:
        setCurrentPage('home')
    }
  }

  const appState: AppState = {
    currentPage,
    setCurrentPage,
    selectedInterviewType,
    setSelectedInterviewType,
    diyConfig,
    setDiyConfig,
    resumeData,
    setResumeData,
    supportingMaterials,
    setSupportingMaterials,
    sessionId,
    setSessionId,
    interviewData,
    setInterviewData,
    setCurrentStep,
  }

  // 获取当前步骤（用于步骤条）
  const getCurrentStep = () => {
    switch (currentPage) {
      case 'home':
      case 'diy':
        return 0
      case 'setup':
        return 1
      case 'interview':
        return 2
      case 'report':
        return 3
      default:
        return 0
    }
  }

  const steps = [
    { label: '选择面试', icon: <HomeIcon /> },
    { label: '上传简历', icon: <UploadIcon /> },
    { label: '智能面试', icon: <ChatIcon /> },
    { label: '查看报告', icon: <ReportIcon /> },
  ]

  // 面包屑路径配置
  const breadcrumbConfig: Record<string, { label: string; parent?: string }> = {
    home: { label: '首页' },
    diy: { label: 'DIY面试官', parent: 'home' },
    setup: { label: '上传简历', parent: 'home' },
    interview: { label: '智能面试', parent: 'setup' },
    report: { label: '查看报告', parent: 'interview' },
  }

  // 生成面包屑路径
  const generateBreadcrumbs = (): { label: string; page: string }[] => {
    const paths: { label: string; page: string }[] = []
    let currentPath: string | undefined = currentPage

    while (currentPath) {
      const crumbConfig: { label: string; parent?: string } | undefined = breadcrumbConfig[currentPath]
      if (crumbConfig) {
        paths.unshift({ label: crumbConfig.label, page: currentPath })
        currentPath = crumbConfig.parent
      } else {
        break
      }
    }

    return paths
  }

  // 处理面包屑点击
  const handleBreadcrumbClick = (page: string) => {
    if (page === 'report' && !interviewData) {
      return
    }
    setCurrentPage(page)
  }

  // 返回上一级
  const handleGoBack = () => {
    const currentConfig = breadcrumbConfig[currentPage]
    if (currentConfig?.parent) {
      handleBreadcrumbClick(currentConfig.parent)
    }
  }

  const breadcrumbs = generateBreadcrumbs()

  return (
    <AppContext.Provider value={appState}>
      <Box sx={{ flexGrow: 1, minHeight: '100vh', bgcolor: 'background.default', display: 'flex', flexDirection: 'column' }}>
        {/* 顶部导航栏 */}
        <AppBar position="static" elevation={0} sx={{ bgcolor: 'primary.main' }}>
          <Toolbar>
            <AIIcon sx={{ mr: 2, fontSize: 32 }} />
            <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 700 }}>
              AI智能面试官
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.9 }}>
              基于大语言模型的智能面试系统
            </Typography>
          </Toolbar>
        </AppBar>

        {/* 主要内容区域 */}
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4, flex: 1 }}>
          {/* 面包屑导航 */}
          {currentPage !== 'home' && (
            <Paper elevation={1} sx={{ p: 2, mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
              {breadcrumbConfig[currentPage]?.parent && (
                <Button
                  startIcon={<BackIcon />}
                  onClick={handleGoBack}
                  size="small"
                  variant="outlined"
                  sx={{ mr: 1 }}
                >
                  返回
                </Button>
              )}
              <Breadcrumbs separator="›" aria-label="breadcrumb">
                <Link
                  underline="hover"
                  color="inherit"
                  sx={{ cursor: 'pointer' }}
                  onClick={() => handleBreadcrumbClick('home')}
                >
                  首页
                </Link>
                {breadcrumbs.slice(1).map((crumb, index) => (
                  <Typography
                    key={crumb.page}
                    color={index === breadcrumbs.length - 2 ? 'text.primary' : 'inherit'}
                    sx={{ cursor: index === breadcrumbs.length - 2 ? 'default' : 'pointer' }}
                    onClick={() => index < breadcrumbs.length - 2 && handleBreadcrumbClick(crumb.page)}
                  >
                    {crumb.label}
                  </Typography>
                ))}
              </Breadcrumbs>
            </Paper>
          )}

          {/* 步骤条 - 只在面试流程中显示 */}
          {currentPage !== 'home' && currentPage !== 'diy' && (
            <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
              <Stepper activeStep={getCurrentStep()} alternativeLabel>
                {steps.map((step) => (
                  <Step key={step.label}>
                    <StepLabel StepIconProps={{ icon: step.icon }}>
                      {step.label}
                    </StepLabel>
                  </Step>
                ))}
              </Stepper>
            </Paper>
          )}

          {/* 页面内容 */}
          <Fade in={true} timeout={300}>
            <Box>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/home" element={<Navigate to="/" replace />} />
                <Route path="/diy" element={<DIYInterviewer />} />
                <Route path="/setup" element={<InterviewSetup />} />
                <Route path="/interview" element={<Interview />} />
                <Route path="/report" element={<Report />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Box>
          </Fade>
        </Container>

        {/* 底部导航 */}
        <Paper sx={{ position: 'fixed', bottom: 0, left: 0, right: 0 }} elevation={3}>
          <BottomNavigation
            showLabels
            value={currentPage === 'home' || currentPage === '' ? 0 : currentPage === 'diy' ? 1 : 0}
            onChange={(_event, newValue) => {
              if (newValue === 0) setCurrentPage('home')
              else if (newValue === 1) setCurrentPage('diy')
            }}
          >
            <BottomNavigationAction label="首页" icon={<HomeIcon />} />
            <BottomNavigationAction label="DIY面试官" icon={<BuildIcon />} />
          </BottomNavigation>
        </Paper>

        {/* 底部留白，避免被导航栏遮挡 */}
        <Box sx={{ height: 56 }} />
      </Box>
    </AppContext.Provider>
  )
}

// 主应用组件
function App() {
  return (
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AppContent />
      </ThemeProvider>
    </BrowserRouter>
  )
}

export default App
