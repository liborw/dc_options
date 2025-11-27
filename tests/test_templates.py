from dataclasses import dataclass

from dc_options import Options, option, render


@dataclass
class Inner(Options):
    value: int = option(default=5)


@dataclass
class Config(Options):
    inner: Inner = option(default_factory=Inner, label="Inner Block")
    title: str = option(default="demo")


def test_render_template_plain():
    cfg = Config()
    output = render(cfg)
    assert "[Inner Block]" in output
    assert "inner.value" in output


def test_render_template_markdown():
    cfg = Config()
    output = render(cfg, template="docs.md.jinja")
    assert "## Inner Block" in output
    assert "title" in output
