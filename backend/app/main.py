import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .engine import DraftEngine
from .models import DraftRequest, DraftResult

app = FastAPI(title="Dota 2 Draft Bot", version="0.7.0")


def allowed_origins_from_env():
    configured = os.getenv("ALLOWED_ORIGINS")
    if configured is None:
        return [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]

    origins = [origin.strip().rstrip("/") for origin in configured.split(",") if origin.strip()]
    if "*" in origins:
        raise ValueError("ALLOWED_ORIGINS must not contain a wildcard")
    return origins


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins_from_env(),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

engine = DraftEngine()


@app.get("/")
def root():
    return {"message": "Dota 2 Draft Bot API is running", "version": app.version}


@app.get("/meta")
def meta():
    return {
        **engine.meta,
        "hero_profile_build": engine.profile_meta,
        **engine.matchup_coverage(),
        "scoring": engine.scoring_configuration(),
        "loaded_heroes": len(engine.heroes),
        "curated_heroes": sum(
            1 for hero in engine.heroes.values() if hero.get("data_quality") != "seed"
        ),
        "complete_profile_coverage": {
            field: sum(1 for hero in engine.heroes.values() if hero.get(field))
            for field in (
                "roles",
                "tag_weights",
                "weakness_weights",
                "lane_profile",
                "power_spikes",
                "team_contributions",
                "item_profile",
                "base_stats",
                "abilities",
                "talents",
                "facets",
                "aghanim",
            )
        },
    }


@app.get("/heroes")
def heroes():
    return {
        "patch": engine.meta["game_patch"],
        "heroes": [
            {
                "name": name,
                "roles": profile.get("roles", {}),
                "data_quality": profile.get("data_quality", "seed"),
            }
            for name, profile in sorted(engine.heroes.items())
        ],
    }


@app.get("/heroes/{hero}")
def hero_profile(hero: str):
    profile = engine.heroes.get(hero)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Unknown hero: {hero}")
    return {"name": hero, **profile}


@app.get("/matchups/{candidate}/{enemy}")
def matchup(candidate: str, enemy: str):
    unknown = [hero for hero in (candidate, enemy) if hero not in engine.heroes]
    if unknown:
        raise HTTPException(status_code=404, detail=f"Unknown hero: {', '.join(unknown)}")
    return {"candidate": candidate, "enemy": enemy, **engine.resolve_matchup(candidate, enemy)}


@app.post("/draft/rank", response_model=list[DraftResult])
def rank_draft(payload: DraftRequest):
    return engine.rank_candidates(
        own_team=payload.own_team.model_dump(),
        enemy_team=payload.enemy_team.model_dump(),
        available_heroes=payload.available_heroes,
        target_role=payload.target_role,
        draft_phase=payload.draft_phase,
        banned_heroes=payload.banned_heroes,
    )
