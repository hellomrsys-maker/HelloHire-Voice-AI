# Mandarin Engine — Layer 4: Semantic Representation (Meaning Layer)
## Chinese Homophone Resolution, Chengyu Idioms & Thematic Roles

### 1. The Homophone Resolution Architecture
Due to an inventory of only ~400 distinct segmental syllables, Mandarin exhibits extreme lexical homophony:
- Syllable `shi` maps to over 30 common morphemes: 是 (be), 事 (matter), 市 (city), 视 (vision), 室 (room), 试 (test), 诗 (poem), 师 (teacher), 狮 (lion), 湿 (wet), 十 (ten), 时 (time), 食 (food), 史 (history)...
- Resolution Mechanism: Bigram/Trigram context Windows, shape classifiers, and neural word-level disambiguation.

### 2. Chengyu (成语) Four-Character Idiomatic Matrix
Chengyu represent condensed classical anecdotes functioning as single lexical units with deep pragmatic connotations:
- `塞翁失马` (sài wēng shī mǎ): Blessing in disguise (literal: the old frontiersman lost his horse).
- `画蛇添足` (huà shé tiān zú): Ruining something by adding superfluous elements (literal: draw snake add feet).
- `半途而废` (bàn tú ér fèi): Giving up halfway.
- `胸有成竹` (xiōng yǒu chéng zhú): Having a well-thought-out plan in advance.
- `名落孙山` (míng luò sūn shān): Failing an examination.
- `卧薪尝胆` (wò xīn cháng dǎn): Enduring hardships to accomplish a grand ambition.

### 3. Thematic Roles in Mandarin Syntax
- **Agent (施事)**: Originator of action (Subject in canonical SVO; prepositional object in `被` passive).
- **Patient / Theme (受事)**: Target undergoing change (Preposed after `把` in disposal clauses).
- **Instrument (工具)**: Prepositional `用` (yòng).
- **Benefactive (受益者)**: Prepositional `给` (gěi) or `替` (tì).
