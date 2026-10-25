"""関心プロファイル（interests.yaml）の初期生成。

仕様: docs/design.md §3.2 / docs/new_features/alphaXiv.md §1
研究プロファイルの RQ ごとの survey_topics を 1 タグにまとめ、どの RQ にも属さない
テーマ全体の survey_topics は Theme タグに入れる。生成後はユーザーが編集する前提なので、
既存ファイルは force なしでは上書きしない。
"""

from pathlib import Path
from typing import Literal

import yaml

from research_os.data.base import StrictModel
from research_os.data.profile import ResearchProfile

DEFAULT_PATH = Path("research/interests.yaml")

Prioritize = Literal["recency", "default", "popular", "historical"]
Schedule = Literal["daily", "weekly", "manual"]


class Topic(StrictModel):
    tag: str
    keywords: list[str]
    prioritize: Prioritize = "recency"
    research_question: str | None = None  # RQ カバレッジ集計用のひも付け


class Interests(StrictModel):
    topics: list[Topic]
    researchers: list[str] = []
    arxiv_categories: list[str] = []
    schedule: Schedule = "manual"


def generate_interests(profile: ResearchProfile) -> Interests:
    topics = [
        Topic(tag=rq.title, keywords=list(rq.survey_topics), research_question=rq.id)
        for rq in profile.research_questions
        if rq.survey_topics
    ]
    covered = {k for t in topics for k in t.keywords}
    rest = [k for k in profile.survey_topics if k not in covered]
    if rest:
        topics.append(Topic(tag="Theme", keywords=rest))
    return Interests(topics=topics, arxiv_categories=["cs.RO"])


def write_interests(interests: Interests, path: Path = DEFAULT_PATH, force: bool = False) -> Path:
    path = Path(path)
    if path.exists() and not force:
        raise FileExistsError(f"{path} は既にあります（上書きするには force を指定）")
    header = (
        "# 関心プロファイル（docs/design.md §3.2 / docs/new_features/alphaXiv.md §1）\n"
        "# research/profile.yaml から `research-os interests init` で生成。以後は手で編集してよい。\n"
    )
    body = yaml.safe_dump(
        interests.model_dump(exclude_none=True), allow_unicode=True, sort_keys=False
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(header + body, encoding="utf-8")
    return path
