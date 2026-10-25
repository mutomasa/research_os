import pytest
import yaml

from research_os.cli import main
from research_os.data.interests import Interests, generate_interests, write_interests
from research_os.data.profile import load_profile


@pytest.fixture
def profile(root):
    return load_profile(root / "research/profile.yaml")


def test_one_topic_per_rq(profile):
    interests = generate_interests(profile)
    by_rq = {t.research_question: t for t in interests.topics if t.research_question}
    assert set(by_rq) == {"RQ1", "RQ2", "RQ3"}
    assert by_rq["RQ2"].tag == "Predictive World Model"
    assert "JEPA" in by_rq["RQ2"].keywords


def test_theme_topics_not_in_any_rq_go_to_theme_tag(profile):
    interests = generate_interests(profile)
    theme = [t for t in interests.topics if t.tag == "Theme"]
    covered = {k for t in interests.topics if t.research_question for k in t.keywords}
    expected = [k for k in profile.survey_topics if k not in covered]
    assert (theme[0].keywords if theme else []) == expected


def test_write_roundtrip_and_no_overwrite(tmp_path, profile):
    out = tmp_path / "interests.yaml"
    write_interests(generate_interests(profile), out)
    reloaded = Interests.model_validate(yaml.safe_load(out.read_text(encoding="utf-8")))
    assert reloaded == generate_interests(profile)
    with pytest.raises(FileExistsError):
        write_interests(generate_interests(profile), out)
    write_interests(generate_interests(profile), out, force=True)


def test_cli_interests_init(tmp_path, root, capsys):
    out = tmp_path / "interests.yaml"
    args = ["--profile", str(root / "research/profile.yaml"), "interests", "init", "--out", str(out)]
    assert main(args) == 0
    assert out.exists()
    assert main(args) == 1  # 既存ファイルは上書きしない
    assert "既にあります" in capsys.readouterr().err


def test_cli_venues(root, capsys):
    args = ["--registry", str(root / "registry/venues.yaml"), "--profile", str(root / "research/profile.yaml"), "venues"]
    assert main(args) == 0
    first = capsys.readouterr().out.splitlines()[0]
    assert "RA-L" in first
