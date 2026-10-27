from pathlib import Path

import pytest

import openjarvis.skills as skills_pkg
from openjarvis.skills.loader import load_skill_directory

DATA = Path(skills_pkg.__file__).parent / "data"
NAMES = [
    "local-seo-schema",
    "premium-web-design",
    "site-screenshot-review",
    "outreach-compliance",
    "client-invoice",
]


@pytest.mark.parametrize("name", NAMES)
def test_skill_loads(name):
    m = load_skill_directory(DATA / name)
    assert m.name == name
    assert m.description
    assert m.markdown_content.strip()
