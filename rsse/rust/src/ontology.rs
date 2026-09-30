//! Recruitment Scenario Simulation Engine (RSSE) Ontology
//! 
//! Defines comprehensive scenario ontologies across 8 enterprise interview formats:
//! 1. Technical Interview
//! 2. Behavioral Interview (STAR Framework)
//! 3. Competency-Based Interview
//! 4. Case Study / Business Case
//! 5. Group Discussion / Consensus Building
//! 6. Human Resources (HR) Screening
//! 7. Executive / C-Suite Leadership Interview
//! 8. Panel Interview (Multi-Examiner Dynamics)
//!
//! Provides zero-copy memory safety, deterministic scoring rubrics,
//! situational cues, dynamic follow-up probe trees, and register expectation models.

#[repr(u16)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum InterviewFormat {
    Technical = 1,
    Behavioral = 2,
    CompetencyBased = 3,
    CaseStudy = 4,
    GroupDiscussion = 5,
    HrScreening = 6,
    Executive = 7,
    Panel = 8,
}

impl InterviewFormat {
    pub fn from_u16(val: u16) -> Option<Self> {
        match val {
            1 => Some(InterviewFormat::Technical),
            2 => Some(InterviewFormat::Behavioral),
            3 => Some(InterviewFormat::CompetencyBased),
            4 => Some(InterviewFormat::CaseStudy),
            5 => Some(InterviewFormat::GroupDiscussion),
            6 => Some(InterviewFormat::HrScreening),
            7 => Some(InterviewFormat::Executive),
            8 => Some(InterviewFormat::Panel),
            _ => None,
        }
    }

    pub fn as_str(&self) -> &'static str {
        match self {
            InterviewFormat::Technical => "Technical Interview",
            InterviewFormat::Behavioral => "Behavioral Interview (STAR)",
            InterviewFormat::CompetencyBased => "Competency-Based Interview",
            InterviewFormat::CaseStudy => "Case Study / Business Case",
            InterviewFormat::GroupDiscussion => "Group Discussion & Consensus",
            InterviewFormat::HrScreening => "Human Resources Screening",
            InterviewFormat::Executive => "Executive / C-Suite Leadership",
            InterviewFormat::Panel => "Multi-Examiner Panel Interview",
        }
    }
}

#[repr(u16)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SeniorityLevel {
    Entry = 1,
    MidLevel = 2,
    Senior = 3,
    StaffPrincipal = 4,
    DirectorExecutive = 5,
}

#[repr(C)]
#[derive(Debug, Clone, Copy)]
pub struct RegisterExpectation {
    pub formality_level: f32,       // 0.0 (casual) to 1.0 (strictly formal)
    pub technical_density: f32,     // Expected density of domain vocabulary [0.0, 1.0]
    pub hedging_tolerance: f32,     // Acceptable level of hedging language (e.g. "maybe", "I guess")
    pub structure_requirement: f32, // Requirement for structured answers (e.g. STAR, MECE) [0.0, 1.0]
    pub target_wpm_min: f32,        // Minimum acceptable words-per-minute
    pub target_wpm_max: f32,        // Maximum acceptable words-per-minute
}

#[repr(C)]
#[derive(Debug, Clone, Copy)]
pub struct CompetencyWeight {
    pub analytical_thinking: f32,
    pub communication_clarity: f32,
    pub leadership_presence: f32,
    pub emotional_regulation: f32,
    pub domain_expertise: f32,
    pub problem_solving: f32,
}

#[repr(C)]
#[derive(Debug, Clone, Copy)]
pub struct ProbeBranch {
    pub trigger_condition_score_threshold: f32, // Trigger if previous turn score < this threshold
    pub is_escalation: bool,                   // True if probe increases cognitive stress
    pub probe_text_ptr: *const u8,
    pub probe_text_len: usize,
}

pub struct ScenarioDefinition {
    pub scenario_id: u16,
    pub format: InterviewFormat,
    pub seniority: SeniorityLevel,
    pub role_title: &'static str,
    pub industry: &'static str,
    pub core_prompt: &'static str,
    pub register: RegisterExpectation,
    pub weights: CompetencyWeight,
    pub key_jargon: &'static [&'static str],
    pub probes_depth: &'static [&'static str],
    pub probes_stress: &'static [&'static str],
    pub failure_modes: &'static [&'static str],
}

// Static master ontology catalog
pub static SCENARIO_CATALOG: &[ScenarioDefinition] = &[
    // 1. Technical Interview: Distributed Systems Lead
    ScenarioDefinition {
        scenario_id: 101,
        format: InterviewFormat::Technical,
        seniority: SeniorityLevel::StaffPrincipal,
        role_title: "Principal Distributed Systems Architect",
        industry: "Cloud Infrastructure & High-Frequency Trading",
        core_prompt: "Design an ultra-low-latency distributed consensus cluster handling 10 million transactions per second with sub-50-microsecond p99 latency across three availability zones. Explain your memory ordering, network protocol, and failure detection strategy.",
        register: RegisterExpectation {
            formality_level: 0.80,
            technical_density: 0.90,
            hedging_tolerance: 0.15,
            structure_requirement: 0.85,
            target_wpm_min: 120.0,
            target_wpm_max: 165.0,
        },
        weights: CompetencyWeight {
            analytical_thinking: 0.30,
            communication_clarity: 0.20,
            leadership_presence: 0.10,
            emotional_regulation: 0.10,
            domain_expertise: 0.20,
            problem_solving: 0.10,
        },
        key_jargon: &[
            "Raft", "Paxos", "RDMA", "kernel-bypass", "DPDK", "cache-coherency", 
            "linearizability", "split-brain", "quorums", "CAS operations", "vector clocks"
        ],
        probes_depth: &[
            "How do you prevent thread starvation under asymmetric packet drop at the NIC ring buffer?",
            "Explain the exact memory fence semantics you will use between the serialization thread and the zero-copy ring buffer."
        ],
        probes_stress: &[
            "Your proposed architecture violates linearizability during partition healing. Walk me through the exact bug you just introduced.",
            "That design will saturate PCIe lanes within 30 seconds. How do you recover without dropping live customer state?"
        ],
        failure_modes: &[
            "Vague hand-waving on network protocol (saying 'we use sockets' instead of kernel-bypass/eBPF)",
            "Ignoring CAP theorem trade-offs under partition",
            "Lack of quantitative latency bounds (using 'fast' instead of microsecond percentiles)"
        ],
    },

    // 2. Behavioral Interview (STAR Method): Crisis Leadership
    ScenarioDefinition {
        scenario_id: 201,
        format: InterviewFormat::Behavioral,
        seniority: SeniorityLevel::Senior,
        role_title: "Engineering Manager - Site Reliability & Security",
        industry: "Global FinTech Platform",
        core_prompt: "Tell me about a time when a catastrophic zero-day security incident compromised production infrastructure while your primary technical leads were unreachable. Walk me through your Situation, Task, Action, and measurable Result.",
        register: RegisterExpectation {
            formality_level: 0.75,
            technical_density: 0.65,
            hedging_tolerance: 0.20,
            structure_requirement: 0.95, // Strict STAR adherence
            target_wpm_min: 110.0,
            target_wpm_max: 155.0,
        },
        weights: CompetencyWeight {
            analytical_thinking: 0.20,
            communication_clarity: 0.25,
            leadership_presence: 0.25,
            emotional_regulation: 0.20,
            domain_expertise: 0.05,
            problem_solving: 0.05,
        },
        key_jargon: &[
            "incident command", "triage", "blast radius", "containment", "RCA", 
            "post-mortem", "stakeholder communication", "SLA breach", "failover", "forensics"
        ],
        probes_depth: &[
            "What specific pushback did you receive from executive stakeholders during the downtime, and how did you de-escalate?",
            "How did you quantitatively measure whether customer trust was restored post-incident?"
        ],
        probes_stress: &[
            "You mentioned 'we decided'. What specifically did YOU do as an individual that changed the outcome?",
            "Why did your monitoring not catch the vulnerability before the exploit occurred?"
        ],
        failure_modes: &[
            "Failing to articulate the personal 'I' vs 'we' in the Action phase",
            "Omitting quantitative results (revenue loss avoided, MTTR reduction)",
            "Defensive emotional reaction when challenged on architectural mistakes"
        ],
    },

    // 3. Competency-Based Interview: Cross-Functional Alignment
    ScenarioDefinition {
        scenario_id: 301,
        format: InterviewFormat::CompetencyBased,
        seniority: SeniorityLevel::MidLevel,
        role_title: "Senior Product Manager - Enterprise AI",
        industry: "Enterprise SaaS & Automation",
        core_prompt: "Demonstrate how you manage irreconcilable requirements between an engineering team pushing for an entire quarter of technical refactoring and a commercial sales team demanding immediate custom feature delivery for a $5M enterprise renewal.",
        register: RegisterExpectation {
            formality_level: 0.75,
            technical_density: 0.60,
            hedging_tolerance: 0.25,
            structure_requirement: 0.85,
            target_wpm_min: 115.0,
            target_wpm_max: 160.0,
        },
        weights: CompetencyWeight {
            analytical_thinking: 0.25,
            communication_clarity: 0.25,
            leadership_presence: 0.20,
            emotional_regulation: 0.15,
            domain_expertise: 0.05,
            problem_solving: 0.10,
        },
        key_jargon: &[
            "trade-off matrix", "opportunity cost", "technical debt interest", "customer advisory board", 
            "ARR impact", "milestone gating", "feature velocity", "uncompromising compromise"
        ],
        probes_depth: &[
            "Walk me through the exact framework or scoring formula you used to prioritize engineering stability vs customer ARR.",
            "If the customer threatened to churn within 48 hours unless you committed in writing, what would you say to the VP of Sales?"
        ],
        probes_stress: &[
            "Your approach sounds like you surrendered to sales and sacrificed engineering integrity. How do you defend that?",
            "What if engineering refuses to build the compromise and threatens walkouts?"
        ],
        failure_modes: &[
            "Taking an absolute side (demonizing either sales or engineering)",
            "Absence of a quantifiable prioritization framework (e.g. RICE, WSJF)",
            "Inability to manage interpersonal friction"
        ],
    },

    // 4. Case Study / Business Case: Market Entry & Unit Economics
    ScenarioDefinition {
        scenario_id: 401,
        format: InterviewFormat::CaseStudy,
        seniority: SeniorityLevel::Senior,
        role_title: "Strategy & Operations Director",
        industry: "Autonomous Mobility & Logistics",
        core_prompt: "Our autonomous electric delivery fleet company is evaluating entering the German urban logistics market with 5,000 vehicles. Our capital cost per vehicle is €65,000 with a 4-year depreciation schedule. Analyze market size, regulatory risks, unit economics per delivery, and propose a Go/No-Go decision framework.",
        register: RegisterExpectation {
            formality_level: 0.85,
            technical_density: 0.75,
            hedging_tolerance: 0.10,
            structure_requirement: 0.95, // MECE framework required
            target_wpm_min: 110.0,
            target_wpm_max: 150.0,
        },
        weights: CompetencyWeight {
            analytical_thinking: 0.35,
            communication_clarity: 0.20,
            leadership_presence: 0.15,
            emotional_regulation: 0.10,
            domain_expertise: 0.10,
            problem_solving: 0.10,
        },
        key_jargon: &[
            "MECE", "unit economics", "TAM/SAM/SOM", "CAPEX/OPEX", "LTV/CAC", 
            "depreciation schedule", "KBA regulations", "last-mile density", "contribution margin"
        ],
        probes_depth: &[
            "Break down the variable operating costs per vehicle-hour, specifically power, teleoperations, and insurance liability.",
            "How does German labor law and works council regulations impact your autonomous operations team?"
        ],
        probes_stress: &[
            "Your delivery volume estimate is double the total market capacity of Berlin and Munich combined. Recalculate your payback period right now.",
            "Battery degradation in German winters reduces range by 38%. How does that destroy your unit economics?"
        ],
        failure_modes: &[
            "Lack of structured MECE breakdown (jumping to conclusions without framing)",
            "Inability to perform mental math on unit margins",
            "Ignoring local jurisdictional constraints and union dynamics"
        ],
    },

    // 5. Group Discussion / Consensus Building: Steering Committee
    ScenarioDefinition {
        scenario_id: 501,
        format: InterviewFormat::GroupDiscussion,
        seniority: SeniorityLevel::Senior,
        role_title: "Lead Systems Integrator",
        industry: "Healthcare Systems & Telemedicine",
        core_prompt: "In this group simulation, the board has mandated an immediate pivot to a unified patient health record across 42 acquired regional hospitals. Two peers in this discussion are aggressively advocating incompatible off-the-shelf vendor solutions, while clinical staff are resisting any digital workflow change. Synthesize consensus without alienating either faction.",
        register: RegisterExpectation {
            formality_level: 0.70,
            technical_density: 0.60,
            hedging_tolerance: 0.25,
            structure_requirement: 0.80,
            target_wpm_min: 115.0,
            target_wpm_max: 155.0,
        },
        weights: CompetencyWeight {
            analytical_thinking: 0.15,
            communication_clarity: 0.25,
            leadership_presence: 0.25,
            emotional_regulation: 0.25,
            domain_expertise: 0.05,
            problem_solving: 0.05,
        },
        key_jargon: &[
            "active listening", "bridging", "consensus building", "HL7/FHIR", "interoperability", 
            "clinical friction", "change management", "stakeholder buy-in", "pilot rollout"
        ],
        probes_depth: &[
            "A vocal participant just interrupted you and dismissed your interoperability concerns. Address their objection directly while keeping the meeting on track.",
            "Summarize the points of agreement established so far and pivot the group toward an action item."
        ],
        probes_stress: &[
            "Both vendors have bribed hospital board members with board seats. Consensus is politically impossible. How do you maneuver?",
            "You are speaking too much and dominating the other participants. How do you re-engage the quiet members?"
        ],
        failure_modes: &[
            "Monopolizing the floor without inviting other participants",
            "Passivity and failing to steer the conversation",
            "Aggressive confrontation instead of diplomatic alignment"
        ],
    },

    // 6. Human Resources (HR) Screening: Cultural Alignment & Motivation
    ScenarioDefinition {
        scenario_id: 601,
        format: InterviewFormat::HrScreening,
        seniority: SeniorityLevel::Entry,
        role_title: "Associate Technology Consultant",
        industry: "Global Management & Technology Consulting",
        core_prompt: "Why our firm, why this specific practice group, and what unique professional philosophy distinguishes your work ethic when assigned to a high-pressure client engagement with ambiguously defined deliverables?",
        register: RegisterExpectation {
            formality_level: 0.80,
            technical_density: 0.45,
            hedging_tolerance: 0.20,
            structure_requirement: 0.75,
            target_wpm_min: 120.0,
            target_wpm_max: 160.0,
        },
        weights: CompetencyWeight {
            analytical_thinking: 0.15,
            communication_clarity: 0.30,
            leadership_presence: 0.20,
            emotional_regulation: 0.25,
            domain_expertise: 0.05,
            problem_solving: 0.05,
        },
        key_jargon: &[
            "core values", "growth mindset", "client advisory", "adaptability", "mentorship", 
            "integrity", "self-starter", "ambiguity navigation", "workplace culture"
        ],
        probes_depth: &[
            "Can you give an example of how your personal values conflicted with an organizational directive and how you navigated it?",
            "What would your former manager say is your most significant growth blindspot?"
        ],
        probes_stress: &[
            "That answer sounds like a rehearsed canned response. Give me an honest, unscripted moment where you failed a colleague.",
            "Our consultants travel 4 days a week and work 70-hour weeks. How do you realistically sustain that without burnout?"
        ],
        failure_modes: &[
            "Generic praise about the company without mentioning specific initiatives or culture",
            "False weaknesses (e.g. 'I work too hard', 'I'm a perfectionist')",
            "Inconsistent narrative between CV timeline and verbal story"
        ],
    },

    // 7. Executive / C-Suite Leadership Interview: Vision & Capital Allocation
    ScenarioDefinition {
        scenario_id: 701,
        format: InterviewFormat::Executive,
        seniority: SeniorityLevel::DirectorExecutive,
        role_title: "Chief Technology Officer (CTO)",
        industry: "Global Aerospace & Defense Systems",
        core_prompt: "The Board is investing $250M over the next 5 years into next-generation sovereign defense AI capabilities. Deliver your strategic vision on capital allocation, talent acquisition in a competitive market, IP retention, and defensive security posture against state-sponsored actors.",
        register: RegisterExpectation {
            formality_level: 0.90,
            technical_density: 0.70,
            hedging_tolerance: 0.05, // Zero tolerance for executive vagueness
            structure_requirement: 0.90,
            target_wpm_min: 105.0,
            target_wpm_max: 145.0,
        },
        weights: CompetencyWeight {
            analytical_thinking: 0.25,
            communication_clarity: 0.25,
            leadership_presence: 0.30,
            emotional_regulation: 0.10,
            domain_expertise: 0.05,
            problem_solving: 0.05,
        },
        key_jargon: &[
            "capital allocation", "sovereign capability", "ITAR compliance", "air-gapped LLMs", 
            "talent retention moat", "board governance", "risk mitigation", "RoIC", "asymmetric defense"
        ],
        probes_depth: &[
            "How do you structure the balance between commercial off-the-shelf defense tech and proprietary classified internal IP?",
            "What specific governance mechanism ensures ethics compliance without paralyzing engineering delivery speed?"
        ],
        probes_stress: &[
            "A foreign intelligence agency has infiltrated your primary subcontractor. The press knows, but the board doesn't. Your first 60 minutes. Go.",
            "Your projected RoIC is lower than the risk-free Treasury yield. Why should the board fund this instead of stock buybacks?"
        ],
        failure_modes: &[
            "Excessive tactical technical details instead of high-level enterprise strategy",
            "Hesitation or lack of decisive executive gravitas",
            "Ignoring fiduciary duty, shareholder value, and geopolitical risk"
        ],
    },

    // 8. Panel Interview: Multi-Examiner Dynamics & Conflicting Feedback
    ScenarioDefinition {
        scenario_id: 801,
        format: InterviewFormat::Panel,
        seniority: SeniorityLevel::StaffPrincipal,
        role_title: "Vice President of Global Infrastructure",
        industry: "Global Telecommunications & Cloud",
        core_prompt: "You are defending your $1.2B 5G Core network modernization roadmap in front of a 4-person panel: the CFO (demanding 25% cost reduction), the CSO (demanding zero-trust air-gapping), the COO (demanding zero-downtime migration), and the Chief Architect. Address the panel and resolve their conflicting mandates.",
        register: RegisterExpectation {
            formality_level: 0.85,
            technical_density: 0.75,
            hedging_tolerance: 0.10,
            structure_requirement: 0.90,
            target_wpm_min: 110.0,
            target_wpm_max: 150.0,
        },
        weights: CompetencyWeight {
            analytical_thinking: 0.25,
            communication_clarity: 0.25,
            leadership_presence: 0.25,
            emotional_regulation: 0.15,
            domain_expertise: 0.05,
            problem_solving: 0.05,
        },
        key_jargon: &[
            "zero-trust", "multi-tenant", "OPEX reduction", "non-disruptive migration", 
            "carrier-grade SLA", "canary deployments", "fiduciary prudence", "panel orchestration"
        ],
        probes_depth: &[
            "The CFO and CSO just gave you contradictory orders. Address both executives by name, validate their objectives, and present the technical synthesis.",
            "How do you maintain eye contact and engagement across a hostile four-person interview panel?"
        ],
        probes_stress: &[
            "The Chief Architect calls your design obsolete and amateurish in front of the entire panel. Respond without being defensive.",
            "We are cutting your budget by 40% effective immediately. What do you cut first: security, reliability, or rollout speed?"
        ],
        failure_modes: &[
            "Fixating on only one panelist and ignoring the other three",
            "Agreeing with contradictory demands without reconciling the trade-off",
            "Becoming defensive or combative under panel pressure"
        ],
    },
];

/// Finds a scenario by its unique identifier.
pub fn get_scenario_by_id(id: u16) -> Option<&'static ScenarioDefinition> {
    SCENARIO_CATALOG.iter().find(|s| s.scenario_id == id)
}

/// Evaluates candidate transcript against register expectations.
/// Returns register compliance score [0.0, 1.0].
pub fn evaluate_register_compliance(
    scenario: &ScenarioDefinition,
    transcript: &str,
    wpm: f32,
) -> f32 {
    if transcript.is_empty() {
        return 0.0;
    }

    let words: Vec<&str> = transcript.split_whitespace().collect();
    let total_words = words.len() as f32;
    if total_words < 5.0 {
        return 0.1;
    }

    // 1. Check Jargon presence
    let mut jargon_hits = 0;
    for jargon in scenario.key_jargon.iter() {
        if transcript.to_lowercase().contains(&jargon.to_lowercase()) {
            jargon_hits += 1;
        }
    }
    let jargon_ratio = (jargon_hits as f32) / (scenario.key_jargon.len() as f32);
    let jargon_score = (jargon_ratio / scenario.register.technical_density.max(0.1)).min(1.0);

    // 2. Check WPM compliance
    let wpm_penalty = if wpm < scenario.register.target_wpm_min {
        ((scenario.register.target_wpm_min - wpm) / scenario.register.target_wpm_min).min(1.0)
    } else if wpm > scenario.register.target_wpm_max {
        ((wpm - scenario.register.target_wpm_max) / scenario.register.target_wpm_max).min(1.0)
    } else {
        0.0
    };
    let wpm_score = (1.0 - wpm_penalty).max(0.0);

    // 3. Hedging analysis (words like 'maybe', 'probably', 'sort of', 'kind of', 'i guess')
    let hedging_markers = ["maybe", "perhaps", "i guess", "kind of", "sort of", "probably", "um", "uh"];
    let mut hedge_count = 0;
    let lower_trans = transcript.to_lowercase();
    for hedge in hedging_markers.iter() {
        if lower_trans.contains(hedge) {
            hedge_count += 1;
        }
    }
    let hedge_density = (hedge_count as f32) / (total_words / 20.0).max(1.0);
    let hedge_score = if hedge_density > scenario.register.hedging_tolerance {
        (1.0 - (hedge_density - scenario.register.hedging_tolerance)).max(0.0)
    } else {
        1.0
    };

    // Composite weighted score
    let final_compliance = (jargon_score * 0.40) + (wpm_score * 0.35) + (hedge_score * 0.25);
    final_compliance.clamp(0.0, 1.0)
}
