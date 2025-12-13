# Specs-Kit: Deepfake Detection Skill

**Skill Path**: `domains/cybersecurity/skills/02-deepfake-detection.md`

**Owner**: Cybersecurity & Media Forensics Lead  
**Version**: 1.0  
**Last Reviewed**: 2025-12-12  
**Market**: Global (English primary, Arabic for Middle East)

## 1) Purpose
Verify authenticity of video and audio content to detect AI-generated synthetic media (deepfakes) with >98% accuracy. Enable trust verification for critical communications, protect against fraud and misinformation, and provide forensic-grade analysis for legal proceedings.

## 2) Technical Coverage (models & techniques)
- **Video Deepfake Detection**: EfficientNet-B7, XceptionNet, Vision Transformers, face manipulation detection, temporal consistency analysis
- **Audio Deepfake Detection**: WaveLM, Wav2Vec 2.0, RawNet2, spectral analysis, prosody analysis
- **Multimodal Analysis**: Audio-visual synchronization, lip-sync accuracy, environmental consistency
- **Forensic Techniques**: GAN fingerprinting, double compression detection, metadata analysis, C2PA provenance validation
- **Datasets**: FaceForensics++, DeepfakeTIMIT, DFDC, Celeb-DF, WildDeepfake

> Models updated monthly with latest deepfake generation techniques; adversarial testing weekly.

## 3) Personas & Consumers
- Security analysts investigating impersonation fraud
- Legal teams requiring forensic evidence
- Brand protection / PR teams monitoring media mentions
- Compliance officers verifying executive communications
- Media verification journalists
- Social media platforms (content moderation)

## 4) Inputs & Preconditions
- **Video file**: MP4, AVI, MOV, MKV, WebM (max 500 MB)
- **Audio file**: MP3, WAV, FLAC, AAC, OGG (max 100 MB)
- **Image file**: JPG, PNG, HEIC, WebP (max 50 MB)
- **URL**: YouTube, Vimeo, Twitter, Instagram, TikTok
- **Reference sample** (optional): Known authentic sample for comparison
- **Analysis mode**: `quick`, `standard` (default), `forensic`
- **Preferred language**: `en` default, `ar` for Middle East

## 5) Outputs & Acceptance Criteria
- **Analysis ID**: Unique identifier for tracking and legal reference
- **Authenticity Verdict**: `authentic | likely_authentic | suspicious | deepfake_detected`
- **Confidence Score**: 0-100% with calibrated probabilities
- **Manipulation Type**: Face swap, voice clone, lip-sync, attribute edit, full synthesis
- **Evidence Markers**: Timestamps and spatial regions showing anomalies (heatmaps for video frames)
- **Technical Indicators**: Specific artifacts detected (e.g., "lighting inconsistency at 00:15-00:18", "spectral discontinuity at 1200Hz")
- **Risk Level**: `low | medium | high | critical` (based on confidence and manipulation severity)
- **Frame-by-Frame Analysis**: Per-frame authenticity scores for video
- **Spectrogram Anomalies**: Frequency bands showing synthetic patterns for audio
- **Recommended Actions**: Next steps (e.g., "Require human review", "Block content distribution", "Escalate to legal")
- **Forensic Report**: Detailed technical report with methodology and evidence (forensic mode only)
- **Bilingual Summary**: Executive summary in English and Arabic

Acceptance criteria:
- Detection accuracy (AUC-ROC) ≥ 0.98
- False positive rate < 2%
- False negative rate < 3%
- Processing time: <10 seconds per minute of video, <5 seconds per minute of audio
- Explainability: Provide evidence markers for 100% of detections

## 6) Core Workflow (operational)
1. **Upload & Validation**: Receive media file or URL; validate format, size, codec
2. **Preprocessing**: Extract frames (video at 1-5 fps), resample audio (16kHz), check file integrity
3. **Face Detection** (video/image): Detect all faces using MTCNN or RetinaFace; track across frames
4. **Video Analysis Pipeline**:
   - Extract face regions and normalize
   - Apply CNN-based manipulation detectors (EfficientNet, Xception)
   - Temporal consistency check: frame-to-frame lighting, shadow, motion
   - Biological signal analysis: blinking, micro-expressions, pulse detection (PPG)
5. **Audio Analysis Pipeline**:
   - Feature extraction: MFCC, mel-spectrograms, prosodic features (pitch, energy, duration)
   - Apply deepfake detection models (WaveLM, RawNet2)
   - Spectral analysis: identify unnatural frequency transitions
   - Prosody analysis: check rhythm, stress patterns, phoneme coarticulation
6. **Multimodal Fusion**: Combine video and audio signals; check lip-sync accuracy; validate environmental consistency (audio ambience matches visual scene)
7. **Ensemble Voting**: Aggregate predictions from multiple models (5-7 models per modality) for robust detection
8. **Confidence Calibration**: Map raw model outputs to calibrated confidence percentages using temperature scaling
9. **Evidence Generation**: Create heatmaps, annotate anomalous regions, extract representative frames/audio clips
10. **Report Generation**: Produce JSON response (API) and PDF forensic report (forensic mode) in bilingual format

## 7) Detection Matrix (manipulation types)

| Manipulation Type | Primary Indicators | Detection Models | Confidence Threshold |
|------------------|-------------------|------------------|---------------------|
| **Face Swap** | Face boundary artifacts, lighting mismatch | EfficientNet-B7, XceptionNet | >90% |
| **Face Reenactment** | Lip-sync errors, expression timing | Temporal CNN, Lip-Sync detector | >85% |
| **Facial Attribute Edit** | Localized artifacts (age, gender, smile) | Vision Transformer, Attribute Classifier | >88% |
| **Voice Cloning** | Spectral discontinuities, prosody anomalies | WaveLM, RawNet2, Wav2Vec 2.0 | >92% |
| **TTS (Text-to-Speech)** | Robotic prosody, missing breath sounds | Spectrogram CNN, Prosody Analyzer | >95% |
| **Lip-Sync Deepfake** | Audio-visual desynchronization | SyncNet, Multimodal Transformer | >90% |
| **Full Synthesis** | Multiple indicators across all categories | Full ensemble | >85% |

## 8) Validation Rules
- **Minimum Resolution**: Video ≥ 480p (720p preferred), Audio ≥ 16kHz sampling rate
- **Face Detectability**: At least 50% of face visible in ≥60% of frames for video analysis
- **Audio Clarity**: SNR (Signal-to-Noise Ratio) ≥ 10 dB for reliable audio analysis
- **Confidence Calibration**: Scores >90% require >95% historical accuracy on validation set
- **Low Confidence Flagging**: Verdicts with confidence <80% auto-flagged for human review
- **Model Generalization**: Test monthly against new deepfake generators not in training set
- **Bias Testing**: Quarterly audit for demographic bias (race, gender, age); retrain if detected
- **Privacy Compliance**: Auto-delete uploaded media after 24 hours; no storage of PII
- **Reference Comparison**: If reference sample provided, require >85% similarity to authentic sample

## 9) Localization
- **Arabic Audio**: Trained on Modern Standard Arabic (MSA) and Gulf dialects
- **Middle Eastern Faces**: Training dataset includes diverse Middle Eastern ethnicities
- **Cultural Sensitivity**: Flag religious content (e.g., clerics, religious leaders) for mandatory human review
- **Bilingual Reports**: All reports available in Arabic and English
- **Saudi Compliance**: Align with Anti-Cyber Crime Law for evidence handling; GCAM guidelines for media content
- **Data Sovereignty**: Option for on-premise deployment to keep data within Saudi borders

## 10) Monitoring & Updates
- **Model Retraining**: Monthly updates incorporating latest deepfake generators (StyleGAN3, Stable Diffusion, diffusion models)
- **Adversarial Testing**: Weekly tests against state-of-the-art deepfake tools (DeepFaceLab, FaceSwap, Wav2Lip)
- **Dataset Expansion**: Continuous addition of new samples from research datasets and real-world detections
- **False Positive Review**: Weekly audit of authentic content flagged as deepfakes; adjust thresholds
- **Performance Benchmarks**: Quarterly evaluation on academic benchmarks (FaceForensics++, DFDC test sets)
- **Emerging Threats**: Monitor research for new manipulation techniques (e.g., diffusion-based video synthesis, voice conversion)
- **C2PA Integration**: Quarterly review of Content Credentials ecosystem; update provenance validation

## 11) Test Scenarios (examples)

### Scenario 1: Face Swap Deepfake (High Quality)
- **Input**: Video of CEO giving statement; face swapped using DeepFaceLab
- **Expected Output**:
  - Verdict: deepfake_detected
  - Confidence: >95%
  - Manipulation Type: Face swap
  - Evidence: Face boundary artifacts at 00:05-00:12, lighting inconsistency on left cheek
  - Risk Level: Critical
  - Recommended Actions: Block distribution, escalate to legal, preserve evidence

### Scenario 2: Voice Cloning (TTS)
- **Input**: Audio recording of CFO authorizing wire transfer; synthesized using WaveNet
- **Expected Output**:
  - Verdict: deepfake_detected
  - Confidence: >98%
  - Manipulation Type: Voice cloning (TTS)
  - Evidence: Spectral discontinuities at 800-1200Hz, robotic prosody, missing breath sounds
  - Risk Level: Critical
  - Recommended Actions: Immediately flag as fraud attempt, notify security, request human verification

### Scenario 3: Authentic Video (True Negative)
- **Input**: Legitimate press conference video from official news source
- **Expected Output**:
  - Verdict: authentic
  - Confidence: >92%
  - Manipulation Type: None detected
  - Evidence: Consistent lighting, natural blinking (15-20 blinks/min), audio-visual sync within 40ms
  - Risk Level: Low
  - Recommended Actions: No action required; media verified as authentic

### Scenario 4: Lip-Sync Deepfake (Moderate Quality)
- **Input**: Video with audio dubbed using Wav2Lip
- **Expected Output**:
  - Verdict: suspicious
  - Confidence: 78%
  - Manipulation Type: Lip-sync manipulation
  - Evidence: Audio-visual desynchronization of 80ms at 00:20-00:35, unnatural lip movement
  - Risk Level: Medium
  - Recommended Actions: Flag for human review, request original source, conduct forensic analysis

### Scenario 5: Low-Quality Video (Ambiguous)
- **Input**: Heavily compressed video (240p, <500 kbps) with poor lighting
- **Expected Output**:
  - Verdict: likely_authentic (low confidence due to quality)
  - Confidence: 65%
  - Manipulation Type: No clear indicators, but quality too poor for reliable analysis
  - Evidence: Compression artifacts mask potential manipulation signatures
  - Risk Level: Low-Medium
  - Recommended Actions: Request higher quality source, inconclusive for legal use

## 12) Dependencies / Artifacts to Maintain
- `deepfake-detection-models.md`: Model architectures, training procedures, hyperparameters
- `model-weights/`: Serialized model checkpoints (updated monthly)
- `forensic-report-template.md`: Structure for legal-grade PDF reports
- `c2pa-integration-guide.md`: Content Authenticity Initiative SDK usage
- `dataset-sources.md`: Training and validation dataset references with version tracking
- `calibration-curves.json`: Confidence score calibration parameters
- `benchmark-results.md`: Performance metrics on standard test sets (updated quarterly)

## 13) Open Items / Follow-ups
- **Real-Time Streaming**: Add support for live video stream analysis (<3 second latency)
- **Blockchain Provenance**: Integrate with blockchain-based media registries (e.g., Truepic, Starling Lab)
- **AI-Generated Text Detection**: Extend to detect GPT-generated text in subtitles and transcripts
- **Explainable AI**: Enhance explainability with attention maps and saliency visualizations
- **Multi-Language Audio**: Expand to 20+ languages beyond English and Arabic
- **3D Face Models**: Incorporate 3D face reconstruction for improved face swap detection
- **Adversarial Robustness**: Test against adversarial attacks designed to fool detectors
- **Regulatory Compliance**: Obtain forensic certification for use in legal proceedings (ISO 17025)
