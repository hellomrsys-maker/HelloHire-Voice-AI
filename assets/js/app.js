/**
 * HelloHire Voice AI — Supreme Interactive Web Portal Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  initSimulator();
  initAudioPlayer();
  initAmsvGrid();
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
    utterance: 'Is memory synchronization verified across all six matrix lanes without any traditional socket latency?',
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
    
    // Categorize byte roles based on AMSV standard
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

  // Populate synthetic values for demonstration
  for (let i = 0; i < 64; i++) {
    if (i === 22) continue;
    const cell = document.getElementById(`amsv-byte-${i}`);
    if (!cell) continue;

    if (i >= 16 && i < 24) {
      // Cog Alpha
      cell.textContent = Math.floor(preset.cognitive_scores['Thinking Ability'] * 255).toString(16).padStart(2, '0').toUpperCase();
    } else if (i >= 24 && i < 32) {
      // Cog Beta
      cell.textContent = Math.floor(preset.cognitive_scores['Analytical & Critical'] * 255).toString(16).padStart(2, '0').toUpperCase();
    } else if (i >= 8 && i < 12) {
      // F0 in Q8.8
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
      if (preset) applyPreset(preset);
    });
  });

  // Apply initial preset
  if (PRESETS[0]) applyPreset(PRESETS[0]);
}

function applyPreset(preset) {
  // Update Utterance & Reply
  document.getElementById('sim-user-text').textContent = `"${preset.utterance}"`;
  document.getElementById('sim-agent-reply').textContent = `"${preset.reply}"`;
  
  // Meta Badges
  document.getElementById('sim-matched-intent').textContent = preset.intent;
  document.getElementById('sim-scenario-name').textContent = preset.scenario;
  document.getElementById('sim-f0-val').textContent = `${preset.f0.toFixed(1)} Hz`;
  document.getElementById('sim-latency-val').textContent = `${preset.latency_ms.toFixed(1)} ms`;
  document.getElementById('sim-irt-theta').textContent = `θ = ${preset.irt_theta.toFixed(2)}`;
  document.getElementById('sim-byte-val').textContent = preset.amsv_byte_22;

  // Update Cognitive Scores
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

  // Update AMSV Grid
  updateAmsvDisplay(preset);
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
