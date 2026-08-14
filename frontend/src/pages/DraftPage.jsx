import { useMemo, useState } from "react";

import HeroSearch from "../components/HeroSearch";
import Team from "../components/Team";
import RecommendationCard from "../components/RecommendationCard";

import { analyzeDraft } from "../services/api";

const positions = [
    {
        id: "1",
        name: "Carry",
        short: "POS 1",
    },
    {
        id: "2",
        name: "Mid",
        short: "POS 2",
    },
    {
        id: "3",
        name: "Offlane",
        short: "POS 3",
    },
    {
        id: "4",
        name: "Soft Support",
        short: "POS 4",
    },
    {
        id: "5",
        name: "Hard Support",
        short: "POS 5",
    },
];

export default function DraftPage() {
    const [enemyTeam, setEnemyTeam] = useState([]);
    const [ownTeam, setOwnTeam] = useState([]);

    const [analysis, setAnalysis] = useState(null);

    const [activePosition, setActivePosition] =
        useState("general");

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const allSelectedHeroes = useMemo(
        () => [...enemyTeam, ...ownTeam],
        [enemyTeam, ownTeam]
    );

    function addEnemyHero(hero) {
        if (enemyTeam.length >= 5) return;

        if (allSelectedHeroes.includes(hero)) {
            return;
        }

        setEnemyTeam((current) => [
            ...current,
            hero,
        ]);

        setAnalysis(null);
    }

    function addOwnHero(hero) {
        if (ownTeam.length >= 5) return;

        if (allSelectedHeroes.includes(hero)) {
            return;
        }

        setOwnTeam((current) => [
            ...current,
            hero,
        ]);

        setAnalysis(null);
    }

    function removeEnemyHero(hero) {
        setEnemyTeam((current) =>
            current.filter(
                (currentHero) => currentHero !== hero
            )
        );

        setAnalysis(null);
    }

    function removeOwnHero(hero) {
        setOwnTeam((current) =>
            current.filter(
                (currentHero) => currentHero !== hero
            )
        );

        setAnalysis(null);
    }

    function resetDraft() {
        setEnemyTeam([]);
        setOwnTeam([]);
        setAnalysis(null);
        setError("");
        setActivePosition("general");
    }

    async function handleAnalyze() {
        if (enemyTeam.length === 0) {
            setError(
                "Add at least one enemy hero before analyzing."
            );

            return;
        }

        try {
            setLoading(true);
            setError("");

            const result = await analyzeDraft(
                enemyTeam,
                ownTeam
            );

            setAnalysis(result);
            setActivePosition("general");
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

    const recommendations =
        activePosition === "general"
            ? analysis?.recommendations?.general ?? []
            : analysis?.recommendations?.positions?.[
                  activePosition
              ] ?? [];

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
                                    bg-blue-600
                                    text-sm
                                    font-black
                                    shadow-lg
                                    shadow-blue-900/30
                                "
                            >
                                D
                            </div>

                            <h1 className="text-sm font-bold tracking-wide text-white sm:text-base">
                                DRAFT ASSISTANT
                            </h1>
                        </div>

                        <p className="mt-0.5 hidden text-[10px] text-slate-500 sm:block">
                            Dota 2 Position Draft Analyzer
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
                    <p className="mb-2 text-[10px] font-bold uppercase tracking-[0.25em] text-blue-400">
                        Draft phase
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
                        Select the enemy lineup and your
                        current team. The analyzer will
                        calculate matchup, counter, role
                        and synergy scores.
                    </p>
                </section>

                {/* Draft arena */}
                <section
                    className="
                        relative
                        rounded-3xl
                        border
                        border-slate-800
                        bg-slate-900/30
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
                            />

                            <div className="mt-3">
                                <HeroSearch
                                    selectedHeroes={
                                        allSelectedHeroes
                                    }
                                    onSelect={
                                        addEnemyHero
                                    }
                                    disabled={
                                        enemyTeam.length >=
                                        5
                                    }
                                />
                            </div>
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
                                    hover:border-blue-500/50
                                    hover:text-blue-400
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
                            />

                            <div className="mt-3">
                                <HeroSearch
                                    selectedHeroes={
                                        allSelectedHeroes
                                    }
                                    onSelect={addOwnHero}
                                    disabled={
                                        ownTeam.length >=
                                        5
                                    }
                                />
                            </div>
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
                            border-slate-800
                            pt-5
                            sm:flex-row
                            lg:mt-6
                            lg:pt-6
                        "
                    >
                        <div className="text-center sm:text-left">
                            <p className="text-xs font-semibold text-slate-300">
                                Ready to analyze?
                            </p>

                            <p className="mt-1 text-[10px] text-slate-600">
                                {enemyTeam.length}/5
                                enemy picks ·{" "}
                                {ownTeam.length}/5
                                friendly picks
                            </p>
                        </div>

                        <button
                            type="button"
                            onClick={handleAnalyze}
                            disabled={
                                loading ||
                                enemyTeam.length === 0
                            }
                            className="
                                w-full
                                rounded-xl
                                bg-blue-600
                                px-6
                                py-3
                                text-sm
                                font-bold
                                text-white
                                shadow-lg
                                shadow-blue-950/30
                                transition-all
                                duration-300
                                hover:bg-blue-500
                                hover:shadow-blue-900/40
                                active:scale-[0.98]
                                disabled:cursor-not-allowed
                                disabled:bg-slate-800
                                disabled:text-slate-600
                                disabled:shadow-none
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
                                <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-blue-400">
                                    Analysis
                                </p>

                                <h2 className="mt-1 text-xl font-black text-white sm:text-2xl">
                                    Recommended picks
                                </h2>
                            </div>

                            {analysis && (
                                <span className="text-[10px] text-slate-600">
                                    {recommendations.length}{" "}
                                    results
                                </span>
                            )}
                        </div>
                    </div>

                    {/* Position navigation */}
                    <div
                        className="
                            mb-4
                            flex
                            gap-2
                            overflow-x-auto
                            pb-1
                        "
                    >
                        <button
                            type="button"
                            onClick={() =>
                                setActivePosition(
                                    "general"
                                )
                            }
                            className={`
                                shrink-0
                                rounded-lg
                                px-3
                                py-2
                                text-xs
                                font-semibold
                                transition-all
                                duration-300
                                ${
                                    activePosition ===
                                    "general"
                                        ? "bg-blue-600 text-white shadow-lg shadow-blue-950/30"
                                        : "border border-slate-800 bg-slate-900 text-slate-500 hover:text-slate-200"
                                }
                            `}
                        >
                            Top Picks
                        </button>

                        {positions.map((position) => (
                            <button
                                key={position.id}
                                type="button"
                                onClick={() =>
                                    setActivePosition(
                                        position.id
                                    )
                                }
                                className={`
                                    shrink-0
                                    rounded-lg
                                    px-3
                                    py-2
                                    text-xs
                                    font-semibold
                                    transition-all
                                    duration-300
                                    ${
                                        activePosition ===
                                        position.id
                                            ? "bg-blue-600 text-white shadow-lg shadow-blue-950/30"
                                            : "border border-slate-800 bg-slate-900 text-slate-500 hover:text-slate-200"
                                    }
                                `}
                            >
                                <span className="sm:hidden">
                                    {position.short}
                                </span>

                                <span className="hidden sm:inline">
                                    {position.name}
                                </span>
                            </button>
                        ))}
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
                                    Your recommendations
                                    will appear here
                                </p>

                                <p className="mt-1 text-xs text-slate-700">
                                    Add enemy heroes and
                                    analyze the draft.
                                </p>
                            </div>
                        </div>
                    ) : recommendations.length === 0 ? (
                        <div className="rounded-2xl border border-slate-800 bg-slate-950/40 p-8 text-center text-sm text-slate-500">
                            No recommendations available
                            for this position.
                        </div>
                    ) : (
                        <div
                            key={activePosition}
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
                                    />
                                )
                            )}
                        </div>
                    )}
                </section>
            </div>
        </main>
    );
}