import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { logger } from 'hono/logger'
import { StripeIdentityService, stripeWebhookMiddleware, formatVerificationResponse } from './stripe-identity.js'

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
  if (['/', '/health', '/docs', '/api/pricing', '/api/identity/config'].includes(path)) {
    return next()
  }
  
  // Stripe webhook endpoint uses signature-based auth, not API key
  if (path === '/api/stripe/webhook') {
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
  allowHeaders: ['Content-Type', 'Authorization', 'Accept-Language', 'X-API-Key', 'Stripe-Signature'],
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

// ============================================
// Stripe Identity Endpoints
// ============================================

// Stripe webhook endpoint (no auth required for webhooks)
app.post('/api/stripe/webhook', stripeWebhookMiddleware, async (c) => {
  const tracer = c.get('tracer')
  const span = tracer.startSpan('stripe.webhook')
  const signature = c.get('stripeSignature')
  
  try {
    const stripeService = new StripeIdentityService(c.env)
    const result = await stripeService.handleWebhook(c.req.raw, signature)
    
    tracer.addEvent(span, 'webhook_processed', { eventType: result.eventType, success: result.success })
    tracer.endSpan(span, result.success ? 'OK' : 'ERROR')
    
    return c.json({
      success: result.success,
      eventType: result.eventType,
      sessionId: result.sessionId,
      timestamp: new Date().toISOString()
    }, result.statusCode || 200)
  } catch (error) {
    tracer.setError(span, error)
    tracer.endSpan(span, 'ERROR')
    
    console.error('Stripe webhook processing error:', error)
    return c.json({
      success: false,
      error: 'Webhook processing failed',
      message: error.message
    }, 500)
  }
})

// Create identity verification session (auth required)
app.post('/api/identity/verify', async (c) => {
  const tracer = c.get('tracer')
  const span = tracer.startSpan('identity.verify.create')
  const language = c.req.header('Accept-Language') || 'en'
  
  try {
    const body = await c.req.json()
    const { userId, email, fullName, userType = 'general', language: userLanguage } = body
    
    if (!userId || !email || !fullName) {
      tracer.setError(span, new Error('Missing required fields'))
      tracer.endSpan(span, 'ERROR')
      return c.json({
        success: false,
        error: 'Missing required fields',
        message: 'userId, email, and fullName are required'
      }, 400)
    }
    
    const stripeService = new StripeIdentityService(c.env)
    let result
    
    // Handle different user types
    if (userType === 'healthcare_professional') {
      const { licenseNumber, specialty } = body
      result = await stripeService.createHealthcareProfessionalVerification({
        userId,
        email,
        fullName,
        licenseNumber,
        specialty,
        language: userLanguage || language
      })
    } else {
      result = await stripeService.createVerificationSession({
        clientReferenceId: userId,
        userEmail: email,
        userName: fullName,
        language: userLanguage || language
      })
    }
    
    if (!result.success) {
      tracer.setError(span, new Error(result.error))
      tracer.endSpan(span, 'ERROR')
      return c.json({
        success: false,
        error: result.error,
        code: result.code,
        message: 'Failed to create verification session'
      }, 400)
    }
    
    tracer.addEvent(span, 'session_created', { 
      sessionId: result.sessionId, 
      userType,
      language: userLanguage || language 
    })
    tracer.endSpan(span, 'OK')
    
    return c.json({
      success: true,
      sessionId: result.sessionId,
      clientSecret: result.clientSecret,
      url: result.url,
      expiresAt: result.expiresAt,
      status: result.status,
      clientConfig: stripeService.getClientConfig(c.env.STRIPE_PUBLISHABLE_KEY),
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    tracer.setError(span, error)
    tracer.endSpan(span, 'ERROR')
    
    console.error('Identity verification creation error:', error)
    return c.json({
      success: false,
      error: 'Verification session creation failed',
      message: error.message
    }, 500)
  }
})

// Get verification session status (auth required)
app.get('/api/identity/verify/:sessionId', async (c) => {
  const tracer = c.get('tracer')
  const sessionId = c.req.param('sessionId')
  const span = tracer.startSpan('identity.verify.get', { 'session.id': sessionId })
  const language = c.req.header('Accept-Language') || 'en'
  
  try {
    const stripeService = new StripeIdentityService(c.env)
    const result = await stripeService.getVerificationSession(sessionId)
    
    if (!result.success) {
      tracer.setError(span, new Error(result.error))
      tracer.endSpan(span, 'ERROR')
      return c.json({
        success: false,
        error: result.error,
        code: result.code,
        message: 'Failed to retrieve verification session'
      }, 400)
    }
    
    tracer.addEvent(span, 'session_retrieved', { 
      sessionId: result.sessionId,
      status: result.status,
      clientReferenceId: result.clientReferenceId 
    })
    tracer.endSpan(span, 'OK')
    
    // Format response for BrainSAIT API
    const formattedResponse = formatVerificationResponse(result, language)
    
    return c.json({
      success: true,
      sessionId: result.sessionId,
      status: result.status,
      ...formattedResponse,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    tracer.setError(span, error)
    tracer.endSpan(span, 'ERROR')
    
    console.error('Identity verification retrieval error:', error)
    return c.json({
      success: false,
      error: 'Verification session retrieval failed',
      message: error.message
    }, 500)
  }
})

// Validate Saudi ID format (utility endpoint)
app.post('/api/identity/validate/saudi-id', async (c) => {
  const tracer = c.get('tracer')
  const span = tracer.startSpan('identity.validate.saudi_id')
  const language = c.req.header('Accept-Language') || 'en'
  
  try {
    const body = await c.req.json()
    const { idNumber } = body
    
    if (!idNumber) {
      tracer.setError(span, new Error('Missing ID number'))
      tracer.endSpan(span, 'ERROR')
      return c.json({
        success: false,
        error: 'Missing ID number',
        message: 'idNumber is required'
      }, 400)
    }
    
    const stripeService = new StripeIdentityService(c.env)
    const isValid = stripeService.validateSaudiIdFormat(idNumber)
    const idType = idNumber.startsWith('1') ? 'saudi_national_id' : 
                   idNumber.startsWith('2') ? 'iqama_residence_id' : 'unknown'
    
    tracer.addEvent(span, 'id_validated', { idNumber, isValid, idType })
    tracer.endSpan(span, 'OK')
    
    return c.json({
      success: true,
      isValid,
      idType,
      idNumber: idNumber.slice(0, 3) + '****' + idNumber.slice(-3), // Mask for security
      message: language === 'ar' 
        ? isValid 
          ? `رقم ${idType === 'saudi_national_id' ? 'الهوية الوطنية' : 'الإقامة'} صالح`
          : 'رقم الهوية غير صالح'
        : isValid
          ? `${idType.replace(/_/g, ' ')} is valid`
          : 'ID number is invalid',
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    tracer.setError(span, error)
    tracer.endSpan(span, 'ERROR')
    
    console.error('Saudi ID validation error:', error)
    return c.json({
      success: false,
      error: 'ID validation failed',
      message: error.message
    }, 500)
  }
})

// Get Stripe client configuration (public)
app.get('/api/identity/config', (c) => {
  const language = c.req.header('Accept-Language') || 'en'
  
  const stripeService = new StripeIdentityService(c.env)
  const config = stripeService.getClientConfig(c.env.STRIPE_PUBLISHABLE_KEY)
  
  return c.json({
    success: true,
    config,
    supportedFeatures: {
      identityVerification: true,
      saudiMarket: true,
      bilingualSupport: ['ar', 'en'],
      documentTypes: ['saudi_id_card', 'iqama', 'passport', 'driving_license'],
      compliance: ['pdpl', 'saudi_moh', 'kyc'],
      privacy: {
        dataRetention: '30 days',
        biometricData: 'processed by Stripe, not stored by BrainSAIT',
        gdprCompliant: true
      }
    },
    instructions: language === 'ar' 
      ? {
          title: 'تعليمات التحقق من الهوية',
          steps: [
            'قم بإنشاء جلسة تحقق باستخدام /api/identity/verify',
            'استخدم clientSecret لتهيئة Stripe.js في الواجهة الأمامية',
            'أرسل المستخدم إلى رابط التحقق (url)',
            'استمع لأحداث الويب هوك للتحديثات',
            'تحقق من حالة الجلسة باستخدام /api/identity/verify/{sessionId}'
          ]
        }
      : {
          title: 'Identity Verification Instructions',
          steps: [
            'Create a verification session using /api/identity/verify',
            'Use clientSecret to initialize Stripe.js in frontend',
            'Redirect user to verification URL',
            'Listen for webhook events for updates',
            'Check session status using /api/identity/verify/{sessionId}'
          ]
        },
    timestamp: new Date().toISOString()
  })
})

// Update documentation endpoint to include Stripe endpoints
app.get('/docs', (c) => {
  const language = c.req.header('Accept-Language') || 'en'
  const isArabic = language === 'ar'
  
  return c.json({
    documentation: {
      baseUrl: 'https://skill-folders-api.brainsait-fadil.workers.dev',
      authentication: 'Bearer token required for /api/* endpoints (except /api/pricing, /api/identity/config)',
      rateLimiting: 'Based on subscription tier',
      endpoints: {
        // Public endpoints
        'GET /': 'Health check and service info (public)',
        'GET /health': 'Service health status (public)',
        'GET /docs': 'This documentation (public)',
        'GET /api/pricing': 'Subscription tiers and pricing (public)',
        'GET /api/identity/config': 'Stripe Identity client configuration (public)',
        
        // Skills endpoints (auth required)
        'GET /api/skills': 'List all skills or filter by category (auth required)',
        'GET /api/skills/:id': 'Get specific skill details (auth required)',
        'GET /api/categories': 'List all skill categories (auth required)',
        
        // Stripe Identity endpoints (auth required except webhook)
        'POST /api/identity/verify': 'Create identity verification session (auth required)',
        'GET /api/identity/verify/:sessionId': 'Get verification session status (auth required)',
        'POST /api/identity/validate/saudi-id': 'Validate Saudi ID/Iqama format (auth required)',
        'POST /api/stripe/webhook': 'Stripe webhook endpoint (no auth, signature required)',
        
        // Coming soon
        'POST /api/skills/:id/execute': 'Execute a skill (auth required, coming soon)'
      },
      headers: {
        'Authorization': 'Bearer sk_your_api_key (required for /api/* except public endpoints)',
        'Accept-Language': 'Optional: en or ar (default: en)',
        'Stripe-Signature': 'Required for /api/stripe/webhook (Stpe webhook signature)'
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
      stripeIdentity: {
        enabled: true,
        description: isArabic ? 'التحقق من الهوية باستخدام Stripe للمستخدمين السعوديين' : 'Identity verification using Stripe for Saudi users',
        supportedDocuments: ['saudi_id_card', 'iqama', 'passport', 'driving_license'],
        compliance: ['PDPL (Saudi Arabia)', 'KYC', 'Healthcare professional verification'],
        webhookEvents: [
          'identity.verification_session.verified',
          'identity.verification_session.requires_input',
          'identity.verification_session.canceled'
        ],
        saudiMarketFeatures: {
          arabicLanguageSupport: true,
          hijriDateSupport: true,
          saudiIdValidation: true,
          healthcareProfessionalFlow: true
        }
      },
      responseFormat: 'JSON with standardized structure',
      getApiKey: isArabic 
        ? 'اتصل بـ sales@brainsait.com أو زر https://brainsait.com/api-keys'
        : 'Contact sales@brainsait.com or visit https://brainsait.com/api-keys',
      support: isArabic
        ? 'الدعم الفني: support@brainsait.com أو +966 55 123 4567'
        : 'Technical support: support@brainsait.com or +966 55 123 4567'
    }
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
    availableEndpoints: [
      '/', '/health', '/docs', 
      '/api/pricing', '/api/identity/config',
      '/api/skills', '/api/skills/:id', '/api/categories',
      '/api/identity/verify', '/api/identity/verify/:sessionId',
      '/api/identity/validate/saudi-id', '/api/stripe/webhook'
    ],
    timestamp: new Date().toISOString()
  }, 404)
})

export default app
