"""
============================================================
RepoCoder Studio
normalization_engine.py
============================================================

Source Code Normalization and Reconstruction Engine.

Purpose
-------
XLCoST program-level rows are tokenized. This module reconstructs
readable Python and Java source code before CandidateRow creation.

This module exists because validation should operate on reconstructed
source code, not token streams.

Important examples
------------------
XLCoST tokenized Python:

    if ( i = = j ) : NEW_LINE INDENT return True

must become:

    if i == j:
        return True

XLCoST tokenized Java:

    import java . util . * ;

must become:

    import java.util.*;

Design boundary
---------------
DatasetLoader loads raw data.
NormalizationEngine reconstructs source code.
CandidateCorpusBuilder creates CandidateRow objects.
ValidationEngine validates CandidateRows.
"""

import re
from typing import List


class NormalizationEngine:
    """
    Reconstructs tokenized source code into parseable code.

    Current scope
    -------------
    - XLCoST Python detokenization
    - XLCoST Java detokenization

    This is intentionally deterministic and non-generative.
    """

    # -------------------------------
    # Public API
    # -------------------------------

    def normalize_python(self, code: str) -> str:
        """
        Normalizes XLCoST Python code.

        Returns
        -------
        str
            Reconstructed Python source code.
        """

        lines = self._tokens_to_indented_lines(code)
        lines = [self._fix_python_line(line) for line in lines]
        return "\n".join(line.rstrip() for line in lines if line.strip()).strip()

    def normalize_java(self, code: str) -> str:
        """
        Normalizes XLCoST Java code.

        Returns
        -------
        str
            Reconstructed Java source code.
        """

        text = self._tokens_to_space_text(code)
        text = self._fix_java_text(text)
        return text.strip()

    # -------------------------------
    # Token helpers
    # -------------------------------

    def _tokenize(self, code: str) -> List[str]:
        """
        Converts raw XLCoST code text into token list.
        """

        if code is None:
            return []

        return str(code).replace("\n", " ").split()

    def _tokens_to_indented_lines(self, code: str) -> List[str]:
        """
        Converts NEW_LINE / INDENT / DEDENT tokens into Python-like lines.
        """

        tokens = self._tokenize(code)

        lines = []
        current = []
        indent = 0

        for tok in tokens:
            if tok == "NEW_LINE":
                if current:
                    lines.append("    " * indent + " ".join(current))
                    current = []
                continue

            if tok == "INDENT":
                indent += 1
                continue

            if tok == "DEDENT":
                if current:
                    lines.append("    " * indent + " ".join(current))
                    current = []
                indent = max(0, indent - 1)
                continue

            current.append(tok)

        if current:
            lines.append("    " * indent + " ".join(current))

        return lines

    def _tokens_to_space_text(self, code: str) -> str:
        """
        Converts tokenized code to space-separated text while removing
        line/indent markers.
        """

        tokens = [
            tok
            for tok in self._tokenize(code)
            if tok not in {"NEW_LINE", "INDENT", "DEDENT"}
        ]

        return " ".join(tokens)

    # -------------------------------
    # Python cleanup
    # -------------------------------

    def _fix_common_token_spacing(self, text: str) -> str:
        """
        Fixes common tokenization artifacts shared by Python and Java.
        """

        if not text:
            return ""

        # Multi-character operators must be fixed before generic spacing.
        multi_ops = {
            "= =": "==",
            "! =": "!=",
            "< =": "<=",
            "> =": ">=",
            "+ =": "+=",
            "- =": "-=",
            "* =": "*=",
            "/ =": "/=",
            "% =": "%=",
            "& &": "&&",
            "| |": "||",
            "+ +": "++",
            "- -": "--",
        }

        for bad, good in multi_ops.items():
            text = text.replace(bad, good)

        # Remove spaces around dot for Java/Python member access.
        text = re.sub(r"\s*\.\s*", ".", text)

        # Brackets and parentheses.
        text = re.sub(r"\(\s+", "(", text)
        text = re.sub(r"\s+\)", ")", text)
        text = re.sub(r"\[\s+", "[", text)
        text = re.sub(r"\s+\]", "]", text)
        text = re.sub(r"\{\s+", "{", text)
        text = re.sub(r"\s+\}", "}", text)

        # Commas and semicolons.
        text = re.sub(r"\s+,", ",", text)
        text = re.sub(r",(?=\S)", ", ", text)
        text = re.sub(r"\s+;", ";", text)

        # Colon for Python.
        text = re.sub(r"\s+:", ":", text)

        # Normalize internal spacing.
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def _fix_python_line(self, line: str) -> str:
        """
        Fixes one reconstructed Python line.
        """

        leading = len(line) - len(line.lstrip(" "))
        indent = line[:leading]
        content = line[leading:]

        content = self._fix_common_token_spacing(content)

        # Remove spaces before parentheses in calls/defs.
        content = re.sub(r"\b([A-Za-z_][A-Za-z0-9_]*)\s+\(", r"\1(", content)

        # Fix list/dict indexing spacing.
        content = re.sub(r"\b([A-Za-z_][A-Za-z0-9_]*)\s+\[", r"\1[", content)

        # Fix common string literal artifacts.
        content = content.replace("' inf '", "'inf'")
        content = content.replace('" inf "', '"inf"')

        # Python print spacing.
        content = content.replace("print (", "print(")

        return indent + content

    # -------------------------------
    # Java cleanup
    # -------------------------------

    def _fix_java_text(self, text: str) -> str:
        """
        Fixes reconstructed Java text.
        """

        text = self._fix_common_token_spacing(text)

        # Java imports and member access.
        text = text.replace("java.util.*", "java.util.*")

        # Remove space before method calls.
        text = re.sub(r"\b([A-Za-z_][A-Za-z0-9_]*)\s+\(", r"\1(", text)

        # Remove spaces around generic angle brackets lightly.
        text = text.replace("< ", "<").replace(" >", ">")

        # Fix array brackets.
        text = text.replace("[ ]", "[]")
        text = text.replace(" []", "[]")

        # Common Java output artifact from XLCoST.
        text = text.replace('"NEW_LINE"', '"\\n"')
        text = text.replace("'NEW_LINE'", "'\\n'")

        # ----------------------------------------------------
        # Conservative logical-operator repairs
        # ----------------------------------------------------
        # XLCoST sometimes loses logical operators between two
        # complete comparison expressions.
        #
        # Example broken Java:
        #     if(n % 2 == 0 n % 3 == 0)
        #
        # Correct Java:
        #     if(n % 2 == 0 || n % 3 == 0)
        #
        text = re.sub(
            r"(==\s*0)\s+([A-Za-z_][A-Za-z0-9_]*\s*%\s*\d+\s*==\s*0)",
            r"\1 || \2",
            text,
        )

        text = re.sub(
            r"(!=\s*0)\s+([A-Za-z_][A-Za-z0-9_]*\s*%\s*\d+\s*!=\s*0)",
            r"\1 || \2",
            text,
        )

        text = re.sub(
            r"(==\s*true)\s+([A-Za-z_][A-Za-z0-9_]*\s*==\s*true)",
            r"\1 && \2",
            text,
        )

        text = re.sub(
            r"(==\s*false)\s+([A-Za-z_][A-Za-z0-9_]*\s*==\s*false)",
            r"\1 && \2",
            text,
        )

        return text.strip()
