// =============================================================================
// engine/rust/src/component_family.rs
// Component family registry — per the spec: stores reusable compositional
// sentence building blocks rather than memorizing full sentences.
// Implements the "one engine = one canonical training file" sentence system.
// =============================================================================

use std::collections::HashMap;
use serde::{Deserialize, Serialize};
use rand::Rng;

// =============================================================================
// RegisterType — mirrors the C++ enum for cross-language consistency
// =============================================================================

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum RegisterType {
    Formal,
    Neutral,
    Informal,
    Technical,
    Creative,
    ChildDirected,
}

// =============================================================================
// ComponentEntry — a single entry in a component family
// Per the spec: stored with register, forms, and creativity weight
// =============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ComponentEntry {
    /// Unique identifier within the family
    pub id: String,

    /// All surface forms this entry can take (e.g., ["Hi", "hi"])
    pub forms: Vec<String>,

    /// Register this entry belongs to
    pub register: RegisterType,

    /// Relative probability weight for selection [0, 1]
    pub creativity_weight: f32,

    /// Whether this entry is a fixed expression (idiom, quotation, etc.)
    pub is_fixed_expression: bool,
}

// =============================================================================
// ComponentFamily — a named family of interchangeable forms
// =============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ComponentFamily {
    /// Family name (e.g., "greeting_family", "identity_family")
    pub family_name: String,

    /// All entries in this family
    pub entries: Vec<ComponentEntry>,

    /// Whether this slot is optional in sentence templates
    pub is_optional: bool,

    /// Description of the family's communicative function
    pub description: String,
}

impl ComponentFamily {
    /// Creates a new empty component family.
    pub fn new(name: impl Into<String>) -> Self {
        Self {
            family_name:  name.into(),
            entries:      Vec::new(),
            is_optional:  false,
            description:  String::new(),
        }
    }

    /// Adds an entry to this family.
    pub fn add_entry(&mut self, entry: ComponentEntry) {
        self.entries.push(entry);
    }

    /// Selects a random entry matching the target register.
    /// Falls back to any entry if no register match is found.
    pub fn select_entry<R: Rng>(
        &self,
        target_register: &RegisterType,
        creativity_level: f32,
        rng: &mut R,
    ) -> Option<&ComponentEntry> {
        if self.entries.is_empty() {
            return None;
        }

        // Compute weights
        let weights: Vec<f32> = self.entries.iter().map(|e| {
            let base = if &e.register == target_register { 1.0f32 }
                       else { 0.3 + 0.4 * creativity_level };
            base * e.creativity_weight
        }).collect();

        // Weighted random selection
        let total: f32 = weights.iter().sum();
        if total <= 0.0 {
            return self.entries.first();
        }

        let mut threshold = rng.gen::<f32>() * total;
        for (i, &w) in weights.iter().enumerate() {
            threshold -= w;
            if threshold <= 0.0 {
                return Some(&self.entries[i]);
            }
        }
        self.entries.last()
    }

    /// Returns all entries matching the given register.
    pub fn entries_for_register(&self, register: &RegisterType) -> Vec<&ComponentEntry> {
        self.entries.iter().filter(|e| &e.register == register).collect()
    }

    /// Returns a random form from a selected entry.
    pub fn select_form<R: Rng>(
        &self,
        target_register: &RegisterType,
        creativity_level: f32,
        rng: &mut R,
    ) -> Option<String> {
        let entry = self.select_entry(target_register, creativity_level, rng)?;
        if entry.forms.is_empty() {
            return None;
        }
        let idx = rng.gen_range(0..entry.forms.len());
        Some(entry.forms[idx].clone())
    }
}

// =============================================================================
// SentenceTemplate — a slot-order template combining component families
// Per the spec Section 5: composition of branches, not memorization
// =============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SentenceTemplate {
    pub template_id:         String,
    pub communication_intent: String,

    /// Ordered list of family names (slot_order from the spec)
    pub slot_order: Vec<String>,

    /// Combinations that are not allowed (blocked_combinations from spec)
    pub blocked_combinations: Vec<String>,

    /// Default register for this template
    pub default_register: RegisterType,

    /// Spacing rules between slots
    pub slot_separators: Vec<String>,  // "" = no space, " " = space, ", " = comma-space
}

impl SentenceTemplate {
    /// Realizes the template by selecting from the family registry.
    pub fn realize<R: Rng>(
        &self,
        registry: &FamilyRegistry,
        target_register: &RegisterType,
        creativity_level: f32,
        rng: &mut R,
    ) -> String {
        let mut parts: Vec<String> = Vec::new();

        for slot_name in &self.slot_order {
            if let Some(family) = registry.get(slot_name) {
                if let Some(form) = family.select_form(target_register, creativity_level, rng) {
                    parts.push(form);
                } else if !family.is_optional {
                    // Required slot had no suitable entry — use first available form
                    if let Some(entry) = family.entries.first() {
                        if let Some(form) = entry.forms.first() {
                            parts.push(form.clone());
                        }
                    }
                }
            }
        }

        // Join parts with intelligent spacing
        let mut result = String::new();
        for (i, part) in parts.iter().enumerate() {
            if i > 0 && !part.is_empty() {
                // Punctuation: no preceding space
                let first_char = part.chars().next().unwrap_or(' ');
                if !matches!(first_char, '.' | ',' | '!' | '?' | ';' | ':' | '\'') {
                    result.push(' ');
                }
            }
            result.push_str(part);
        }

        // Capitalize first letter
        let mut chars = result.chars();
        match chars.next() {
            None        => String::new(),
            Some(first) => first.to_uppercase().collect::<String>() + chars.as_str(),
        }
    }
}

// =============================================================================
// FamilyRegistry — central store of all component families
// =============================================================================

#[derive(Debug, Default, Serialize, Deserialize)]
pub struct FamilyRegistry {
    families: HashMap<String, ComponentFamily>,
}

impl FamilyRegistry {
    pub fn new() -> Self {
        let mut registry = Self::default();
        registry.load_english_defaults();
        registry
    }

    pub fn register(&mut self, family: ComponentFamily) {
        self.families.insert(family.family_name.clone(), family);
    }

    pub fn get(&self, name: &str) -> Option<&ComponentFamily> {
        self.families.get(name)
    }

    pub fn get_mut(&mut self, name: &str) -> Option<&mut ComponentFamily> {
        self.families.get_mut(name)
    }

    pub fn family_names(&self) -> Vec<&str> {
        self.families.keys().map(|k| k.as_str()).collect()
    }

    pub fn len(&self) -> usize {
        self.families.len()
    }

    pub fn is_empty(&self) -> bool {
        self.families.is_empty()
    }

    /// Merges another registry into this one (for multi-language extension).
    pub fn merge(&mut self, other: FamilyRegistry) {
        for (name, family) in other.families {
            self.families.entry(name).or_insert(family);
        }
    }

    /// Loads the canonical English component families per the spec architecture.
    /// This is the programmatic equivalent of the YAML training file families section.
    fn load_english_defaults(&mut self) {
        // ---- greeting_family ----
        let mut greeting = ComponentFamily::new("greeting_family");
        greeting.description = "Greetings used to open communication".into();
        greeting.add_entry(ComponentEntry {
            id: "hi".into(),
            forms: vec!["Hi".into()],
            register: RegisterType::Neutral,
            creativity_weight: 1.0,
            is_fixed_expression: false,
        });
        greeting.add_entry(ComponentEntry {
            id: "hey".into(),
            forms: vec!["Hey".into()],
            register: RegisterType::Informal,
            creativity_weight: 1.0,
            is_fixed_expression: false,
        });
        greeting.add_entry(ComponentEntry {
            id: "hello".into(),
            forms: vec!["Hello".into()],
            register: RegisterType::Neutral,
            creativity_weight: 1.0,
            is_fixed_expression: false,
        });
        greeting.add_entry(ComponentEntry {
            id: "hey_there".into(),
            forms: vec!["Hey there".into()],
            register: RegisterType::Informal,
            creativity_weight: 0.8,
            is_fixed_expression: false,
        });
        greeting.add_entry(ComponentEntry {
            id: "good_morning".into(),
            forms: vec!["Good morning".into()],
            register: RegisterType::Neutral,
            creativity_weight: 0.9,
            is_fixed_expression: false,
        });
        greeting.add_entry(ComponentEntry {
            id: "greetings".into(),
            forms: vec!["Greetings".into()],
            register: RegisterType::Formal,
            creativity_weight: 0.8,
            is_fixed_expression: false,
        });
        self.register(greeting);

        // ---- identity_connector_family ----
        let mut identity = ComponentFamily::new("identity_connector_family");
        identity.description = "Connectors between greeting and name in self-introduction".into();
        identity.add_entry(ComponentEntry {
            id: "i_am".into(),
            forms: vec!["I am".into()],
            register: RegisterType::Neutral,
            creativity_weight: 1.0,
            is_fixed_expression: false,
        });
        identity.add_entry(ComponentEntry {
            id: "contracted".into(),
            forms: vec!["I'm".into()],
            register: RegisterType::Informal,
            creativity_weight: 1.0,
            is_fixed_expression: false,
        });
        identity.add_entry(ComponentEntry {
            id: "my_name_is".into(),
            forms: vec!["my name is".into()],
            register: RegisterType::Neutral,
            creativity_weight: 0.9,
            is_fixed_expression: false,
        });
        identity.add_entry(ComponentEntry {
            id: "they_call_me".into(),
            forms: vec!["they call me".into()],
            register: RegisterType::Informal,
            creativity_weight: 0.6,
            is_fixed_expression: false,
        });
        self.register(identity);

        // ---- name_family ----
        let mut name_fam = ComponentFamily::new("name_family");
        name_fam.description = "Person name slot — links to approved_person_name entry".into();
        name_fam.add_entry(ComponentEntry {
            id: "ash".into(),
            forms: vec!["Ash".into()],
            register: RegisterType::Neutral,
            creativity_weight: 1.0,
            is_fixed_expression: false,
        });
        name_fam.add_entry(ComponentEntry {
            id: "alex".into(),
            forms: vec!["Alex".into()],
            register: RegisterType::Neutral,
            creativity_weight: 1.0,
            is_fixed_expression: false,
        });
        name_fam.add_entry(ComponentEntry {
            id: "sam".into(),
            forms: vec!["Sam".into()],
            register: RegisterType::Neutral,
            creativity_weight: 1.0,
            is_fixed_expression: false,
        });
        self.register(name_fam);

        // ---- punctuation_family ----
        let mut punct = ComponentFamily::new("punctuation_family");
        punct.description = "Sentence-final punctuation".into();
        punct.add_entry(ComponentEntry {
            id: "period".into(),
            forms: vec![".".into()],
            register: RegisterType::Neutral,
            creativity_weight: 1.0,
            is_fixed_expression: false,
        });
        punct.add_entry(ComponentEntry {
            id: "exclamation".into(),
            forms: vec!["!".into()],
            register: RegisterType::Informal,
            creativity_weight: 0.7,
            is_fixed_expression: false,
        });
        self.register(punct);

        // ---- farewell_family ----
        let mut farewell = ComponentFamily::new("farewell_family");
        farewell.description = "Farewell expressions".into();
        for (id, form, reg, weight) in &[
            ("goodbye", "Goodbye", RegisterType::Neutral, 1.0f32),
            ("bye",     "Bye",     RegisterType::Informal, 1.0),
            ("farewell","Farewell", RegisterType::Formal, 0.9),
            ("see_you", "See you later", RegisterType::Informal, 0.9),
            ("take_care","Take care", RegisterType::Neutral, 0.8),
            ("until_next","Until next time", RegisterType::Formal, 0.7),
        ] {
            farewell.add_entry(ComponentEntry {
                id: id.to_string(),
                forms: vec![form.to_string()],
                register: reg.clone(),
                creativity_weight: *weight,
                is_fixed_expression: false,
            });
        }
        self.register(farewell);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use rand::SeedableRng;
    use rand::rngs::SmallRng;

    #[test]
    fn test_registry_loads_defaults() {
        let registry = FamilyRegistry::new();
        assert!(registry.get("greeting_family").is_some());
        assert!(registry.get("identity_connector_family").is_some());
        assert!(registry.get("name_family").is_some());
        assert!(registry.get("punctuation_family").is_some());
    }

    #[test]
    fn test_select_form_neutral() {
        let registry = FamilyRegistry::new();
        let greeting = registry.get("greeting_family").unwrap();
        let mut rng = SmallRng::seed_from_u64(42);
        let form = greeting.select_form(&RegisterType::Neutral, 0.5, &mut rng);
        assert!(form.is_some());
        let form = form.unwrap();
        assert!(!form.is_empty());
    }

    #[test]
    fn test_template_realize() {
        let registry = FamilyRegistry::new();
        let template = SentenceTemplate {
            template_id: "test".into(),
            communication_intent: "greet".into(),
            slot_order: vec![
                "greeting_family".into(),
                "identity_connector_family".into(),
                "name_family".into(),
                "punctuation_family".into(),
            ],
            blocked_combinations: vec![],
            default_register: RegisterType::Neutral,
            slot_separators: vec![],
        };
        let mut rng = SmallRng::seed_from_u64(0);
        let result = template.realize(&registry, &RegisterType::Neutral, 0.5, &mut rng);
        assert!(!result.is_empty());
        println!("Realized: {}", result);
    }

    #[test]
    fn test_register_and_get() {
        let mut registry = FamilyRegistry::new();
        let mut custom = ComponentFamily::new("test_family");
        custom.add_entry(ComponentEntry {
            id: "foo".into(),
            forms: vec!["foo".into(), "bar".into()],
            register: RegisterType::Neutral,
            creativity_weight: 1.0,
            is_fixed_expression: false,
        });
        registry.register(custom);
        assert!(registry.get("test_family").is_some());
        assert_eq!(registry.get("test_family").unwrap().entries.len(), 1);
    }
}
