import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Alert,
  Grid,
  Paper,
  Chip,
  Divider,
  Fade,
  Button,
} from '@mui/material'
import {
  Download as DownloadIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material'
import { interviewApi } from '../services/api'

interface InterviewReportProps {
  sessionId: string | null
}

interface Dimension {
  name: string
  score: number
  feedback: string
}

interface Report {
  session_id: string
  mode: string
  total_questions: number
  average_score: number
  dimensions_summary: Dimension[]
  strengths: string[]
  weaknesses: string[]
  recommendations: string[]
  overall_feedback: string
}

const InterviewReport: React.FC<InterviewReportProps> = ({ sessionId }) => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [report, setReport] = useState<Report | null>(null)

  useEffect(() => {
    const fetchReport = async () => {
      if (!sessionId) return

      try {
        setLoading(true)
        setError(null)
        const response = await interviewApi.getReport(sessionId)
        setReport(response.data)
      } catch (err: any) {
        if (err.response?.status === 500) {
          setError('面试尚未完成或报告生成失败')
        } else {
          setError('获取报告失败')
        }
      } finally {
        setLoading(false)
      }
    }

    fetchReport()
  }, [sessionId])

  const handleDownload = () => {
    if (!report) return
    
    const reportData = JSON.stringify(report, null, 2)
    const blob = new Blob([reportData], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `interview-report-${report.session_id}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const getScoreColor = (score: number): string => {
    if (score >= 80) return '#4caf50'
    if (score >= 60) return '#ff9800'
    return '#f44336'
  }

  if (!sessionId) {
    return (
      <Card>
        <CardContent>
          <Typography color="text.secondary" align="center" sx={{ py: 4 }}>
            请先完成面试会话以查看报告
          </Typography>
        </CardContent>
      </Card>
    )
  }

  if (loading) {
    return (
      <Box sx={{ p: 4 }}>
        <LinearProgress />
        <Typography align="center" sx={{ mt: 2 }}>
          正在生成面试报告...
        </Typography>
      </Box>
    )
  }

  if (error) {
    return (
      <Alert severity="info" sx={{ m: 2 }}>
        {error}
      </Alert>
    )
  }

  if (!report) {
    return (
      <Alert severity="warning" sx={{ m: 2 }}>
        无法加载报告数据
      </Alert>
    )
  }

  return (
    <Fade in>
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5" component="h2">
            面试报告
          </Typography>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={handleDownload}
          >
            下载报告
          </Button>
        </Box>

        {/* 总体评分 */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Grid container spacing={3} alignItems="center">
              <Grid item xs={12} md={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <AssessmentIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
                  <Typography variant="h3" color="primary" fontWeight="bold">
                    {report.average_score.toFixed(1)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    综合得分（满分100）
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={8}>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    面试模式
                  </Typography>
                  <Chip
                    label={report.mode === 'structured' ? '结构化面试' : '开放式面试'}
                    color="primary"
                  />
                </Box>
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    回答数量
                  </Typography>
                  <Typography variant="body1">
                    {report.total_questions} 个问题
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* 维度评分 */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              能力维度评估
            </Typography>
            <Grid container spacing={3}>
              {report.dimensions_summary.map((dim, index) => (
                <Grid item xs={12} sm={6} key={index}>
                  <Paper sx={{ p: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="subtitle1" fontWeight="medium">
                        {dim.name === 'accuracy' ? '准确性' :
                         dim.name === 'completeness' ? '完整性' :
                         dim.name === 'logic' ? '逻辑性' : '深度'}
                      </Typography>
                      <Typography variant="h6" fontWeight="bold" color={getScoreColor(dim.score)}>
                        {dim.score.toFixed(1)}
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={dim.score}
                      sx={{
                        height: 10,
                        borderRadius: 5,
                        backgroundColor: '#e0e0e0',
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: getScoreColor(dim.score),
                        },
                      }}
                    />
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                      {dim.feedback}
                    </Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>

        {/* 优势与不足 */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom color="success.main">
                  优势亮点
                </Typography>
                {report.strengths.length > 0 ? (
                  <ul>
                    {report.strengths.map((strength, index) => (
                      <li key={index}>
                        <Typography variant="body2">{strength}</Typography>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    继续加油，展现更多亮点！
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom color="error.main">
                  待提升项
                </Typography>
                {report.weaknesses.length > 0 ? (
                  <ul>
                    {report.weaknesses.map((weakness, index) => (
                      <li key={index}>
                        <Typography variant="body2">{weakness}</Typography>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    表现不错，继续保持！
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* 学习建议 */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              学习建议
            </Typography>
            {report.recommendations.length > 0 ? (
              <ol>
                {report.recommendations.map((rec, index) => (
                  <li key={index}>
                    <Typography variant="body1" sx={{ mb: 1 }}>
                      {rec}
                    </Typography>
                  </li>
                ))}
              </ol>
            ) : (
              <Typography variant="body2" color="text.secondary">
                暂无具体建议
              </Typography>
            )}
            
            {report.overall_feedback && (
              <>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle2" gutterBottom>
                  总体评价：
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {report.overall_feedback}
                </Typography>
              </>
            )}
          </CardContent>
        </Card>
      </Box>
    </Fade>
  )
}

export default InterviewReport
