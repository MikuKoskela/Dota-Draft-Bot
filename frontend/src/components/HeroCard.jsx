export default function HeroCard({
    hero,
    variant = "default",
    onRemove,
    onSelect,
}) {
    const isEmpty = !hero;

    if (isEmpty) {
        return (
            <div
                className="
                    relative
                    aspect-[3/4]
                    w-full
                    overflow-hidden
                    rounded-lg
                    border
                    border-dashed
                    border-slate-700
                    bg-slate-900/60
                    transition-all
                    duration-300
                    hover:border-slate-500
                    hover:bg-slate-800/70
                "
            >
                <div className="flex h-full flex-col items-center justify-center gap-2 p-3 text-center">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full border border-slate-700 bg-slate-800 text-xl text-slate-500">
                        +
                    </div>

                    <span className="text-xs font-medium text-slate-500">
                        Empty slot
                    </span>
                </div>
            </div>
        );
    }

    const isRecommendation = variant === "recommendation";

    return (
        <div
            className={`
                group
                relative
                aspect-[3/4]
                w-full
                overflow-hidden
                rounded-lg
                border
                bg-slate-900
                shadow-lg
                transition-all
                duration-300
                ease-out
                hover:-translate-y-1
                hover:scale-[1.02]
                hover:shadow-2xl
                ${
                    isRecommendation
                        ? "border-blue-500/30 hover:border-blue-400/70"
                        : "border-slate-700 hover:border-slate-500"
                }
            `}
        >
            {/* Placeholder hero image */}
            <div
                className="
                    absolute
                    inset-0
                    flex
                    items-center
                    justify-center
                    bg-gradient-to-br
                    from-slate-700
                    via-slate-800
                    to-slate-950
                "
            >
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_30%,rgba(59,130,246,0.22),transparent_45%)]" />

                <div className="relative px-2 text-center">
                    <div className="mb-2 text-[10px] uppercase tracking-[0.2em] text-slate-500">
                        Hero image
                    </div>

                    <div className="text-sm font-bold text-slate-200 sm:text-base">
                        {hero}
                    </div>
                </div>
            </div>

            {/* Bottom gradient */}
            <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-black/90 to-transparent" />

            {/* Hero name */}
            <div className="absolute inset-x-0 bottom-0 p-2 sm:p-3">
                <p className="truncate text-xs font-bold text-white sm:text-sm">
                    {hero}
                </p>
            </div>

            {/* Remove button */}
            {onRemove && (
                <button
                    type="button"
                    onClick={() => onRemove(hero)}
                    className="
                        absolute
                        right-1.5
                        top-1.5
                        flex
                        h-7
                        w-7
                        items-center
                        justify-center
                        rounded-full
                        bg-black/60
                        text-xs
                        text-slate-300
                        opacity-100
                        backdrop-blur
                        transition-all
                        duration-200
                        hover:bg-red-500/80
                        hover:text-white
                        sm:opacity-0
                        sm:group-hover:opacity-100
                    "
                    aria-label={`Remove ${hero}`}
                >
                    ×
                </button>
            )}

            {/* Recommendation score */}
            {isRecommendation && (
                <div className="absolute left-2 top-2 rounded-md border border-blue-400/20 bg-black/60 px-2 py-1 text-[10px] font-semibold text-blue-300 backdrop-blur">
                    Recommended
                </div>
            )}

            {onSelect && (
                <button
                    type="button"
                    onClick={() => onSelect(hero)}
                    className="absolute inset-0 cursor-pointer"
                    aria-label={`Select ${hero}`}
                />
            )}
        </div>
    );
}