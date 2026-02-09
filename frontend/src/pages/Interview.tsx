import { useState, useEffect, useRef, useMemo } from 'react'
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Avatar,
  Chip,
  LinearProgress,
  Fade,
  Card,
  CardContent,
  Divider,
  Grid,
} from '@mui/material'
import {
  Send as SendIcon,
  SmartToy as AIIcon,
  Person as PersonIcon,
  AccessTime as TimeIcon,
  QuestionAnswer as QuestionIcon,
  TrendingUp as ProgressIcon,
  NavigateNext as NextIcon,
} from '@mui/icons-material'
import { useApp } from '../App'
import './Interview.css'

// 题目数据结构
interface Question {
  id: string
  text: string
  category: string
  difficulty: number
  type: 'technical' | 'project' | 'design'
  followup?: string[]
}

// 完整题库
const QUESTION_BANK: Question[] = [
  // Go 语言题目
  { id: 'go-1', text: 'Go语言的goroutine和线程有什么区别？', category: 'Go语言', difficulty: 3, type: 'technical', followup: ['GMP调度模型中，P（Processor）的作用是什么？', 'goroutine的栈空间是如何管理的？'] },
  { id: 'go-2', text: 'Go语言的channel底层实现原理是什么？', category: 'Go语言', difficulty: 4, type: 'technical', followup: ['有缓冲channel和无缓冲channel的区别？', 'select语句是如何实现多路复用的？'] },
  { id: 'go-3', text: 'Go语言的垃圾回收机制是怎样的？', category: 'Go语言', difficulty: 4, type: 'technical', followup: ['三色标记法的工作原理？', '写屏障（Write Barrier）的作用？'] },
  { id: 'go-4', text: 'Go语言的interface底层是如何实现的？', category: 'Go语言', difficulty: 5, type: 'technical', followup: ['空接口和非空接口的区别？', '接口的动态类型是如何存储的？'] },
  { id: 'go-5', text: 'Go语言的context包有什么作用？', category: 'Go语言', difficulty: 3, type: 'technical', followup: ['如何实现请求超时控制？', 'context的取消信号是如何传递的？'] },
  { id: 'go-6', text: 'Go语言的defer语句执行顺序是怎样的？', category: 'Go语言', difficulty: 3, type: 'technical', followup: ['defer和return的执行顺序？', 'defer在循环中的使用注意事项？'] },
  { id: 'go-7', text: 'Go语言的sync.Map和原生map有什么区别？', category: 'Go语言', difficulty: 4, type: 'technical', followup: ['sync.Map的实现原理？', '什么场景下适合使用sync.Map？'] },
  { id: 'go-8', text: 'Go语言的slice底层结构是什么样的？', category: 'Go语言', difficulty: 3, type: 'technical', followup: ['slice的扩容机制？', 'slice作为函数参数是值传递还是引用传递？'] },
  
  // MySQL 题目
  { id: 'mysql-1', text: 'MySQL的索引底层使用什么数据结构？为什么选择这种结构？', category: 'MySQL', difficulty: 4, type: 'technical', followup: ['B+树和B树的区别？', '索引的最左前缀原则？'] },
  { id: 'mysql-2', text: 'MySQL的事务隔离级别有哪些？分别解决了什么问题？', category: 'MySQL', difficulty: 3, type: 'technical', followup: ['幻读和不可重复读的区别？', 'MVCC是如何实现的？'] },
  { id: 'mysql-3', text: 'MySQL的InnoDB存储引擎有什么特点？', category: 'MySQL', difficulty: 4, type: 'technical', followup: ['InnoDB的锁机制？', 'redo log和undo log的作用？'] },
  { id: 'mysql-4', text: '如何优化MySQL的慢查询？', category: 'MySQL', difficulty: 4, type: 'technical', followup: ['Explain命令的关键字段解读？', '覆盖索引和回表查询？'] },
  { id: 'mysql-5', text: 'MySQL的主从复制原理是什么？', category: 'MySQL', difficulty: 4, type: 'technical', followup: ['binlog的三种格式有什么区别？', '主从延迟的原因和解决方案？'] },
  { id: 'mysql-6', text: 'MySQL的锁有哪些类型？', category: 'MySQL', difficulty: 3, type: 'technical', followup: ['行锁和表锁的区别？', '意向锁的作用？'] },
  { id: 'mysql-7', text: 'MySQL的索引设计原则有哪些？', category: 'MySQL', difficulty: 3, type: 'technical', followup: ['什么情况下不适合创建索引？', '联合索引的设计注意事项？'] },
  
  // Redis 题目
  { id: 'redis-1', text: 'Redis为什么这么快？', category: 'Redis', difficulty: 3, type: 'technical', followup: ['Redis的I/O多路复用？', 'Redis的单线程模型？'] },
  { id: 'redis-2', text: 'Redis的数据类型有哪些？分别适合什么场景？', category: 'Redis', difficulty: 3, type: 'technical', followup: ['Sorted Set底层实现？', 'HyperLogLog的使用场景？'] },
  { id: 'redis-3', text: 'Redis的持久化机制有哪些？', category: 'Redis', difficulty: 4, type: 'technical', followup: ['RDB和AOF的优缺点？', 'AOF重写的原理？'] },
  { id: 'redis-4', text: 'Redis的缓存穿透、缓存击穿、缓存雪崩是什么？如何解决？', category: 'Redis', difficulty: 4, type: 'technical', followup: ['布隆过滤器的原理？', '热点key的解决方案？'] },
  { id: 'redis-5', text: 'Redis的集群方案有哪些？', category: 'Redis', difficulty: 5, type: 'technical', followup: ['Redis Cluster的数据分片？', '一致性哈希的原理？'] },
  { id: 'redis-6', text: 'Redis的过期删除策略有哪些？', category: 'Redis', difficulty: 4, type: 'technical', followup: ['惰性删除和定期删除的区别？', '内存淘汰策略有哪些？'] },
  
  // 系统设计题目
  { id: 'design-1', text: '设计一个秒杀系统，要求支持10万QPS，如何保证不超卖？', category: '系统设计', difficulty: 5, type: 'design' },
  { id: 'design-2', text: '如何设计一个短链接服务？', category: '系统设计', difficulty: 4, type: 'design' },
  { id: 'design-3', text: '设计一个消息推送系统，支持千万级用户', category: '系统设计', difficulty: 5, type: 'design' },
  { id: 'design-4', text: '设计一个分布式ID生成器', category: '系统设计', difficulty: 4, type: 'design' },
  { id: 'design-5', text: '如何设计一个高并发的计数器系统？', category: '系统设计', difficulty: 4, type: 'design' },
  { id: 'design-6', text: '设计一个实时排行榜系统', category: '系统设计', difficulty: 4, type: 'design' },
  
  // 项目深挖题目（需要根据简历动态生成，这里是示例）
  { id: 'project-1', text: '请介绍你最近参与的最有挑战性的项目', category: '项目经历', difficulty: 4, type: 'project', followup: ['你在项目中具体负责什么？', '遇到了什么技术难点？如何解决的？', '如果重新做这个项目，你会如何改进？'] },
  { id: 'project-2', text: '你提到做过性能优化，能具体说说吗？', category: '项目经历', difficulty: 4, type: 'project', followup: ['优化的指标是什么？', '采取了哪些优化手段？', '优化前后的对比数据？'] },
  { id: 'project-3', text: '项目中遇到过什么线上故障？如何处理的？', category: '项目经历', difficulty: 4, type: 'project', followup: ['故障的原因是什么？', '如何快速定位问题？', '事后有什么改进措施？'] },
]

// 开场白
const OPENING_QUESTIONS = [
  ['你好，请简单介绍一下自己。', '今天的面试大概需要45分钟，分为技术基础、项目深挖和场景设计三个环节。你准备好了吗？'],
  ['欢迎参加面试！请先做个自我介绍吧。', '本次面试将考察你的技术深度和项目经验，预计40-50分钟。'],
  ['你好，很高兴见到你。请简单介绍一下你的背景。', '我们会聊一些技术问题和你过往的项目经历，准备好了吗？'],
]

// 结束语
const CLOSING_MESSAGES = [
  '今天的面试到此结束，感谢你的参与！你有什么问题想问我吗？',
  '面试环节已经结束，谢谢你的配合。有什么想了解的可以问我。',
  '好的，面试就到这里。你对这个岗位或者公司有什么想了解的吗？',
]

// 根据技能栈筛选题目
function filterQuestionsBySkills(questions: Question[], skills: string[]): Question[] {
  if (!skills || skills.length === 0) return questions
  
  // 技能关键词匹配
  const skillKeywords: Record<string, string[]> = {
    'Go': ['Go', 'Golang', 'Goroutine', 'Channel'],
    'Java': ['Java', 'Spring', 'JVM'],
    'Python': ['Python', 'Django', 'Flask'],
    'MySQL': ['MySQL', 'SQL', '索引', '事务'],
    'Redis': ['Redis', '缓存'],
    'MongoDB': ['MongoDB', 'NoSQL'],
    'Kafka': ['Kafka', '消息队列'],
    'RocketMQ': ['RocketMQ', '消息队列'],
  }
  
  return questions.filter(q => {
    // 检查题目是否匹配用户的技能栈
    for (const skill of skills) {
      const keywords = skillKeywords[skill] || [skill]
      for (const keyword of keywords) {
        if (q.category.includes(keyword) || q.text.includes(keyword)) {
          return true
        }
      }
    }
    return false
  })
}

// 随机打乱数组
function shuffleArray<T>(array: T[]): T[] {
  const shuffled = [...array]
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
  }
  return shuffled
}

// 生成面试流程
function generateInterviewFlow(skills: string[], experienceYears: number): InterviewFlow[] {
  const flow: InterviewFlow[] = []
  
  // 1. 开场白（随机选择一组）
  const opening = OPENING_QUESTIONS[Math.floor(Math.random() * OPENING_QUESTIONS.length)]
  flow.push({
    type: 'opening',
    phase: '开场破冰',
    questions: opening,
  })
  
  // 2. 技术基础题（根据技能筛选，随机选择3-4道）
  const technicalQuestions = filterQuestionsBySkills(
    QUESTION_BANK.filter(q => q.type === 'technical'),
    skills
  )
  const selectedTech = shuffleArray(technicalQuestions).slice(0, 4)
  
  for (let i = 0; i < selectedTech.length; i++) {
    const q = selectedTech[i]
    flow.push({
      type: 'technical',
      phase: '技术基础',
      question: {
        id: q.id,
        text: q.text,
        category: q.category,
        difficulty: q.difficulty,
      },
    })
    
    // 50% 概率添加追问
    if (q.followup && q.followup.length > 0 && Math.random() > 0.5) {
      const followup = q.followup[Math.floor(Math.random() * q.followup.length)]
      flow.push({
        type: 'followup',
        phase: '追问环节',
        question: followup,
        strategy: '深度追问',
      })
    }
  }
  
  // 3. 项目深挖（1-2道）
  const projectQuestions = QUESTION_BANK.filter(q => q.type === 'project')
  const selectedProject = shuffleArray(projectQuestions).slice(0, 1 + Math.floor(Math.random() * 2))
  
  for (const q of selectedProject) {
    flow.push({
      type: 'project',
      phase: '项目深挖',
      question: {
        id: q.id,
        text: q.text,
        category: q.category,
        difficulty: q.difficulty,
      },
    })
  }
  
  // 4. 系统设计（根据经验年限选择难度）
  const designQuestions = QUESTION_BANK.filter(q => q.type === 'design')
  // 经验越多，难度越高
  const difficultyThreshold = experienceYears >= 5 ? 5 : experienceYears >= 3 ? 4 : 3
  const suitableDesign = designQuestions.filter(q => q.difficulty <= difficultyThreshold)
  const selectedDesign = suitableDesign[Math.floor(Math.random() * suitableDesign.length)]
  
  if (selectedDesign) {
    flow.push({
      type: 'design',
      phase: '场景设计',
      question: {
        id: selectedDesign.id,
        text: selectedDesign.text,
        category: selectedDesign.category,
        difficulty: selectedDesign.difficulty,
      },
    })
  }
  
  return flow
}

interface InterviewQuestion2 {
  id: string
  text: string
  category: string
  difficulty: number
}

interface InterviewFlow {
  type: 'opening' | 'technical' | 'followup' | 'project' | 'design'
  phase: string
  questions?: string[]
  question?: InterviewQuestion2 | string
  strategy?: string
}

interface Message {
  id: string
  role: 'interviewer' | 'candidate'
  content: string
  timestamp: Date
  evaluation?: {
    score: number
    feedback: string
    assessment?: string
    answerLength?: number
    hasTechnicalKeywords?: boolean
    hasExplanation?: boolean
    hasCodeExample?: boolean
    hasRealCase?: boolean
    questionText?: string
    questionCategory?: string
  }
  isFollowup?: boolean
}

export default function Interview() {
  const { resumeData, setCurrentStep, setInterviewData } = useApp()
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [elapsedTime, setElapsedTime] = useState(0)
  const [totalScore, setTotalScore] = useState(0)
  const [questionCount, setQuestionCount] = useState(0)
  const [isInterviewEnded, setIsInterviewEnded] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // 根据简历数据动态生成面试流程
  const interviewFlow = useMemo(() => {
    const skills = resumeData?.skills ? Object.values(resumeData.skills).flat() as string[] : ['Go', 'MySQL', 'Redis']
    const years = resumeData?.years_of_experience || 3
    return generateInterviewFlow(skills, years)
  }, [resumeData])

  // 计时器
  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedTime((prev) => prev + 1)
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // 初始化开场问题
  useEffect(() => {
    if (messages.length === 0) {
      const opening = interviewFlow[0]
      if (opening.questions) {
        opening.questions.forEach((q) => {
          addMessage('interviewer', q)
        })
      }
    }
  }, [interviewFlow])

  const addMessage = (role: 'interviewer' | 'candidate', content: string, extra?: any) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      role,
      content,
      timestamp: new Date(),
      ...extra,
    }
    setMessages((prev) => [...prev, newMessage])
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    // 添加用户消息
    addMessage('candidate', inputMessage)
    setInputMessage('')
    setIsLoading(true)

    // 模拟API调用延迟
    await new Promise((resolve) => setTimeout(resolve, 1500))

    // 基于回答质量的评估
    const answerLength = inputMessage.trim().length
    const answerContent = inputMessage.trim()
    const hasTechnicalKeywords = /\b(go|goroutine|channel|mysql|redis|索引|调度|gc|并发|锁|缓存|事务|数据库|算法|数据结构|架构|系统|设计|优化|性能)\b/i.test(answerContent)
    const hasExplanation = answerContent.includes('因为') || answerContent.includes('所以') || answerContent.includes('例如') || answerContent.includes('比如') || answerContent.includes('首先') || answerContent.includes('其次') || answerContent.includes('最后')
    const hasCodeExample = /```|`[^`]+`/.test(answerContent) || answerContent.includes('func ') || answerContent.includes('func(') || answerContent.includes('class ') || answerContent.includes('def ')
    const hasRealCase = answerContent.includes('项目') || answerContent.includes('实际') || answerContent.includes('曾经') || answerContent.includes('之前') || answerContent.includes('做过')
    
    // 获取当前问题信息
    const currentQuestion = interviewFlow[currentQuestionIndex]
    const questionText = typeof currentQuestion?.question === 'object' ? currentQuestion?.question?.text : currentQuestion?.question
    const questionCategory = typeof currentQuestion?.question === 'object' ? currentQuestion?.question?.category : '技术问题'
    
    // 详细评估
    let score: number
    let feedback: string
    let assessment: string = ''
    
    if (answerLength < 5) {
      score = Math.floor(Math.random() * 10) + 35 // 35-44分
      feedback = '回答过于简短，几乎没有任何实质内容'
      assessment = 'too_short'
    } else if (answerLength < 15) {
      score = Math.floor(Math.random() * 15) + 45 // 45-59分
      feedback = '回答过于简短，需要展开说明'
      assessment = 'too_short'
    } else if (answerLength < 30) {
      if (!hasTechnicalKeywords) {
        score = Math.floor(Math.random() * 10) + 50 // 50-59分
        feedback = '回答缺少专业技术术语，显得不够深入'
        assessment = 'lack_technical'
      } else {
        score = Math.floor(Math.random() * 10) + 60 // 60-69分
        feedback = '回答较为简单，缺少深入分析'
        assessment = 'shallow'
      }
    } else if (!hasTechnicalKeywords && !hasExplanation) {
      score = Math.floor(Math.random() * 15) + 55 // 55-69分
      feedback = '回答未体现技术理解，需要更专业的表达'
      assessment = 'lack_technical'
    } else if (hasTechnicalKeywords && hasExplanation && (hasCodeExample || hasRealCase)) {
      score = Math.floor(Math.random() * 15) + 80 // 80-94分
      feedback = '回答非常优秀，既有理论又有实践'
      assessment = 'excellent'
    } else if (hasTechnicalKeywords && hasExplanation) {
      score = Math.floor(Math.random() * 15) + 70 // 70-84分
      feedback = '回答涵盖技术点且有清晰解释'
      assessment = 'good'
    } else if (hasTechnicalKeywords) {
      score = Math.floor(Math.random() * 15) + 65 // 65-79分
      feedback = '提到了技术点，但缺少深入解释'
      assessment = 'partial'
    } else {
      score = Math.floor(Math.random() * 15) + 60 // 60-74分
      feedback = '回答尚可，但可以更加完整和深入'
      assessment = 'average'
    }
    
    const evaluation = { 
      score, 
      feedback,
      assessment,
      answerLength,
      hasTechnicalKeywords,
      hasExplanation,
      hasCodeExample,
      hasRealCase,
      questionText,
      questionCategory
    }

    // 更新总分
    setTotalScore((prev) => prev + evaluation.score)
    setQuestionCount((prev) => prev + 1)

    // 根据当前进度返回下一步
    if (currentQuestionIndex < interviewFlow.length - 1) {
      const nextIndex = currentQuestionIndex + 1
      setCurrentQuestionIndex(nextIndex)
      const nextFlow = interviewFlow[nextIndex]

      if (nextFlow.type === 'followup' && typeof nextFlow.question === 'string') {
        addMessage('interviewer', nextFlow.question, {
          isFollowup: true,
          evaluation,
        })
      } else if (nextFlow.question && typeof nextFlow.question === 'object') {
        addMessage('interviewer', nextFlow.question.text, {
          evaluation,
        })
      }
    } else {
      // 面试结束 - 随机选择结束语
      const closing = CLOSING_MESSAGES[Math.floor(Math.random() * CLOSING_MESSAGES.length)]
      addMessage('interviewer', closing)
    }

    setIsLoading(false)
  }

  const handleEndInterview = () => {
    const avgScore = questionCount > 0 ? Math.round(totalScore / questionCount) : 0
    setIsInterviewEnded(true)
    setInterviewData({
      totalScore: avgScore,
      duration: elapsedTime,
      questionCount,
      messages,
    })
    setCurrentStep(3)
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const currentFlow = interviewFlow[currentQuestionIndex]

  return (
    <Box sx={{ height: 'calc(100vh - 250px)', display: 'flex', gap: 2 }}>
      {/* 左侧对话区域 */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* 进度和状态栏 */}
        <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
          <Grid container alignItems="center" spacing={2}>
            <Grid item xs={3}>
              <Box display="flex" alignItems="center">
                <TimeIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">{formatTime(elapsedTime)}</Typography>
              </Box>
              <Typography variant="caption" color="text.secondary">
                / 45:00
              </Typography>
            </Grid>
            <Grid item xs={3}>
              <Box display="flex" alignItems="center">
                <QuestionIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">{questionCount}</Typography>
              </Box>
              <Typography variant="caption" color="text.secondary">
                问题数
              </Typography>
            </Grid>
            <Grid item xs={3}>
              <Box display="flex" alignItems="center">
                <ProgressIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">
                  {questionCount > 0 ? Math.round(totalScore / questionCount) : 0}
                </Typography>
              </Box>
              <Typography variant="caption" color="text.secondary">
                平均分
              </Typography>
            </Grid>
            <Grid item xs={3}>
              <Chip
                label={currentFlow?.phase || '面试中'}
                color="primary"
                sx={{ fontWeight: 600 }}
              />
            </Grid>
          </Grid>
          <LinearProgress
            variant="determinate"
            value={(elapsedTime / (45 * 60)) * 100}
            sx={{ mt: 2, height: 6, borderRadius: 3 }}
          />
        </Paper>

        {/* 消息列表 */}
        <Paper
          elevation={2}
          sx={{
            flex: 1,
            overflow: 'auto',
            p: 2,
            mb: 2,
            bgcolor: 'grey.50',
          }}
        >
          {messages.map((message) => (
            <Fade key={message.id} in={true} timeout={300}>
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: message.role === 'candidate' ? 'flex-end' : 'flex-start',
                  mb: 2,
                }}
              >
                <Box
                  sx={{
                    display: 'flex',
                    flexDirection: message.role === 'candidate' ? 'row-reverse' : 'row',
                    alignItems: 'flex-start',
                    maxWidth: '80%',
                  }}
                >
                  <Avatar
                    sx={{
                      bgcolor: message.role === 'candidate' ? 'secondary.main' : 'primary.main',
                      mr: message.role === 'candidate' ? 0 : 1,
                      ml: message.role === 'candidate' ? 1 : 0,
                    }}
                  >
                    {message.role === 'candidate' ? <PersonIcon /> : <AIIcon />}
                  </Avatar>
                  <Box>
                    <Paper
                      elevation={1}
                      sx={{
                        p: 2,
                        bgcolor: message.role === 'candidate' ? 'secondary.light' : 'white',
                        color: message.role === 'candidate' ? 'white' : 'inherit',
                        borderRadius: 2,
                      }}
                    >
                      <Typography variant="body1">{message.content}</Typography>
                    </Paper>
                    
                    {/* 评估信息 - 只在面试结束后显示 */}
                    {isInterviewEnded && message.evaluation && message.role === 'interviewer' && (
                      <Box mt={1}>
                        <Chip
                          label={`评分: ${message.evaluation.score}分`}
                          size="small"
                          color={message.evaluation.score >= 80 ? 'success' : 'warning'}
                          sx={{ mr: 1 }}
                        />
                        {message.isFollowup && (
                          <Chip
                            label="追问"
                            size="small"
                            color="info"
                            variant="outlined"
                          />
                        )}
                      </Box>
                    )}
                  </Box>
                </Box>
              </Box>
            </Fade>
          ))}
          
          {isLoading && (
            <Box display="flex" justifyContent="flex-start" mb={2}>
              <Box display="flex" alignItems="center">
                <Avatar sx={{ bgcolor: 'primary.main', mr: 1 }}>
                  <AIIcon />
                </Avatar>
                <Paper elevation={1} sx={{ p: 2, borderRadius: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    AI面试官正在思考...
                  </Typography>
                </Paper>
              </Box>
            </Box>
          )}
          
          <div ref={messagesEndRef} />
        </Paper>

        {/* 输入区域 */}
        <Paper elevation={2} sx={{ p: 2 }}>
          <Box display="flex" gap={1}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="输入你的回答..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              disabled={isLoading}
              multiline
              maxRows={4}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 3,
                },
              }}
            />
            <Button
              variant="contained"
              color="primary"
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isLoading}
              sx={{ minWidth: 100, borderRadius: 3 }}
              endIcon={<SendIcon />}
            >
              发送
            </Button>
          </Box>
        </Paper>
      </Box>

      {/* 右侧信息面板 */}
      <Box sx={{ width: 300, display: { xs: 'none', md: 'block' } }}>
        <Card elevation={2} sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              候选人信息
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="body1" gutterBottom>
              <strong>{resumeData?.name || '张三'}</strong>
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {resumeData?.estimated_level || '中级'} · {resumeData?.years_of_experience || 3.5}年经验
            </Typography>
            <Box mt={2}>
              <Typography variant="caption" color="text.secondary">
                重点考察领域：
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={0.5} mt={0.5}>
                {(resumeData?.interview_strategy?.focus_areas || ['Go', 'MySQL', 'Redis']).map(
                  (area: string, index: number) => (
                    <Chip key={index} label={area} size="small" variant="outlined" />
                  )
                )}
              </Box>
            </Box>
          </CardContent>
        </Card>

        <Card elevation={2} sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              面试指南
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="body2" paragraph>
              <strong>1.</strong> 请认真回答每个问题，展示自己的技术能力
            </Typography>
            <Typography variant="body2" paragraph>
              <strong>2.</strong> 面试官可能会根据回答进行追问，请做好准备
            </Typography>
            <Typography variant="body2" paragraph>
              <strong>3.</strong> 系统设计题需要详细说明设计思路和方案
            </Typography>
            <Typography variant="body2">
              <strong>4.</strong> 保持冷静，展现你的思维过程
            </Typography>
          </CardContent>
        </Card>

        <Button
          variant="outlined"
          color="secondary"
          fullWidth
          onClick={handleEndInterview}
          startIcon={<NextIcon />}
          sx={{ borderRadius: 3 }}
        >
          结束面试并查看报告
        </Button>
      </Box>
    </Box>
  )
}
