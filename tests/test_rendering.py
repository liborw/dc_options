from dc_options.rendering import replace_text


def test_replace_first_only_keep_markers():
    text = "A <x>old</x> B <x>123</x> C"
    assert replace_text(text, "NEW", "<x>", "</x>") \
           == "A <x>NEW</x> B <x>123</x> C"


def test_identical_markers():
    text = "Hello ##name## and ##id##"
    assert replace_text(text, "X", "##") == "Hello ##X## and ##id##"


def test_missing_end_marker():
    text = "Start <tag>oops"
    assert replace_text(text, "X", "<tag>", "</tag>") == text


def test_no_markers_present():
    text = "nothing to replace"
    assert replace_text(text, "Y", "<x>", "</x>") == text


def test_multiline_replace_first():
    text = (
        "L1\n"
        "START\n"
        "middle\n"
        "END\n"
        "L5\n"
        "START\n"
        "second\n"
        "END\n"
    )
    expected = (
        "L1\n"
        "STARTREPLACEDEND\n"
        "L5\n"
        "START\n"
        "second\n"
        "END\n"
    )
    assert replace_text(text, "REPLACED", "START", "END") == expected


def test_empty_section_content():
    text = "A [[ ]] B [[old]]"
    assert replace_text(text, "X", "[[", "]]") == "A [[X]] B [[old]]"
