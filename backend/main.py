from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List

import dota_analyzer


app = FastAPI(
    title="Dota 2 Draft Assistant API",
    version="1.0.0"
)


# ==================================================
# CORS
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# REQUEST MODELS
# ==================================================

class AnalyzeRequest(BaseModel):
    enemy_team: List[str] = Field(default_factory=list)
    own_team: List[str] = Field(default_factory=list)


# ==================================================
# BASIC ROUTE
# ==================================================

@app.get("/")
def root():
    return {
        "message": "Dota 2 Draft Assistant API is running"
    }


# ==================================================
# GET ALL HEROES
# ==================================================

@app.get("/api/heroes")
def get_heroes():

    heroes = (
        dota_analyzer.hero_df["localized_name"]
        .dropna()
        .tolist()
    )

    return {
        "heroes": heroes
    }


# ==================================================
# HERO SEARCH
# ==================================================

@app.get("/api/heroes/search")
def search_heroes(
    q: str = Query(..., min_length=1)
):

    results = dota_analyzer.suggest_hero_input(
        dota_analyzer.hero_df,
        q
    )

    return {
        "query": q,
        "heroes": results[:10]
    }


# ==================================================
# ANALYZE DRAFT
# ==================================================

@app.post("/api/analyze")
def analyze_draft(request: AnalyzeRequest):

    enemy_team = request.enemy_team
    own_team = request.own_team

    # --------------------------------------------------
    # BASIC VALIDATION
    # --------------------------------------------------

    if not enemy_team:
        raise HTTPException(
            status_code=400,
            detail="Enemy team cannot be empty."
        )

    if len(enemy_team) > 5:
        raise HTTPException(
            status_code=400,
            detail="Enemy team cannot contain more than 5 heroes."
        )

    if len(own_team) > 4:
        raise HTTPException(
            status_code=400,
            detail="Own team cannot contain more than 4 heroes."
        )

    all_selected = enemy_team + own_team

    if len(all_selected) != len(set(all_selected)):
        raise HTTPException(
            status_code=400,
            detail="A hero cannot be selected more than once."
        )

    valid_heroes = set(
        dota_analyzer.hero_df["localized_name"]
    )

    invalid_enemy = [
        hero
        for hero in enemy_team
        if hero not in valid_heroes
    ]

    invalid_own = [
        hero
        for hero in own_team
        if hero not in valid_heroes
    ]

    if invalid_enemy or invalid_own:
        raise HTTPException(
            status_code=400,
            detail={
                "invalid_enemy": invalid_enemy,
                "invalid_own": invalid_own
            }
        )

    matchup_cache = (
        dota_analyzer.build_enemy_matchup_cache(
            enemy_team
        )
    )

    position_names = {
        1: "Carry",
        2: "Mid",
        3: "Offlane",
        4: "Soft Support",
        5: "Hard Support",
    }

    general_picks = (
        dota_analyzer.get_general_top_picks(
            enemy_team,
            own_team,
            matchup_cache,
            top_n=5
        )
    )

    general_results = []

    for hero, position, score_data in general_picks:

        general_results.append({
            "hero": hero,
            "position": position,
            "position_name": position_names[position],
            "score": score_data
        })


    position_results = {}

    for position in range(1, 6):

        picks = (
            dota_analyzer.get_top_picks_for_position(
                position,
                enemy_team,
                own_team,
                matchup_cache,
                top_n=5
            )
        )

        position_results[str(position)] = [
            {
                "hero": hero,
                "position": position,
                "position_name": position_names[position],
                "score": score_data
            }
            for hero, score_data in picks
        ]


    return {
        "enemy_team": enemy_team,
        "own_team": own_team,

        "recommendations": {
            "general": general_results,
            "positions": position_results
        }
    }