from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    """YAML の書き間違い（未知のキー）を黙って無視しないモデル。"""

    model_config = ConfigDict(extra="forbid")
