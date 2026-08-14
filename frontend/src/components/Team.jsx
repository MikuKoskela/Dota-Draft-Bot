import HeroCard from "./HeroCard";

export default function Team({
    title,
    heroes,
    onRemove,
    side = "enemy",
}) {
    const isEnemy = side === "enemy";

    const slots = Array.from(
        { length: 5 },
        (_, index) => heroes[index] ?? null
    );

    return (
        <section
            className="
                w-full
                rounded-2xl
                border
                border-slate-800
                bg-slate-950/70
                p-3
                shadow-xl
                backdrop-blur
                transition-all
                duration-500
                sm:p-4
                lg:p-5
            "
        >
            {/* Team header */}
            <div className="mb-3 flex items-center justify-between sm:mb-4">
                <div className="flex items-center gap-2">
                    <span
                        className={`
                            h-2.5
                            w-2.5
                            rounded-full
                            ${
                                isEnemy
                                    ? "bg-red-500 shadow-[0_0_12px_rgba(239,68,68,0.7)]"
                                    : "bg-blue-500 shadow-[0_0_12px_rgba(59,130,246,0.7)]"
                            }
                        `}
                    />

                    <h2 className="text-sm font-bold tracking-wide text-slate-100 sm:text-base">
                        {title}
                    </h2>
                </div>

                <span className="text-xs text-slate-500">
                    {heroes.length}/5
                </span>
            </div>

            {/* Heroes */}
            <div
                className="
                    grid
                    grid-cols-5
                    gap-1.5
                    sm:gap-2
                    lg:gap-3
                "
            >
                {slots.map((hero, index) => (
                    <HeroCard
                        key={`${hero ?? "empty"}-${index}`}
                        hero={hero}
                        onRemove={hero ? onRemove : undefined}
                    />
                ))}
            </div>
        </section>
    );
}