# Specs-Kit: Saudi Healthcare Insurance Regulatory Compliance Skill

**Skill Path**: `04-healthcare-insurance-saudi/01-regulatory-compliance-saudi`

**Owner**: Compliance & Health Insurance Domain Lead  \\
**Version**: 1.0  \\
**Last Reviewed**: 2025-12-13  \\
**Market**: Saudi Arabia (Arabic primary, English secondary)

## 1) Purpose
Provide authoritative, citation-backed compliance guidance for Saudi healthcare insurance operations (benefits design, claims adjudication, underwriting, member rights, provider contracting, data/privacy).

## 2) Regulatory Coverage (sources to track)
- **Insurance Authority / CCHI**: Unified Policy, Private Health Insurance Law, circulars on waiting periods, exclusions, underwriting, policy wording.
- **Ministry of Health (MoH)**: Provider licensing, clinical protocols impacting payer obligations.
- **Saudi Health Council (SHC)**: Pricing references, clinical coding/DRG guidance where payer rules apply.
- **SDAIA PDPL & health data retention**: Data and privacy handling for PHI/PII.

> Maintain Arabic primary sources; include citation string: `[Authority] - [Doc/Article] - [Date]` in every output.

## 3) Personas & Consumers
- Claims operations analyst
- Compliance/legal reviewer
- Customer care (member/provider inquiries)
- Product/benefits design owner

## 4) Inputs & Preconditions
- Policy/benefit wording, waiting period clauses, exclusions
- Claim scenario (diagnosis/procedure codes, dates of service, provider type)
- Provider contract terms (network tiering, reimbursement model)
- Member inquiry/complaint (Arabic/English)
- Preferred language for response (`ar` default, `en` secondary)

## 5) Outputs & Acceptance Criteria
- **Verdict**: `compliant | non-compliant | ambiguous (needs regulator confirmation)`
- **Evidence**: exact citation (Arabic title, article/circular number, date)
- **Required Actions**: steps, accountable role, target date
- **Customer-safe message**: bilingual summary, non-binding legal disclaimer
- **Traceability**: decision ID, version of source document

Acceptance criteria: Every response contains verdict + citation + actions. Outdated citation rate < 1%; response time target < 120 seconds.

## 6) Core Workflow (operational)
1. Classify inquiry (policy wording, claims, underwriting, provider contract, data/privacy).
2. Map authority priority: Insurance Authority/CCHI → SHC → MoH → PDPL.
3. Retrieve most recent circular/article (Arabic source preferred) and capture version/date.
4. Apply interpretation hierarchy: law → implementing regulation → circular → FAQ/clarification.
5. Evaluate facts vs. rule; note assumptions and missing data.
6. Produce bilingual response with citation string, verdict, and action list (owner + due date).
7. Flag edge cases for human review (emergency care, maternity, chronic diseases, appeals, data privacy).
8. Log decision with traceability ID; store citation and source version for audit.

## 7) Decision Matrix (routing guide)
- **Policy wording / waiting periods / exclusions** → Insurance Authority/CCHI unified policy & circulars.
- **Claims turnaround / appeals / emergency coverage** → Insurance Authority/CCHI + SHC timing rules; MoH for clinical protocol alignment.
- **Provider licensing / clinical compliance** → MoH primary, SHC secondary.
- **Data handling / PHI** → PDPL (SDAIA) + sectoral health data retention.

## 8) Validation Rules
- Always return Arabic citation text; English summary allowed but not a substitute.
- Include document date/version in every citation.
- If source freshness > 90 days and newer circular exists, mark response as **needs update** and escalate.
- Redact member identifiers in stored traces; do not log full PHI.

## 9) Localization
- Arabic-first answers for official references; mirror English summary beneath.
- Preserve regulator terminology; avoid free translation of legal terms.

## 10) Monitoring & Updates
- Weekly sweep for new circulars; immediate refresh on detected updates.
- Change log entry: source, date, impacted rules, action required, owner.
- Regression set: emergency coverage, maternity, chronic disease, appeals SLA, data privacy.

## 11) Test Scenarios (examples)
1. **Emergency care out-of-network**: Expect ruling that emergency must be covered, cite Insurance Authority emergency rule; action = reimburse per tariff, log exception.
2. **Maternity waiting period**: Validate waiting period clause; cite latest circular; action = update policy wording if misaligned.
3. **Appeal timeline**: Member appeal filed after claim denial; check SHC/MoH timing; action = communicate SLA and reopen if breached.
4. **Data sharing with provider**: Ensure PDPL compliance; action = mask identifiers and ensure lawful basis.

## 12) Dependencies / Artifacts to Maintain
- `cchi-regulations-implementation.md` (implementation notes & mappings)
- `sahi-regulatory-updates.md` (update log + change impacts)
- `saudi-healthcare-laws.md` (source links and citation registry)

## 13) Open Items / Follow-ups
- Automate circular ingestion (RSS/email/portal scrape) with Arabic OCR if PDFs.
- Add structured citation registry (YAML/JSON) for source versioning.
- Extend decision matrix with pre-authorization SLAs and penalties once new circulars arrive.
