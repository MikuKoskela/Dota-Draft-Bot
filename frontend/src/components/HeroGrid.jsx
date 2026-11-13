import { Plus } from "lucide-react";
import { heroData } from "../data/heroData.Js";

const heroImages = new Map(
    Object.values(heroData).map((hero) => [hero.displayName, hero.image])
);

const positionNames = {
    pos1: "Carry",
    pos2: "Mid",
    pos3: "Offlane",
    pos4: "Soft Support",
    pos5: "Hard Support",
};

export default function HeroGrid({
    heroes = [],
    position,
    side,
    selectedHeroes = [],
    minRoleConfidence = 0.45,
    onSelect,
}) {
    const sideLabel = side === "enemy" ? "Enemy" : "Your team";
    const sideAccent = side === "enemy"
        ? {
            border: "hover:border-red-500/60",
            shadow: "hover:shadow-red-950/30",
            text: "text-red-300",
            button: "bg-red-700",
        }
        : {
            border: "hover:border-emerald-500/60",
            shadow: "hover:shadow-emerald-950/30",
            text: "text-emerald-300",
            button: "bg-emerald-700",
        };
    const eligibleHeroes = heroes
        .filter(
            (hero) =>
                position
                && (hero.roles?.[position] ?? 0) >= minRoleConfidence
                && !selectedHeroes.includes(hero.name)
        )
        .sort(
            (heroA, heroB) =>
                (heroB.roles?.[position] ?? 0) - (heroA.roles?.[position] ?? 0)
        );

    return (
        <section className="rounded-2xl border border-[#39352e] bg-[#111213]/75 p-3 pb-4">
            <div className="flex flex-col items-center justify-center gap-1 p-4 text-center">
                <h2 className="border-b border-amber-600 pb-1 text-xl font-black tracking-tight text-white sm:text-2xl">
                    {position
                        ? `Pos ${position.slice(-1)} · ${positionNames[position]} heroes`
                        : "Choose a position"}
                </h2>
                <p className="text-[10px] text-slate-500">
                    {position
                        ? `${eligibleHeroes.length} heroes with at least ${Math.round(minRoleConfidence * 100)}% role fit · specialists first`
                        : "Click an empty position on either team to browse heroes for that role"}
                </p>
            </div>

            {eligibleHeroes.length > 0 ? (
                <div className="grid grid-cols-3 gap-2 sm:grid-cols-5 md:grid-cols-6 lg:grid-cols-7 xl:grid-cols-8">
                    {eligibleHeroes.map((hero) => (
                        <button
                            key={hero.name}
                            type="button"
                            onClick={() => onSelect(hero.name)}
                            className={`group relative overflow-hidden rounded-xl border border-slate-700/70 bg-slate-950 text-left shadow-sm transition hover:-translate-y-0.5 ${sideAccent.border} hover:shadow-lg ${sideAccent.shadow}`}
                            aria-label={`Add ${hero.name} to ${sideLabel} at ${positionNames[position]}`}
                        >
                            {heroImages.has(hero.name) ? (
                                <img
                                    src={heroImages.get(hero.name)}
                                    alt=""
                                    className="aspect-video w-full bg-slate-800 object-cover"
                                />
                            ) : (
                                <div className="flex aspect-video items-center justify-center bg-slate-800 text-xs text-slate-400">
                                    {hero.name}
                                </div>
                            )}
                            <span className="block truncate px-2 py-1.5 text-[9px] font-semibold text-slate-300 sm:text-[10px]">
                                {hero.name}
                            </span>
                            <span className={`block px-2 pb-1.5 text-[9px] ${sideAccent.text}`}>
                                {Math.round((hero.roles?.[position] ?? 0) * 100)}% {sideLabel} role fit
                            </span>
                            <span className={`absolute right-1 top-1 flex h-5 w-5 items-center justify-center rounded-full ${sideAccent.button} text-white opacity-0 transition group-hover:opacity-100`}>
                                <Plus size={12} />
                            </span>
                        </button>
                    ))}
                </div>
            ) : (
                <div className="rounded-xl border border-dashed border-slate-800 px-4 py-10 text-center text-xs text-slate-500">
                    {position
                        ? `No unpicked heroes meet the role-confidence threshold for ${positionNames[position]}.`
                        : "Choose an empty position on either team to see eligible heroes."}
                </div>
            )}
        </section>
    );
}
