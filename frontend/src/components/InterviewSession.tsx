import React, { useState, useEffect, useCallback } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  LinearProgress,
  Alert,
  Stepper,
  Step,
  StepLabel,
  Paper,
  Chip,
  Fade,
} from '@mui/material'
import {
  Send as SendIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material'
import { interviewApi } from '../services/api'

interface InterviewSessionProps {
  sessionId: string | null
}

interface Question {
  id: string
  question: string
  question_type: string
  difficulty: number
}

interface Evaluation {
  name: string
  score: number
  feedback: string
}

const InterviewSession: React.FC<InterviewSessionProps> = ({ sessionId }) => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null)
  const [answer, setAnswer] = useState('')
  const [evaluation, setEvaluation] = useState<{
    evaluation: Evaluation[]
    total_score: number
    feedback: string
    suggestions: string[]
  } | null>(null)
  const [questionNumber, setQuestionNumber] = useState(0)
  const [isCompleted, setIsCompleted] = useState(false)
  const [history, setHistory] = useState<Array<{ question: string; answer: string; score: number }>>([])

  const fetchQuestion = useCallback(async () => {
    if (!sessionId) return
    
    try {
      setLoading(true)
      setError(null)
      const response = await interviewApi.getQuestion(sessionId)
      setCurrentQuestion(response.data)
      setEvaluation(null)
      setAnswer('')
    } catch (err: any) {
      if (err.response?.status === 404) {
        // No more questions
        setIsCompleted(true)
        setCurrentQuestion(null)
      } else {
        setError('获取问题失败')
      }
    } finally {
      setLoading(false)
    }
  }, [sessionId])

  useEffect(() => {
    if (sessionId) {
      fetchQuestion()
    }
  }, [sessionId, fetchQuestion])

  const handleSubmitAnswer = async () => {
    if (!sessionId || !currentQuestion || !answer.trim()) return

    try {
      setLoading(true)
      const response = await interviewApi.submitAnswer({
        session_id: sessionId,
        question_id: currentQuestion.id,
        answer: answer,
      })

      setEvaluation(response.data)
      setQuestionNumber((prev) => prev + 1)
      setHistory((prev) => [
        ...prev,
        {
          question: currentQuestion.question,
          answer: answer,
          score: response.data.total_score,
        },
      ])

      // Check if there's a next question
      if (response.data.next_question) {
        setTimeout(() => {
          setCurrentQuestion(response.data.next_question)
          setEvaluation(null)
          setAnswer('')
        }, 2000)
      } else {
        setTimeout(() => {
          setIsCompleted(true)
          setCurrentQuestion(null)
        }, 2000)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || '提交失败')
    } finally {
      setLoading(false)
    }
  }

  if (!sessionId) {
    return (
      <Card>
        <CardContent>
          <Typography color="text.secondary" align="center" sx={{ py: 4 }}>
            请先前往"知识库管理"标签页开始面试会话
          </Typography>
        </CardContent>
      </Card>
    )
  }

  if (isCompleted) {
    return (
      <Fade in>
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <CheckIcon color="success" sx={{ fontSize: 60, mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              面试完成！
            </Typography>
            <Typography color="text.secondary" gutterBottom>
              您已完成所有问题的回答
            </Typography>
            <Typography variant="body1" sx={{ mt: 2 }}>
              请切换到"面试报告"标签页查看详细评估
            </Typography>
          </CardContent>
        </Card>
      </Fade>
    )
  }

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {history.length > 0 && (
        <Paper sx={{ p: 2, mb: 2, maxHeight: 200, overflow: 'auto' }}>
          <Typography variant="subtitle2" gutterBottom>
            回答历史
          </Typography>
          <Stepper activeStep={history.length} orientation="vertical">
            {history.map((item, index) => (
              <Step key={index}>
                <StepLabel>
                  <Typography variant="caption">
                    问题 {index + 1}: 得分 {item.score.toFixed(1)}
                  </Typography>
                </StepLabel>
              </Step>
            ))}
          </Stepper>
        </Paper>
      )}

      {currentQuestion && !evaluation && (
        <Fade in>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Chip
                  label={`难度: ${'★'.repeat(currentQuestion.difficulty)}`}
                  color={currentQuestion.difficulty > 3 ? 'error' : 'primary'}
                  size="small"
                  sx={{ mr: 1 }}
                />
                <Chip
                  label={currentQuestion.question_type === 'concept' ? '概念题' : 
                         currentQuestion.question_type === 'application' ? '应用题' : '分析题'}
                  variant="outlined"
                  size="small"
                />
              </Box>

              <Typography variant="h6" gutterBottom>
                问题 {questionNumber + 1}
              </Typography>
              
              <Typography variant="body1" sx={{ mb: 3, whiteSpace: 'pre-wrap' }}>
                {currentQuestion.question}
              </Typography>

              <TextField
                label="您的回答"
                multiline
                rows={6}
                fullWidth
                variant="outlined"
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="请输入您的回答..."
                disabled={loading}
              />

              <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  variant="contained"
                  endIcon={<SendIcon />}
                  onClick={handleSubmitAnswer}
                  disabled={!answer.trim() || loading}
                >
                  提交回答
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Fade>
      )}

      {evaluation && (
        <Fade in>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom color="primary">
                评估结果
              </Typography>

              <Box sx={{ mb: 2 }}>
                <Typography variant="h4" color="primary" align="center">
                  {evaluation.total_score.toFixed(1)} 分
                </Typography>
              </Box>

              <Box sx={{ mb: 2 }}>
                {evaluation.evaluation.map((dim, index) => (
                  <Box key={index} sx={{ mb: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">
                        {dim.name === 'accuracy' ? '准确性' :
                         dim.name === 'completeness' ? '完整性' :
                         dim.name === 'logic' ? '逻辑性' : '深度'}
                      </Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {dim.score} 分
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={dim.score}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: '#e0e0e0',
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: dim.score >= 80 ? '#4caf50' : dim.score >= 60 ? '#ff9800' : '#f44336',
                        },
                      }}
                    />
                    <Typography variant="caption" color="text.secondary">
                      {dim.feedback}
                    </Typography>
                  </Box>
                ))}
              </Box>

              <Typography variant="subtitle2" gutterBottom>
                总体反馈：
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                {evaluation.feedback}
              </Typography>

              {evaluation.suggestions.length > 0 && (
                <>
                  <Typography variant="subtitle2" gutterBottom>
                    改进建议：
                  </Typography>
                  <ul>
                    {evaluation.suggestions.map((suggestion, index) => (
                      <li key={index}>
                        <Typography variant="body2" color="text.secondary">
                          {suggestion}
                        </Typography>
                      </li>
                    ))}
                  </ul>
                </>
              )}

              {currentQuestion && (
                <Box sx={{ mt: 2, textAlign: 'center' }}>
                  <Typography color="text.secondary">
                    正在加载下一题...
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Fade>
      )}
    </Box>
  )
}

export default InterviewSession
