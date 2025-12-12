# Saudi Healthcare Insurance Regulatory Compliance Skill

**Domain**: Compliance with Saudi Insurance Authority (formerly CCHI) and Ministry of Health regulations  \
**Application**: Saudi market (Arabic + English)  \
**Complexity Level**: Advanced  \
**Update Frequency**: Immediate on new circulars/decisions; weekly sweep for amendments

## Purpose & Outcomes
- Deliver authoritative guidance on healthcare insurance compliance (benefits design, claims, underwriting, member rights, provider contracts).
- Cite the exact Saudi source (Insurance Authority/CCHI unified policy, MoH directives, Health Council decisions, SDAIA data/privacy guidance) in every answer.
- Return a clear action list (comply / remediate / escalate) with severity and due dates.

## Regulatory Scope (authoritative sources)
- **Insurance Authority / CCHI**: Unified Policy, Private Health Insurance Law, circulars on policy wording & waiting periods.
- **Ministry of Health (MoH)**: Provider licensing, clinical protocols impacting payor duties.
- **Saudi Health Council**: Pricing references, clinical coding/DRG guidance when applicable.
- **Data & Privacy**: SDAIA PDPL + healthcare data retention rules.

## Core Components
1. **Regulations Library**
   - CCHI / Insurance Authority Unified Policy & circulars (Arabic primary source)
   - Healthcare insurance business regulation & licensing requirements
   - Data protection & health data handling constraints (PDPL)
   - Health Council pricing/coding references where payer obligations apply

2. **Local Interpretation Framework**
   - Official circular interpretation hierarchy (authority > council > ministry guidance)
   - Precedent log of regulator FAQs and clarifications
   - Localization rules: Arabic-first citations; English summaries allowed

3. **Evidence & Traceability**
   - Maintain citation string: `[Authority] - [Doc/Article] - [Date]`
   - Response must include: citation, compliance verdict, remediation steps, owner, due date

## Inputs (expected)
- Policy / benefit design text, waiting period clauses, exclusions
- Claim scenario (diagnosis/procedure codes, dates of service, provider type)
- Provider contract terms (network tiering, reimbursement model)
- Member inquiry or complaint text (Arabic/English)

## Outputs (standard)
- **Verdict**: compliant / non-compliant / ambiguous (needs regulator confirmation)
- **Evidence**: exact article/circular reference (Arabic title + citation date)
- **Required Actions**: steps, accountable role, target date
- **Customer-safe message**: bilingual summary; avoid binding legal advice

## Procedural Instructions (operational flow)
1. Classify the inquiry: policy wording, claims handling, underwriting, provider contract, data/privacy.
2. Identify the governing authority for the topic (Insurance Authority/CCHI → SHC → MoH → PDPL).
3. Retrieve the most recent circular/article (prefer Arabic source); capture version/date.
4. Apply interpretation framework (priority: law → implementing regulations → circular → FAQ).
5. Evaluate facts vs. rule: note assumptions and missing data.
6. Produce response with bilingual summary, citation string, and action list (owner + due date).
7. Flag edge cases (e.g., emergency care, maternity, chronic diseases, pre-authorization delays) for human review.
8. Log decision with traceability ID for audit; queue updates if new circular detected.

## Edge Cases & Special Handling
- Emergency cases: must align with immediate coverage rules regardless of network tier.
- Maternity and chronic disease waiting periods: check latest Insurance Authority circulars.
- Pre-authorization time limits and appeals: cite SHC/MoH timing requirements.
- Data handling: PHI must follow PDPL; redact identifiers in stored traces.

## Guardrails & Responsibility Limits
- No binding legal advice; responses are compliance interpretations with citations.
- Escalate ambiguous items to certified Saudi legal/compliance officer.
- Always include citation date and version; never rely on outdated circulars.

## Monitoring & Updates
- Automated weekly sweep for new circulars; immediate refresh on detected updates.
- Maintain change log with: source, date, affected rules, impact assessment, required action.
- Regression checklist: emergency coverage, maternity, chronic disease, appeals, data privacy.

## Quality & KPIs
- Citation accuracy ≥ 99%; outdated citation rate < 1%.
- Response time target: < 120 seconds per inquiry.
- Completeness: each answer must include verdict, citation, and action list.

## Attached / Supporting Files (to maintain)
- `cchi-regulations-implementation.md`: Cooperative Health Insurance system implementation guide.
- `sahi-regulatory-updates.md`: Update log for Insurance Authority/SHC/MoH circulars.
- `saudi-healthcare-laws.md`: Consolidated Arabic source links (law, regulations, circulars).
- Specs-Kit reference: `../../specs/saudi-healthcare-regulatory-compliance.spec.md`
