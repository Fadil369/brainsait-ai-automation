import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { logger } from 'hono/logger'

const app = new Hono()

// Tracing utilities
const generateTraceId = () => crypto.randomUUID()
const generateSpanId = () => crypto.randomUUID().slice(0, 16)

class Tracer {
  constructor(c) {
    this.c = c
    this.traceId = generateTraceId()
    this.spans = []
    this.startTime = Date.now()
  }

  startSpan(name, attributes = {}) {
    const span = {
      spanId: generateSpanId(),
      traceId: this.traceId,
      name,
      startTime: Date.now(),
      attributes,
      events: [],
      status: 'OK'
    }
    this.spans.push(span)
    return span
  }

  endSpan(span, status = 'OK') {
    span.endTime = Date.now()
    span.duration = span.endTime - span.startTime
    span.status = status
  }

  addEvent(span, name, attributes = {}) {
    span.events.push({
      name,
      timestamp: Date.now(),
      attributes
    })
  }

  setError(span, error) {
    span.status = 'ERROR'
    span.error = {
      message: error.message,
      stack: error.stack,
      type: error.name
    }
  }

  // Export trace data for logging/analytics
  export() {
    return {
      traceId: this.traceId,
      totalDuration: Date.now() - this.startTime,
      spanCount: this.spans.length,
      spans: this.spans,
      metadata: {
        service: 'skill-folders-api',
        version: '1.0.0',
        environment: 'cloudflare-workers'
      }
    }
  }

  // Write to Cloudflare Analytics Engine
  async writeToAnalytics(env) {
    if (!env?.ANALYTICS) return
    
    try {
      const trace = this.export()
      env.ANALYTICS.writeDataPoint({
        blobs: [
          this.traceId,
          this.c.req.path,
          this.c.req.method,
          JSON.stringify(trace.spans.map(s => s.name))
        ],
        doubles: [
          trace.totalDuration,
          trace.spanCount
        ],
        indexes: [
          this.c.get('apiKey')?.slice(0, 8) || 'anonymous'
        ]
      })
    } catch (e) {
      console.error('Analytics write failed:', e)
    }
  }
}

// Subscription tiers configuration (Saudi market pricing)
const TIERS = {
  starter: { 
    limit: 10000, 
    skills: ['legal-compliance'], 
    price: 'SAR 7,500-12,000/month',
    priceUSD: '$2,000-3,200/month' 
  },
  professional: { 
    limit: 100000, 
    skills: ['legal-compliance', 'cybersecurity', 'healthcare-saudi'], 
    price: 'SAR 22,500-37,500/month',
    priceUSD: '$6,000-10,000/month' 
  },
  enterprise: { 
    limit: Infinity, 
    skills: '*', 
    price: 'SAR 75,000+/month',
    priceUSD: '$20,000+/month' 
  }
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

// Tracing middleware
const tracing = async (c, next) => {
  const tracer = new Tracer(c)
  c.set('tracer', tracer)
  
  // Create root span for the request
  const rootSpan = tracer.startSpan('http.request', {
    'http.method': c.req.method,
    'http.url': c.req.url,
    'http.path': c.req.path,
    'http.user_agent': c.req.header('User-Agent') || 'unknown',
    'client.ip': c.req.header('CF-Connecting-IP') || 'unknown'
  })
  c.set('rootSpan', rootSpan)
  
  // Add trace ID to response headers
  c.header('X-Trace-ID', tracer.traceId)
  c.header('X-Request-Id', tracer.traceId)
  
  try {
    await next()
    
    // End root span with response info
    rootSpan.attributes['http.status_code'] = c.res.status
    tracer.endSpan(rootSpan, c.res.status >= 400 ? 'ERROR' : 'OK')
  } catch (error) {
    tracer.setError(rootSpan, error)
    tracer.endSpan(rootSpan, 'ERROR')
    throw error
  } finally {
    // Log trace summary
    const trace = tracer.export()
    console.log(JSON.stringify({
      level: 'trace',
      traceId: trace.traceId,
      path: c.req.path,
      method: c.req.method,
      status: c.res?.status,
      duration: trace.totalDuration,
      spans: trace.spans.map(s => ({
        name: s.name,
        duration: s.duration,
        status: s.status
      }))
    }))
    
    // Write to Analytics Engine (non-blocking)
    c.executionCtx?.waitUntil(tracer.writeToAnalytics(c.env))
  }
}

// Middleware
app.use('*', logger())
app.use('*', cors({
  origin: '*', // Allow all origins for API access
  allowHeaders: ['Content-Type', 'Authorization', 'Accept-Language', 'X-API-Key'],
  allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  exposeHeaders: ['Content-Length', 'X-RateLimit-Limit', 'X-RateLimit-Remaining', 'X-Request-Id', 'X-Trace-ID'],
  maxAge: 600,
  credentials: true,
}))
app.use('*', tracing)  // Add tracing before other middleware
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
    environment: 'cloudflare-workers',
    timestamp: new Date().toISOString()
  })
})

// Skills API
app.get('/api/skills', async (c) => {
  const tracer = c.get('tracer')
  const span = tracer.startSpan('skills.list', {
    'skills.category_filter': c.req.query('category') || 'all'
  })
  
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
    tracer.addEvent(span, 'category_found', { category, count: skills[category].length })
    tracer.endSpan(span)
    return c.json({
      category,
      skills: skills[category],
      count: skills[category].length,
      language
    })
  }

  tracer.addEvent(span, 'all_categories', { count: Object.values(skills).flat().length })
  tracer.endSpan(span)
  return c.json({
    categories: Object.keys(skills),
    totalSkills: Object.values(skills).flat().length,
    language
  })
})

// Get specific skill
app.get('/api/skills/:id', async (c) => {
  const tracer = c.get('tracer')
  const id = c.req.param('id')
  const span = tracer.startSpan('skills.get', { 'skills.id': id })
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

  tracer.addEvent(span, 'skill_retrieved', { id, category: skill.category })
  tracer.endSpan(span)
  return c.json({
    skill,
    language,
    timestamp: new Date().toISOString()
  })
})

// Categories endpoint
app.get('/api/categories', (c) => {
  const tracer = c.get('tracer')
  const span = tracer.startSpan('categories.list')
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

  tracer.addEvent(span, 'categories_retrieved', { count: categories.length })
  tracer.endSpan(span)
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
      baseUrl: 'https://skill-folders-api.brainsait-fadil.workers.dev',
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
      tracing: {
        enabled: true,
        description: 'All requests include distributed tracing',
        responseHeaders: {
          'X-Trace-ID': 'Unique trace identifier for debugging',
          'X-Request-Id': 'Same as X-Trace-ID for compatibility'
        },
        features: [
          'Request/response timing',
          'Span-based operation tracking',
          'Error capture and propagation',
          'Analytics Engine integration'
        ]
      },
      responseFormat: 'JSON with standardized structure',
      getApiKey: 'Contact sales@brainsait.com or visit https://brainsait.com/api-keys'
    }
  })
})

// Pricing endpoint (public) - Saudi Market Focused
app.get('/api/pricing', (c) => {
  const language = c.req.header('Accept-Language') || 'en'
  
  return c.json({
    market: 'Saudi Arabia (KSA)',
    currency: 'SAR (Saudi Riyal)',
    tiers: {
      starter: {
        name: language === 'ar' ? 'باقة البداية' : 'Starter',
        priceSAR: 'SAR 7,500-12,000/month',
        priceUSD: '$2,000-3,200/month',
        features: language === 'ar' ? [
          'وصول لـ 3 مهارات أساسية',
          '10,000 استدعاء API شهرياً',
          'دعم عبر البريد الإلكتروني',
          'التحديثات الأمنية',
          'مجال الامتثال القانوني فقط',
          'واجهة عربية / إنجليزية'
        ] : [
          '3 foundational skills access',
          '10,000 API calls/month',
          'Email support (Arabic/English)',
          'Security updates',
          'Legal Compliance domain only',
          'Bilingual interface'
        ],
        bestFor: language === 'ar' 
          ? 'الشركات الصغيرة والمتوسطة في السعودية' 
          : 'Small to medium businesses in Saudi Arabia',
        recommended: language === 'ar' ? 'للبدء' : 'For getting started'
      },
      professional: {
        name: language === 'ar' ? 'باقة المحترفين' : 'Professional',
        priceSAR: 'SAR 22,500-37,500/month',
        priceUSD: '$6,000-10,000/month',
        features: language === 'ar' ? [
          'وصول لـ 9+ مهارات متقدمة',
          '100,000 استدعاء API شهرياً',
          'دعم فني مخصص (عربي/إنجليزي)',
          'التحديثات الأمنية والتشريعية',
          'جميع المجالات: قانوني، أمن سيبراني، رعاية صحية',
          'تقارير شهرية مفصلة',
          'واجهة عربية / إنجليزية'
        ] : [
          '9+ advanced skills access',
          '100,000 API calls/month',
          'Dedicated technical support (Arabic/English)',
          'Security and regulatory updates',
          'All domains: legal, cybersecurity, healthcare',
          'Detailed monthly reports',
          'Bilingual interface'
        ],
        bestFor: language === 'ar' 
          ? 'الشركات الكبيرة والمؤسسات الصحية' 
          : 'Large enterprises and healthcare institutions',
        recommended: language === 'ar' ? 'الأكثر طلباً' : 'Most popular'
      },
      enterprise: {
        name: language === 'ar' ? 'باقة المؤسسات' : 'Enterprise',
        priceSAR: 'SAR 75,000+/month',
        priceUSD: '$20,000+/month',
        features: language === 'ar' ? [
          'وصول غير محدود لجميع المهارات',
          'استدعاء API غير محدود',
          'دعم فني 24/7 مع مدير حساب مخصص',
          'تحديثات فورية للتشريعات السعودية',
          'تخصيص كامل للمهارات والواجهات',
          'تقارير مخصصة ولوحات تحكم',
          'تكامل مع الأنظمة الداخلية',
          'تدريب للموظفين'
        ] : [
          'Unlimited access to all skills',
          'Unlimited API calls',
          '24/7 technical support with dedicated account manager',
          'Real-time Saudi regulatory updates',
          'Full customization of skills and interfaces',
          'Custom reports and dashboards',
          'Integration with internal systems',
          'Employee training'
        ],
        bestFor: language === 'ar' 
          ? 'الشركات الكبرى وشركات التأمين الصحي' 
          : 'Major corporations and health insurance companies',
        recommended: language === 'ar' ? 'للحلول المتكاملة' : 'For comprehensive solutions'
      }
    },
    contact: language === 'ar' 
      ? 'للحصول على عرض سعر مخصص: sales@brainsait.com أو +966 55 123 4567' 
      : 'For custom pricing: sales@brainsait.com or +966 55 123 4567',
    terms: language === 'ar' 
      ? 'جميع الأسعار تشمل ضريبة القيمة المضافة 15%' 
      : 'All prices include 15% VAT',
    note: language === 'ar' 
      ? 'الأسعار بالريال السعودي (SAR) هي الأسعار الرسمية' 
      : 'Saudi Riyal (SAR) prices are the official prices'
  })
})

// Error handling
app.onError((err, c) => {
  const tracer = c.get('tracer')
  const rootSpan = c.get('rootSpan')
  
  if (tracer && rootSpan) {
    tracer.setError(rootSpan, err)
    tracer.endSpan(rootSpan, 'ERROR')
  }
  
  console.error('Unhandled error:', err)
  
  return c.json({
    error: 'Internal Server Error',
    message: 'Something went wrong',
    traceId: tracer?.traceId,
    timestamp: new Date().toISOString()
  }, 500)
})

app.notFound((c) => {
  return c.json({
    error: 'Not Found',
    message: 'The requested endpoint does not exist',
    availableEndpoints: ['/', '/health', '/docs', '/api/pricing', '/api/skills', '/api/skills/:id', '/api/categories'],
    timestamp: new Date().toISOString()
  }, 404)
})

export default app
