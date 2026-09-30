# Layer 2: Morphological Analysis (Word Layer) — Indonesian Language Engine

## 1. Agglutinative Affixation System
Indonesian morphology is predominantly agglutinative, building words from root bases through prefixes, suffixes, circumfixes, and reduplication.

### 1.1 The meN- Prefix & Nasal Assimilation Rules
The active transitive prefix `meN-` has six allomorphs (`me-`, `mem-`, `men-`, `meny-`, `meng-`, `menge-`) governed strictly by the initial phoneme of the root:
1. **Root starts with Voiceless Stop / Fricative (`p, t, s, k`)**: Consonant **deletes** and assimilates into homorganic nasal:
   - `p` $\to$ `m`: *pakai* $\to$ *memakai*, *potong* $\to$ *memotong*, *tulis* $\to$ *menulis*.
   - `t` $\to$ `n`: *tarik* $\to$ *menarik*, *tolong* $\to$ *menolong*.
   - `s` $\to$ `ny`: *sapu* $\to$ *menyapu*, *sewa* $\to$ *menyewa*.
   - `k` $\to$ `ng`: *kirim* $\to$ *mengirim*, *kejar* $\to$ *mengejar*.
   *(Exception: foreign loanwords often resist deletion: proses -> memproses, kritik -> mengkritik).*
2. **Root starts with Voiced Stop (`b, d, j, g`)**: Consonant is **retained** after homorganic nasal:
   - `b`: *baca* $\to$ *membaca*, *beli* $\to$ *membeli*.
   - `d`: *dengar* $\to$ *mendengar*, *dorong* $\to$ *mendorong*.
   - `j`: *jual* $\to$ *menjual*, *jemput* $\to$ *menjemput*.
   - `g`: *goreng* $\to$ *menggoreng*, *gigit* $\to$ *menggigit*.
3. **Root starts with Vowels (`a, e, i, o, u`) or `h, kh`**: Prefix becomes `meng-`:
   - *ambil* $\to$ *mengambil*, *isi* $\to$ *mengisi*, *ubah* $\to$ *mengubah*, *hitung* $\to$ *menghitung*.
4. **Root starts with Liquids or Nasals (`l, r, m, n, ny, ng, w, y`)**: Prefix becomes `me-`:
   - *lihat* $\to$ *melihat*, *rasa* $\to$ *merasa*, *masak* $\to$ *memasak*, *nyanyi* $\to$ *menyanyi*.
5. **Monosyllabic Roots**: Prefix becomes `menge-`:
   - *bom* $\to$ *mengebom*, *cat* $\to$ *mengecat*, *lap* $\to$ *mengelap*, *klik* $\to$ *mengeklik*.

### 1.2 Other Verbal Prefixes
- **`di-`**: Passive voice marker (*dibaca, ditulis, dikirim*).
- **`ter-`**: Accidental, non-volitional, stative, or superlative (*tertidur* = fallen asleep, *terbuka* = open, *terbesar* = biggest).
- **`ber-`**: Intransitive, stative, or possessive verb (*berjalan* = walk, *berbahasa* = speak language). Drops `r` before roots starting with `r` or containing `-er-` in the first syllable: *bekerja* (from *kerja*), *berenang* (from *renang*).

### 1.3 Verbal Suffixes: -kan and -i
- **`-kan`**: Causative (*tidur* $\to$ *menidurkan* = put to sleep) or Benefactive (*beli* $\to$ *membelikan* = buy for someone).
- **`-i`**: Locative (*datang* $\to$ *mendatangi* = visit a place) or Iterative/repetitive (*pukul* $\to$ *memukuli* = beat repeatedly).

### 1.4 Nominal Circumfixes
- **`peN-...-an`**: Action/process nominalizer (*didik* $\to$ *pendidikan* = education, *bangun* $\to$ *pembangunan* = development).
- **`ke-...-an`**: State, condition, or abstract entity (*adil* $\to$ *keadilan* = justice, *sehat* $\to$ *kesehatan* = health).
- **`per-...-an`**: Result, place, or reciprocal noun (*janjian* $\to$ *perjanjian* = treaty/agreement, *sahabat* $\to$ *persahabatan* = friendship).

## 2. Reduplication Typology (Reduplikasi)
- **Full (Dwilingga)**: Plurality, diversity (*anak-anak, buku-buku, rumah-rumah*).
- **Partial (Dwipurwa)**: Morphological base (*daun* $\to$ *dedaunan*, *pohon* $\to$ *pepohonan*).
- **Imitative / Sound-Shift (Dwilingga Salin Suara)**: Semantic nuance (*sayur-mayur, bolak-balik, warna-warni*).
- **Affixed (Reduplikasi Berimbuhan)**: *makan-makan, jalan-jalan, tolong-menolong*.
