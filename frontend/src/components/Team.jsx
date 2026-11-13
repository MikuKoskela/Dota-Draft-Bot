import HeroCard from "./HeroCard";

const positions = [
    ["pos1", "POS 1"],
    ["pos2", "POS 2"],
    ["pos3", "POS 3"],
    ["pos4", "POS 4"],
    ["pos5", "POS 5"],
];

export default function Team({
    title,
    heroes,
    onRemove,
    onSelectPosition,
    selectedPosition,
    side = "own",
    maxHeroes,
}) {
    const enemy = side === "enemy";
    const count = Object.values(heroes).filter(Boolean).length;

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
                        : "border-emerald-500/40 bg-emerald-950/[0.10]"
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
                            : "-right-20 bg-emerald-500/10"
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
                                    : "bg-emerald-500/10 text-emerald-300"
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
                            Click an open position to choose a hero
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
                                : "text-emerald-300"
                        }
                    `}
                >
                    {count} / {maxHeroes}
                </span>
            </div>

            <div
                className={`
                    relative
                    grid
                    gap-1.5
                    sm:gap-2
                    grid-cols-6
                `}
            >
                {positions.map(([role, label], index) => {
                    const hero = heroes[role];
                    const canSelect = !hero && count < maxHeroes;
                    const isFinalPick = !enemy && !hero && !canSelect;
                    const rowAlignment = enemy
                        ? index === 3
                            ? "col-start-2"
                            : index === 4
                                ? "col-start-4"
                                : ""
                        : index === 3
                            ? "col-start-3"
                            : "";
                    const content = (
                        <>
                            <p className="mb-1 text-center text-[8px] font-bold tracking-wide text-slate-500 sm:text-[9px]">
                                {label}
                                {isFinalPick && (
                                    <span className="ml-1 text-amber-400">FINAL</span>
                                )}
                            </p>
                            <HeroCard
                                hero={hero}
                                onRemove={hero ? onRemove : undefined}
                                emptyLabel={isFinalPick ? "Final pick" : "Choose hero"}
                            />
                        </>
                    );

                    return (
                        <div key={role} className={`col-span-2 min-w-0 ${rowAlignment}`}>
                            {canSelect ? (
                                <button
                                    type="button"
                                    onClick={() => onSelectPosition?.(role)}
                                    aria-label={`Choose ${label} for ${enemy ? "enemy team" : "your team"}`}
                                    aria-pressed={selectedPosition === role}
                                    className={`block w-full rounded-lg text-left outline-none transition focus-visible:ring-2 focus-visible:ring-amber-400 ${
                                        selectedPosition === role
                                            ? "ring-2 ring-amber-400"
                                            : "hover:ring-1 hover:ring-slate-500"
                                    }`}
                                >
                                    {content}
                                </button>
                            ) : (
                                <div>{content}</div>
                            )}
                        </div>
                    );
                })}
            </div>
        </section>
    );
}