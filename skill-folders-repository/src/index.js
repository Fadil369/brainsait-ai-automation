import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { logger } from 'hono/logger'

const app = new Hono()

// Middleware
app.use('*', logger())
app.use('*', cors({
  origin: ['https://brainsait.com', 'http://localhost:3000'],
  allowHeaders: ['Content-Type', 'Authorization', 'Accept-Language'],
  allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  exposeHeaders: ['Content-Length'],
  maxAge: 600,
  credentials: true,
}))

// Health check endpoint
app.get('/', (c) => {
  return c.json({
    status: 'healthy',
    service: 'Skill Folders API',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
    endpoints: {
      skills: '/api/skills',
      categories: '/api/categories',
      health: '/health',
      docs: '/docs'
    }
  })
})

// Health endpoint
app.get('/health', (c) => {
  return c.json({
    status: 'ok',
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  })
})

// Skills API
app.get('/api/skills', async (c) => {
  const category = c.req.query('category')
  const language = c.req.header('Accept-Language') || 'en'
  
  // Mock data - in production, this would come from KV or R2
  const skills = {
    'legal-compliance': [
      {
        id: 'legal-001',
        name: 'Regulatory Knowledge Base',
        description: 'Access and interpretation of laws and regulations',
        category: 'legal-compliance',
        complexity: 'advanced',
        executionTime: '2-3 minutes',
        languages: ['en', 'ar']
      },
      {
        id: 'legal-002',
        name: 'Auditing Scripts',
        description: 'Automated tools for privacy and compliance violation detection',
        category: 'legal-compliance',
        complexity: 'advanced',
        executionTime: '5-10 minutes',
        languages: ['en', 'ar']
      }
    ],
    'cybersecurity': [
      {
        id: 'cyber-001',
        name: 'Threat Analysis',
        description: 'Real-time threat detection and network activity monitoring',
        category: 'cybersecurity',
        complexity: 'very-advanced',
        executionTime: '< 5 seconds',
        languages: ['en', 'ar']
      },
      {
        id: 'cyber-002',
        name: 'Deepfake Detection',
        description: 'Media authenticity verification (video/audio)',
        category: 'cybersecurity',
        complexity: 'advanced',
        executionTime: '< 10 seconds',
        languages: ['en', 'ar']
      }
    ],
    'healthcare-saudi': [
      {
        id: 'health-001',
        name: 'Saudi Healthcare Regulatory Compliance',
        description: 'Compliance with Saudi healthcare insurance regulations',
        category: 'healthcare-saudi',
        complexity: 'advanced',
        executionTime: '1-2 minutes',
        languages: ['ar', 'en']
      },
      {
        id: 'health-002',
        name: 'Claims Processing Automation',
        description: 'Automated healthcare claims processing for Saudi market',
        category: 'healthcare-saudi',
        complexity: 'advanced',
        executionTime: '< 60 seconds',
        languages: ['ar', 'en']
      }
    ]
  }

  if (category && skills[category]) {
    return c.json({
      category,
      skills: skills[category],
      count: skills[category].length,
      language
    })
  }

  return c.json({
    categories: Object.keys(skills),
    totalSkills: Object.values(skills).flat().length,
    language
  })
})

// Get specific skill
app.get('/api/skills/:id', async (c) => {
  const id = c.req.param('id')
  const language = c.req.header('Accept-Language') || 'en'
  
  // Mock skill data
  const skill = {
    id,
    name: 'Regulatory Knowledge Base',
    description: 'Access and interpretation of laws and regulations',
    category: 'legal-compliance',
    complexity: 'advanced',
    executionTime: '2-3 minutes',
    languages: ['en', 'ar'],
    components: [
      'Legislative Texts Library: EU AI Act, GDPR, ISO 27001',
      'Legal Text Interpretation Rules: Interpretation framework',
      'Automatic Legal Updates System: Update mechanism'
    ],
    proceduralInstructions: [
      'Receive inquiry about specific legal requirements',
      'Search in the organization\'s legislative database',
      'Apply standard interpretation rules',
      'Provide answer with reference to legal materials'
    ],
    responsibilityLimits: [
      'Does not provide binding legal advice',
      'Indicates need for review by certified lawyer',
      'Focuses on regulatory interpretation, not legal opinion'
    ]
  }

  return c.json({
    skill,
    language,
    timestamp: new Date().toISOString()
  })
})

// Categories endpoint
app.get('/api/categories', (c) => {
  const language = c.req.header('Accept-Language') || 'en'
  
  const categories = [
    {
      id: 'legal-compliance',
      name: 'Legal Auditor Compliance',
      description: 'Legal compliance auditing and regulatory knowledge management',
      skillCount: 3,
      market: 'global'
    },
    {
      id: 'cybersecurity',
      name: 'Cyber Guardian MDR',
      description: 'Cybersecurity threat detection and incident response',
      skillCount: 3,
      market: 'global'
    },
    {
      id: 'healthcare-saudi',
      name: 'Healthcare Insurance (Saudi Market)',
      description: 'Specialized skills for Saudi healthcare insurance market',
      skillCount: 6,
      market: 'saudi-arabia'
    }
  ]

  return c.json({
    categories,
    totalCategories: categories.length,
    language,
    timestamp: new Date().toISOString()
  })
})

// Documentation endpoint
app.get('/docs', (c) => {
  return c.json({
    documentation: {
      baseUrl: 'https://skill-folders-api.brainsait.workers.dev',
      authentication: 'Bearer token required for write operations',
      rateLimiting: '100 requests per hour per IP',
      endpoints: {
        'GET /': 'Health check and service info',
        'GET /health': 'Service health status',
        'GET /api/skills': 'List all skills or filter by category',
        'GET /api/skills/:id': 'Get specific skill details',
        'GET /api/categories': 'List all skill categories',
        'GET /docs': 'This documentation'
      },
      headers: {
        'Accept-Language': 'Optional: en or ar (default: en)',
        'Authorization': 'Required for write operations'
      },
      responseFormat: 'JSON with standardized structure'
    }
  })
})

// Error handling
app.onError((err, c) => {
  console.error('Error:', err)
  return c.json({
    error: 'Internal server error',
    message: err.message,
    timestamp: new Date().toISOString()
  }, 500)
})

app.notFound((c) => {
  return c.json({
    error: 'Not found',
    message: 'The requested endpoint does not exist',
    timestamp: new Date().toISOString()
  }, 404)
})

export default app
