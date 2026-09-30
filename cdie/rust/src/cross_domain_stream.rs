//! cross_domain_stream.rs — Real-time stream processing for cross-domain idea transfer in Rust

pub struct CrossDomainAnalysis {
    pub cdti: f32,
    pub transfer_grade: u8,
    pub has_cross_domain_bridge: bool,
    pub manifold_distance: f32,
}

pub fn analyze_cross_domain(text: &str) -> CrossDomainAnalysis {
    let lower = text.to_lowercase();
    let connectors = ["like a", "similar to how", "just as", "akin to", "analogous to", "draws inspiration from"];
    let bio_terms = ["dna", "cellular", "evolution", "immune", "antigen", "organism"];
    let tech_terms = ["latency", "cache", "throughput", "concurrency", "distributed", "database"];

    let has_connector = connectors.iter().any(|c| lower.contains(c));
    let has_bio = bio_terms.iter().any(|b| lower.contains(b));
    let has_tech = tech_terms.iter().any(|t| lower.contains(t));

    let has_bridge = has_connector && has_bio && has_tech;
    let distance = if has_bio && has_tech { 0.85 } else { 0.25 };

    let cdti = if has_bridge {
        0.88
    } else if has_bio && has_tech {
        0.55
    } else if has_connector {
        0.40
    } else {
        0.20
    };

    let grade = if cdti >= 0.75 { 1 }
        else if cdti >= 0.55 { 2 }
        else if cdti >= 0.35 { 3 }
        else { 4 };

    CrossDomainAnalysis {
        cdti,
        transfer_grade: grade,
        has_cross_domain_bridge: has_bridge,
        manifold_distance: distance,
    }
}
