import HeroCard from "./HeroCard";

export default function Team({
    title,
    heroes,
    onRemove,
    enemy = false,
    maxHeroes,
}) {
    const slots = Array.from(
        { length: maxHeroes },
        (_, index) => heroes[index] ?? null
    );

    return (
        <section
            className={`
                relative
                overflow-hidden
                rounded-2xl
                border
                ${
                    enemy
                        ? "border-red-500/50 bg-red-950/[0.08]"
                        : "border-blue-500/50 bg-blue-950/[0.08]"
                }
                p-3
                shadow-2xl
                backdrop-blur-xl
                transition-all
                duration-500
                sm:p-4
                lg:p-5
            `}
        >
            <div
                className={`
                    pointer-events-none
                    absolute
                    -top-20
                    ${
                        enemy
                            ? "-left-20 bg-red-500/10"
                            : "-right-20 bg-blue-500/10"
                    }
                    h-40
                    w-40
                    rounded-full
                    blur-3xl
                `}
            />

            <div className="relative mb-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div
                        className={`
                            flex
                            h-8
                            w-8
                            items-center
                            justify-center
                            rounded-lg
                            ${
                                enemy
                                    ? "bg-red-500/10 text-red-400"
                                    : "bg-blue-500/10 text-blue-400"
                            }
                        `}
                    >
                        {enemy ? "⚔" : "🛡"}
                    </div>

                    <div>
                        <h2 className="text-sm font-black uppercase tracking-wider text-white sm:text-base">
                            {title}
                        </h2>

                        <p className="text-[9px] text-slate-600">
                            {enemy
                                ? "Opposing lineup"
                                : "Your lineup"}
                        </p>
                    </div>
                </div>

                <span
                    className={`
                        text-xs
                        font-black
                        ${
                            enemy
                                ? "text-red-400"
                                : "text-blue-400"
                        }
                    `}
                >
                    {heroes.length} / {maxHeroes}
                </span>
            </div>

            <div
                className={`
                    relative
                    grid
                    gap-1.5
                    sm:gap-2
                    ${
                        maxHeroes === 4
                            ? "grid-cols-4"
                            : "grid-cols-5"
                    }
                `}
            >
                {slots.map((hero, index) => (
                    <HeroCard
                        key={`${hero ?? "empty"}-${index}`}
                        hero={hero}
                        enemy={enemy}
                        onRemove={
                            hero
                                ? onRemove
                                : undefined
                        }
                    />
                ))}
            </div>
        </section>
    );
}