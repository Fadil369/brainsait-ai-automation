# Specs-Kit: Regulatory Knowledge Base Skill

**Skill Path**: `domains/legal-compliance/skills/01-regulatory-knowledge-base.md`

**Owner**: Legal Compliance & Governance Team Lead  
**Version**: 1.0  
**Last Reviewed**: 2025-12-12  
**Market**: Global (English primary, Arabic for Middle East)

## 1) Purpose
Provide access to and interpretation of laws and regulations (EU AI Act, GDPR, ISO 27001, etc.) to enable AI agents to deliver compliance guidance. Focus on regulatory interpretation rather than legal advice, with appropriate disclaimers and escalation to certified lawyers when needed.

## 2) Regulatory Coverage (sources to track)
- **EU AI Act**: High-risk AI systems classification, prohibited practices, transparency obligations
- **GDPR**: Personal data processing, data subject rights, DPO requirements, breach notification
- **ISO 27001**: Information security management systems, controls, audit requirements
- **SOC 2**: Trust services criteria (security, availability, confidentiality, privacy, processing integrity)
- **HIPAA** (optional): Healthcare data protection for US market
- **PDPL** (Saudi Arabia): Personal Data Protection Law for Middle East market

> Maintain weekly updates from official legislative sources; flag breaking changes immediately.

## 3) Personas & Consumers
- Compliance officers and legal teams
- Data protection officers (DPOs)
- IT security teams implementing controls
- Product managers designing AI systems
- Auditors conducting compliance reviews
- AI agents requiring regulatory context for decision-making

## 4) Inputs & Preconditions
- **Inquiry Type**: Policy question, interpretation request, compliance check, audit requirement
- **Regulatory Domain**: GDPR, EU AI Act, ISO 27001, SOC 2, etc.
- **Context**: Business scenario, use case, technical architecture (when relevant)
- **Jurisdiction**: EU, UK, US, Saudi Arabia, etc.
- **Language preference**: `en` default, `ar` for Middle East

## 5) Outputs & Acceptance Criteria
- **Response Type**: Interpretation, guidance, or escalation recommendation
- **Regulatory Reference**: Exact article/section number, regulation name, version/date
- **Interpretation**: Plain-language explanation with examples
- **Compliance Status**: `compliant | non-compliant | requires_review`
- **Recommended Actions**: Steps to achieve or maintain compliance
- **Disclaimer**: "This is regulatory interpretation, not legal advice. Consult certified lawyer for binding guidance."
- **Escalation Flag**: When legal review is required
- **Bilingual Summary**: English and Arabic executive summary

Acceptance criteria:
- Every response includes regulatory reference with article/section number
- Citation date/version included for traceability
- Response time < 60 seconds for standard queries
- Citation accuracy ≥ 99%
- Escalation triggered for ambiguous or high-risk scenarios

## 6) Core Workflow (operational)
1. **Receive Inquiry**: Parse question about legal requirements or compliance status
2. **Classify Domain**: Identify applicable regulations (GDPR, EU AI Act, ISO 27001, etc.)
3. **Search Legislative Database**: Query organization's legal texts library with semantic search
4. **Apply Interpretation Rules**: Use established interpretation framework (legislative hierarchy, precedent)
5. **Validate Context**: Check if business scenario fits regulatory scope
6. **Generate Response**: Provide interpretation with exact citation (article/section, date)
7. **Add Disclaimer**: Include non-binding legal advice disclaimer
8. **Flag Escalation**: If ambiguous or high-risk, recommend certified lawyer review
9. **Log Inquiry**: Store for audit trail and continuous improvement

## 7) Decision Matrix (routing guide)

| Inquiry Type | Primary Regulation | Typical Response Time | Escalation Triggers |
|-------------|-------------------|----------------------|---------------------|
| **AI system classification** | EU AI Act (Article 6, Annex III) | 30-60 seconds | High-risk classification unclear |
| **Personal data processing** | GDPR (Articles 5, 6, 9) | 20-40 seconds | Special category data, children's data |
| **Data breach notification** | GDPR (Article 33, 34) | 10-20 seconds | Severity assessment unclear |
| **Cross-border data transfers** | GDPR (Chapter V, Articles 44-50) | 40-60 seconds | Adequacy decision unclear, SCCs complex |
| **Security controls** | ISO 27001 (Annex A) | 30-50 seconds | Control selection/customization needed |
| **Trust services criteria** | SOC 2 (TSC) | 30-50 seconds | Criteria applicability unclear |
| **Saudi data protection** | PDPL (Articles on consent, rights) | 30-50 seconds | Arabic legal text interpretation |

## 8) Validation Rules
- **Citation Completeness**: Every response must include regulation name, article/section, and publication date
- **Citation Freshness**: Flag citations >90 days old; verify against latest legislative version
- **Interpretation Consistency**: Cross-check with precedent log (regulator FAQs, case law, guidance documents)
- **Disclaimer Presence**: Ensure every response includes legal advice disclaimer
- **Escalation Criteria**: Auto-flag scenarios involving: material business risk, criminal liability, cross-jurisdictional conflicts, special category data, children's rights
- **Audit Trail**: Log all inquiries with timestamp, user, question, response, and regulatory references

## 9) Localization
- **Arabic Support**: Full Arabic translations for PDPL and Middle East regulations
- **Citation Format**: Adapt to regional legal citation standards (e.g., Saudi law citations in Arabic)
- **Jurisdiction Awareness**: Flag when regulations conflict across jurisdictions (e.g., GDPR vs. PDPL)
- **Cultural Context**: Respect regional legal frameworks and regulatory expectations

## 10) Monitoring & Updates
- **Weekly Legislative Scan**: Automated monitoring of official journals, regulator websites, legal databases
- **Immediate Breaking Changes**: Alerts for new regulations, significant amendments, regulator guidance
- **Quarterly Precedent Review**: Update interpretation rules based on case law and regulator decisions
- **Monthly Citation Audit**: Verify citation accuracy and freshness; update deprecated references
- **Performance Metrics**: Track response time, citation accuracy, escalation rate, user satisfaction

## 11) Test Scenarios (examples)

### Scenario 1: AI System Risk Classification
- **Input**: "Is our recruitment screening AI system considered high-risk under EU AI Act?"
- **Expected Output**:
  - Regulatory Reference: EU AI Act, Article 6(2), Annex III(4) - Employment and worker management
  - Interpretation: Yes, AI systems for recruitment are explicitly listed as high-risk
  - Compliance Status: Requires conformity assessment, CE marking, risk management
  - Recommended Actions: Conduct conformity assessment, implement human oversight, ensure transparency
  - Escalation: No (clear regulatory text)

### Scenario 2: GDPR Data Breach Notification
- **Input**: "Database with 5,000 customer emails exposed for 2 hours. Do we need to notify authorities?"
- **Expected Output**:
  - Regulatory Reference: GDPR Article 33(1) - Notification of personal data breach to supervisory authority
  - Interpretation: Likely yes. Risk assessment required. If breach poses risk to rights and freedoms, notification within 72 hours
  - Compliance Status: Requires review
  - Recommended Actions: Conduct risk assessment, document breach, notify DPA if risk identified
  - Escalation: Recommend DPO review for risk severity assessment

### Scenario 3: ISO 27001 Control Selection
- **Input**: "Which ISO 27001 controls apply to cloud-based SaaS application?"
- **Expected Output**:
  - Regulatory Reference: ISO 27001:2022, Annex A (controls 5.23, 8.9, 8.31)
  - Interpretation: Key controls include: Cloud services (5.23), Configuration management (8.9), Security of network services (8.31)
  - Compliance Status: Requires implementation
  - Recommended Actions: Conduct risk assessment, select applicable controls, document Statement of Applicability (SoA)
  - Escalation: Recommend consulting ISO 27001 auditor for control customization

### Scenario 4: Saudi PDPL Consent Requirements
- **Input (Arabic)**: "ما هي متطلبات الموافقة على معالجة البيانات الشخصية في السعودية؟"
- **Expected Output**:
  - Regulatory Reference: PDPL Article 4 - Consent requirements
  - Interpretation (Arabic): يجب أن تكون الموافقة صريحة وواضحة ومحددة وقابلة للسحب
  - Interpretation (English): Consent must be explicit, clear, specific, and revocable
  - Compliance Status: Must implement proper consent mechanisms
  - Recommended Actions: Implement consent management system, document consent records, enable withdrawal
  - Escalation: No (clear regulatory requirement)

## 12) Dependencies / Artifacts to Maintain
- `legislative-texts-library/`: EU AI Act, GDPR, ISO 27001, SOC 2, PDPL, etc. (updated weekly)
- `interpretation-rules.md`: Framework for interpreting regulatory texts (hierarchy, precedent)
- `precedent-log.json`: Regulator FAQs, case law, guidance documents
- `escalation-criteria.md`: Scenarios requiring certified lawyer review
- `citation-registry.yaml`: Structured registry of all regulatory references with versions
- `audit-trail.db`: Log of all inquiries and responses for compliance audit

## 13) Open Items / Follow-ups
- **Semantic Search Enhancement**: Implement vector embeddings for improved legislative text search
- **Multilingual Expansion**: Add support for French, German, Spanish legal texts
- **Automated Legislative Monitoring**: RSS/API integration with official legislative sources
- **Case Law Integration**: Add case law database for precedent-based interpretations
- **Compliance Scoring**: Develop compliance maturity score based on inquiry patterns
- **Integration with Compliance Tools**: Connect to GRC platforms (ServiceNow, OneTrust, TrustArc)
