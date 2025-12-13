/**
 * Stripe Identity Integration Tests
 * 
 * These tests verify the Stripe Identity integration for BrainSAIT
 * Note: These are mock tests - actual Stripe API calls require valid credentials
 */

import { describe, it, expect, beforeEach, afterEach } from '@jest/globals'
import { StripeIdentityService, formatVerificationResponse } from '../src/stripe-identity.js'

// Mock environment
const mockEnv = {
  STRIPE_SECRET_KEY: 'sk_test_mock_key',
  STRIPE_WEBHOOK_SECRET: 'whsec_mock_secret'
}

// Mock Stripe client
jest.mock('stripe', () => {
  return jest.fn().mockImplementation(() => ({
    identity: {
      verificationSessions: {
        create: jest.fn().mockResolvedValue({
          id: 'vs_mock_session_123',
          client_secret: 'vs_mock_secret_123',
          url: 'https://verify.stripe.com/mock',
          expires_at: Math.floor(Date.now() / 1000) + 3600,
          status: 'requires_input',
          metadata: {
            client_reference_id: 'user_123',
            user_email: 'test@brainsait.com',
            user_name: 'Test User'
          }
        }),
        retrieve: jest.fn().mockResolvedValue({
          id: 'vs_mock_session_123',
          status: 'verified',
          metadata: {
            client_reference_id: 'user_123',
            user_email: 'test@brainsait.com',
            user_name: 'Test User'
          },
          verified_at: Math.floor(Date.now() / 1000),
          verified_outputs: {
            document: {
              type: 'id_card',
              id_number: '1122334455',
              expiry_date: '2030-12-31',
              issued_by: 'Saudi Arabia'
            }
          }
        })
      }
    },
    webhooks: {
      constructEvent: jest.fn().mockReturnValue({
        type: 'identity.verification_session.verified',
        data: {
          object: {
            id: 'vs_mock_session_123',
            metadata: {
              client_reference_id: 'user_123',
              user_email: 'test@brainsait.com',
              user_name: 'Test User'
            }
          }
        }
      })
    }
  }))
})

describe('StripeIdentityService', () => {
  let stripeService

  beforeEach(() => {
    stripeService = new StripeIdentityService(mockEnv)
  })

  describe('createVerificationSession', () => {
    it('should create a verification session successfully', async () => {
      const options = {
        clientReferenceId: 'user_123',
        userEmail: 'test@brainsait.com',
        userName: 'Test User',
        language: 'en'
      }

      const result = await stripeService.createVerificationSession(options)

      expect(result.success).toBe(true)
      expect(result.sessionId).toBe('vs_mock_session_123')
      expect(result.clientSecret).toBe('vs_mock_secret_123')
      expect(result.url).toBe('https://verify.stripe.com/mock')
      expect(result.status).toBe('requires_input')
    })

    it('should handle errors when creating session', async () => {
      // Mock error
      stripeService.stripe.identity.verificationSessions.create.mockRejectedValueOnce(
        new Error('Stripe API error')
      )

      const options = {
        clientReferenceId: 'user_123',
        userEmail: 'test@brainsait.com',
        userName: 'Test User'
      }

      const result = await stripeService.createVerificationSession(options)

      expect(result.success).toBe(false)
      expect(result.error).toBe('Stripe API error')
    })
  })

  describe('getVerificationSession', () => {
    it('should retrieve a verification session successfully', async () => {
      const result = await stripeService.getVerificationSession('vs_mock_session_123')

      expect(result.success).toBe(true)
      expect(result.sessionId).toBe('vs_mock_session_123')
      expect(result.status).toBe('verified')
      expect(result.clientReferenceId).toBe('user_123')
      expect(result.userEmail).toBe('test@brainsait.com')
      expect(result.userName).toBe('Test User')
      expect(result.document).toBeDefined()
      expect(result.document.type).toBe('id_card')
    })

    it('should handle errors when retrieving session', async () => {
      // Mock error
      stripeService.stripe.identity.verificationSessions.retrieve.mockRejectedValueOnce(
        new Error('Session not found')
      )

      const result = await stripeService.getVerificationSession('invalid_session')

      expect(result.success).toBe(false)
      expect(result.error).toBe('Session not found')
    })
  })

  describe('validateSaudiIdFormat', () => {
    it('should validate Saudi national ID (starts with 1)', () => {
      expect(stripeService.validateSaudiIdFormat('1122334455')).toBe(true)
    })

    it('should validate Iqama number (starts with 2)', () => {
      expect(stripeService.validateSaudiIdFormat('2122334455')).toBe(true)
    })

    it('should reject invalid ID numbers', () => {
      expect(stripeService.validateSaudiIdFormat('3122334455')).toBe(false) // Wrong starting digit
      expect(stripeService.validateSaudiIdFormat('112233445')).toBe(false)  // Too short
      expect(stripeService.validateSaudiIdFormat('11223344556')).toBe(false) // Too long
      expect(stripeService.validateSaudiIdFormat('11223344aa')).toBe(false)  // Non-numeric
    })
  })

  describe('handleWebhook', () => {
    it('should process webhook events successfully', async () => {
      const mockRequest = {
        text: jest.fn().mockResolvedValue('{}')
      }
      const signature = 'mock_signature'

      const result = await stripeService.handleWebhook(mockRequest, signature)

      expect(result.success).toBe(true)
      expect(result.eventType).toBe('identity.verification_session.verified')
      expect(result.sessionId).toBe('vs_mock_session_123')
    })

    it('should handle webhook signature verification failure', async () => {
      // Mock signature verification error
      stripeService.stripe.webhooks.constructEvent.mockImplementationOnce(() => {
        throw new Error('Invalid signature')
      })

      const mockRequest = {
        text: jest.fn().mockResolvedValue('{}')
      }
      const signature = 'invalid_signature'

      const result = await stripeService.handleWebhook(mockRequest, signature)

      expect(result.success).toBe(false)
      expect(result.error).toBe('Invalid signature')
      expect(result.statusCode).toBe(400)
    })
  })
})

describe('formatVerificationResponse', () => {
  const mockVerificationData = {
    status: 'verified',
    sessionId: 'vs_mock_session_123',
    verifiedAt: 1672531200,
    clientReferenceId: 'user_123',
    userEmail: 'test@brainsait.com',
    userName: 'Test User',
    document: {
      type: 'id_card',
      id_number: '1122334455',
      expiry_date: '2030-12-31',
      issued_by: 'Saudi Arabia'
    }
  }

  it('should format response in English', () => {
    const result = formatVerificationResponse(mockVerificationData, 'en')

    expect(result.verification.status).toBe('verified')
    expect(result.verification.statusMessage).toBe('Verified')
    expect(result.verification.sessionId).toBe('vs_mock_session_123')
    expect(result.verification.document.type).toBe('id_card')
    expect(result.compliance.kycStatus).toBe('compliant')
    expect(result.compliance.saudiRegulations.pdplCompliant).toBe(true)
    expect(result.compliance.saudiRegulations.mohApproved).toBe(true)
    expect(result.nextSteps).toContain('Full platform access')
  })

  it('should format response in Arabic', () => {
    const result = formatVerificationResponse(mockVerificationData, 'ar')

    expect(result.verification.statusMessage).toBe('تم التحقق')
    expect(result.compliance.kycStatus).toBe('compliant')
    expect(result.nextSteps).toContain('الوصول الكامل للمنصة')
  })

  it('should handle different statuses', () => {
    const pendingData = { ...mockVerificationData, status: 'requires_input' }
    const result = formatVerificationResponse(pendingData, 'en')

    expect(result.verification.statusMessage).toBe('Requires additional input')
    expect(result.compliance.kycStatus).toBe('pending')
    expect(result.nextSteps).toContain('Complete verification process')
  })
})

describe('Healthcare Professional Verification', () => {
  let stripeService

  beforeEach(() => {
    stripeService = new StripeIdentityService(mockEnv)
  })

  it('should create healthcare professional verification session', async () => {
    const professionalInfo = {
      userId: 'doctor_123',
      email: 'doctor@hospital.sa',
      fullName: 'د. أحمد محمد',
      licenseNumber: 'MED-12345',
      specialty: 'Cardiology',
      language: 'ar'
    }

    // Mock the healthcare-specific call
    stripeService.stripe.identity.verificationSessions.create.mockResolvedValueOnce({
      id: 'vs_healthcare_123',
      client_secret: 'vs_healthcare_secret_123',
      url: 'https://verify.stripe.com/healthcare',
      expires_at: Math.floor(Date.now() / 1000) + 3600,
      metadata: {
        client_reference_id: 'doctor_123',
        user_email: 'doctor@hospital.sa',
        user_name: 'د. أحمد محمد',
        professional_license: 'MED-12345',
        medical_specialty: 'Cardiology',
        user_type: 'healthcare_professional'
      }
    })

    const result = await stripeService.createHealthcareProfessionalVerification(professionalInfo)

    expect(result.success).toBe(true)
    expect(result.sessionId).toBe('vs_healthcare_123')
    expect(result.metadata.user_type).toBe('healthcare_professional')
    expect(result.metadata.medical_specialty).toBe('Cardiology')
  })
})

// Saudi Market Compliance Tests
describe('Saudi Market Compliance', () => {
  let stripeService

  beforeEach(() => {
    stripeService = new StripeIdentityService(mockEnv)
  })

  it('should include Saudi-specific configuration', () => {
    const config = stripeService.getClientConfig('pk_test_mock')

    expect(config.saudiMarketSpecific).toBeDefined()
    expect(config.saudiMarketSpecific.supportedIdTypes).toContain('saudi_id_card')
    expect(config.saudiMarketSpecific.supportedIdTypes).toContain('iqama')
    expect(config.saudiMarketSpecific.arabicNameSupport).toBe(true)
    expect(config.saudiMarketSpecific.hijriDateSupport).toBe(true)
  })

  it('should support bilingual interface', () => {
    const config = stripeService.getClientConfig('pk_test_mock')

    expect(config.identityVerificationOptions.languages.ar).toBe('العربية')
    expect(config.identityVerificationOptions.languages.en).toBe('English')
  })
})
