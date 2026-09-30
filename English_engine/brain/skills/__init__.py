"""
skills package - Core linguistic capabilities for English_engine.
"""

from .tokenization import EnglishTokenizer, Token
from .pos_tagging import EnglishPOSTagger, TaggedToken
from .parsing import EnglishParser, ParseTree, DependencyTree
from .lemmatization import EnglishLemmatizer, LemmaResult
from .ner import EnglishNamedEntityRecognizer, NamedEntity
from .coreference import EnglishCoreferenceResolver
from .srl import EnglishSemanticRoleLabeler, SemanticRoleFrame
from .sentiment import EnglishSentimentClassifier, SentimentResult
from .g2p import EnglishG2PConverter, G2PResult
from .stt_decoder import EnglishSTTDecoder, STTDecodeResult
from .generation import EnglishTextGenerator

__all__ = [
    "EnglishTokenizer",
    "Token",
    "EnglishPOSTagger",
    "TaggedToken",
    "EnglishParser",
    "ParseTree",
    "DependencyTree",
    "EnglishLemmatizer",
    "LemmaResult",
    "EnglishNamedEntityRecognizer",
    "NamedEntity",
    "EnglishCoreferenceResolver",
    "EnglishSemanticRoleLabeler",
    "SemanticRoleFrame",
    "EnglishSentimentClassifier",
    "SentimentResult",
    "EnglishG2PConverter",
    "G2PResult",
    "EnglishSTTDecoder",
    "STTDecodeResult",
    "EnglishTextGenerator",
]
