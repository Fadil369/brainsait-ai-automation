# Skill Folders Repository

## Overview
This repository contains a comprehensive collection of AI agent skills organized into specialized domains. Each skill folder represents a specific capability that can be integrated into AI agents to enhance their functionality and domain expertise.

## Skill Domains (New Organized Structure)

The skills are now organized in domain-specific folders under `/domains/`:

### 1. Legal Compliance (`domains/legal-compliance/`)
**Purpose**: Legal compliance auditing and regulatory knowledge management
- **Skills**: Regulatory Knowledge Base (EU AI Act, GDPR, ISO 27001, PDPL)
- **Specs**: Complete specification files with test scenarios
- **Features**: Automated compliance auditing, regulatory interpretation, citation tracking

### 2. Cybersecurity (`domains/cybersecurity/`)
**Purpose**: Advanced cybersecurity threat detection and media authentication
- **Skills**: 
  - Threat Analysis (<5s response time, MITRE ATT&CK mapping, 24/7 monitoring)
  - Deepfake Detection (>98% accuracy, video/audio analysis, forensic reports)
- **Specs**: Detailed operational workflows and integration requirements
- **Features**: Real-time threat intelligence, anomaly detection, incident response

### 3. Healthcare (Saudi Market) (`domains/healthcare-saudi/`)
**Purpose**: Specialized compliance for Saudi healthcare insurance
- **Skills**: Regulatory Compliance (CCHI/Insurance Authority, MoH, SHC alignment)
- **Specs**: Saudi-specific regulatory framework with Arabic citations
- **Features**: Claims processing, policy wording validation, PDPL compliance

## Implementation Structure

Each skill folder contains:
- `README.md`: Overview and documentation
- `SKILL.md`: Detailed skill specification
- Supporting files: Implementation guides, templates, scripts

## Key Features

### Bilingual Support
- All skills support Arabic/English output
- Cultural and linguistic adaptation for target markets
- Compliance with local regulations and practices

### Integration Ready
- Standardized API interfaces
- Clear integration protocols
- Comprehensive documentation

### Scalable Architecture
- Modular skill design
- Easy skill addition and modification
- Cross-skill compatibility

## Business Value

### For Enterprises
- **Domain Expertise**: Convert human expertise into digital assets
- **Quality Assurance**: Standardized, error-free operations
- **High Profitability**: Recurring revenue with high margins

### For AI Agents
- **Expanded Capabilities**: Access to specialized domain knowledge
- **Consistent Quality**: Standardized processes and outputs
- **Rapid Deployment**: Pre-built, tested skill modules

## Market Focus

### Primary Markets
1. **Financial Services**: Banks, financing companies
2. **Healthcare**: Hospitals, pharmaceutical companies
3. **Technology**: Software companies, cloud service providers

### Geographic Focus
- **Saudi Arabia**: Primary market with specialized healthcare skills
- **Middle East**: Arabic language and cultural adaptation
- **Global**: Compliance with international standards

## Implementation Roadmap

### Phase 1: Evaluation & Setup (Q1 2026)
- Assess current work needs
- Select appropriate skills
- Prepare implementation environment

### Phase 2: Integration & Deployment (Q2 2026)
- Connect skills with agent platform
- Configure basic settings
- Test core functionality

### Phase 3: Optimization & Customization (Q3 2026)
- Customize skills for specific needs
- Optimize performance based on usage
- Add custom skills as needed

## Key Performance Indicators (KPIs)

1. **Skill Execution Accuracy**: > 95%
2. **Response Time**: < 5 seconds for critical tasks
3. **Threat/Compliance Violation Detection Rate**: Industry leading
4. **Time Savings**: Compared to human execution

## License & Commercial Model

### Commercial Tiers (Saudi Market Pricing)
1. **Starter Tier**: SAR 7,500-12,000/month (~$2,000-3,200/month)
   - 3 foundational skills
   - 10,000 API calls/month
   - Email support (Arabic/English)
   - Legal Compliance domain only

2. **Professional Tier**: SAR 22,500-37,500/month (~$6,000-10,000/month)
   - All skills in chosen domain
   - 100,000 API calls/month
   - Priority support 24/7
   - Custom configurations + webhooks
   - Monthly compliance reports

3. **Enterprise Tier**: SAR 75,000+/month (~$20,000+/month)
   - All skills, all domains
   - Unlimited API calls
   - Dedicated support & SLA
   - Custom skill development
   - On-premise deployment option
   - SAMA, NCA, SDAIA compliance
   - Dedicated account manager

### Usage Terms
1. Commercial use requires valid licensing
2. Redistribution or resale prohibited
3. Security vulnerability reporting required
4. Compliance with local and international laws

## API Access

### Live Endpoints
- **API Base URL**: https://skill-folders-api.brainsait-fadil.workers.dev
- **API Documentation**: https://skill-folders-api.brainsait-fadil.workers.dev/docs
- **Landing Page**: [English](../docs/landing/index.html) | [العربية](../docs/ar/index.html)

### Public Endpoints (No Authentication Required)
```bash
# Service info
curl https://skill-folders-api.brainsait-fadil.workers.dev/

# Health check
curl https://skill-folders-api.brainsait-fadil.workers.dev/health

# Pricing tiers
curl https://skill-folders-api.brainsait-fadil.workers.dev/api/pricing
```

### Protected Endpoints (Authentication Required)
```bash
# List all skills
curl -H "Authorization: Bearer sk_your_api_key" \
  https://skill-folders-api.brainsait-fadil.workers.dev/api/skills

# Get skill details
curl -H "Authorization: Bearer sk_your_api_key" \
  https://skill-folders-api.brainsait-fadil.workers.dev/api/skills/cyber-001

# Filter by category
curl -H "Authorization: Bearer sk_your_api_key" \
  "https://skill-folders-api.brainsait-fadil.workers.dev/api/skills?category=healthcare-saudi"
```

## Getting Started

### Option 1: API Integration (Recommended)
1. **Sign Up**: Visit [brainsait.com/trial](https://brainsait.com/trial) for 14-day free trial
2. **Get API Key**: Obtain your API key from the dashboard
3. **Integrate**: Use our [tutorials](../docs/ar/tutorials.html) for step-by-step guides
4. **Deploy**: Start making API calls to access AI skills

### Option 2: On-Premise Deployment (Enterprise)
1. **Contact Sales**: Email sales@brainsait.com for enterprise licensing
2. **Deploy Worker**: Self-host using Cloudflare Workers or similar
3. **Configure**: Set up KV storage and environment variables
4. **Customize**: Add custom skills for your specific needs

## Support & Maintenance
- Weekly updates for laws and regulations
- Monthly review of tools and software
- Quarterly performance and effectiveness assessment

## Contact
For implementation support, customization requests, or partnership inquiries, please contact the development team.
