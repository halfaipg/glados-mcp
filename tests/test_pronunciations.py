import pickle

import pytest

from glados_mcp.synth import pronunciations
from glados_mcp.utils import resources
from glados_mcp.utils.spoken_text_converter import SpokenTextConverter


@pytest.fixture(scope="module")
def phoneme_dict():
    with resources.data_path("lang_phoneme_dict.pkl").open("rb") as f:
        entries = dict(pickle.load(f))
    entries.update(pronunciations.extra_entries())
    return entries


def test_days_and_months_have_fixed_pronunciations(phoneme_dict):
    assert pronunciations.lookup("friday", phoneme_dict) == "fɹˈaɪdeɪ"
    assert pronunciations.lookup("july", phoneme_dict) == "dʒuːlˈaɪ"
    for word in ["monday", "saturday", "january", "december", "fridays"]:
        assert pronunciations.lookup(word, phoneme_dict)


def test_initialisms_are_spelled_out_in_any_case(phoneme_dict):
    spelled = "ˈeɪ pˈiː ˈaɪ"
    assert pronunciations.lookup("API", phoneme_dict) == spelled
    assert pronunciations.lookup("api", phoneme_dict) == spelled
    assert pronunciations.lookup("apis", phoneme_dict) == spelled + "z"
    assert pronunciations.lookup("US", phoneme_dict) == "jˈuː ˈɛs"


def test_shouted_words_are_not_spelled_out(phoneme_dict):
    assert pronunciations.lookup("NOT", phoneme_dict) == phoneme_dict["not"]
    assert pronunciations.lookup("NO", phoneme_dict) == phoneme_dict["no"]
    assert pronunciations.lookup("JSON", phoneme_dict) == pronunciations.WORDS["json"]


def test_unknown_words_fall_back_to_the_model(phoneme_dict):
    assert pronunciations.lookup("XQZ", phoneme_dict) == "ˈɛks kjˈuː zˈiː"  # short and all caps: spelled
    assert pronunciations.lookup("ZXQVBNMKL", phoneme_dict) is None  # long: left to the model
    assert pronunciations.lookup("zxqvb", phoneme_dict) is None


def test_single_capital_letter_is_its_name(phoneme_dict):
    assert pronunciations.lookup("I", phoneme_dict) == "ˈaɪ"


def test_converter_keeps_capitals_for_the_phonemizer():
    spoken = SpokenTextConverter().text_to_spoken("The API is down on Friday.")
    assert spoken == "the API is down on friday."
