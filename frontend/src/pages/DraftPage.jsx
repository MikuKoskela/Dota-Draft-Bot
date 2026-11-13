import { useEffect, useMemo, useState } from "react";

import Team from "../components/Team";
import RecommendationCard from "../components/RecommendationCard";

import { getHeroProfile, getHeroes, getMeta, rankDraft } from "../api/api";
import HeroGrid from "../components/HeroGrid";
import HeroProfileModal from "../components/HeroProfileModal";

const MAX_ENEMY_HEROES = 5;
const MAX_OWN_HEROES = 4;
const positions = [
    {
        id: "pos1",
        name: "Carry",
        short: "POS 1",
    },
    {
        id: "pos2",
        name: "Mid",
        short: "POS 2",
    },
    {
        id: "pos3",
        name: "Offlane",
        short: "POS 3",
    },
    {
        id: "pos4",
        name: "Soft Support",
        short: "POS 4",
    },
    {
        id: "pos5",
        name: "Hard Support",
        short: "POS 5",
    },
];

const DEFAULT_DRAFT_PHASE = "mid";
const emptyTeam = () => Object.fromEntries(positions.map(({ id }) => [id, null]));
const selectedCount = (team) => Object.values(team).filter(Boolean).length;

export default function DraftPage() {
    const [enemyTeam, setEnemyTeam] = useState(emptyTeam);
    const [ownTeam, setOwnTeam] = useState(emptyTeam);
    const [heroes, setHeroes] = useState([]);
    const [meta, setMeta] = useState(null);
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [loadingRoster, setLoadingRoster] = useState(true);
    const [error, setError] = useState("");
    const [profileModal, setProfileModal] = useState(null);

    useEffect(() => {
        Promise.all([getHeroes(), getMeta()])
            .then(([heroList, engineMeta]) => {
                setHeroes(heroList);
                setMeta(engineMeta);
            })
            .catch((err) => setError(err.message || "Could not load draft data."))
            .finally(() => setLoadingRoster(false));
    }, []);

    const allSelectedHeroes = useMemo(
        () => [
            ...Object.values(enemyTeam),
            ...Object.values(ownTeam),
        ].filter(Boolean),
        [enemyTeam, ownTeam]
    );
    const enemyPicksComplete = selectedCount(enemyTeam) === MAX_ENEMY_HEROES;
    const activeSelectionSide = enemyPicksComplete ? "own" : "enemy";
    const activeSelectionRole = positions.find(({ id }) =>
        !(activeSelectionSide === "enemy" ? enemyTeam[id] : ownTeam[id])
    )?.id ?? null;
    const roleConfidenceFloor = meta?.role_min_confidence ?? 0.45;

    function addEnemyHero(hero) {
        const nextPosition = positions.find(({ id }) => !enemyTeam[id]);
        if (!nextPosition) return;
        if (allSelectedHeroes.includes(hero)) return;
        setEnemyTeam((current) => ({ ...current, [nextPosition.id]: hero }));
        setAnalysis(null);
        setError("");
    }

    function addOwnHero(hero) {
        if (!enemyPicksComplete) {
            setError("Complete all five enemy picks before selecting your team.");
            return;
        }
        const nextPosition = positions.find(({ id }) => !ownTeam[id]);
        if (!nextPosition || selectedCount(ownTeam) >= MAX_OWN_HEROES) return;
        if (allSelectedHeroes.includes(hero)) return;
        const updatedTeam = { ...ownTeam, [nextPosition.id]: hero };
        setOwnTeam(updatedTeam);
        setAnalysis(null);
        setError("");
        if (selectedCount(updatedTeam) === MAX_OWN_HEROES) {
            requestFinalPick(updatedTeam, enemyTeam, DEFAULT_DRAFT_PHASE);
        }
    }

    function removeEnemyHero(hero) {
        setEnemyTeam((current) => Object.fromEntries(
            Object.entries(current).map(([role, currentHero]) => [
                role,
                currentHero === hero ? null : currentHero,
            ])
        ));
        setAnalysis(null);
    }

    function removeOwnHero(hero) {
        setOwnTeam((current) => Object.fromEntries(
            Object.entries(current).map(([role, currentHero]) => [
                role,
                currentHero === hero ? null : currentHero,
            ])
        ));
        setAnalysis(null);
    }

    function resetDraft() {
        setEnemyTeam(emptyTeam());
        setOwnTeam(emptyTeam());
        setAnalysis(null);
        setError("");
        setProfileModal(null);
    }

    async function requestFinalPick(ownDraft, enemyDraft, phase) {
        const targetRole = positions.find(({ id }) => !ownDraft[id]);
        if (!targetRole) return;
        try {
            setLoading(true);
            setError("");
            const picks = await rankDraft(
                ownDraft,
                enemyDraft,
                targetRole.id,
                phase
            );
            setAnalysis({
                targetRole: targetRole.id,
                recommendations: picks.map((pick) => ({
                    ...pick,
                    position: targetRole.id,
                    position_name: targetRole.name,
                })),
            });
        } catch (err) {
            console.error(err);

            setError(
                err.message ||
                    "Something went wrong while analyzing the draft."
            );
        } finally {
            setLoading(false);
        }
    }

    function handleAnalyze() {
        if (selectedCount(enemyTeam) !== MAX_ENEMY_HEROES) {
            setError("Add all five enemy heroes first.");
            return;
        }
        if (selectedCount(ownTeam) !== MAX_OWN_HEROES) {
            setError("Add four friendly heroes to get the final-pick ranking.");
            return;
        }
        requestFinalPick(ownTeam, enemyTeam, DEFAULT_DRAFT_PHASE);
    }

    async function openHeroProfile(hero) {
        setProfileModal({ hero, profile: null, loading: true, error: "" });
        try {
            const profile = await getHeroProfile(hero);
            setProfileModal({ hero, profile, loading: false, error: "" });
        } catch (err) {
            setProfileModal({
                hero,
                profile: null,
                loading: false,
                error: err.message || "Could not load hero profile.",
            });
        }
    }

    const recommendations = analysis?.recommendations ?? [];
    const targetRole = positions.find(({ id }) => !ownTeam[id]);

    return (
        <main className="min-h-screen overflow-x-hidden">
            {/* Header */}
            <header
                className="
                    sticky
                    top-0
                    z-40
                    border-b
                    border-slate-800/80
                    bg-slate-950/85
                    backdrop-blur-xl
                "
            >
                <div
                    className="
                        mx-auto
                        flex
                        max-w-7xl
                        items-center
                        justify-between
                        px-4
                        py-3
                        sm:px-6
                        lg:px-8
                    "
                >
                    <div>
                        <div className="flex items-center gap-2">
                            <div
                                className="
                                    flex
                                    h-8
                                    w-8
                                    items-center
                                    justify-center
                                    rounded-lg
                                    bg-gradient-to-br
                                    from-red-700
                                    to-red-950
                                    text-sm
                                    font-black
                                    shadow-lg
                                    shadow-red-950/50
                                "
                            >
                                D
                            </div>

                            <h1 className="text-sm font-bold tracking-wide text-white sm:text-base">
                                DOTA 2 DRAFT ASSISTANT (BETA)
                            </h1>
                        </div>

                        <p className="mt-0.5 hidden text-[10px] text-slate-500 sm:block">
                            Dota 2 Position Draft Analyzer
                            {meta?.game_patch ? ` · Patch ${meta.game_patch}` : ""}
                        </p>
                    </div>

                    <button
                        type="button"
                        onClick={resetDraft}
                        className="
                            rounded-lg
                            border
                            border-slate-700
                            bg-slate-900
                            px-3
                            py-2
                            text-xs
                            font-semibold
                            text-slate-400
                            transition-all
                            duration-200
                            hover:border-slate-500
                            hover:text-white
                            active:scale-95
                        "
                    >
                        Reset
                    </button>
                </div>
            </header>

            <div
                className="
                    mx-auto
                    max-w-7xl
                    px-3
                    py-5
                    sm:px-6
                    sm:py-8
                    lg:px-8
                    lg:py-10
                "
            >
                {/* Hero intro */}
                <section
                    className="
                        mb-5
                        text-center
                        sm:mb-8
                    "
                >
                    <p className="mb-2 text-[10px] font-bold uppercase tracking-[0.25em] text-amber-400">
                        Dota 2 · Draft Strategy
                    </p>

                    <h2
                        className="
                            text-2xl
                            font-black
                            tracking-tight
                            text-white
                            sm:text-4xl
                        "
                    >
                        Build your draft
                    </h2>

                    <p
                        className="
                            mx-auto
                            mt-2
                            max-w-xl
                            text-xs
                            leading-relaxed
                            text-slate-500
                            sm:text-sm
                        "
                    >
                        Fill the enemy lineup first. The eligible hero pool advances through positions automatically, then ranks your final pick after four friendly picks.
                    </p>
                </section>

                {/* Draft arena */}
                <section
                    className="
                        relative
                        rounded-3xl
                        border
                        border-[#39352e]
                        bg-[#111213]/80
                        p-2
                        shadow-2xl
                        sm:p-4
                        lg:p-6
                    "
                >
                    {/* Desktop center decoration */}
                    <div
                        className="
                            pointer-events-none
                            absolute
                            left-1/2
                            top-0
                            hidden
                            h-full
                            w-px
                            -translate-x-1/2
                            bg-gradient-to-b
                            from-transparent
                            via-slate-800
                            to-transparent
                            lg:block
                        "
                    />

                    <div
                        className="
                            grid
                            grid-cols-1
                            gap-3
                            transition-all
                            duration-500
                            lg:grid-cols-[1fr_auto_1fr]
                            lg:items-center
                            lg:gap-6
                        "
                    >
                        {/* Enemy team */}
                        <div className="order-1">
                            <Team
                                title="Enemy Team"
                                heroes={enemyTeam}
                                onRemove={removeEnemyHero}
                                side="enemy"
                                maxHeroes={MAX_ENEMY_HEROES}
                            />
                        </div>

                        {/* VS */}
                        <div
                            className="
                                order-2
                                flex
                                items-center
                                justify-center
                                py-1
                                lg:py-0
                            "
                        >
                            <div
                                className="
                                    flex
                                    h-10
                                    w-10
                                    items-center
                                    justify-center
                                    rounded-full
                                    border
                                    border-slate-700
                                    bg-slate-950
                                    text-[10px]
                                    font-black
                                    text-slate-500
                                    shadow-xl
                                    transition-all
                                    duration-500
                                    hover:scale-110
                                    hover:border-amber-500/50
                                    hover:text-amber-300
                                    sm:h-12
                                    sm:w-12
                                "
                            >
                                VS
                            </div>
                        </div>

                        {/* Own team */}
                        <div className="order-3">
                            <Team
                                title="Your Team"
                                heroes={ownTeam}
                                onRemove={removeOwnHero}
                                side="own"
                                maxHeroes={MAX_OWN_HEROES}
                            />
                            {!enemyPicksComplete && (
                                <p className="mt-2 text-[10px] text-amber-400/80">
                                    Fill enemy positions in order to unlock your four picks.
                                </p>
                            )}
                        </div>
                    </div>

                    {/* Analyze */}
                    <div
                        className="
                            mt-5
                            flex
                            flex-col
                            items-center
                            justify-center
                            gap-3
                            border-t
                            border-[#39352e]
                            pt-5
                            sm:flex-row
                            lg:mt-6
                            lg:pt-6
                        "
                    >
                        <button
                            type="button"
                            onClick={handleAnalyze}
                            disabled={
                                loading ||
                                loadingRoster ||
                                selectedCount(ownTeam) !== MAX_OWN_HEROES ||
                                !enemyPicksComplete
                            }
                            className="
                                w-full
                                rounded-xl
                                bg-gradient-to-r
                                from-red-700
                                to-red-600
                                px-6
                                py-3
                                text-sm
                                font-bold
                                text-white
                                shadow-lg
                                shadow-red-950/40
                                transition-all
                                duration-300
                                hover:from-red-600
                                hover:to-red-500
                                hover:shadow-red-900/40
                                active:scale-[0.98]
                                disabled:cursor-not-allowed
                                disabled:bg-slate-800
                                disabled:from-slate-800
                                disabled:to-slate-800
                                disabled:text-slate-600
                                disabled:shadow-none
                                disabled:hover:from-slate-800
                                disabled:hover:to-slate-800
                                sm:w-auto
                            "
                        >
                            {loading
                                ? "Analyzing..."
                                : "Analyze Draft"}
                        </button>
                    </div>

                    {error && (
                        <div
                            className="
                                mt-4
                                rounded-xl
                                border
                                border-red-500/20
                                bg-red-500/5
                                px-4
                                py-3
                                text-center
                                text-xs
                                text-red-400
                            "
                        >
                            {error}
                        </div>
                    )}
                </section>
                
                {/* Eligible heroes */}
                <section
                    className="
                        mt-8
                        transition-all
                        duration-500
                        sm:mt-10
                    "
                >
                    {enemyPicksComplete && selectedCount(ownTeam) === MAX_OWN_HEROES ? (
                        <div className="rounded-2xl border border-amber-500/20 bg-amber-500/[0.03] px-4 py-8 text-center">
                            <p className="text-sm font-bold text-slate-200">
                                Your four picks are set · Pos {targetRole?.id.slice(-1)} {targetRole?.name} is the final pick
                            </p>
                            <p className="mt-1 text-xs text-slate-500">
                                {loading
                                    ? "Ranking position-eligible heroes…"
                                    : "Your ranked recommendations are below."}
                            </p>
                        </div>
                    ) : (
                        <HeroGrid
                            heroes={heroes}
                            position={activeSelectionRole}
                            side={activeSelectionSide}
                            selectedHeroes={allSelectedHeroes}
                            minRoleConfidence={roleConfidenceFloor}
                            onSelect={activeSelectionSide === "enemy" ? addEnemyHero : addOwnHero}
                        />
                    )}
                </section>




                {/* Results */}
                <section
                    className="
                        mt-8
                        transition-all
                        duration-500
                        sm:mt-10
                    "
                >
                    <div className="mb-4">
                        <div className="flex items-end justify-between">
                            <div>
                                <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-amber-400">
                                    Analysis
                                </p>

                                <h2 className="mt-1 text-xl font-black text-white sm:text-2xl">
                                    Final pick recommendations
                                </h2>
                                <p className="mt-1 text-[10px] text-slate-500">
                                    {targetRole
                                        ? `Unfilled role: Pos ${targetRole.id.slice(-1)} · ${targetRole.name}`
                                        : "All positions are filled"}
                                </p>
                            </div>

                            {analysis && (
                                <span className="text-[10px] text-slate-600">
                                    {recommendations.length}{" "}
                                    results
                                </span>
                            )}
                        </div>
                        {meta && (
                            <details className="mb-4 rounded-xl border border-slate-800 bg-slate-950/50 p-3">
                                <summary className="cursor-pointer text-xs font-semibold text-slate-400">
                                    Engine v{meta.engine_version} · Patch {meta.game_patch} ·{" "}
                                    {meta.loaded_heroes} heroes · {meta.directed_matchups.toLocaleString()} matchups
                                </summary>
                                <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                                    <div>
                                        <p className="mb-1 text-[9px] font-bold uppercase tracking-wider text-slate-500">
                                            Score component weights
                                        </p>
                                        <div className="space-y-1">
                                            {Object.entries(meta.scoring.component_weights).map(([name, value]) => (
                                                <div key={name} className="flex justify-between text-[10px] capitalize">
                                                    <span className="text-slate-500">{name.replaceAll("_", " ")}</span>
                                                    <span className="text-slate-300">{(value * 100).toFixed(0)}%</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                    <div>
                                        <p className="mb-1 text-[9px] font-bold uppercase tracking-wider text-slate-500">
                                            Lane component weights
                                        </p>
                                        <div className="space-y-1">
                                            {Object.entries(meta.scoring.lane_component_weights).map(([name, value]) => (
                                                <div key={name} className="flex justify-between text-[10px] capitalize">
                                                    <span className="text-slate-500">{name.replaceAll("_", " ")}</span>
                                                    <span className="text-slate-300">{(value * 100).toFixed(0)}%</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                    <div>
                                        <p className="mb-1 text-[9px] font-bold uppercase tracking-wider text-slate-500">
                                            Matchup confidence and phase risk
                                        </p>
                                        <div className="space-y-1 text-[10px] text-slate-400">
                                            <p>Curated: {meta.curated_matchups.toLocaleString()}</p>
                                            <p>Inferred: {meta.inferred_matchups.toLocaleString()}</p>
                                            <p>Role confidence floor: {meta.role_min_confidence}</p>
                                            <p>{meta.scoring.graph_rule_weighting}</p>
                                            {Object.entries(meta.scoring.matchup_confidence_multipliers).map(([name, value]) => (
                                                <p key={`confidence-${name}`}>Matchup {name}: {value}</p>
                                            ))}
                                            {Object.entries(meta.scoring.counter_risk_multipliers).map(([name, value]) => (
                                                <p key={`phase-${name}`} className="capitalize">{name.replaceAll("_", " ")} risk: {value}×</p>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </details>
                        )}
                    </div>

                    {/* Recommendation grid */}
                    {!analysis ? (
                        <div
                            className="
                                flex
                                min-h-64
                                items-center
                                justify-center
                                rounded-2xl
                                border
                                border-dashed
                                border-slate-800
                                bg-slate-950/30
                                px-6
                                text-center
                            "
                        >
                            <div>
                                <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full border border-slate-800 bg-slate-900 text-xl text-slate-600">
                                    +
                                </div>

                                <p className="text-sm font-semibold text-slate-500">
                                    Your final-pick recommendations will appear here
                                </p>

                                <p className="mt-1 text-xs text-slate-700">
                                    Assign four friendly picks to unique positions, then analyze the missing role.
                                </p>
                            </div>
                        </div>
                    ) : recommendations.length === 0 ? (
                        <div className="rounded-2xl border border-slate-800 bg-slate-950/40 p-8 text-center text-sm text-slate-500">
                            No recommendations available for the missing position.
                        </div>
                    ) : (
                        <div
                            key={analysis.targetRole}
                            className="
                                grid
                                grid-cols-2
                                gap-2
                                animate-[fadeUp_350ms_ease-out]
                                sm:grid-cols-3
                                sm:gap-3
                                lg:grid-cols-5
                            "
                        >
                            {recommendations.map(
                                (
                                    recommendation,
                                    index
                                ) => (
                                    <RecommendationCard
                                        key={
                                            recommendation.hero
                                        }
                                        recommendation={
                                            recommendation
                                        }
                                        rank={index + 1}
                                        onHeroProfile={openHeroProfile}
                                    />
                                )
                            )}
                        </div>
                    )}
                </section>
            </div>
            <HeroProfileModal
                {...(profileModal || {})}
                onClose={() => setProfileModal(null)}
            />
        </main>
    );
}