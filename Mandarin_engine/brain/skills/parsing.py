"""
Mandarin Syntactic and Structural Dependency Parsing Skill.
Analyzes Chinese sentence structures: Topic-Comment, 把-disposal, 被-passive,
serial verbs, and aspectual completion.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional


@dataclass
class ParseNode:
    index: int
    token: str
    pos: str
    head: int
    deprel: str


@dataclass
class MandarinSentenceStructure:
    is_topic_comment: bool = False
    topic: Optional[str] = None
    comment: Optional[str] = None
    is_ba_construction: bool = False
    ba_disposed_object: Optional[str] = None
    is_bei_construction: bool = False
    bei_agent: Optional[str] = None
    is_serial_verb: bool = False
    verbs: List[str] = field(default_factory=list)
    aspect_markers: List[str] = field(default_factory=list)
    nodes: List[ParseNode] = field(default_factory=list)


class MandarinParser:
    """
    Syntactic analyzer identifying Chinese grammatical constructions and dependency links.
    """

    def parse(self, tagged_tokens: List[Tuple[str, str]]) -> MandarinSentenceStructure:
        res = MandarinSentenceStructure()
        tokens = [t[0] for t in tagged_tokens]
        tags = [t[1] for t in tagged_tokens]

        # 1. Detect Aspect Markers
        for token, tag in tagged_tokens:
            if tag in {"AS", "SP"} and token in {"了", "着", "过"}:
                res.aspect_markers.append(token)

        # 2. Detect Verbs
        res.verbs = [token for token, tag in tagged_tokens if tag in {"VV", "VC", "VE"}]
        if len(res.verbs) >= 2:
            res.is_serial_verb = True

        # 3. Detect 把 Construction
        if "把" in tokens:
            ba_idx = tokens.index("把")
            res.is_ba_construction = True
            # Disposed object lies between '把' and the next verb
            obj_tokens = []
            for j in range(ba_idx + 1, len(tokens)):
                if tags[j] in {"VV", "VC", "VE"}:
                    break
                obj_tokens.append(tokens[j])
            if obj_tokens:
                res.ba_disposed_object = "".join(obj_tokens)

        # 4. Detect 被 Construction
        if "被" in tokens:
            bei_idx = tokens.index("被")
            res.is_bei_construction = True
            agent_tokens = []
            for j in range(bei_idx + 1, len(tokens)):
                if tags[j] in {"VV", "VC", "VE"}:
                    break
                agent_tokens.append(tokens[j])
            if agent_tokens:
                res.bei_agent = "".join(agent_tokens)

        # 5. Detect Topic-Comment Structure
        # If comma exists, or first constituent is a definite noun followed by a pronoun subject
        if "，" in tokens:
            comma_idx = tokens.index("，")
            res.is_topic_comment = True
            res.topic = "".join(tokens[:comma_idx])
            res.comment = "".join(tokens[comma_idx + 1:])
        elif len(tokens) >= 4 and tags[0] in {"NN", "NR"} and tags[1] == "PN":
            res.is_topic_comment = True
            res.topic = tokens[0]
            res.comment = "".join(tokens[1:])

        # 6. Construct Parse Nodes
        for i, (tok, tg) in enumerate(tagged_tokens):
            head = 0
            dep = "root"
            if tg in {"NN", "NR", "PN"}:
                dep = "nsubj" if i == 0 or (res.is_ba_construction and i < tokens.index("把")) else "dobj"
            elif tg == "P" and tok in {"把", "被"}:
                dep = "case:ba" if tok == "把" else "case:bei"
            elif tg == "M":
                dep = "clf"
            elif tg in {"AS", "SP"}:
                dep = "aspect"
            elif tg == "AD":
                dep = "advmod"

            res.nodes.append(ParseNode(index=i + 1, token=tok, pos=tg, head=head, deprel=dep))

        return res
