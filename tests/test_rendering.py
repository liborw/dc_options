from dc_options.rendering import replace_text


def test_replace_all_simple():
    text = "A <x> B <x> C"
    assert replace_text(text, "Y", "<x>") == "A Y B Y C"


def test_replace_first_only():
    text = "A <x> B <x> C"
    assert replace_text(text, "Y", "<x>", replace_all=False) == "A Y B <x> C"


def test_identical_markers():
    text = "Hello ##name##, id ##123##."
    assert replace_text(text, "X", "##") == "Hello X, id X."


def test_missing_end_marker():
    text = "Start <tag> but never ends"
    assert replace_text(text, "X", "<tag>", "</tag>") == text


def test_no_markers_present():
    text = "nothing to replace here"
    assert replace_text(text, "X", "<tag>", "</tag>") == text


def test_replace_empty_section():
    text = "A [[ ]] B [[ ]]"
    assert replace_text(text, "X", "[[", "]]") == "A X B X"


def test_nested_markers_not_supported():
    text = "<a> one <a> two </a> three </a>"
    # Current logic replaces only outermost or first match depending on replace_all.
    # This verifies current (non-nested) behavior.
    assert replace_text(text, "X", "<a>", "</a>") == "X"
