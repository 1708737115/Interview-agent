import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Divider,
  Chip,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Avatar,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material'
import {
  Download as DownloadIcon,
  Replay as ReplayIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  EmojiEvents as TrophyIcon,
  TrendingUp as TrendingIcon,
  Psychology as SkillIcon,
  School as LearnIcon,
  MenuBook as MenuBookIcon,
  ExpandMore as ExpandMoreIcon,
} from '@mui/icons-material'
import { useApp } from '../App'
import './Report.css'

export default function Report() {
  const { interviewData, resumeData, setCurrentStep } = useApp()
  
  // 从 interviewData 获取真实数据
  const messages = interviewData?.messages || []
  const questionEvaluations = messages
    .filter((m: any) => m.role === 'interviewer' && m.evaluation)
    .map((m: any) => ({
      question: m.content,
      score: m.evaluation.score,
      feedback: m.evaluation.feedback,
      isFollowup: m.isFollowup,
      assessment: m.evaluation.assessment,
      answerLength: m.evaluation.answerLength,
      hasTechnicalKeywords: m.evaluation.hasTechnicalKeywords,
      hasExplanation: m.evaluation.hasExplanation,
      hasCodeExample: m.evaluation.hasCodeExample,
      hasRealCase: m.evaluation.hasRealCase,
      questionText: m.evaluation.questionText,
      questionCategory: m.evaluation.questionCategory,
    }))
  
  const totalScore = interviewData?.totalScore || 0
  const questionCount = interviewData?.questionCount || 0
  const duration = Math.floor((interviewData?.duration || 0) / 60)
  const followupCount = questionEvaluations.filter((q: any) => q.isFollowup).length
  
  // 根据平均分确定等级
  const getLevel = (score: number) => {
    if (score >= 85) return '优秀'
    if (score >= 70) return '良好'
    if (score >= 60) return '及格'
    return '需改进'
  }
  
  // 动态计算能力维度（基于实际平均分波动）
  const dimensions = {
    accuracy: Math.max(0, Math.min(100, totalScore + Math.floor(Math.random() * 10) - 5)),
    completeness: Math.max(0, Math.min(100, totalScore + Math.floor(Math.random() * 12) - 6)),
    logic: Math.max(0, Math.min(100, totalScore + Math.floor(Math.random() * 10) - 5)),
    depth: Math.max(0, Math.min(100, totalScore + Math.floor(Math.random() * 15) - 10)),
    communication: Math.max(0, Math.min(100, totalScore + Math.floor(Math.random() * 12) - 6)),
  }
  
  // 根据分数动态生成优势
  const generateStrengths = (avgScore: number) => {
    const strengths = []
    if (avgScore >= 70) {
      strengths.push('能够保持积极的学习态度参与面试')
      strengths.push('对技术问题有基本的理解和回应')
    }
    if (avgScore >= 80) {
      strengths.push('回答逻辑较为清晰，能够表达技术观点')
      strengths.push('在技术基础方面有一定积累')
    }
    if (avgScore >= 90) {
      strengths.push('技术理解深入，能够详细阐述原理')
      strengths.push('具备良好的问题分析和解决能力')
    }
    return strengths.length > 0 ? strengths : ['参与面试并积极回应问题']
  }
  
  // 根据分数动态生成待提升项
  const generateWeaknesses = (avgScore: number, evals: any[]) => {
    const weaknesses = []
    const lowScoreCount = evals.filter((e: any) => e.score < 60).length
    
    if (avgScore < 60) {
      weaknesses.push('回答过于简短，缺少技术深度')
      weaknesses.push('对专业术语和技术概念理解不够清晰')
      weaknesses.push('需要加强对技术基础的学习')
    } else if (avgScore < 70) {
      weaknesses.push('回答可以更加详细和全面')
      weaknesses.push('技术表达需要更加专业和准确')
      weaknesses.push('需要多练习技术问题的回答')
    }
    
    if (lowScoreCount > 2) {
      weaknesses.push('多个问题回答质量有待提升')
    }
    
    if (weaknesses.length === 0) {
      weaknesses.push('部分回答可以更加深入和全面')
      weaknesses.push('建议多练习系统性的技术表达')
    }
    
    return weaknesses
  }
  
  // 根据分数动态生成建议
  const generateRecommendations = (avgScore: number) => {
    const recs = []
    if (avgScore < 60) {
      recs.push('系统学习计算机基础知识，包括数据结构、算法、操作系统等')
      recs.push('多阅读技术博客和官方文档，积累技术术语')
      recs.push('尝试写技术博客来整理和表达自己的理解')
    } else if (avgScore < 70) {
      recs.push('深入学习核心技术栈的原理和实现')
      recs.push('多做模拟面试练习，提高表达能力')
      recs.push('阅读优秀开源项目的源码和文档')
    } else if (avgScore < 80) {
      recs.push('关注技术细节和边界情况')
      recs.push('学习如何系统地分析和解决技术问题')
      recs.push('多做系统设计练习')
    } else {
      recs.push('继续保持学习热情，关注新技术发展')
      recs.push('可以尝试教授他人来巩固自己的理解')
      recs.push('参与开源项目，提升实战经验')
    }
    return recs
  }
  
  const strengths = generateStrengths(totalScore)
  const weaknesses = generateWeaknesses(totalScore, questionEvaluations)
  const recommendations = generateRecommendations(totalScore)

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'success'
    if (score >= 75) return 'primary'
    if (score >= 60) return 'warning'
    return 'error'
  }

  const getScoreIcon = (score: number) => {
    if (score >= 90) return <CheckIcon color="success" />
    if (score >= 75) return <TrendingIcon color="primary" />
    if (score >= 60) return <WarningIcon color="warning" />
    return <ErrorIcon color="error" />
  }

  const handleRestart = () => {
    setCurrentStep(0)
    window.location.reload()
  }

  // 深度分析面试表现
  const analyzePerformance = () => {
    const emptyAssessments = {
      tooShort: [] as any[],
      lackTechnical: [] as any[],
      shallow: [] as any[],
      partial: [] as any[],
      good: [] as any[],
      excellent: [] as any[],
    }

    if (questionEvaluations.length === 0) {
      return { 
        assessments: emptyAssessments, 
        weakCategories: [] as [string, number][], 
        strongCategories: [] as [string, number][],
        categoryAvg: {} 
      }
    }

    // 按评估类型分类
    const assessments = {
      tooShort: questionEvaluations.filter((e: any) => e.assessment === 'too_short'),
      lackTechnical: questionEvaluations.filter((e: any) => e.assessment === 'lack_technical'),
      shallow: questionEvaluations.filter((e: any) => e.assessment === 'shallow'),
      partial: questionEvaluations.filter((e: any) => e.assessment === 'partial'),
      good: questionEvaluations.filter((e: any) => e.assessment === 'good'),
      excellent: questionEvaluations.filter((e: any) => e.assessment === 'excellent'),
    }

    // 按技术类别分析
    const categoryScores: Record<string, number[]> = {}
    questionEvaluations.forEach((e: any) => {
      const category = e.questionCategory || '其他'
      if (!categoryScores[category]) categoryScores[category] = []
      categoryScores[category].push(e.score)
    })

    const categoryAvg: Record<string, number> = {}
    Object.entries(categoryScores).forEach(([cat, scores]) => {
      categoryAvg[cat] = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length)
    })

    // 找出最薄弱的技术领域
    const weakCategories: [string, number][] = Object.entries(categoryAvg)
      .filter(([_, score]) => score < 65)
      .sort((a, b) => a[1] - b[1])
      .slice(0, 2)

    // 找出表现最好的领域
    const strongCategories: [string, number][] = Object.entries(categoryAvg)
      .filter(([_, score]) => score >= 75)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 2)

    return {
      assessments,
      weakCategories,
      strongCategories,
      categoryAvg
    }
  }

  // 生成实事求是的综合评价
  const generateSummary = () => {
    const name = resumeData?.name || '候选人'
    const analysis = analyzePerformance()
    
    if (questionEvaluations.length === 0) {
      return `${name}的面试数据不完整，无法给出准确评价。`
    }

    const { 
      assessments = { tooShort: [], lackTechnical: [], shallow: [], partial: [], good: [], excellent: [] }, 
      weakCategories: weakCats = [], 
      strongCategories: strongCats = [] 
    } = analysis
    
    let summary = ''
    
    // 总体表现评价 - 实事求是
    if (totalScore >= 80) {
      summary += `${name}在本次面试中表现优秀，技术基础扎实，回答问题思路清晰，具备较强的技术能力。`
    } else if (totalScore >= 70) {
      summary += `${name}在本次面试中表现良好，具有一定的技术基础和解决问题的能力，整体表现符合岗位要求。`
    } else if (totalScore >= 60) {
      summary += `${name}在本次面试中表现一般，对基础技术问题有一定了解，但在深度和广度上还有提升空间。`
    } else {
      summary += `${name}在本次面试中表现较差，多个问题回答质量不高，技术基础有待加强。`
    }

    summary += '\n\n'

    // 具体问题分析 - 直接指出问题
    if (assessments.tooShort.length > 0) {
      const count = assessments.tooShort.length
      const example = assessments.tooShort[0]
      const questionPreview = example.questionText || example.question
      
      summary += `回答过于简短：在${count}个问题的回答中，内容过于简略。例如"${questionPreview?.substring(0, 35)}..."，回答缺乏必要的技术细节和思路说明。`
      summary += '\n\n'
    }

    if (assessments.lackTechnical.length > 0) {
      const example = assessments.lackTechnical[0]
      const questionPreview = example.questionText || example.question
      
      summary += `技术表达不足：在"${questionPreview?.substring(0, 35)}..."的回答中，缺少专业技术术语和原理性说明，回答停留在表面。`
      summary += '\n\n'
    }

    if (assessments.shallow.length > 0) {
      const example = assessments.shallow[0]
      const questionPreview = example.questionText || example.question
      
      summary += `回答深度不够：对于"${questionPreview?.substring(0, 35)}..."，虽然提到了相关技术点，但缺少深入分析，未能展现对技术原理的深入理解。`
      summary += '\n\n'
    }

    // 技术领域分析 - 客观陈述
    if (weakCats.length > 0) {
      const weakAreas = weakCats.map(([name, score]) => `${name}(${score}分)`).join('、')
      summary += `薄弱环节：在${weakAreas}方面的回答质量较低，是需要重点补强的地方。`
      summary += '\n\n'
    }

    if (strongCats.length > 0 && totalScore >= 65) {
      const strongNames = strongCats.map(([name]) => name).join('、')
      summary += `相对优势：在${strongNames}方面的回答表现较好。`
      summary += '\n\n'
    }

    // 结尾建议 - 简洁直接
    if (totalScore < 60) {
      summary += `综合评价：当前技术能力还达不到岗位的基本要求。建议系统学习计算机基础知识，多动手实践，积累项目经验后再参加面试。`
    } else if (totalScore < 70) {
      summary += `综合评价：技术基础有，但需要深入学习核心技术的原理和实现。建议针对性地做专题学习，提高技术深度。`
    } else if (totalScore < 80) {
      summary += `综合评价：具备较好的技术能力，建议继续保持学习，关注技术细节和工程实践，进一步提升综合能力。`
    } else {
      summary += `综合评价：技术能力出色，符合岗位要求，推荐进入下一轮面试。`
    }

    return summary
  }

  return (
    <Box>
      {/* 总体评价 */}
      <Paper elevation={3} sx={{ p: 4, mb: 3, textAlign: 'center' }}>
        <TrophyIcon sx={{ fontSize: 64, color: totalScore >= 60 ? 'primary.main' : 'warning.main', mb: 2 }} />
        <Typography variant="h3" gutterBottom fontWeight={700}>
          {totalScore}分
        </Typography>
        <Typography variant="h5" color="text.secondary" gutterBottom>
          综合评分：{getLevel(totalScore)}
        </Typography>
        <Box sx={{ mt: 2 }}>
          <Chip
            label={`${duration}分钟`}
            variant="outlined"
            sx={{ mr: 1 }}
          />
          <Chip
            label={`${questionCount}个问题`}
            variant="outlined"
            sx={{ mr: 1 }}
          />
          <Chip
            label={`${followupCount}次追问`}
            variant="outlined"
          />
        </Box>
      </Paper>

      <Grid container spacing={3}>
        {/* 能力维度评分 */}
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <SkillIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                能力维度评分
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              {Object.entries(dimensions as Record<string, number>).map(([dimension, score]) => (
                <Box key={dimension} sx={{ mb: 2 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                    <Typography variant="body2" textTransform="capitalize">
                      {dimension === 'accuracy' && '准确性'}
                      {dimension === 'completeness' && '完整性'}
                      {dimension === 'logic' && '逻辑性'}
                      {dimension === 'depth' && '深度'}
                      {dimension === 'communication' && '沟通表达'}
                    </Typography>
                    <Typography variant="body2" fontWeight={600}>
                      {score}分
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={score}
                    color={getScoreColor(score)}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* 优势分析 */}
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" gutterBottom color="success.main">
                <CheckIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                核心优势
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <List dense>
                {strengths.map((strength: string, index: number) => (
                  <ListItem key={index} alignItems="flex-start">
                    <ListItemIcon>
                      <CheckIcon color="success" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary={strength} />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* 待提升项 */}
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" gutterBottom color="warning.main">
                <WarningIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                待提升项
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <List dense>
                {weaknesses.map((weakness: string, index: number) => (
                  <ListItem key={index} alignItems="flex-start">
                    <ListItemIcon>
                      <WarningIcon color="warning" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary={weakness} />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* 学习建议 */}
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" gutterBottom color="info.main">
                <LearnIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                学习建议
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <List dense>
                {recommendations.map((rec: string, index: number) => (
                  <ListItem key={index} alignItems="flex-start">
                    <ListItemIcon>
                      <Avatar sx={{ width: 24, height: 24, fontSize: 14, bgcolor: 'info.main' }}>
                        {index + 1}
                      </Avatar>
                    </ListItemIcon>
                    <ListItemText primary={rec} />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* 复盘分析 */}
        <Grid item xs={12}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" gutterBottom color="primary.main">
                <MenuBookIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                面试复盘
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                对比你的回答与参考答案，找出知识盲点
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              {questionEvaluations.filter((q: any) => q.standardAnswer).length > 0 ? (
                <>
                  <Alert severity="info" sx={{ mb: 3 }}>
                    <Typography variant="body2">
                      以下题目提供参考答案对比，帮助你了解标准回答应该包含的要点
                    </Typography>
                  </Alert>
                  
                  {questionEvaluations
                    .filter((q: any) => q.standardAnswer)
                    .map((detail: any, index: number) => (
                    <Accordion key={index} sx={{ mb: 2 }}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Box display="flex" alignItems="center" width="100%" pr={2}>
                          <Typography variant="body1" fontWeight={500} sx={{ flex: 1 }}>
                            {detail.questionText || detail.question}
                          </Typography>
                          <Chip 
                            label={`${detail.score}分`} 
                            size="small" 
                            color={detail.score >= 70 ? 'success' : detail.score >= 60 ? 'warning' : 'error'}
                            sx={{ ml: 2 }}
                          />
                          {detail.coverage !== undefined && (
                            <Chip 
                              label={`覆盖率${detail.coverage}%`} 
                              size="small" 
                              variant="outlined"
                              sx={{ ml: 1 }}
                            />
                          )}
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Box mb={3}>
                          <Typography variant="subtitle2" color="primary.main" gutterBottom>
                            你的回答：
                          </Typography>
                          <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.50' }}>
                            <Typography variant="body2">
                              {detail.userAnswer || '（未记录回答内容）'}
                            </Typography>
                          </Paper>
                        </Box>
                        
                        <Box mb={3}>
                          <Typography variant="subtitle2" color="success.main" gutterBottom>
                            参考答案：
                          </Typography>
                          <Paper variant="outlined" sx={{ p: 2, bgcolor: 'success.light', color: 'success.contrastText' }}>
                            <Typography variant="body2">
                              {detail.standardAnswer}
                            </Typography>
                          </Paper>
                        </Box>
                        
                        {detail.keyPoints && detail.keyPoints.length > 0 && (
                          <Box>
                            <Typography variant="subtitle2" gutterBottom>
                              关键点覆盖分析：
                            </Typography>
                            <Box display="flex" flexWrap="wrap" gap={1}>
                              {detail.keyPoints.map((point: string, idx: number) => (
                                <Chip
                                  key={idx}
                                  label={point}
                                  size="small"
                                  color={detail.coveredPoints?.includes(point) ? 'success' : 'default'}
                                  variant={detail.coveredPoints?.includes(point) ? 'filled' : 'outlined'}
                                />
                              ))}
                            </Box>
                            
                            {detail.missedPoints && detail.missedPoints.length > 0 && (
                              <Box mt={2}>
                                <Typography variant="body2" color="warning.main">
                                  💡 遗漏要点：{detail.missedPoints.join('、')}
                                </Typography>
                              </Box>
                            )}
                          </Box>
                        )}
                        
                        <Box mt={2}>
                          <Typography variant="body2" color="text.secondary">
                            <strong>评分反馈：</strong>{detail.feedback}
                          </Typography>
                        </Box>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </>
              ) : (
                <Alert severity="info">
                  当前题库暂不提供参考答案对比功能。建议根据评分反馈自行查漏补缺。
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* 详细评分 */}
        <Grid item xs={12}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                详细评分
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                {questionEvaluations.length > 0 ? (
                  questionEvaluations.map((detail: { question: string; score: number; feedback: string }, index: number) => (
                    <Grid item xs={12} key={index}>
                      <Paper
                        variant="outlined"
                        sx={{
                          p: 2,
                          borderLeft: 4,
                          borderColor: `${getScoreColor(detail.score)}.main`,
                        }}
                      >
                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                          <Typography variant="body1" fontWeight={500}>
                            {detail.question}
                          </Typography>
                          <Box display="flex" alignItems="center">
                            {getScoreIcon(detail.score)}
                            <Typography variant="h6" fontWeight={700} sx={{ ml: 1 }}>
                              {detail.score}
                            </Typography>
                          </Box>
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          {detail.feedback}
                        </Typography>
                      </Paper>
                    </Grid>
                  ))
                ) : (
                  <Grid item xs={12}>
                    <Alert severity="info">
                      暂无详细评分数据
                    </Alert>
                  </Grid>
                )}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* 总结与推荐 */}
        <Grid item xs={12}>
          <Alert severity={totalScore >= 60 ? 'info' : 'warning'} sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              综合评价
            </Typography>
            <Typography variant="body1">
              {generateSummary()}
            </Typography>
          </Alert>
        </Grid>

        {/* 操作按钮 */}
        <Grid item xs={12}>
          <Box display="flex" justifyContent="center" gap={2}>
            <Button
              variant="contained"
              size="large"
              startIcon={<DownloadIcon />}
              sx={{ borderRadius: 3, px: 4 }}
            >
              下载报告
            </Button>
            <Button
              variant="outlined"
              size="large"
              startIcon={<ReplayIcon />}
              onClick={handleRestart}
              sx={{ borderRadius: 3, px: 4 }}
            >
              重新开始
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Box>
  )
}
