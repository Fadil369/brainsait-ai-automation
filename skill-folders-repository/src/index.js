import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { logger } from 'hono/logger'

const app = new Hono()

// Subscription tiers configuration
const TIERS = {
  starter: { limit: 10000, skills: ['legal-compliance'], price: '$500-1,000/month' },
  professional: { limit: 100000, skills: ['legal-compliance', 'cybersecurity', 'healthcare-saudi'], price: '$2,000-5,000/month' },
  enterprise: { limit: Infinity, skills: '*', price: '$10,000+/month' }
}

// API Key validation middleware
const validateApiKey = async (c, next) => {
  const path = c.req.path
  
  // Public endpoints (no auth required)
  if (['/', '/health', '/docs', '/api/pricing'].includes(path)) {
    return next()
  }
  
  const authHeader = c.req.header('Authorization')
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return c.json({
      error: 'Unauthorized',
      message: 'API key required. Get yours at https://brainsait.com/api-keys',
      pricing: '/api/pricing'
    }, 401)
  }
  
  const apiKey = authHeader.replace('Bearer ', '')
  
  // In production: validate against KV store
  // const keyData = await c.env.SKILLS_KV.get(`apikey:${apiKey}`, 'json')
  
  // Demo: accept any key starting with 'sk_' for testing
  if (!apiKey.startsWith('sk_')) {
    return c.json({
      error: 'Invalid API key',
      message: 'API key format: sk_xxxxxxxx'
    }, 401)
  }
  
  // Track usage (in production: increment counter in KV)
  c.set('apiKey', apiKey)
  c.set('tier', 'professional') // Demo: default tier
  
  return next()
}

// Rate limiting middleware
const rateLimit = async (c, next) => {
  const apiKey = c.get('apiKey')
  if (!apiKey) return next()
  
  // In production: check rate limit in KV
  // const usage = await c.env.SKILLS_KV.get(`usage:${apiKey}:${Date.now()}`, 'json')
  // const tier = TIERS[c.get('tier')]
  // if (usage >= tier.limit) return c.json({ error: 'Rate limit exceeded' }, 429)
  
  // Add usage headers
  c.header('X-RateLimit-Limit', '100000')
  c.header('X-RateLimit-Remaining', '99999')
  c.header('X-RateLimit-Reset', new Date(Date.now() + 3600000).toISOString())
  
  return next()
}

// Middleware
app.use('*', logger())
app.use('*', cors({
  origin: '*', // Allow all origins for API access
  allowHeaders: ['Content-Type', 'Authorization', 'Accept-Language', 'X-API-Key'],
  allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  exposeHeaders: ['Content-Length', 'X-RateLimit-Limit', 'X-RateLimit-Remaining', 'X-Request-Id'],
  maxAge: 600,
  credentials: true,
}))
app.use('*', validateApiKey)
app.use('*', rateLimit)

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
      authentication: 'Bearer token required for /api/* endpoints',
      rateLimiting: 'Based on subscription tier',
      endpoints: {
        'GET /': 'Health check and service info (public)',
        'GET /health': 'Service health status (public)',
        'GET /docs': 'This documentation (public)',
        'GET /api/pricing': 'Subscription tiers and pricing (public)',
        'GET /api/skills': 'List all skills or filter by category (auth required)',
        'GET /api/skills/:id': 'Get specific skill details (auth required)',
        'GET /api/categories': 'List all skill categories (auth required)',
        'POST /api/skills/:id/execute': 'Execute a skill (auth required, coming soon)'
      },
      headers: {
        'Authorization': 'Bearer sk_your_api_key (required for /api/* except /api/pricing)',
        'Accept-Language': 'Optional: en or ar (default: en)'
      },
      responseFormat: 'JSON with standardized structure',
      getApiKey: 'Contact sales@brainsait.com or visit https://brainsait.com/api-keys'
    }
  })
})

// Pricing endpoint (public)
app.get('/api/pricing', (c) => {
  return c.json({
    tiers: {
      starter: {
        price: '$500-1,000/month',
        features: [
          '3 basic skills access',
          '10,000 API calls/month',
          'Email support',
          'Security updates',
          'Legal Compliance domain only'
        ],
        bestFor: 'Small teams getting started with AI compliance'
      },
      professional: {
        price: '$2,000-5,000/month',
        features: [
          'All skills in chosen domain',
          '100,000 API calls/month',
          'Priority support',
          'Custom skill configuration',
          'Webhook integrations',
          'Usage analytics dashboard'
        ],
        bestFor: 'Growing companies with specific domain needs'
      },
      enterprise: {
        price: '$10,000+/month',
        features: [
          'All skills, all domains',
          'Unlimited API calls',
          'Dedicated support & SLA',
          'Custom skill development',
          'On-premise deployment option',
          'SSO & advanced security',
          'Arabic/English bilingual support',
          'Regulatory update alerts'
        ],
        bestFor: 'Large organizations requiring full compliance coverage'
      }
    },
    contact: {
      sales: 'sales@brainsait.com',
      website: 'https://brainsait.com/pricing',
      demo: 'https://brainsait.com/demo'
    },
    trial: {
      available: true,
      duration: '14 days',
      tier: 'professional',
      signup: 'https://brainsait.com/trial'
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
