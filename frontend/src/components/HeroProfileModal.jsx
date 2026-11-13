function Section({ title, children }) {
    return (
        <section className="rounded-xl border border-slate-800 bg-slate-900/70 p-3">
            <h3 className="mb-2 text-[10px] font-bold uppercase tracking-wider text-amber-300">
                {title}
            </h3>
            {children}
        </section>
    );
}

export default function HeroProfileModal({ hero, profile, loading, error, onClose }) {
    if (!hero) return null;

    return (
        <div
            className="fixed inset-0 z-[70] flex items-center justify-center bg-black/75 p-3 backdrop-blur-sm"
            onMouseDown={(event) => {
                if (event.target === event.currentTarget) onClose();
            }}
        >
            <div
                role="dialog"
                aria-modal="true"
                aria-label={`${hero} profile`}
                className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-2xl border border-slate-700 bg-slate-950 p-4 shadow-2xl sm:p-6"
            >
                <div className="mb-4 flex items-start justify-between gap-4">
                    <div>
                        <p className="text-[9px] font-bold uppercase tracking-[0.2em] text-amber-400">
                            Hero profile
                        </p>
                        <h2 className="mt-1 text-xl font-black text-white">{hero}</h2>
                        {profile && (
                            <p className="mt-1 text-[10px] text-slate-500">
                                {profile.primary_attribute} · {profile.attack_type} ·{" "}
                                {profile.data_quality} · profile confidence{" "}
                                {Math.round(profile.profile_confidence * 100)}%
                            </p>
                        )}
                    </div>
                    <button
                        type="button"
                        onClick={onClose}
                        className="rounded-lg border border-slate-700 px-3 py-1 text-sm text-slate-400 hover:text-white"
                        aria-label="Close profile"
                    >
                        ×
                    </button>
                </div>

                {loading && <p className="py-12 text-center text-sm text-slate-500">Loading profile…</p>}
                {error && <p className="rounded-lg bg-red-500/10 p-3 text-sm text-red-300">{error}</p>}

                {profile && !loading && (
                    <div className="grid gap-3 sm:grid-cols-2">
                        <Section title="Roles">
                            <div className="space-y-1">
                                {Object.entries(profile.roles || {}).map(([role, value]) => (
                                    <div key={role} className="flex justify-between text-xs capitalize">
                                        <span className="text-slate-400">{role.replace("pos", "Pos ")}</span>
                                        <span className="text-slate-200">{Math.round(value * 100)}%</span>
                                    </div>
                                ))}
                            </div>
                        </Section>
                        <Section title="Stats and power spikes">
                            <div className="space-y-1">
                                {Object.entries(profile.base_stats || {}).map(([key, value]) => (
                                    <div key={key} className="flex justify-between gap-2 text-[10px]">
                                        <span className="capitalize text-slate-500">{key.replaceAll("_", " ")}</span>
                                        <span className="text-slate-300">{String(value)}</span>
                                    </div>
                                ))}
                            </div>
                            <div className="mt-2 flex flex-wrap gap-2 border-t border-slate-800 pt-2 text-[10px] text-slate-400">
                                {Object.entries(profile.power_spikes || {}).map(([phase, value]) => (
                                    <span key={phase} className="capitalize">
                                        {phase}: {Number(value).toFixed(2)}
                                    </span>
                                ))}
                            </div>
                        </Section>
                        <Section title="12-part lane profile">
                            <div className="grid grid-cols-2 gap-x-3 gap-y-1">
                                {Object.entries(profile.lane_profile || {}).map(([key, value]) => (
                                    <div key={key} className="flex justify-between gap-1 text-[10px]">
                                        <span className="capitalize text-slate-500">{key.replaceAll("_", " ")}</span>
                                        <span className="text-slate-300">{Number(value).toFixed(2)}</span>
                                    </div>
                                ))}
                            </div>
                        </Section>
                        <Section title="Tags and weaknesses">
                            <p className="text-xs leading-relaxed text-slate-300">
                                {(profile.tags || []).join(" · ") || "No tags"}
                            </p>
                            <p className="mt-2 text-[10px] leading-relaxed text-slate-500">
                                Weak to: {(profile.weaknesses || []).join(" · ") || "No listed weaknesses"}
                            </p>
                            <details className="mt-2 border-t border-slate-800 pt-2">
                                <summary className="cursor-pointer text-[10px] text-slate-500">
                                    Weighted evidence
                                </summary>
                                <div className="mt-2 space-y-1 text-[10px]">
                                    {Object.entries(profile.tag_weights || {}).map(([tag, value]) => (
                                        <div key={tag} className="flex justify-between capitalize">
                                            <span className="text-slate-500">{tag.replaceAll("_", " ")}</span>
                                            <span className="text-slate-300">{Number(value).toFixed(2)}</span>
                                        </div>
                                    ))}
                                    {Object.entries(profile.weakness_weights || {}).map(([weakness, value]) => (
                                        <div key={weakness} className="flex justify-between capitalize">
                                            <span className="text-amber-500/70">{weakness.replaceAll("_", " ")}</span>
                                            <span className="text-slate-300">{Number(value).toFixed(2)}</span>
                                        </div>
                                    ))}
                                </div>
                            </details>
                        </Section>
                        <Section title="Abilities">
                            <div className="space-y-2">
                                {(profile.abilities || []).map((ability) => (
                                    <div key={ability.name}>
                                        <p className="text-xs font-semibold text-slate-200">
                                            {ability.display_name}
                                            {ability.availability !== "base_kit" && (
                                                <span className="ml-1 text-[9px] text-amber-400">
                                                    {ability.availability.replaceAll("_", " ")}
                                                </span>
                                            )}
                                        </p>
                                        <p className="text-[10px] leading-relaxed text-slate-500">
                                            {ability.description}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </Section>
                        <Section title="Talents and facets">
                            <div className="space-y-2">
                                {(profile.talents || []).map((talent) => (
                                    <p key={talent.name} className="text-[10px] text-slate-300">
                                        {talent.description}
                                    </p>
                                ))}
                                {(profile.facets || []).map((facet) => (
                                    <div key={facet.name}>
                                        <p className="text-xs font-semibold text-slate-200">
                                            {facet.title || facet.name}
                                        </p>
                                        <p className="text-[10px] leading-relaxed text-slate-500">
                                            {facet.description}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </Section>
                        <Section title="Aghanim upgrades">
                            <div className="space-y-2 text-[10px] leading-relaxed text-slate-400">
                                <p><strong className="text-slate-200">Scepter:</strong> {profile.aghanim?.scepter_description || "No upgrade listed"}</p>
                                <p><strong className="text-slate-200">Shard:</strong> {profile.aghanim?.shard_description || "No upgrade listed"}</p>
                            </div>
                        </Section>
                        <Section title="Team contribution and item dependencies">
                            <div className="space-y-1 text-[10px] text-slate-400">
                                {Object.entries(profile.team_contributions || {}).map(([key, value]) => (
                                    <span key={key} className="mr-2 inline-block capitalize">
                                        {key.replaceAll("_", " ")} {Number(value).toFixed(2)}
                                    </span>
                                ))}
                            </div>
                            <div className="mt-2 space-y-1 text-[10px] text-slate-500">
                                {Object.entries(profile.item_profile || {}).map(([key, value]) => (
                                    <div key={key} className="flex justify-between gap-2">
                                        <span className="capitalize">{key.replaceAll("_", " ")}</span>
                                        <span>{Number(value).toFixed(2)}</span>
                                    </div>
                                ))}
                            </div>
                        </Section>
                        <Section title="Profile sources">
                            <details>
                                <summary className="cursor-pointer text-[10px] text-slate-500">
                                    View source metadata
                                </summary>
                                <pre className="mt-2 overflow-x-auto whitespace-pre-wrap text-[9px] leading-relaxed text-slate-500">
                                    {JSON.stringify(profile.profile_sources, null, 2)}
                                </pre>
                            </details>
                        </Section>
                    </div>
                )}
            </div>
        </div>
    );
}
