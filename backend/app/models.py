
from typing import Literal
from pydantic import BaseModel, Field

Role = Literal["pos1","pos2","pos3","pos4","pos5"]
DraftPhase = Literal["blind","early","mid","late","last_pick"]

class Team(BaseModel):
    pos1: str | None = None
    pos2: str | None = None
    pos3: str | None = None
    pos4: str | None = None
    pos5: str | None = None

class DraftRequest(BaseModel):
    own_team: Team
    enemy_team: Team
    available_heroes: list[str] | None = None
    banned_heroes: list[str] = Field(default_factory=list)
    target_role: Role
    draft_phase: DraftPhase = "mid"

class MatchupDetail(BaseModel):
    enemy: str
    lane: float
    mid_game: float
    late_game: float
    score: float
    source: Literal["curated","curated_inverse","inferred"]
    confidence: float
    effective_lane: float
    effective_mid_game: float
    effective_late_game: float
    reasons: list[str]

class DraftResult(BaseModel):
    hero: str
    score: float
    raw_score: float
    patch: str
    data_quality: str
    matchup_confidence: float
    matchup_details: list[MatchupDetail]
    component_scores: dict[str, float]
    breakdown: dict[str, float]
    knowledge_graph_reasons: list[str]
    explanation: str
