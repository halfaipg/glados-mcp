"""Pronunciations the bundled dictionary gets wrong or lacks.

The dictionary contains no capitalised words, so names of days, months and
products fall through to a grapheme-to-phoneme model that guesses badly
("Friday" came out as "FRID-ay"), and it has no letter names, so acronyms
such as API or URL were unintelligible. This module supplies both.
"""

from __future__ import annotations

from collections.abc import Mapping

# Letter names, used to spell out initialisms.
LETTERS: dict[str, str] = {
    "A": "ˈeɪ", "B": "bˈiː", "C": "sˈiː", "D": "dˈiː", "E": "ˈiː", "F": "ˈɛf", "G": "dʒˈiː",
    "H": "ˈeɪtʃ", "I": "ˈaɪ", "J": "dʒˈeɪ", "K": "kˈeɪ", "L": "ˈɛl", "M": "ˈɛm", "N": "ˈɛn",
    "O": "ˈoʊ", "P": "pˈiː", "Q": "kjˈuː", "R": "ˈɑːɹ", "S": "ˈɛs", "T": "tˈiː", "U": "jˈuː",
    "V": "vˈiː", "W": "dˈʌbəljˌuː", "X": "ˈɛks", "Y": "wˈaɪ", "Z": "zˈiː",
}  # fmt: skip

# Always spelled letter by letter, in any capitalisation.
INITIALISMS: frozenset[str] = frozenset(
    """api url uri css html http https xml csv pdf cpu gpu sdk cli mcp llm dns ssh ssl tls aws gcp ide tts
    ui ux id os pr ci cd db io ip vm npm jwt orm rpc cdn faq tbd wip lgtm usa uk eu ml qa rgb fps kb mb gb tb
    php rss ftp tcp udp utf vpn svg png jpg dll sso mfa otp crm kpi roi ceo cto cfo hr nda eol eof""".split()
)

# Two-letter words that are ordinary words even when written in capitals ("NO", "OK").
_SHORT_WORDS: frozenset[str] = frozenset(
    "ok no so oh go do up my me we he is it if in on to be or at as an by of hi am ai".split()
)

# Unknown all-caps words up to this length are spelled out; longer ones are read as words.
_MAX_SPELLED = 5

_DAYS = {
    "monday": "mˈʌndeɪ", "tuesday": "tˈuːzdeɪ", "wednesday": "wˈɛnzdeɪ", "thursday": "θˈɜːzdeɪ",
    "friday": "fɹˈaɪdeɪ", "saturday": "sˈæɾɚdˌeɪ", "sunday": "sˈʌndeɪ",
}  # fmt: skip

# Whole words, keyed in lowercase. These override the dictionary.
WORDS: dict[str, str] = {
    **_DAYS,
    **{f"{day}s": f"{phonemes}z" for day, phonemes in _DAYS.items()},
    "january": "dʒˈænjuːˌɛɹi", "february": "fˈɛbɹuːˌɛɹi", "april": "ˈeɪpɹəl", "june": "dʒˈuːn",
    "july": "dʒuːlˈaɪ", "september": "sɛptˈɛmbɚ", "october": "ɑːktˈoʊbɚ", "december": "dᵻsˈɛmbɚ",
    "america": "ɐmˈɛɹɪkə", "american": "ɐmˈɛɹɪkən", "british": "bɹˈɪɾɪʃ", "europe": "jˈʊɹəp",
    "european": "jˌʊɹəpˈiːən", "christmas": "kɹˈɪsməs",
    "ok": "oʊkˈeɪ", "nasa": "nˈæsə", "todo": "tˈuːdˈuː", "wifi": "wˈaɪfaɪ", "sudo": "sˈuːduː",
    "github": "ɡˈɪthʌb", "gitlab": "ɡˈɪtlæb", "microsoft": "mˈaɪkɹəsˌɔft", "anthropic": "ænθɹˈɑːpɪk",
    "json": "dʒˈeɪsən", "yaml": "jˈæməl", "toml": "tˈɑːməl", "sql": "sˈiːkwəl",
    "javascript": "dʒˈɑːvəskɹˌɪpt", "kubernetes": "kˌuːbɚnˈɛɾiːz", "postgres": "pˈoʊstɡɹɛs",
    "redis": "ɹˈɛdɪs", "numpy": "nˈʌmpaɪ", "nginx": "ˈɛndʒɪn ˈɛks", "pytest": "pˈaɪtɛst",
    "async": "ˈeɪsɪŋk", "regex": "ɹˈɛdʒɛks", "frontend": "fɹˈʌntɛnd", "backend": "bˈækɛnd",
    "localhost": "lˈoʊkəlhˌoʊst", "devops": "dˈɛvɑːps", "unix": "jˈuːnɪks", "macos": "mˌækoʊˈɛs",
    "rebase": "ɹiːbˈeɪs", "oauth": "ˈoʊɔːθ",
}  # fmt: skip


def spell(word: str) -> str:
    """Phonemes for a word read letter by letter."""
    return " ".join(LETTERS[c] for c in word.upper() if c in LETTERS)


def extra_entries() -> dict[str, str]:
    """Entries to merge into the phoneme dictionary (lowercase keys)."""
    entries = dict(WORDS)
    for name in INITIALISMS:
        entries[name] = spell(name)
        entries[f"{name}s"] = spell(name) + "z"  # "APIs", "URLs"
    return entries


def lookup(word: str, phoneme_dict: Mapping[str, str]) -> str | None:
    """Phonemes for a word, or None if the caller should fall back to the model.

    `phoneme_dict` must already include `extra_entries()`. Capitalisation matters
    only for all-caps words, which may be initialisms to spell out.
    """
    lower = word.lower()
    if word.isascii() and word.isalpha() and word.isupper():
        if len(word) == 1:
            return LETTERS[word]
        if lower in INITIALISMS:
            return spell(word)
        known = lower in phoneme_dict and (len(word) > 2 or lower in _SHORT_WORDS)
        if not known and len(word) <= _MAX_SPELLED:
            return spell(word)
    return phoneme_dict.get(lower)
