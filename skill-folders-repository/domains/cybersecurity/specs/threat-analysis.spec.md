# Specs-Kit: Threat Analysis Skill

**Skill Path**: `domains/cybersecurity/skills/01-threat-analysis.md`

**Owner**: Cybersecurity & SOC Team Lead  
**Version**: 1.0  
**Last Reviewed**: 2025-12-12  
**Market**: Global (English primary, Arabic for Middle East)

## 1) Purpose
Provide real-time threat detection, network activity monitoring, and security anomaly identification with <5 second latency. Enable proactive threat intelligence and rapid incident response through ML-based behavioral analysis and MITRE ATT&CK framework mapping.

## 2) Technical Coverage (sources & integrations)
- **SIEM Platforms**: Splunk, ELK Stack, Azure Sentinel, Google Chronicle, IBM QRadar
- **Log Sources**: Firewall logs, IDS/IPS alerts, EDR telemetry, cloud platform logs (AWS CloudTrail, Azure Monitor, GCP Cloud Logging)
- **Threat Intelligence**: MITRE ATT&CK, VirusTotal, AlienVault OTX, STIX/TAXII feeds, MISP, OpenCTI
- **Network Sensors**: Palo Alto, Fortinet, Cisco, Zeek (Bro), NetFlow, PCAP
- **Behavioral Baselines**: UEBA (User and Entity Behavior Analytics), ML anomaly detection

> Maintain threat intelligence feeds updated hourly; baseline recalculation daily.

## 3) Personas & Consumers
- SOC (Security Operations Center) analysts
- Incident response team
- Threat hunters
- CISO / Security leadership (executive reports)
- Compliance auditors (audit trail access)

## 4) Inputs & Preconditions
- Real-time log streams from security infrastructure (firewalls, endpoints, cloud)
- Network traffic data (NetFlow, PCAP, Zeek logs)
- Threat intelligence feeds (IOCs, reputation data)
- Security policies and acceptable use baselines
- Asset inventory and criticality ratings
- Preferred language for alerts (`en` default, `ar` for Middle East)

## 5) Outputs & Acceptance Criteria
- **Alert ID**: Unique identifier for correlation and tracking
- **Severity**: `critical | high | medium | low | info`
- **Threat Type**: Malware, phishing, data exfiltration, brute force, C2 communication, etc.
- **Affected Assets**: List of compromised or targeted systems with criticality rating
- **IOCs**: IP addresses, domains, file hashes, URLs, user accounts
- **MITRE ATT&CK TTPs**: Mapped tactics, techniques, and procedures
- **Recommended Actions**: Immediate containment steps with priority order and timeline
- **Confidence Score**: 0-100% indicating detection confidence
- **Evidence Chain**: Log excerpts, packet captures, forensic artifacts
- **Timeline**: Event sequence from initial detection to current state
- **Bilingual Summary**: English and Arabic incident description

Acceptance criteria: 
- Detection latency < 5 seconds
- False positive rate < 5%
- MITRE ATT&CK coverage ≥ 95% of techniques
- Alert accuracy ≥ 90%
- Time to containment < 15 minutes for critical threats

## 6) Core Workflow (operational)
1. **Ingest**: Collect logs from firewalls, EDR, SIEM, cloud platforms
2. **Normalize**: Convert diverse log formats into unified schema
3. **Baseline**: Establish normal behavior patterns for users, systems, network segments
4. **Detect**: Apply ML models (Random Forest, Isolation Forest, LSTM) and rule-based detection
5. **Enrich**: Query threat intelligence feeds for IOC reputation and threat actor attribution
6. **Classify**: Map to MITRE ATT&CK framework and assign severity based on asset criticality
7. **Prioritize**: Calculate risk score (Severity × Asset Criticality × Confidence)
8. **Alert**: Generate bilingual alert with evidence, recommended actions, and timeline
9. **Track**: Log all detections with alert ID for compliance, forensics, and threat hunting
10. **Feedback Loop**: Incorporate analyst feedback (true positive / false positive) for model improvement

## 7) Detection Matrix (routing guide)

| Threat Category | Primary Detection Method | Data Sources | MITRE Tactics |
|----------------|-------------------------|--------------|---------------|
| **C2 Communication** | Network beaconing patterns, suspicious domains | Firewall logs, DNS logs, proxy logs | Command and Control |
| **Data Exfiltration** | Unusual outbound data volume, protocol anomalies | NetFlow, DLP, cloud logs | Exfiltration |
| **Malware Execution** | Process creation anomalies, suspicious file writes | EDR, Windows Event Logs | Execution |
| **Privilege Escalation** | Unauthorized admin access, token manipulation | Active Directory logs, endpoint logs | Privilege Escalation |
| **Lateral Movement** | Unusual authentication patterns, SMB/RDP abuse | Network logs, authentication logs | Lateral Movement |
| **Phishing** | Malicious URL clicks, credential harvesting | Email gateway, web proxy | Initial Access |
| **Brute Force** | Failed authentication spikes, password spraying | Authentication logs, VPN logs | Credential Access |
| **DDoS** | Traffic volume spikes, SYN floods | NetFlow, firewall, CDN logs | Impact |

## 8) Validation Rules
- **Baseline Refresh**: Recalculate behavioral baselines daily; account for business seasonality
- **Threat Intel Freshness**: IOC feeds updated hourly; stale feeds (>24 hours) marked and alerted
- **Model Drift Detection**: Monitor ML model performance weekly; retrain if accuracy drops >5%
- **False Positive Threshold**: If FP rate exceeds 5% for any detection rule, auto-disable and escalate
- **Confidence Calibration**: Confidence scores must be calibrated; scores >90% require >95% historical accuracy
- **Evidence Chain**: Every alert must include at least 3 supporting log entries or forensic artifacts
- **Privacy Compliance**: Redact PII from alerts; full logs available only to authorized analysts

## 9) Localization
- **Arabic Support**: All alerts available in Arabic for Middle East SOC teams
- **Timezone Awareness**: Convert timestamps to local timezone (Saudi Arabia: UTC+3)
- **Cultural Context**: Adjust baselines for regional work schedules (Saudi: Sunday-Thursday)
- **Regulatory Alignment**: Tag alerts with relevant compliance frameworks (NCA, SAMA, ISO 27001)

## 10) Monitoring & Updates
- **Model Retraining**: Weekly retraining with new threat data and analyst feedback
- **Threat Intelligence Updates**: Hourly sync with external feeds; daily internal threat reports
- **Baseline Refresh**: Daily recalculation; weekly review for anomalies in baseline itself
- **False Positive Review**: Weekly review of dismissed alerts; adjust thresholds and rules
- **Performance Metrics**: Real-time dashboard tracking detection latency, FP/FN rates, MTTR (Mean Time to Respond)
- **Threat Landscape Changes**: Monthly review of emerging threats (zero-days, new malware families, APT campaigns)

## 11) Test Scenarios (examples)

### Scenario 1: C2 Beaconing Detection
- **Input**: Network logs showing periodic connections to suspicious external IP (beaconing pattern)
- **Expected Output**: 
  - Severity: High
  - Threat Type: Command and Control
  - MITRE: T1071 (Application Layer Protocol)
  - IOCs: Suspicious IP, beacon interval, domain
  - Recommended Actions: Block IP at firewall, isolate endpoint, investigate process
  - Confidence: >90%

### Scenario 2: Data Exfiltration via Cloud Storage
- **Input**: NetFlow showing large data transfer to consumer cloud storage (Dropbox, Google Drive) from sensitive server
- **Expected Output**:
  - Severity: Critical
  - Threat Type: Data Exfiltration
  - MITRE: T1567 (Exfiltration Over Web Service)
  - Affected Assets: Database server, user account
  - Recommended Actions: Suspend user account, block cloud storage domain, review access logs
  - Confidence: >85%

### Scenario 3: Privilege Escalation Attempt
- **Input**: Windows Event Log showing multiple failed attempts to access LSASS process, followed by successful token manipulation
- **Expected Output**:
  - Severity: Critical
  - Threat Type: Privilege Escalation
  - MITRE: T1134 (Access Token Manipulation)
  - Evidence: Event IDs 4672, 4688, Sysmon EID 10
  - Recommended Actions: Isolate endpoint immediately, force password reset, forensic memory dump
  - Confidence: >95%

### Scenario 4: Insider Threat - After-Hours Access
- **Input**: VPN login from authorized user at 3 AM (unusual time), followed by access to sensitive HR files
- **Expected Output**:
  - Severity: Medium
  - Threat Type: Insider Threat / Anomalous Behavior
  - MITRE: T1078 (Valid Accounts)
  - Evidence: VPN logs, file access logs, UEBA anomaly score
  - Recommended Actions: Notify user's manager, review recent activities, monitor for next 48 hours
  - Confidence: 70-80% (requires investigation)

## 12) Dependencies / Artifacts to Maintain
- `mitre-attack-mapping.md`: Complete mapping of detection rules to ATT&CK framework
- `threat-intel-sources.yaml`: Configured threat intelligence feeds and API keys
- `detection-rules.yaml`: Custom Sigma/YARA rules and ML model configurations
- `baseline-config.json`: Behavioral baseline parameters and thresholds
- `soc-playbooks.md`: Incident response playbooks for each threat type
- `false-positive-registry.json`: Known false positives and suppression rules

## 13) Open Items / Follow-ups
- **Automated Response Playbooks**: Implement auto-remediation for low-risk threats (e.g., auto-block known malicious IPs)
- **Threat Hunting Workflows**: Build proactive hunting queries based on TTPs not yet observed
- **Cloud-Native Detection**: Expand coverage for serverless (Lambda, Azure Functions) and container (Kubernetes) threats
- **Adversarial ML**: Test detection models against adversarial evasion techniques
- **Integration with SOAR**: Connect to Security Orchestration platforms (Phantom, Demisto) for automated ticketing and response
- **Threat Intelligence Sharing**: Contribute detected IOCs back to community threat intel platforms
