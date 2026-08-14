import HeroCard from "./HeroCard";

const positionNames = {
    1: "Carry",
    2: "Mid",
    3: "Offlane",
    4: "Soft Support",
    5: "Hard Support",
};

function ScoreBar({ label, value }) {
    const normalized = Math.max(
        0,
        Math.min(100, ((value + 1) / 2) * 100)
    );

    return (
        <div className="space-y-1">
            <div className="flex justify-between text-[10px]">
                <span className="text-slate-500">
                    {label}
                </span>

                <span className="text-slate-400">
                    {Number(value).toFixed(2)}
                </span>
            </div>

            <div className="h-1 overflow-hidden rounded-full bg-slate-800">
                <div
                    className="h-full rounded-full bg-blue-500 transition-all duration-700"
                    style={{
                        width: `${normalized}%`,
                    }}
                />
            </div>
        </div>
    );
}

export default function RecommendationCard({
    recommendation,
    rank,
}) {
    const {
        hero,
        position,
        position_name,
        score,
    } = recommendation;

    return (
        <article
            className="
                group
                rounded-xl
                border
                border-slate-800
                bg-slate-950
                p-2
                shadow-lg
                transition-all
                duration-300
                hover:-translate-y-1
                hover:border-blue-500/40
                hover:shadow-blue-950/20
                sm:p-3
            "
        >
            <div className="mb-2 flex items-center justify-between">
                <span className="text-xs font-bold text-slate-500">
                    #{rank}
                </span>

                <span className="rounded-md bg-blue-500/10 px-2 py-1 text-[9px] font-semibold text-blue-400">
                    {position_name ||
                        positionNames[position]}
                </span>
            </div>

            <HeroCard
                hero={hero}
                variant="recommendation"
            />

            <div className="mt-3 space-y-2">
                <div>
                    <p className="text-sm font-bold text-white">
                        {hero}
                    </p>

                    <p className="text-[10px] text-slate-500">
                        {positionNames[position]}
                    </p>
                </div>

                <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-2">
                    <div className="mb-2 flex items-center justify-between">
                        <span className="text-[10px] uppercase tracking-wider text-slate-500">
                            Total
                        </span>

                        <span className="text-sm font-bold text-blue-400">
                            {score.total}
                        </span>
                    </div>

                    <div className="space-y-2">
                        <ScoreBar
                            label="Matchup"
                            value={score.matchup}
                        />

                        <ScoreBar
                            label="Counter"
                            value={score.counter}
                        />

                        <ScoreBar
                            label="Role"
                            value={score.role}
                        />

                        <ScoreBar
                            label="Synergy"
                            value={score.synergy}
                        />
                    </div>
                </div>
            </div>
        </article>
    );
}