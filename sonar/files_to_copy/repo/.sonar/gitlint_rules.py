"""
These rules govern gitlint, a pre-commit tool to validate each git commit
message
"""

import nltk
from gitlint.options import ListOption
from gitlint.rules import CommitMessageTitle, LineRule, RuleViolation

DEFAULT_BANNED_CHARS = "$^%@!*()"


class SpecialChars(LineRule):
    """
    This rule will enforce that the commit message title does not contain any
    banned characters.
    """

    # A rule MUST have a human friendly name
    name = "title-no-special-chars"

    # A rule MUST have a *unique* id
    id = "UL1"

    # A line-rule MUST have a target (not required for CommitRules).
    target = CommitMessageTitle

    # A rule MAY have an option_spec if its behavior should be configurable.
    options_spec = [
        ListOption(
            "special-chars",
            list(DEFAULT_BANNED_CHARS),
            "Comma separated list of characters that should not occur in the title",
        )
    ]

    def validate(self, line, _commit):
        """
        Validate each line

        Args:
            line (str): line
            _commit (???): ???

        Returns:
            list: List of violations
        """
        violations = []
        # options can be accessed by looking them up by their name in self.options
        for char in self.options["special-chars"].value:
            if char in line:
                violation = RuleViolation(
                    self.id,
                    "Title contains the special character '{0}'".format(char),
                    line,
                )
                violations.append(violation)

        return violations


# inspired by https://github.com/coala/coala-bears/pull/315/files#diff-e0a334e6d00dfb6b1fbebb7c515ca4f8
def check_imperative(sentence: str) -> str:
    """
    Check the given sentence to see if it starts in the imperative tense. Note,\
    this is not completely accurate due to inherent limitations of nlp.

    Args:
        sentence (str): Sentence to check

    Returns:
        str: Empty string if first word is in imperative, the first word otherwise
    """

    try:
        words = nltk.word_tokenize(nltk.sent_tokenize(sentence)[0])
        word, tag = nltk.pos_tag(["I"] + words)[1:2][0]
        # https://pythonprogramming.net/part-of-speech-tagging-nltk-tutorial/
        if (
            tag.startswith("VBZ")
            or tag.startswith("VBD")
            or tag.startswith("VBG")
            or tag.startswith("VBN")
        ):
            return word
        if tag.startswith("VBP") or tag.startswith("VB"):
            return ""  # this word is okay
        return word  # perhaps not a verb?
    except LookupError:
        print(
            "NLTK data missing, install by running following commands "
            "`python -m nltk.downloader punkt"
            " maxent_treebank_pos_tagger averaged_perceptron_tagger`"
        )
        return "nltk"  # force an error by returning a non-empty string


class ImperativeTenseTitle(LineRule):
    """
    This rule will enforce that the commit message title starts in imperative tense.
    """

    # A rule MUST have a human friendly name
    name = "title-imperative"

    # A rule MUST have a *unique* id
    id = "UL2"

    # A line-rule MUST have a target (not required for CommitRules).
    target = CommitMessageTitle

    def validate(self, line, _commit):
        """
        Validate each line

        Args:
            line (str): line
            _commit (???): ???

        Returns:
            list: List of violations
        """
        violations = []
        word = check_imperative(line)
        if word:
            violation = RuleViolation(
                self.id, f"Title must start in the imperative: '{word}'", line
            )
            violations.append(violation)

        return violations
