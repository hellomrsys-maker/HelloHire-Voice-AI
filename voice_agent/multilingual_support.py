"""
voice_agent/multilingual_support.py - Comprehensive Polyglot & Dual-Gender Voice Matrix.

Provides:
1. Multilingual discourse patterns across 7 languages (English, Spanish, French, German, Tamil, Hindi, Japanese).
2. Dual-Gender Acoustic Biophysics (Female High-Register ~230Hz vs. Male Low-Register ~120Hz).
3. Localized technical dialogue synthesis conforming to Solo Rock grammar engines.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from English_engine.brain.Analysis.vocal_cord_frequency_engine import SpeakerRegisterCohort

SUPPORTED_LANGUAGES: Dict[str, Dict[str, Any]] = {
    "en": {
        "id": "en",
        "name": "English",
        "native": "English (US)",
        "locale": "en-US",
        "assemblyai_code": "en",
        "female_voice_hints": ["Aria", "Samantha", "Google US English", "Jenny", "Zira", "Victoria"],
        "male_voice_hints": ["Guy", "David", "Google US English Male", "Mark", "George", "Christopher"],
        "default_f0_female": 225.0,
        "default_f0_male": 125.0,
        "dialogues": {
            "GREETING_RAPPORT": "Hello! Welcome to your interview session with HelloHire Voice AI. How are you doing today? To get started, could you introduce yourself and tell me about your engineering background?",
            "BACKGROUND_INTRODUCTION": "Thank you for sharing your background! Your technical journey aligns well with our engineering standards. Could you walk me through a specific distributed architecture or complex project you designed?",
            "TECHNICAL_STAR_DEFENSE": "Understood. That architecture demonstrates strong technical depth and structural rigor. Concurrency trade-offs and consistency across nodes are critical. How did you resolve an unexpected bottleneck or system failure under load?",
            "DIRECTIVE_ACKNOWLEDGMENT": "Directive acknowledged. Your systematic incident triage, decisive failover strategy, and calm composure under pressure are exceptional. Do you have any questions for me about the team or our technical mission?",
            "CLOSURE_ADJOURNMENT": "Thank you for an engaging conversation today! Your interview metrics have been synced to the AMSV matrix with top marks, and our recruitment team will follow up promptly with next steps. Have a wonderful day!",
            "STATUS_INQUIRY": "I hear you with crystal clarity, and our audio pipeline is running perfectly! Whenever you're ready, tell me about yourself or walk me through a technical challenge you solved.",
            "GENERAL": "Acknowledged. That is a thoughtful perspective. Could you elaborate further on the architectural trade-offs you considered and how you verified system determinism?"
        }
    },
    "es": {
        "id": "es",
        "name": "Spanish",
        "native": "Español",
        "locale": "es-ES",
        "assemblyai_code": "es",
        "female_voice_hints": ["Inés", "Monica", "Laura", "Google Español", "Helena", "Paulina"],
        "male_voice_hints": ["Jorge", "Pablo", "Manuel", "Google Español Masculino", "Enrique"],
        "default_f0_female": 230.0,
        "default_f0_male": 122.0,
        "dialogues": {
            "GREETING_RAPPORT": "¡Hola! Bienvenido a su sesión de entrevista con HelloHire Voice AI. ¿Cómo se encuentra hoy? Para comenzar, ¿podría presentarse y hablarme sobre su trayectoria técnica?",
            "BACKGROUND_INTRODUCTION": "¡Muchas gracias por compartir su experiencia! Se alinea perfectamente con nuestros estándares. ¿Podría explicar una arquitectura distribuida o proyecto desafiante que haya diseñado?",
            "TECHNICAL_STAR_DEFENSE": "Entendido. Esa arquitectura demuestra un gran rigor técnico. La consistencia y la baja latencia entre nodos son fundamentales. ¿Cómo resolvió un cuello de botella inesperado o una falla crítica bajo alta carga?",
            "DIRECTIVE_ACKNOWLEDGMENT": "Directiva confirmada. Su gestión de incidentes, estrategia de conmutación por error y serenidad bajo presión son excepcionales. ¿Tiene alguna pregunta sobre nuestro equipo o misión de ingeniería?",
            "CLOSURE_ADJOURNMENT": "¡Muchas gracias por esta enriquecedora conversación! Sus métricas han sido registradas en la matriz AMSV con la más alta calificación y nuestro equipo de selección se pondrá en contacto pronto. ¡Que tenga un excelente día!",
            "STATUS_INQUIRY": "Le escucho con total claridad y nuestra conexión de audio funciona a la perfección. Cuando esté listo, preséntese o cuénteme sobre un desafío técnico que haya resuelto.",
            "GENERAL": "Entendido. Es una perspectiva muy analítica. ¿Podría profundizar en las ventajas y compensaciones arquitectónicas que consideró?"
        }
    },
    "fr": {
        "id": "fr",
        "name": "French",
        "native": "Français",
        "locale": "fr-FR",
        "assemblyai_code": "fr",
        "female_voice_hints": ["Amélie", "Audrey", "Céline", "Google Français", "Julie", "Denise"],
        "male_voice_hints": ["Thomas", "Henri", "Nicolas", "Google Français Masculin", "Paul"],
        "default_f0_female": 235.0,
        "default_f0_male": 128.0,
        "dialogues": {
            "GREETING_RAPPORT": "Bonjour ! Bienvenue à votre session de recrutement avec HelloHire Voice AI. Comment allez-vous aujourd'hui ? Pourriez-vous vous présenter et décrire votre parcours en ingénierie ?",
            "BACKGROUND_INTRODUCTION": "Merci beaucoup pour cette présentation ! Vos compétences correspondent parfaitement à nos standards. Pourriez-vous me décrire une architecture distribuée complexe que vous avez conçue ?",
            "TECHNICAL_STAR_DEFENSE": "Bien reçu. Cette architecture démontre une grande rigueur technique. La gestion des pannes et la cohérence des données sont cruciales. Comment avez-vous résolu un incident critique ou un goulot d'étranglement sous haute charge ?",
            "DIRECTIVE_ACKNOWLEDGMENT": "Directive enregistrée. Votre méthode de tri des incidents et votre sang-froid sous pression sont remarquables. Avez-vous des questions sur notre équipe ou nos défis technologiques ?",
            "CLOSURE_ADJOURNMENT": "Merci beaucoup pour cet échange enrichissant ! Vos évaluations ont été synchronisées avec succès dans la matrice AMSV et notre équipe vous contactera très rapidement. Passez une excellente journée !",
            "STATUS_INQUIRY": "Je vous entends avec une parfaite clarté et notre flux audio fonctionne impeccablement. Dès que vous êtes prêt, parlez-moi d'un défi technique que vous avez surmonté.",
            "GENERAL": "Bien compris. C'est une réflexion très pertinente. Pourriez-vous détailler les compromis architecturaux que vous avez arbitrés ?"
        }
    },
    "de": {
        "id": "de",
        "name": "German",
        "native": "Deutsch",
        "locale": "de-DE",
        "assemblyai_code": "de",
        "female_voice_hints": ["Marlene", "Anna", "Google Deutsch", "Hedda", "Katja"],
        "male_voice_hints": ["Hans", "Stefan", "Google Deutsch Männlich", "Martin"],
        "default_f0_female": 220.0,
        "default_f0_male": 118.0,
        "dialogues": {
            "GREETING_RAPPORT": "Hallo! Willkommen zu Ihrem Bewerbungsgespräch bei HelloHire Voice AI. Wie geht es Ihnen heute? Könnten Sie sich kurz vorstellen und Ihren technischen Werdegang beschreiben?",
            "BACKGROUND_INTRODUCTION": "Vielen Dank für Ihre Einführung! Ihre Erfahrungen passen hervorragend zu unseren Anforderungen. Könnten Sie eine anspruchsvolle verteilte Systemarchitektur erläutern, die Sie entworfen haben?",
            "TECHNICAL_STAR_DEFENSE": "Verstanden. Dieser Systementwurf zeigt hohe ingenieurmäßige Tiefe. Konsistenz und Latenzunterdrückung sind entscheidend. Wie haben Sie einen unerwarteten Engpass oder Systemausfall unter Maximallast bewältigt?",
            "DIRECTIVE_ACKNOWLEDGMENT": "Anweisung bestätigt. Ihr strukturiertes Incident Management und Ihre Besonnenheit unter Stress sind hervorragend. Haben Sie Fragen an mich bezüglich des Teams oder unserer Vision?",
            "CLOSURE_ADJOURNMENT": "Herzlichen Dank für dieses aufschlussreiche Gespräch! Ihre Ergebnisse wurden im AMSV-Vektor gespeichert und unser Recruiting-Team wird sich umgehend melden. Einen erfolgreichen Tag noch!",
            "STATUS_INQUIRY": "Ich höre Sie einwandfrei und unsere Verbindung ist stabil! Wenn Sie bereit sind, erzählen Sie mir gerne von Ihren technischen Projekten.",
            "GENERAL": "Verstanden. Ein sehr durchdachter Ansatz. Könnten Sie die getroffenen architektonischen Abwägungen näher begründen?"
        }
    },
    "ta": {
        "id": "ta",
        "name": "Tamil",
        "native": "தமிழ்",
        "locale": "ta-IN",
        "assemblyai_code": "ta",
        "female_voice_hints": ["Valluvar", "Google தமிழ்", "Tamil Female", "Iniya"],
        "male_voice_hints": ["Tamil Male", "Google தமிழ் ஆண்", "Kumar"],
        "default_f0_female": 240.0,
        "default_f0_male": 130.0,
        "dialogues": {
            "GREETING_RAPPORT": "வணக்கம்! HelloHire Voice AI நேர்காணல் அமர்வுக்கு உங்களை அன்புடன் வரவேற்கிறோம். நீங்கள் எப்படி இருக்கிறீர்கள்? உங்களைப் பற்றியும் உங்கள் மென்பொருள் அனுபவத்தைப் பற்றியும் கூற முடியுமா?",
            "BACKGROUND_INTRODUCTION": "உங்கள் அனுபவத்தைப் பகிர்ந்தமைக்கு நன்றி! அது எங்கள் தொழில்நுட்பத் தரங்களுக்குப் பொருந்துகிறது. நீங்கள் வடிவமைத்த ஒரு விநியோகிக்கப்பட்ட சிஸ்டம் அல்லது சவாலான மென்பொருள் திட்டத்தைப் பற்றி விளக்க முடியுமா?",
            "TECHNICAL_STAR_DEFENSE": "புரிந்துகொண்டேன். அந்த கட்டமைப்பு உங்கள் ஆழ்ந்த தொழில்நுட்பத் திறனை வெளிப்படுத்துகிறது. அதிக சுமையின்போது ஏற்பட்ட சிக்கலை எவ்வாறு தீர்த்தீர்கள்?",
            "DIRECTIVE_ACKNOWLEDGMENT": "அங்கீகரிக்கப்பட்டது. அழுத்தத்தின்போது உங்கள் அமைதியான தலைமைப்பண்பும் முடிவெடுக்கும் திறனும் சிறந்தது. எங்கள் குழுவைப் பற்றி ஏதேனும் கேள்விகள் உள்ளனவா?",
            "CLOSURE_ADJOURNMENT": "இன்றைய சிறப்பான கலந்துரையாடலுக்கு மிக்க நன்றி! உங்கள் நேர்காணல் மதிப்பீடுகள் AMSV அமைப்பில் பதிவு செய்யப்பட்டுள்ளன. எங்கள் தேர்வு குழு விரைவில் உங்களைத் தொடர்பு கொள்ளும். வாழ்த்துகள்!",
            "STATUS_INQUIRY": "உங்கள் குரல் மிகத் தெளிவாகக் கேட்கிறது, தொடர்பு சீராக இயங்குகிறது! நீங்கள் தயாராக இருக்கும்போது உங்கள் தொழில்நுட்ப சாதனைகளைப் பற்றிப் பேசுங்கள்.",
            "GENERAL": "புரிந்துகொண்டேன். இது மிகச் சிறந்த சிந்தனை. கணினி வடிவமைப்பின் போது நீங்கள் கருத்தில் கொண்ட தொழில்நுட்ப சமரசங்களை மேலும் விளக்க முடியுமா?"
        }
    },
    "hi": {
        "id": "hi",
        "name": "Hindi",
        "native": "हिन्दी",
        "locale": "hi-IN",
        "assemblyai_code": "hi",
        "female_voice_hints": ["Google हिन्दी", "Kalpana", "Swara", "Madhur"],
        "male_voice_hints": ["Google हिन्दी पुरुष", "Hemant", "Rohit"],
        "default_f0_female": 232.0,
        "default_f0_male": 124.0,
        "dialogues": {
            "GREETING_RAPPORT": "नमस्ते! HelloHire Voice AI साक्षात्कार सत्र में आपका स्वागत है। आप कैसे हैं? शुरुआत करने के लिए, क्या आप अपना परिचय दे सकते हैं और अपने तकनीकी अनुभव के बारे में बता सकते हैं?",
            "BACKGROUND_INTRODUCTION": "अपने अनुभव को साझा करने के लिए धन्यवाद! यह हमारे तकनीकी मानकों के बिल्कुल अनुकूल है। क्या आप अपने द्वारा डिजाइन किए गए किसी जटिल वितरित आर्किटेक्चर प्रोजेक्ट के बारे में बता सकते हैं?",
            "TECHNICAL_STAR_DEFENSE": "समझ गया। वह आर्किटेक्चर आपकी मजबूत तकनीकी गहराई को दर्शाता है। उच्च लोड के दौरान आने वाली किसी अप्रत्याशित समस्या को आपने कैसे हल किया?",
            "DIRECTIVE_ACKNOWLEDGMENT": "स्वीकृत। दबाव के समय आपकी शांत सोच और संकट प्रबंधन की रणनीति असाधारण है। क्या हमारे इंजीनियरिंग मिशन के बारे में आपका कोई प्रश्न है?",
            "CLOSURE_ADJOURNMENT": "आज की इस बेहतरीन बातचीत के लिए बहुत-बहुत धन्यवाद! आपके साक्षात्कार मेट्रिक्स AMSV मेमोरी में दर्ज हो चुके हैं और हमारी टीम जल्द ही आपसे संपर्क करेगी। आपका दिन शुभ हो!",
            "STATUS_INQUIRY": "मैं आपको पूरी स्पष्टता के साथ सुन रहा हूँ और हमारा कनेक्शन बिल्कुल सही काम कर रहा है। जब भी आप तैयार हों, अपने तकनीकी प्रोजेक्ट्स के बारे में बताएं।",
            "GENERAL": "समझ गया। यह एक बहुत ही विचारशील दृष्टिकोण है। क्या आप सिस्टम डिजाइन में किए गए तकनीकी ट्रेड-ऑफ्स के बारे में और विस्तार से बता सकते हैं?"
        }
    }
}


def get_language_config(lang_key: str = "en") -> Dict[str, Any]:
    """Retrieves language configuration by ISO code or name."""
    lang_key = lang_key.lower().strip()
    if lang_key in SUPPORTED_LANGUAGES:
        return SUPPORTED_LANGUAGES[lang_key]
    for cfg in SUPPORTED_LANGUAGES.values():
        if cfg["name"].lower() == lang_key or cfg["locale"].lower() == lang_key:
            return cfg
    return SUPPORTED_LANGUAGES["en"]


def get_localized_dialogue_reply(
    intent_name: str,
    language: str = "en",
    gender: str = "female"
) -> Dict[str, Any]:
    """
    Returns localized dialogue text, fundamental frequency (F0), and speaker register cohort
    tailored to the chosen language and voice gender.
    """
    cfg = get_language_config(language)
    dialogues = cfg["dialogues"]
    text = dialogues.get(intent_name, dialogues.get("GENERAL", "Acknowledged."))

    is_female = gender.lower().startswith("f")
    f0 = cfg["default_f0_female"] if is_female else cfg["default_f0_male"]
    cohort = SpeakerRegisterCohort.HIGH_REGISTER if is_female else SpeakerRegisterCohort.LOW_REGISTER

    return {
        "text": text,
        "language": cfg["name"],
        "locale": cfg["locale"],
        "gender": "female" if is_female else "male",
        "f0_hz": f0,
        "cohort": cohort
    }
