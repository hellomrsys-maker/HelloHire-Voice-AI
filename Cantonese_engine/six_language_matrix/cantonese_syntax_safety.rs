//! Cantonese Syntax Safety & Zero-Bridge Memory Layout
//! Operating under The Zero-Bridge Synchronous Memory Rule.
//! Fixed 64-byte Atomic Memory State Vector (AMSV) with Magic 0x59554554 ("YUET").

#[repr(C, align(64))]
pub struct CantoneseAtomicStateVector {
    pub magic: [u8; 4],             // 0x00: 0x59554554 ("YUET")
    pub version_major: u8,          // 0x04: Major version
    pub version_minor: u8,          // 0x05: Minor version
    pub engine_mode: u8,            // 0x06: 0x01 = Inference, 0x02 = Parsing
    pub dialect_mode: u8,           // 0x07: 0x01 = Hong Kong, 0x02 = Guangzhou, 0x03 = Taishan
    pub reserved_head: [u8; 10],    // 0x08..0x11: Reserved
    pub syntax_capability: u8,      // 0x12 (Byte 18): Bitfield: V, N, CLF, DOC
    pub doc_inversion_flag: u8,     // 0x13 (Byte 19): 0x01 = Canonical V+DO+IO, 0x00 = Calque
    pub nine_tone_flag: u8,         // 0x14 (Byte 20): Bitfield: valid, entering tone, distinct
    pub aspect_marker_flag: u8,     // 0x15 (Byte 21): 0x01 = Postverbal aspect verified
    pub register_tier: u8,          // 0x16 (Byte 22): 1 = Colloquial, 2 = Formal
    pub sfp_concord_flag: u8,       // 0x17 (Byte 23): Bitfield: SFP present, cluster valid
    pub editorial_confidence: f32,  // 0x18..0x1B (Bytes 24..27): Float32 quality score
    pub reserved_mid: [u8; 24],     // 0x1C..0x33: Reserved
    pub sub_ai_syntax_active: u8,   // 0x34 (Byte 52): 0x01 if active
    pub sub_ai_phonology_active: u8,// 0x35 (Byte 53): 0x01 if active
    pub sub_ai_pragmatic_active: u8,// 0x36 (Byte 54): 0x01 if active
    pub sub_ai_editorial_active: u8,// 0x37 (Byte 55): 0x01 if active
    pub reserved_tail: [u8; 8],     // 0x38..0x3F: Padding to 64 bytes
}

pub const CANTONESE_MAGIC: u32 = 0x59554554;

impl CantoneseAtomicStateVector {
    pub fn new() -> Self {
        Self {
            magic: *b"YUET",
            version_major: 1,
            version_minor: 0,
            engine_mode: 1,
            dialect_mode: 1,
            reserved_head: [0u8; 10],
            syntax_capability: 0,
            doc_inversion_flag: 0,
            nine_tone_flag: 0,
            aspect_marker_flag: 0,
            register_tier: 1,
            sfp_concord_flag: 0,
            editorial_confidence: 0.0,
            reserved_mid: [0u8; 24],
            sub_ai_syntax_active: 0,
            sub_ai_phonology_active: 0,
            sub_ai_pragmatic_active: 0,
            sub_ai_editorial_active: 0,
            reserved_tail: [0u8; 8],
        }
    }

    #[inline(always)]
    pub fn is_magic_valid(&self) -> bool {
        &self.magic == b"YUET"
    }
}
