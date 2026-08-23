import { useEffect, useRef, useState } from "react";
import { searchHeroes } from "../api/api";

export default function HeroSearch({
    selectedHeroes = [],
    onSelect,
    disabled = false,
}) {
    const [query, setQuery] = useState("");
    const [suggestions, setSuggestions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const inputRef = useRef(null);

    useEffect(() => {
        if (!query.trim()) {
            setSuggestions([]);
            setError("");
            return;
        }

        const timeout = setTimeout(async () => {
            try {
                setLoading(true);
                setError("");

                const data = await searchHeroes(query);

                const heroIds = data.heroes.map((hero) =>
                typeof hero === "string"
                    ? hero
                    : hero.name
                );  
                const filtered = heroIds.filter(
                    (heroId) => !selectedHeroes.includes(heroId)
                );

setSuggestions(filtered);

                setSuggestions(filtered);
            } catch (err) {
                console.error(err);
                setError("Could not search heroes.");
                setSuggestions([]);
            } finally {
                setLoading(false);
            }
        }, 250);

        return () => clearTimeout(timeout);
    }, [query, selectedHeroes]);

    function handleSelect(hero) {
        onSelect(hero);
        setQuery("");
        setSuggestions([]);

        requestAnimationFrame(() => {
            inputRef.current?.focus();
        });
    }

    return (
        <div className="relative w-full">
            <div
                className="
                    flex
                    items-center
                    gap-2
                    rounded-xl
                    border
                    border-slate-700
                    bg-slate-900/90
                    px-3
                    py-2
                    shadow-lg
                    transition-all
                    duration-300
                    focus-within:border-blue-500
                    focus-within:ring-2
                    focus-within:ring-blue-500/10
                "
            >
                <span className="text-slate-500">⌕</span>

                <input
                    ref={inputRef}
                    value={query}
                    onChange={(event) =>
                        setQuery(event.target.value)
                    }
                    disabled={disabled}
                    placeholder="Search hero..."
                    className="
                        min-w-0
                        flex-1
                        bg-transparent
                        py-1
                        text-sm
                        text-white
                        outline-none
                        placeholder:text-slate-600
                    "
                />

                {loading && (
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-slate-600 border-t-blue-400" />
                )}
            </div>

            {/* Suggestions */}
            {suggestions.length > 0 && (
                <div
                    className="
                        absolute
                        left-0
                        right-0
                        top-[calc(100%+8px)]
                        z-50
                        overflow-hidden
                        rounded-xl
                        border
                        border-slate-700
                        bg-slate-950
                        shadow-2xl
                        animate-[fadeIn_180ms_ease-out]
                    "
                >
                    {suggestions.map((hero) => (
                        <button
                            key={hero}
                            type="button"
                            onClick={() => handleSelect(hero)}
                            className="
                                flex
                                w-full
                                items-center
                                gap-3
                                border-b
                                border-slate-800
                                px-3
                                py-3
                                text-left
                                transition-colors
                                duration-150
                                last:border-b-0
                                hover:bg-slate-800
                                active:bg-slate-700
                            "
                        >
                            {/* Placeholder image */}
                            <div
                                className="
                                    flex
                                    h-10
                                    w-10
                                    shrink-0
                                    items-center
                                    justify-center
                                    rounded-md
                                    bg-gradient-to-br
                                    from-slate-600
                                    to-slate-900
                                    text-[8px]
                                    uppercase
                                    text-slate-400
                                "
                            >
                                IMG
                            </div>

                            <span className="text-sm font-medium text-slate-200">
                                {hero}
                            </span>
                        </button>
                    ))}
                </div>
            )}

            {error && (
                <p className="mt-2 text-xs text-red-400">
                    {error}
                </p>
            )}
        </div>
    );
}