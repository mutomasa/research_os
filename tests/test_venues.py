import pytest
import yaml
from pydantic import ValidationError

from research_os.data.venues import VenueRegistry, load_venues


def _raw(root):
    return yaml.safe_load((root / "registry/venues.yaml").read_text(encoding="utf-8"))


def test_load_real_registry(root):
    registry = load_venues(root / "registry/venues.yaml")
    assert len(registry.venues) == 15
    assert registry.get("ral").label == "RA-L"
    assert registry.get("scirobotics").label == "Science Robotics"
    assert set(registry.get("ral").policies.co_presents_with) == {"icra", "iros"}


def test_unverified_policies_and_no_guessed_deadlines(root):
    for v in load_venues(root / "registry/venues.yaml").venues:
        assert v.policies.verified is False
        assert v.deadlines == []


def test_duplicate_venue_id_rejected(root):
    raw = _raw(root)
    raw["venues"].append(dict(raw["venues"][0]))
    with pytest.raises(ValidationError, match="重複"):
        VenueRegistry.model_validate(raw)


def test_unknown_co_presents_with_rejected(root):
    raw = _raw(root)
    raw["venues"][0]["policies"]["co_presents_with"] = ["nope"]
    with pytest.raises(ValidationError, match="nope"):
        VenueRegistry.model_validate(raw)


def test_unknown_key_rejected(root):
    raw = _raw(root)
    raw["venues"][0]["fitt"] = "◎"
    with pytest.raises(ValidationError):
        VenueRegistry.model_validate(raw)
