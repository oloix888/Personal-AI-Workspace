from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_required_skill_pack_roots_exist() -> None:
    expected = [
        ROOT / "skills" / "_shared" / "contract",
        ROOT / "skills" / "_shared" / "schemas",
        ROOT / "skills" / "_shared" / "fixtures",
        ROOT / "skill-pack" / "src" / "paiw_skill_pack",
        ROOT / "skill-pack" / "scripts",
    ]
    assert [str(path.relative_to(ROOT)) for path in expected if not path.is_dir()] == []


def test_python_package_is_importable() -> None:
    import paiw_skill_pack

    assert paiw_skill_pack.__version__ == "0.1.0-beta.1"


def test_skill_pack_validation_workflow_covers_every_repository_change() -> None:
    workflow = (ROOT / ".github/workflows/validate-skill-pack.yml").read_text(
        encoding="utf-8"
    )

    assert "paths" not in workflow
