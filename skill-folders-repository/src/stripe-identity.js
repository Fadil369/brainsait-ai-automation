import Stripe from 'stripe'

/**
 * Stripe Identity integration for BrainSAIT
 * Handles KYC verification for healthcare professionals and educators in Saudi Arabia
 */
export class StripeIdentityService {
  constructor(env) {
    this.stripe = new Stripe(env.STRIPE_SECRET_KEY, {
      apiVersion: '2025-02-24.acacia', // Latest version with Identity support
      appInfo: {
        name: 'BrainSAIT Identity Verification',
        version: '1.0.0',
        url: 'https://brainsait.com'
      }
    })
    this.webhookSecret = env.STRIPE_WEBHOOK_SECRET
  }

  /**
   * Create a verification session for identity verification
   * @param {Object} options - Verification options
   * @param {string} options.clientReferenceId - Internal user ID
   * @param {string} options.userEmail - User email
   * @param {string} options.userName - User full name
   * @param {string} options.language - Preferred language ('ar' or 'en')
   * @returns {Promise<Object>} Verification session
   */
  async createVerificationSession(options) {
    const { clientReferenceId, userEmail, userName, language = 'en' } = options
    
    try {
      const session = await this.stripe.identity.verificationSessions.create({
        type: 'document',
        metadata: {
          client_reference_id: clientReferenceId,
          user_email: userEmail,
          user_name: userName,
          platform: 'brainsait',
          market: 'saudi-arabia'
        },
        options: {
          document: {
            allowed_types: ['driving_license', 'id_card', 'passport'],
            require_id_number: true,
            require_live_capture: true,
            require_matching_selfie: true
          }
        },
        return_url: `https://brainsait.com/verification/complete?session_id={VERIFICATION_SESSION_ID}`,
        locale: language === 'ar' ? 'ar' : 'en'
      })

      return {
        success: true,
        sessionId: session.id,
        clientSecret: session.client_secret,
        url: session.url,
        expiresAt: session.expires_at,
        status: session.status
      }
    } catch (error) {
      console.error('Stripe Identity session creation error:', error)
      return {
        success: false,
        error: error.message,
        code: error.code
      }
    }
  }

  /**
   * Retrieve a verification session
   * @param {string} sessionId - Stripe verification session ID
   * @returns {Promise<Object>} Session details
   */
  async getVerificationSession(sessionId) {
    try {
      const session = await this.stripe.identity.verificationSessions.retrieve(sessionId)
      
      return {
        success: true,
        sessionId: session.id,
        status: session.status,
        clientReferenceId: session.metadata?.client_reference_id,
        userEmail: session.metadata?.user_email,
        userName: session.metadata?.user_name,
        verifiedAt: session.verified_at,
        lastError: session.last_error,
        document: session.verified_outputs?.document,
        selfie: session.verified_outputs?.selfie
      }
    } catch (error) {
      console.error('Stripe Identity session retrieval error:', error)
      return {
        success: false,
        error: error.message,
        code: error.code
      }
    }
  }

  /**
   * Handle Stripe webhook events
   * @param {Request} request - Incoming webhook request
   * @param {string} signature - Stripe signature header
   * @returns {Promise<Object>} Webhook processing result
   */
  async handleWebhook(request, signature) {
    let event
    
    try {
      const body = await request.text()
      event = this.stripe.webhooks.constructEvent(body, signature, this.webhookSecret)
    } catch (error) {
      console.error('Webhook signature verification failed:', error)
      return {
        success: false,
        error: 'Invalid signature',
        statusCode: 400
      }
    }

    // Handle different event types
    switch (event.type) {
      case 'identity.verification_session.verified':
        await this.handleVerificationVerified(event.data.object)
        break
        
      case 'identity.verification_session.requires_input':
        await this.handleVerificationRequiresInput(event.data.object)
        break
        
      case 'identity.verification_session.canceled':
        await this.handleVerificationCanceled(event.data.object)
        break
        
      default:
        console.log(`Unhandled event type: ${event.type}`)
    }

    return {
      success: true,
      eventType: event.type,
      sessionId: event.data.object?.id,
      statusCode: 200
    }
  }

  /**
   * Handle successful verification
   * @param {Object} session - Verified session
   */
  async handleVerificationVerified(session) {
    const userId = session.metadata?.client_reference_id
    const userEmail = session.metadata?.user_email
    const userName = session.metadata?.user_name
    
    console.log(`✅ Identity verified for user: ${userId} (${userEmail})`)
    
    // In production: Update user status in your database
    // await updateUserVerificationStatus(userId, 'verified', {
    //   verifiedAt: session.verified_at,
    //   documentType: session.verified_outputs?.document?.type,
    //   documentNumber: session.verified_outputs?.document?.id_number,
    //   expiryDate: session.verified_outputs?.document?.expiry_date
    // })
    
    // Send notification (email, in-app, etc.)
    // await sendVerificationSuccessNotification(userEmail, userName)
  }

  /**
   * Handle verification requiring additional input
   * @param {Object} session - Session requiring input
   */
  async handleVerificationRequiresInput(session) {
    const userId = session.metadata?.client_reference_id
    const userEmail = session.metadata?.user_email
    const reason = session.last_error?.reason || 'unknown'
    
    console.log(`⚠️ Verification requires input for user: ${userId}, reason: ${reason}`)
    
    // In production: Notify user to provide additional information
    // await sendVerificationActionRequiredNotification(userEmail, reason)
  }

  /**
   * Handle canceled verification
   * @param {Object} session - Canceled session
   */
  async handleVerificationCanceled(session) {
    const userId = session.metadata?.client_reference_id
    const userEmail = session.metadata?.user_email
    
    console.log(`❌ Verification canceled for user: ${userId}`)
    
    // In production: Update user status
    // await updateUserVerificationStatus(userId, 'canceled')
  }

  /**
   * Generate client-side configuration for Stripe.js
   * @param {string} publishableKey - Stripe publishable key
   * @returns {Object} Client configuration
   */
  getClientConfig(publishableKey) {
    return {
      publishableKey,
      identityVerificationOptions: {
        sessionIdPlaceholder: '{VERIFICATION_SESSION_ID}',
        supportedDocuments: ['driving_license', 'id_card', 'passport'],
        languages: {
          ar: 'العربية',
          en: 'English'
        },
        saudiMarketSpecific: {
          supportedIdTypes: ['saudi_id_card', 'iqama'],
          arabicNameSupport: true,
          hijriDateSupport: true
        }
      }
    }
  }

  /**
   * Validate Saudi ID number format
   * @param {string} idNumber - Saudi ID or Iqama number
   * @returns {boolean} Whether ID format is valid
   */
  validateSaudiIdFormat(idNumber) {
    // Saudi ID: 10 digits starting with 1
    // Iqama: 10 digits starting with 2
    const saudiIdRegex = /^1\d{9}$/
    const iqamaRegex = /^2\d{9}$/
    
    return saudiIdRegex.test(idNumber) || iqamaRegex.test(idNumber)
  }

  /**
   * Create a custom verification flow for healthcare professionals
   * @param {Object} professionalInfo - Healthcare professional information
   * @returns {Promise<Object>} Custom verification session
   */
  async createHealthcareProfessionalVerification(professionalInfo) {
    const { userId, email, fullName, licenseNumber, specialty, language = 'ar' } = professionalInfo
    
    // Additional metadata for healthcare context
    const metadata = {
      client_reference_id: userId,
      user_email: email,
      user_name: fullName,
      professional_license: licenseNumber,
      medical_specialty: specialty,
      user_type: 'healthcare_professional',
      compliance_standard: 'saudi_moh',
      platform: 'brainsait_healthcare'
    }
    
    try {
      const session = await this.stripe.identity.verificationSessions.create({
        type: 'document',
        metadata,
        options: {
          document: {
            allowed_types: ['id_card', 'passport'],
            require_id_number: true,
            require_live_capture: true,
            require_matching_selfie: true,
            require_address: false
          }
        },
        return_url: `https://health.brainsait.com/verification/complete?session_id={VERIFICATION_SESSION_ID}&user_type=healthcare`,
        locale: language,
        submitted: false
      })

      return {
        success: true,
        sessionId: session.id,
        clientSecret: session.client_secret,
        url: session.url,
        metadata,
        expiresAt: session.expires_at
      }
    } catch (error) {
      console.error('Healthcare professional verification error:', error)
      return {
        success: false,
        error: error.message,
        code: error.code
      }
    }
  }
}

/**
 * Middleware to verify Stripe webhook signature
 */
export const stripeWebhookMiddleware = async (c, next) => {
  const signature = c.req.header('stripe-signature')
  
  if (!signature) {
    return c.json({
      error: 'Missing Stripe signature',
      message: 'stripe-signature header is required'
    }, 400)
  }
  
  c.set('stripeSignature', signature)
  await next()
}

/**
 * Utility function to format verification response for BrainSAIT API
 */
export function formatVerificationResponse(verificationData, language = 'en') {
  const isArabic = language === 'ar'
  
  const statusMessages = {
    verified: isArabic ? 'تم التحقق' : 'Verified',
    requires_input: isArabic ? 'يتطلب إدخالاً إضافياً' : 'Requires additional input',
    canceled: isArabic ? 'ملغي' : 'Canceled',
    processing: isArabic ? 'قيد المعالجة' : 'Processing'
  }
  
  return {
    verification: {
      status: verificationData.status,
      statusMessage: statusMessages[verificationData.status] || verificationData.status,
      sessionId: verificationData.sessionId,
      verifiedAt: verificationData.verifiedAt,
      document: verificationData.document ? {
        type: verificationData.document.type,
        idNumber: verificationData.document.id_number,
        expiryDate: verificationData.document.expiry_date,
        issuedBy: verificationData.document.issued_by
      } : null,
      user: {
        id: verificationData.clientReferenceId,
        email: verificationData.userEmail,
        name: verificationData.userName
      }
    },
    compliance: {
      kycStatus: verificationData.status === 'verified' ? 'compliant' : 'pending',
      saudiRegulations: {
        pdplCompliant: true,
        mohApproved: verificationData.status === 'verified',
        dataRetention: '30 days as per Saudi regulations'
      }
    },
    nextSteps: verificationData.status === 'verified' 
      ? isArabic 
        ? ['الوصول الكامل للمنصة', 'بدء استخدام الخدمات الصحية', 'تحديث الملف الشخصي']
        : ['Full platform access', 'Begin using healthcare services', 'Update profile']
      : isArabic
        ? ['إكمال عملية التحقق', 'تقديم المستندات المطلوبة', 'الاتصال بالدعم إذا لزم الأمر']
        : ['Complete verification process', 'Submit required documents', 'Contact support if needed']
  }
}
