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
    side = "own",
    maxHeroes,
}) {
    const enemy = side === "enemy";
    const count = Object.values(heroes).filter(Boolean).length;
    const occupiedPositions = positions.filter(([role]) => heroes[role]);
    const emptyPositions = positions
        .filter(([role]) => !heroes[role])
        .slice(0, Math.max(0, maxHeroes - count));
    const visiblePositions = (enemy
        ? positions
        : [...occupiedPositions, ...emptyPositions].sort(
            ([roleA], [roleB]) =>
                positions.findIndex(([role]) => role === roleA)
                - positions.findIndex(([role]) => role === roleB)
        ));

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
                            {enemy
                                ? "Opposing lineup"
                                : "Four picks · fifth is your recommendation"}
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
                {visiblePositions.map(([role, label], index) => {
                    const hero = heroes[role];
                    const rowAlignment = enemy
                        ? index === 3
                            ? "col-start-2"
                            : index === 4
                                ? "col-start-4"
                                : ""
                        : index === 3
                            ? "col-start-3"
                            : "";
                    return (
                        <div key={role} className={`col-span-2 min-w-0 ${rowAlignment}`}>
                            <p className="mb-1 text-center text-[8px] font-bold tracking-wide text-slate-500 sm:text-[9px]">
                                {label}
                            </p>
                            <HeroCard
                                hero={hero}
                                enemy={enemy}
                                onRemove={hero ? onRemove : undefined}
                            />
                        </div>
                    );
                })}
            </div>
        </section>
    );
}