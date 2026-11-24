import pytest

from glados_mcp.manager import MAX_CHUNK_CHARS, GladosManager, _split_text
from glados_mcp.utils import resources


def test_short_text_is_one_chunk():
    assert _split_text("Hello there. How are you?") == ["Hello there. How are you?"]


def test_long_text_splits_on_sentences_without_losing_words():
    text = " ".join(f"This is sentence number {i} of the test." for i in range(40))
    chunks = _split_text(text)
    assert len(chunks) > 1
    assert all(len(c) <= MAX_CHUNK_CHARS for c in chunks)
    assert " ".join(chunks) == text


def test_single_overlong_sentence_is_broken_up():
    text = "word " * 200
    chunks = _split_text(text)
    assert all(len(c) <= MAX_CHUNK_CHARS for c in chunks)
    assert " ".join(chunks).split() == text.split()


def test_models_dir_override(monkeypatch, tmp_path):
    monkeypatch.setenv("GLADOS_MCP_MODELS_DIR", str(tmp_path))
    assert resources.models_dir() == tmp_path
    assert resources.missing_models() == list(resources.MODELS)


def test_bundled_data_is_present():
    for name in ["glados.json", "phoneme_to_id.pkl", "lang_phoneme_dict.pkl", "token_to_idx.pkl", "idx_to_token.pkl"]:
        assert resources.data_path(name).is_file()
    for name in ["looping_radio_mix.wav", "portal_elevator_chime.wav"]:
        assert resources.sound_path(name).is_file()


def test_speak_rejects_empty_text():
    with pytest.raises(ValueError):
        GladosManager().speak("   ")


def test_unknown_alert_is_rejected():
    with pytest.raises(ValueError):
        GladosManager().alert("klaxon")
