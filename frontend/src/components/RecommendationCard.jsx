import HeroCard from "./HeroCard";

function labelFor(value) {
    return value.replaceAll("_", " ");
}

function ScoreBar({ label, value }) {
    const normalized = Math.max(0, Math.min(100, Number(value) || 0));
    return (
        <div className="space-y-1">
            <div className="flex justify-between gap-2 text-[10px] capitalize">
                <span className="text-slate-500">{labelFor(label)}</span>
                <span className="text-slate-400">{normalized.toFixed(1)}</span>
            </div>
            <div className="h-1 overflow-hidden rounded-full bg-slate-800">
                <div
                    className="h-full rounded-full bg-amber-500 transition-all duration-700"
                    style={{ width: `${normalized}%` }}
                />
            </div>
        </div>
    );
}

export default function RecommendationCard({
    recommendation,
    rank,
    onHeroProfile,
}) {
    const {
        hero,
        position_name: positionName,
        score,
        component_scores: componentScores = {},
        breakdown = {},
        matchup_details: matchupDetails = [],
    } = recommendation;

    return (
        <article className="group rounded-xl border border-[#39352e] bg-[#111213] p-2 shadow-lg transition-all duration-300 hover:-translate-y-1 hover:border-amber-500/40 hover:shadow-amber-950/20 sm:p-3">
            <div className="mb-2 flex items-center justify-between">
                <span className="text-xs font-bold text-slate-500">#{rank}</span>
                <span className="rounded-md bg-amber-500/10 px-2 py-1 text-[9px] font-semibold text-amber-300">
                    {positionName}
                </span>
            </div>

            <HeroCard hero={hero} variant="recommendation" />

            <div className="mt-3 space-y-2">
                <div>
                    <p className="text-sm font-bold text-white">{hero}</p>
                    <p className="text-[10px] text-slate-500">
                        {recommendation.data_quality} · matchup confidence{" "}
                        {Math.round(recommendation.matchup_confidence * 100)}%
                    </p>
                </div>

                <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-2">
                    <div className="mb-2 flex items-center justify-between">
                        <span className="text-[10px] uppercase tracking-wider text-slate-500">
                            Draft score
                        </span>
                        <span className="text-sm font-bold text-amber-300">
                            {Number(score).toFixed(1)}
                        </span>
                    </div>
                    <div className="space-y-2">
                        {Object.entries(componentScores).map(([name, value]) => (
                            <ScoreBar key={name} label={name} value={value} />
                        ))}
                    </div>
                </div>

                <button
                    type="button"
                    onClick={() => onHeroProfile(hero)}
                    className="w-full rounded-lg border border-slate-800 px-2 py-2 text-[10px] font-semibold text-slate-400 transition hover:border-amber-500/40 hover:text-amber-300"
                >
                    Hero profile and matchups
                </button>

                <details className="rounded-lg border border-slate-800 bg-slate-900/40 p-2">
                    <summary className="cursor-pointer text-[10px] font-semibold text-slate-400">
                        Score breakdown · raw {Number(recommendation.raw_score).toFixed(1)}
                    </summary>
                    <p className="mt-2 text-[10px] leading-relaxed text-slate-400">
                        {recommendation.explanation}
                    </p>
                    <div className="mt-2 space-y-1">
                        {Object.entries(breakdown).map(([name, value]) => (
                            <div key={name} className="flex justify-between gap-2 text-[10px]">
                                <span className="capitalize text-slate-500">{labelFor(name)}</span>
                                <span className="text-slate-300">{Number(value).toFixed(1)}</span>
                            </div>
                        ))}
                    </div>
                    {matchupDetails.length > 0 && (
                        <div className="mt-3 border-t border-slate-800 pt-2">
                            <p className="mb-2 text-[9px] font-bold uppercase tracking-wider text-slate-500">
                                Matchup detail
                            </p>
                            <div className="space-y-2">
                                {matchupDetails.map((matchup) => (
                                    <div key={matchup.enemy} className="text-[10px]">
                                        <div className="flex justify-between gap-2">
                                            <span className="text-slate-300">{matchup.enemy}</span>
                                            <span className="text-amber-300">
                                                {matchup.score.toFixed(1)} · {matchup.source} ·{" "}
                                                {Math.round(matchup.confidence * 100)}%
                                            </span>
                                        </div>
                                        {matchup.reasons?.length > 0 && (
                                            <p className="mt-0.5 leading-relaxed text-slate-600">
                                                {matchup.reasons.join("; ")}
                                            </p>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                    {recommendation.knowledge_graph_reasons?.length > 0 && (
                        <p className="mt-3 border-t border-slate-800 pt-2 text-[10px] leading-relaxed text-slate-500">
                            {recommendation.knowledge_graph_reasons.join("; ")}
                        </p>
                    )}
                </details>
            </div>
        </article>
    );
}
