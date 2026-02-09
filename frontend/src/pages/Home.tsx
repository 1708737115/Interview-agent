import React from 'react'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  Chip,
  Button,
  Divider,
  Paper,
} from '@mui/material'
import {
  Code as CodeIcon,
  GTranslate as GoIcon,
  Coffee as JavaIcon,
  School as SchoolIcon,
  EmojiPeople as PeopleIcon,
  ArrowForward as ArrowIcon,
  Build as BuildIcon,
} from '@mui/icons-material'
import { useApp, PRESET_INTERVIEWS } from '../App'

const iconMap: Record<string, React.ReactNode> = {
  'Code': <CodeIcon sx={{ fontSize: 40 }} />,
  'GTranslate': <GoIcon sx={{ fontSize: 40 }} />,
  'Coffee': <JavaIcon sx={{ fontSize: 40 }} />,
  'School': <SchoolIcon sx={{ fontSize: 40 }} />,
  'EmojiPeople': <PeopleIcon sx={{ fontSize: 40 }} />,
}

export default function Home() {
  const { setCurrentPage, setSelectedInterviewType } = useApp()

  const handleSelectInterview = (interview: typeof PRESET_INTERVIEWS[0]) => {
    setSelectedInterviewType(interview)
    setCurrentPage('setup')
  }

  const handleDIY = () => {
    setCurrentPage('diy')
  }

  return (
    <Box>
      {/* 欢迎区域 */}
      <Paper elevation={3} sx={{ p: 4, mb: 4, textAlign: 'center', bgcolor: 'primary.main', color: 'white' }}>
        <Typography variant="h3" gutterBottom fontWeight={700}>
          选择你的面试类型
        </Typography>
        <Typography variant="h6" sx={{ opacity: 0.9 }}>
          我们提供多种预设面试模式，你也可以DIY自己的专属面试官
        </Typography>
      </Paper>

      {/* 预设面试类型 */}
      <Typography variant="h5" gutterBottom fontWeight={600} sx={{ mb: 3 }}>
        预设面试类型
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {PRESET_INTERVIEWS.map((interview) => (
          <Grid item xs={12} sm={6} md={4} key={interview.id}>
            <Card 
              elevation={2} 
              sx={{ 
                height: '100%',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 6,
                },
              }}
            >
              <CardActionArea onClick={() => handleSelectInterview(interview)} sx={{ height: '100%' }}>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Box sx={{ color: 'primary.main', mr: 2 }}>
                      {iconMap[interview.icon] || <CodeIcon sx={{ fontSize: 40 }} />}
                    </Box>
                    <Box flex={1}>
                      <Typography variant="h6" fontWeight={600}>
                        {interview.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {interview.duration}分钟 · {interview.style === 'strict' ? '严格' : interview.style === 'friendly' ? '友好' : '标准'}模式
                      </Typography>
                    </Box>
                  </Box>

                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {interview.description}
                  </Typography>

                  <Divider sx={{ my: 1.5 }} />

                  <Box>
                    <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                      重点考察：
                    </Typography>
                    <Box display="flex" flexWrap="wrap" gap={0.5}>
                      {interview.focusAreas.map((area, index) => (
                        <Chip
                          key={index}
                          label={area}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </Box>

                  <Box display="flex" justifyContent="flex-end" mt={2}>
                    <Button
                      size="small"
                      endIcon={<ArrowIcon />}
                      color="primary"
                    >
                      开始准备
                    </Button>
                  </Box>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}

        {/* DIY面试官卡片 */}
        <Grid item xs={12} sm={6} md={4}>
          <Card
            elevation={2}
            sx={{
              height: '100%',
              border: '2px dashed',
              borderColor: 'secondary.main',
              background: 'linear-gradient(135deg, #fff5f8 0%, #ffffff 100%)',
              transition: 'transform 0.2s, box-shadow 0.2s',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: 6,
              },
            }}
          >
            <CardActionArea onClick={handleDIY} sx={{ height: '100%' }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Box sx={{ color: 'secondary.main', mr: 2 }}>
                    <BuildIcon sx={{ fontSize: 40 }} />
                  </Box>
                  <Box flex={1}>
                    <Typography variant="h6" fontWeight={600} color="secondary.main">
                      DIY 面试官
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      自定义面试风格
                    </Typography>
                  </Box>
                </Box>

                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  打造专属于你的面试官，适合考研复试、企业内部面试、技术分享等个性化场景
                </Typography>

                <Divider sx={{ my: 1.5 }} />

                <Box>
                  <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                    支持自定义：
                  </Typography>
                  <Box display="flex" flexWrap="wrap" gap={0.5}>
                    <Chip label="面试风格" size="small" variant="outlined" />
                    <Chip label="题库范围" size="small" variant="outlined" />
                    <Chip label="追问策略" size="small" variant="outlined" />
                    <Chip label="评估标准" size="small" variant="outlined" />
                  </Box>
                </Box>

                <Box display="flex" justifyContent="flex-end" mt={2}>
                  <Button
                    size="small"
                    endIcon={<ArrowIcon />}
                    color="secondary"
                  >
                    开始配置
                  </Button>
                </Box>
              </CardContent>
            </CardActionArea>
          </Card>
        </Grid>
      </Grid>

      {/* 功能特点介绍 */}
      <Paper elevation={2} sx={{ p: 4, mt: 4 }}>
        <Typography variant="h5" gutterBottom fontWeight={600}>
          系统功能特点
        </Typography>
        <Grid container spacing={3} sx={{ mt: 1 }}>
          <Grid item xs={12} md={4}>
            <Box textAlign="center">
              <Typography variant="h6" color="primary" gutterBottom>
                🎯 智能简历解析
              </Typography>
              <Typography variant="body2" color="text.secondary">
                上传简历自动解析，生成个性化面试策略，针对性考察你的技能栈
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box textAlign="center">
              <Typography variant="h6" color="primary" gutterBottom>
                🧠 多轮追问机制
              </Typography>
              <Typography variant="body2" color="text.secondary">
                基于牛客风格设计，最多8次智能追问，深度挖掘你的技术能力
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box textAlign="center">
              <Typography variant="h6" color="primary" gutterBottom>
                📊 全面评估报告
              </Typography>
              <Typography variant="body2" color="text.secondary">
                多维度能力评分，提供详细反馈和改进建议，帮助你快速成长
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  )
}
