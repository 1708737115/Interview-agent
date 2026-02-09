import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Document APIs (旧版，保留兼容)
export const documentApi = {
  upload: (formData: FormData, onProgress?: (progress: number) => void) => api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(progress)
      }
    }
  }),
  getAll: () => api.get('/documents'),
  delete: (id: string) => api.delete(`/documents/${id}`),
}

// 简历相关API (新版)
export const resumeApi = {
  // 上传并解析简历
  parseResume: async (file: File, onProgress?: (progress: number) => void) => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/resume/parse', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      },
    })
    return response.data
  },

  // 获取简历解析结果
  getResumeData: async (resumeId: string) => {
    const response = await api.get(`/resume/${resumeId}`)
    return response.data
  },
}

// Interview APIs (新版智能面试)
export const interviewApi = {
  // 旧版API (保留兼容)
  start: (data: {
    mode: 'structured' | 'open'
    knowledge_base_ids: string[]
    candidate_info?: string
    duration_minutes: number
  }) => api.post('/interview/start', data),
  
  getQuestion: (sessionId: string) => api.get(`/interview/${sessionId}/question`),
  
  submitAnswer: (data: {
    session_id: string
    question_id: string
    answer: string
  }) => api.post('/interview/answer', data),
  
  getReport: (sessionId: string) => api.get(`/interview/${sessionId}/report`),
  
  end: (sessionId: string) => api.post(`/interview/${sessionId}/end`),
  
  chat: (data: { session_id: string; message: string }) => api.post('/chat', data),

  // 新版API (AI智能面试)
  // 开始面试
  startAIInterview: async (resumeId: string) => {
    const response = await api.post('/interview/ai/start', { resume_id: resumeId })
    return response.data
  },

  // 获取下一步行动
  getNextAction: async (sessionId: string) => {
    const response = await api.get(`/interview/ai/${sessionId}/next`)
    return response.data
  },

  // 提交回答
  submitAIAnswer: async (sessionId: string, answer: string) => {
    const response = await api.post(`/interview/ai/${sessionId}/answer`, { answer })
    return response.data
  },

  // 结束面试并获取报告
  endAIInterview: async (sessionId: string) => {
    const response = await api.post(`/interview/ai/${sessionId}/end`)
    return response.data
  },

  // 获取面试报告
  getAIReport: async (sessionId: string) => {
    const response = await api.get(`/interview/ai/${sessionId}/report`)
    return response.data
  },
}

// 知识库相关API
export const knowledgeBaseApi = {
  // 获取知识库统计
  getStats: async () => {
    const response = await api.get('/knowledge-base/stats')
    return response.data
  },

  // 搜索问题
  searchQuestions: async (query: string, category?: string) => {
    const response = await api.get('/knowledge-base/search', {
      params: { query, category },
    })
    return response.data
  },
}

export default api
