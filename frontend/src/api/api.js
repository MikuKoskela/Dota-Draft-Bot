const API_URL = import.meta.env.VITE_API_URL?.replace(/\/+$/, "")
    || (import.meta.env.DEV ? "http://localhost:8000" : "");

async function request(path, options) {
    if (!API_URL) {
        throw new Error("VITE_API_URL must be set to the HTTPS API URL before production build.");
    }
    if (import.meta.env.PROD && !API_URL.startsWith("https://")) {
        throw new Error("The production API URL must use HTTPS.");
    }

    const response = await fetch(`${API_URL}${path}`, options);
    if (!response.ok) {
        let detail = `Request failed (${response.status})`;
        try {
            const body = await response.json();
            detail = typeof body.detail === "string"
                ? body.detail
                : JSON.stringify(body.detail ?? body);
        } catch {
            // Keep the HTTP status message when the server does not return JSON.
        }
        throw new Error(detail);
    }
    return response.json();
}

export async function getHeroes() {
    const data = await request("/heroes");
    return data.heroes;
}

export function getMeta() {
    return request("/meta");
}

export function getHeroProfile(hero) {
    return request(`/heroes/${encodeURIComponent(hero)}`);
}

export function getMatchup(candidate, enemy) {
    return request(
        `/matchups/${encodeURIComponent(candidate)}/${encodeURIComponent(enemy)}`
    );
}

export function rankDraft(ownTeam, enemyTeam, targetRole, draftPhase) {
    return request("/draft/rank", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            own_team: ownTeam,
            enemy_team: enemyTeam,
            target_role: targetRole,
            draft_phase: draftPhase,
        }),
    });
}
