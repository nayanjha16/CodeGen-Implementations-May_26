"""Detokenize AVATAR-TC delexicalized code back to real source.

AVATAR / CodeXGLUE store code with every token space-separated, string-internal
spaces replaced by the marker U+2581 ("\u2581"), and -- for Python, which is
whitespace-significant -- explicit ``NEW_LINE`` / ``INDENT`` / ``DEDENT``
structure tokens.

Model outputs are normal source code, so the references (and the Java inputs we
feed into the prompt) must be detokenized before any BLEU / CodeBLEU / BERTScore
comparison; otherwise real Python is scored against tokens like
``NEW_LINE INDENT fibo = [ 0 ]`` and every n-gram / embedding metric collapses to
near zero.
"""

from __future__ import annotations

import re

SPACE_MARKER = "\u2581"  # the AVATAR/CodeXGLUE in-string space placeholder
_INDENT_UNIT = "    "


def _restore_string_spaces(src: str) -> str:
    """Collapse the in-string space marker back to a single space."""
    return re.sub(r"\s*" + SPACE_MARKER + r"\s*", " ", src)


def detokenize_python(code: str) -> str:
    """Convert an AVATAR-tokenized Python string into real Python source.

    Handles the ``NEW_LINE`` / ``INDENT`` / ``DEDENT`` structure tokens and the
    in-string space marker. Token-internal spacing (e.g. ``fibo [ i - 1 ]``) is
    intentionally left as-is: BLEU / CodeBLEU re-tokenize with their own code
    tokenizers, so spacing does not affect those scores, and the result still
    parses as valid Python.
    """
    lines: list[str] = []
    indent = 0
    current: list[str] = []

    for tok in code.split():
        if tok == "NEW_LINE":
            lines.append(_INDENT_UNIT * indent + " ".join(current))
            current = []
        elif tok == "INDENT":
            indent += 1
        elif tok == "DEDENT":
            indent = max(0, indent - 1)
        else:
            current.append(tok)

    if current:
        lines.append(_INDENT_UNIT * indent + " ".join(current))

    return _restore_string_spaces("\n".join(lines))


def detokenize_java(code: str) -> str:
    """Convert an AVATAR-tokenized Java string into readable Java source.

    Java is brace-delimited, so there are no ``NEW_LINE`` / ``INDENT`` /
    ``DEDENT`` tokens to expand -- only the in-string space marker needs
    restoring. The (already space-separated) token stream is left intact, which
    the model reads fine as a single-line program.
    """
    return _restore_string_spaces(code)
