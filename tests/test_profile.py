import pytest
import yaml
from pydantic import ValidationError

from research_os.data.profile import ResearchProfile, effective_venues, load_profile
from research_os.data.venues import load_venues


@pytest.fixture
def registry(root):
    return load_venues(root / "registry/venues.yaml")


def _raw(root):
    return yaml.safe_load((root / "research/profile.yaml").read_text(encoding="utf-8"))


def test_load_real_profile(root, registry):
    prof = load_profile(root / "research/profile.yaml")
    assert [rq.id for rq in prof.research_questions] == ["RQ1", "RQ2", "RQ3"]
    prof.check_venues(registry)


def test_effective_venues_sorted_by_priority(root, registry):
    prof = load_profile(root / "research/profile.yaml")
    labels = [v.label for v in effective_venues(registry, prof)[:6]]
    assert labels[:4] == ["RA-L", "ICRA", "IROS", "RSS"]
    assert set(labels[4:]) == {"T-RO", "IJRR"}


def test_override_changes_only_given_fields(root, registry):
    raw = _raw(root)
    raw["venue_overrides"] = {"case": {"priority": 1}}
    venues = effective_venues(registry, ResearchProfile.model_validate(raw))
    case = next(v for v in venues if v.venue_id == "case")
    assert case.priority == 1
    assert case.fit == registry.get("case").fit
    assert registry.get("case").priority is None  # レジストリ側は変えない


def test_unknown_venue_reference_rejected(root, registry):
    raw = _raw(root)
    raw["survey_venues"].append("neurips")
    with pytest.raises(ValueError, match="neurips"):
        ResearchProfile.model_validate(raw).check_venues(registry)


def test_unknown_rq_in_submission_plan_rejected(root):
    raw = _raw(root)
    raw["submission_plan"][0]["research_questions"] = ["RQ9"]
    with pytest.raises(ValidationError, match="RQ9"):
        ResearchProfile.model_validate(raw)
