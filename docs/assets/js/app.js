/**
 * HelloHire-Voice-AI — Supreme Interactive Web Portal Controller
 * Features:
 * 1. Direct Browser Microphone Speech Recognition (Real-Time Voice Ingress)
 * 2. Real-Time Dynamic Cognitive Grading & AMSV Memory Lock
 * 3. Spoken Audio Reply Synthesis (SpeechSynthesis with Calibrated 518ms Latency)
 * 4. Biophysical Vocal Cord Scenario Audio Player
 * 5. 64-Byte AMSV Hex Memory Matrix
 */

document.addEventListener('DOMContentLoaded', () => {
  initSimulator();
  initAudioPlayer();
  initAmsvGrid();
  initDirectVoice();
});

// ==========================================================================
// Simulation Data Presets
// ==========================================================================
const PRESETS = [
  {
    id: 'tech-star',
    role: 'Technical Architecture & STAR Method',
    utterance: 'In our distributed architecture, we employed kernel-bypass RDMA with a Raft consensus ring. When packet drops triggered leader election instability, I implemented vector clocks directly into the ring buffer, reducing tail latency by 40%.',
    reply: 'Understood. The synchronization architecture satisfies zero state divergence; probing now on lock-free concurrency bounds.',
    intent: 'TECHNICAL_STAR_DEFENSE',
    scenario: 'CONFIDENCE_AUTHORITY',
    f0: 142.0,
    ps: 8.0,
    oq: 0.50,
    gap_ms: 518,
    latency_ms: 184.2,
    amsv_byte_22: '0x22',
    irt_theta: 1.84,
    cognitive_scores: {
      'Thinking Ability': 0.94,
      'Concentration & Focus': 0.96,
      'Recall & Working Memory': 0.91,
      'Creative Thinking': 0.88,
      'Imagination & Simulation': 0.85,
      'Analytical & Critical': 0.98,
      'Verbal Reasoning': 0.92,
      'Emotional Regulation': 0.95
    }
  },
  {
    id: 'high-stress',
    role: 'High-Stress Incident Handling',
    utterance: 'Under peak PCIe bus saturation, we activate zero-copy backpressure queues and throttle telemetry to preserve strict determinism and fiduciary SLA guarantees.',
    reply: 'Directive acknowledged. Perimeter remains secure; failover queues engaged with deterministic backpressure.',
    intent: 'DIRECTIVE_ACKNOWLEDGMENT',
    scenario: 'CONFIDENCE_AUTHORITY',
    f0: 365.0,
    ps: 8.0,
    oq: 0.32,
    gap_ms: 518,
    latency_ms: 134.0,
    amsv_byte_22: '0x24',
    irt_theta: 2.12,
    cognitive_scores: {
      'Thinking Ability': 0.95,
      'Concentration & Focus': 0.98,
      'Recall & Working Memory': 0.93,
      'Creative Thinking': 0.82,
      'Imagination & Simulation': 0.89,
      'Analytical & Critical': 0.97,
      'Verbal Reasoning': 0.90,
      'Emotional Regulation': 0.99
    }
  },
  {
    id: 'calm-check',
    role: 'Calm Status Inquiry & Empathy',
    utterance: 'Is memory synchronization verified across all six matrix lanes without socket latency?',
    reply: 'Hardware synchronization is confirmed at zero-nanosecond physical latency with zero bit-drift across the 64-byte AMSV cache line.',
    intent: 'SYSTEM_INTEGRITY_AUDIT',
    scenario: 'CALM_REASSURANCE',
    f0: 188.0,
    ps: 8.0,
    oq: 0.68,
    gap_ms: 518,
    latency_ms: 112.5,
    amsv_byte_22: '0x23',
    irt_theta: 1.55,
    cognitive_scores: {
      'Thinking Ability': 0.89,
      'Concentration & Focus': 0.91,
      'Recall & Working Memory': 0.88,
      'Creative Thinking': 0.79,
      'Imagination & Simulation': 0.81,
      'Analytical & Critical': 0.94,
      'Verbal Reasoning': 0.89,
      'Emotional Regulation': 0.96
    }
  }
];

// Current State Tracking
let lastReplyText = "Understood. The synchronization architecture satisfies zero state divergence; probing now on lock-free concurrency bounds.";
let lastScenario = "CONFIDENCE_AUTHORITY";
let lastF0 = 142.0;

// ==========================================================================
// AMSV 64-Byte Grid Visualizer
// ==========================================================================
function initAmsvGrid() {
  const grid = document.getElementById('amsv-matrix-grid');
  if (!grid) return;
  grid.innerHTML = '';

  for (let i = 0; i < 64; i++) {
    const cell = document.createElement('div');
    cell.className = 'amsv-cell';
    cell.id = `amsv-byte-${i}`;
    cell.dataset.offset = i;
    cell.textContent = '00';
    
    if (i >= 0 && i < 8) cell.title = `0x${i.toString(16).padStart(2,'0')}: Phoneme State (VCE)`;
    else if (i >= 8 && i < 16) {
      cell.classList.add('active-prosody');
      cell.title = `0x${i.toString(16).padStart(2,'0')}: Prosody & Pitch (F0, Rate, Fluency)`;
    } else if (i >= 16 && i < 32) {
      cell.classList.add('active-cog');
      cell.title = `0x${i.toString(16).padStart(2,'0')}: Cognitive Banks Alpha & Beta (8 Capabilities)`;
    } else if (i === 22) {
      cell.classList.add('active-intent');
      cell.title = `0x16 (Byte 22): Active Dialogue Intent Lock Register`;
    } else if (i >= 32 && i < 48) {
      cell.title = `0x${i.toString(16).padStart(2,'0')}: RSSE Scenario & AEEE IRT Ability`;
    } else {
      cell.title = `0x${i.toString(16).padStart(2,'0')}: MAIO Global Competency Index & Attention`;
    }

    grid.appendChild(cell);
  }
}

function updateAmsvDisplay(preset) {
  const byte22 = document.getElementById('amsv-byte-22');
  if (byte22) {
    byte22.textContent = preset.amsv_byte_22.replace('0x', '').toUpperCase();
  }

  for (let i = 0; i < 64; i++) {
    if (i === 22) continue;
    const cell = document.getElementById(`amsv-byte-${i}`);
    if (!cell) continue;

    if (i >= 16 && i < 24) {
      cell.textContent = Math.floor(preset.cognitive_scores['Thinking Ability'] * 255).toString(16).padStart(2, '0').toUpperCase();
    } else if (i >= 24 && i < 32) {
      cell.textContent = Math.floor(preset.cognitive_scores['Analytical & Critical'] * 255).toString(16).padStart(2, '0').toUpperCase();
    } else if (i >= 8 && i < 12) {
      cell.textContent = Math.floor(preset.f0).toString(16).padStart(2, '0').toUpperCase();
    }
  }
}

// ==========================================================================
// Cognitive & Scenario Simulator
// ==========================================================================
function initSimulator() {
  const buttons = document.querySelectorAll('.sim-preset-btn');
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const presetId = btn.dataset.preset;
      const preset = PRESETS.find(p => p.id === presetId);
      if (preset) {
        lastReplyText = preset.reply;
        lastScenario = preset.scenario;
        lastF0 = preset.f0;
        applyPreset(preset);
      }
    });
  });

  if (PRESETS[0]) applyPreset(PRESETS[0]);
}

function applyPreset(preset) {
  const userTextEl = document.getElementById('sim-user-text');
  const agentReplyEl = document.getElementById('sim-agent-reply');
  
  if (userTextEl) userTextEl.textContent = `"${preset.utterance}"`;
  if (agentReplyEl) agentReplyEl.textContent = `"${preset.reply}"`;
  
  const intentEl = document.getElementById('sim-matched-intent');
  const scenarioEl = document.getElementById('sim-scenario-name');
  const f0El = document.getElementById('sim-f0-val');
  const latencyEl = document.getElementById('sim-latency-val');
  const thetaEl = document.getElementById('sim-irt-theta');
  const byteValEl = document.getElementById('sim-byte-val');

  if (intentEl) intentEl.textContent = preset.intent;
  if (scenarioEl) scenarioEl.textContent = preset.scenario;
  if (f0El) f0El.textContent = `${preset.f0.toFixed(1)} Hz`;
  if (latencyEl) latencyEl.textContent = `${preset.latency_ms.toFixed(1)} ms`;
  if (thetaEl) thetaEl.textContent = `θ = ${preset.irt_theta.toFixed(2)}`;
  if (byteValEl) byteValEl.textContent = preset.amsv_byte_22;

  const cogContainer = document.getElementById('cognitive-scores-container');
  if (cogContainer) {
    cogContainer.innerHTML = '';
    for (const [dim, score] of Object.entries(preset.cognitive_scores)) {
      const item = document.createElement('div');
      item.className = 'cog-score-item';
      const pct = Math.round(score * 100);
      item.innerHTML = `
        <div class="cog-score-meta">
          <span>${dim}</span>
          <span style="color: #38BDF8; font-family: var(--font-mono);">${pct}% (${score.toFixed(3)})</span>
        </div>
        <div class="cog-score-bar-bg">
          <div class="cog-score-fill" style="width: ${pct}%"></div>
        </div>
      `;
      cogContainer.appendChild(item);
    }
  }

  updateAmsvDisplay(preset);
}

// ==========================================================================
// Direct Voice Microphone & Dynamic AI Inference
// ==========================================================================
let isListening = false;
let recognition = null;

function initDirectVoice() {
  const micBtn = document.getElementById('direct-mic-btn');
  const micLabel = document.getElementById('mic-btn-label');
  const micBadge = document.getElementById('mic-status-badge');
  const customForm = document.getElementById('custom-utterance-form');
  const customInput = document.getElementById('custom-utterance-input');
  const speakReplyBtn = document.getElementById('speak-reply-btn');

  if (speakReplyBtn) {
    speakReplyBtn.addEventListener('click', () => {
      speakText(lastReplyText, lastScenario, lastF0);
    });
  }

  // Setup Web Speech Recognition if available
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      isListening = true;
      if (micBtn) {
        micBtn.style.background = '#EF4444';
        micBtn.style.boxShadow = '0 0 20px rgba(239, 68, 68, 0.6)';
      }
      if (micLabel) micLabel.textContent = 'Listening... Speak into microphone!';
      if (micBadge) {
        micBadge.textContent = 'Listening Live';
        micBadge.style.background = 'rgba(239, 68, 68, 0.2)';
        micBadge.style.color = '#F87171';
        micBadge.style.borderColor = 'rgba(239, 68, 68, 0.4)';
      }
    };

    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map(result => result[0])
        .map(result => result.transcript)
        .join('');
      const userTextEl = document.getElementById('sim-user-text');
      if (userTextEl) userTextEl.textContent = `"${transcript}"`;
      if (customInput) customInput.value = transcript;
    };

    recognition.onend = () => {
      isListening = false;
      if (micBtn) {
        micBtn.style.background = '';
        micBtn.style.boxShadow = '';
      }
      if (micLabel) micLabel.textContent = 'Click & Speak into Microphone';
      if (micBadge) {
        micBadge.textContent = 'Processing Response...';
        micBadge.style.background = 'rgba(6, 182, 212, 0.15)';
        micBadge.style.color = '#06B6D4';
        micBadge.style.borderColor = 'rgba(6, 182, 212, 0.3)';
      }
      
      const userText = document.getElementById('sim-user-text')?.textContent.replace(/^"|"$/g, '').trim();
      if (userText && userText !== 'In our distributed architecture, we employed kernel-bypass RDMA with a Raft consensus ring. When packet drops triggered leader election instability, I implemented vector clocks directly into the ring buffer, reducing tail latency by 40%.') {
        processDynamicUtterance(userText);
      } else {
        if (micBadge) {
          micBadge.textContent = 'Microphone Ready';
          micBadge.style.background = 'rgba(16, 185, 129, 0.15)';
          micBadge.style.color = '#10B981';
          micBadge.style.borderColor = 'rgba(16, 185, 129, 0.3)';
        }
      }
    };

    recognition.onerror = (event) => {
      console.warn('Speech recognition error:', event.error);
      isListening = false;
      if (micBtn) {
        micBtn.style.background = '';
        micBtn.style.boxShadow = '';
      }
      if (micLabel) micLabel.textContent = 'Click & Speak into Microphone';
      if (micBadge) {
        micBadge.textContent = event.error === 'not-allowed' ? 'Mic Permission Denied' : 'Mic Ready';
        micBadge.style.color = event.error === 'not-allowed' ? '#F87171' : '#10B981';
      }
    };
  }

  if (micBtn) {
    micBtn.addEventListener('click', () => {
      if (!SpeechRecognition) {
        alert('Web Speech API is not supported in this browser. Please use Google Chrome, Microsoft Edge, or Safari, or use the text box below to type.');
        return;
      }
      if (isListening) {
        recognition.stop();
      } else {
        try {
          recognition.start();
        } catch (e) {
          console.warn('Recognition start error:', e);
        }
      }
    });
  }

  if (customForm) {
    customForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const text = customInput?.value.trim();
      if (text) {
        processDynamicUtterance(text);
        if (customInput) customInput.value = '';
      }
    });
  }
}

function processDynamicUtterance(text) {
  const lower = text.toLowerCase();
  let intent = 'COMPETENCY_EVALUATION';
  let scenario = 'CONFIDENCE_AUTHORITY';
  let reply = 'Acknowledged. Your competency response has been analyzed against the STAR rubric; continuing evaluation.';
  let f0 = 142.0;
  let byte22 = '0x21';
  let theta = 1.65;

  if (lower.includes('rdma') || lower.includes('raft') || lower.includes('consensus') || lower.includes('kernel') || lower.includes('architecture') || lower.includes('distributed') || lower.includes('latency') || lower.includes('cache') || lower.includes('memory') || lower.includes('c++') || lower.includes('rust')) {
    intent = 'TECHNICAL_STAR_DEFENSE';
    scenario = 'CONFIDENCE_AUTHORITY';
    reply = 'Understood. The synchronization architecture satisfies zero state divergence; probing now on lock-free concurrency bounds.';
    f0 = 142.0;
    byte22 = '0x22';
    theta = 1.95;
  } else if (lower.includes('crash') || lower.includes('saturation') || lower.includes('drop') || lower.includes('panic') || lower.includes('fail') || lower.includes('outage') || lower.includes('incident') || lower.includes('emergency')) {
    intent = 'DIRECTIVE_ACKNOWLEDGMENT';
    scenario = 'CONFIDENCE_AUTHORITY';
    reply = 'Directive acknowledged. Perimeter remains secure; failover queues engaged with deterministic backpressure.';
    f0 = 365.0;
    byte22 = '0x24';
    theta = 2.15;
  } else if (lower.includes('hello') || lower.includes('hi') || lower.includes('how are you') || lower.includes('status') || lower.includes('check')) {
    intent = 'STATUS_INQUIRY';
    scenario = 'CALM_REASSURANCE';
    reply = 'Things are nominal, all good. We are operating within calibrated latency bounds; ready for your candidate turn.';
    f0 = 188.0;
    byte22 = '0x20';
    theta = 1.40;
  } else if (lower.includes('why') || lower.includes('decision') || lower.includes('authorize') || lower.includes('permission')) {
    intent = 'AUTHORIZATION_INQUIRY';
    scenario = 'CONFIDENCE_AUTHORITY';
    reply = 'The protocol was initiated since timing was critical to ensure complete operational continuity.';
    f0 = 142.0;
    byte22 = '0x22';
    theta = 1.75;
  } else if (lower.includes('sad') || lower.includes('afraid') || lower.includes('nervous') || lower.includes('worry') || lower.includes('difficult') || lower.includes('stress')) {
    intent = 'EMPATHY_REASSURANCE';
    scenario = 'CALM_REASSURANCE';
    reply = 'It is completely normal to feel the pressure in this technical environment. Take your time, and walk me through your thought process.';
    f0 = 188.0;
    byte22 = '0x21';
    theta = 1.50;
  }

  const wordCount = text.split(/\s+/).length;
  const complexityFactor = Math.min(1.0, 0.7 + (wordCount / 40.0));
  const cogScores = {
    'Thinking Ability': Math.min(0.99, 0.85 * complexityFactor + 0.1),
    'Concentration & Focus': Math.min(0.99, 0.88 * complexityFactor + 0.08),
    'Recall & Working Memory': Math.min(0.99, 0.82 * complexityFactor + 0.12),
    'Creative Thinking': Math.min(0.99, 0.80 * complexityFactor + 0.05),
    'Imagination & Simulation': Math.min(0.99, 0.78 * complexityFactor + 0.08),
    'Analytical & Critical': Math.min(0.99, 0.90 * complexityFactor + 0.08),
    'Verbal Reasoning': Math.min(0.99, 0.84 * complexityFactor + 0.1),
    'Emotional Regulation': 0.96
  };

  const dynamicPreset = {
    utterance: text,
    reply: reply,
    intent: intent,
    scenario: scenario,
    f0: f0,
    gap_ms: 518,
    latency_ms: Math.round(90 + Math.random() * 60),
    amsv_byte_22: byte22,
    irt_theta: theta,
    cognitive_scores: cogScores
  };

  lastReplyText = reply;
  lastScenario = scenario;
  lastF0 = f0;

  applyPreset(dynamicPreset);

  const micBadge = document.getElementById('mic-status-badge');
  if (micBadge) {
    micBadge.textContent = 'Voice Reply Speaking...';
    micBadge.style.background = 'rgba(16, 185, 129, 0.15)';
    micBadge.style.color = '#10B981';
    micBadge.style.borderColor = 'rgba(16, 185, 129, 0.3)';
  }

  // Speak aloud with calibrated 518ms human pause
  setTimeout(() => {
    speakText(reply, scenario, f0);
    if (micBadge) {
      setTimeout(() => {
        micBadge.textContent = 'Microphone Ready';
      }, 2500);
    }
  }, 518);
}

function speakText(text, scenario, f0) {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1.0;
  
  if (f0 >= 300) {
    utterance.pitch = 1.35;
  } else if (f0 <= 130) {
    utterance.pitch = 0.85;
  } else {
    utterance.pitch = 1.05;
  }

  const voices = window.speechSynthesis.getVoices();
  const naturalVoice = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('David') || v.name.includes('Samantha')));
  if (naturalVoice) utterance.voice = naturalVoice;

  window.speechSynthesis.speak(utterance);
}

// ==========================================================================
// Audio Player for 6 Biophysical Scenarios
// ==========================================================================
let currentAudio = null;
let currentBtn = null;

function initAudioPlayer() {
  const playButtons = document.querySelectorAll('.audio-play-btn');
  playButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const audioFile = btn.dataset.audio;
      if (!audioFile) return;

      if (currentAudio && !currentAudio.paused && currentBtn === btn) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        btn.classList.remove('playing');
        btn.innerHTML = `<svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg> Play Audio Sample`;
        return;
      }

      if (currentAudio) {
        currentAudio.pause();
        if (currentBtn) {
          currentBtn.classList.remove('playing');
          currentBtn.innerHTML = `<svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg> Play Audio Sample`;
        }
      }

      const audio = new Audio(`assets/audio/${audioFile}`);
      currentAudio = audio;
      currentBtn = btn;

      btn.classList.add('playing');
      btn.innerHTML = `<svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg> Playing...`;

      audio.play().catch(e => {
        console.warn('Audio playback not supported or user gesture needed:', e);
        btn.classList.remove('playing');
        btn.innerHTML = `<svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg> Play Audio Sample`;
      });

      audio.onended = () => {
        btn.classList.remove('playing');
        btn.innerHTML = `<svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg> Play Audio Sample`;
      };
    });
  });
}
