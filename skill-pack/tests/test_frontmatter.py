import pytest

from paiw_skill_pack.frontmatter import FrontmatterError, parse_skill_frontmatter


def test_parse_valid_frontmatter() -> None:
    result = parse_skill_frontmatter(
        "---\nname: example\ndescription: Use when testing. Do not use for production.\n---\n# Body\n"
    )
    assert result["name"] == "example"


def test_description_requires_positive_and_negative_boundary() -> None:
    with pytest.raises(FrontmatterError):
        parse_skill_frontmatter(
            "---\nname: example\ndescription: A generic helper.\n---\n# Body\n"
        )
