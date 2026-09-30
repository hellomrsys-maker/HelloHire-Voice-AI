#!/usr/bin/env python3
# Patch Tamil engine: fix invalid YAML where 'context:' key is nested inside list
import sys

path = 'polyglot_ai_system/language_engines/Tamil_engine.training.yaml'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# The bad block: context: key is indented at list-item level inside inclusive_exclusive_examples
# We hoist it to a sibling key BEFORE the list, at top-level mapping indent (2 spaces)
old_fragment = (
    '  inclusive_exclusive_examples:\n'
    '    - { pronoun: "\u0BA8\u0BBE\u0BAE\u0BCD (n\u0101m)",     type: "inclusive", meaning: "we \u2014 speaker + listener + others" }\n'
    '    - { pronoun: "\u0BA8\u0BBE\u0B99\u0BCD\u0B95\u0BB3\u0BCD (n\u0101\u1E45ka\u1E37)", type: "exclusive", meaning: "we \u2014 speaker + others but NOT listener" }\n'
    '    context: "This distinction is grammatically obligatory in Tamil; must be tracked in context"\n'
)

new_fragment = (
    '  inclusive_exclusive_note: "This distinction is grammatically obligatory in Tamil; must be tracked in context"\n'
    '  inclusive_exclusive_examples:\n'
    '    - { pronoun: "\u0BA8\u0BBE\u0BAE\u0BCD (n\u0101m)",     type: "inclusive", meaning: "we \u2014 speaker + listener + others" }\n'
    '    - { pronoun: "\u0BA8\u0BBE\u0B99\u0BCD\u0B95\u0BB3\u0BCD (n\u0101\u1E45ka\u1E37)", type: "exclusive", meaning: "we \u2014 speaker + others but NOT listener" }\n'
)

if old_fragment in content:
    content = content.replace(old_fragment, new_fragment, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('PATCHED OK')
else:
    print('PATTERN NOT FOUND — manual inspection needed')
    sys.exit(1)
