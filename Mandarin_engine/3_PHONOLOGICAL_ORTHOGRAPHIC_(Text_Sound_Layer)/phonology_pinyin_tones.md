# Mandarin Engine — Layer 3: Phonological & Orthographic Layer
## Chinese Tones, Pinyin G2P, Tone Sandhi & Hanzi Orthography

### 1. The Quad-Tone System & Chao Pitch Values
Mandarin phonology operates over ~400 base syllables modulated by 4 phonemic tones plus a neutral tone:
```text
Tone 1 (阴平): 55 (High Level)       — ā (妈 / mā - mother)
Tone 2 (阳平): 35 (High Rising)      — á (麻 / má - hemp)
Tone 3 (上声): 214 (Low Dipping)     — ǎ (马 / mǎ - horse)
Tone 4 (去声): 51 (High Falling)     — à (骂 / mà - scold)
Neutral (轻声): Dynamic light pitch  — a (吗 / ma - question particle)
```

### 2. Tone Sandhi Rules (声调变调律)
1. **Third Tone Sandhi (三声连读变调)**:
   - $3 + 3 \longrightarrow 2 + 3$
   - 例: `你好` (nǐ + hǎo) $\longrightarrow$ pronounced [ní hǎo].
   - Three 3rd tones: `我想买` (wǒ xiǎng mǎi) $\longrightarrow$ [wó xiáng mǎi] or [wǒ xiáng mǎi].
2. **Half Third Tone (半三声)**:
   - When Tone 3 precedes Tone 1, 2, 4, or neutral, the rising tail (4) is dropped: $214 \longrightarrow 21$.
3. **"一" (yī) Sandhi Matrix**:
   - In isolation or ordinals: Tone 1 (`第一` dì-yī).
   - Before Tone 4: Becomes Tone 2 (`一定` yí dìng, `一个` yí ge).
   - Before Tone 1, 2, 3: Becomes Tone 4 (`一天` yì tiān, `一年` yì nián, `一起` yì qǐ).
4. **"不" (bù) Sandhi**:
   - Before Tone 1, 2, 3: Retains Tone 4 (`不好` bù hǎo, `不行` bù xíng).
   - Before Tone 4: Becomes Tone 2 (`不是` bú shì, `不对` bú duì).

### 3. Erhua (儿化 - Rhotacization)
Common in Standard Mandarin and Northern dialects: suffix `-er` fuses into the syllable nucleus with vowel centralization and nasal coda deletion (`花儿` huār, `小孩儿` xiǎoháir).
