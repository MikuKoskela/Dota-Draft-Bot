const API_URL = "http://localhost:8000/api";

export async function getHeroes() {
    const response = await fetch(`${API_URL}/heroes`);

    if (!response.ok) {
        throw new Error("Failed to fetch heroes");
    }

    return response.json();
}


export async function searchHeroes(query) {
    const response = await fetch(
        `${API_URL}/heroes/search?q=${encodeURIComponent(query)}`
    );

    if (!response.ok) {
        throw new Error("Failed to search heroes");
    }

    return response.json();
}


export async function analyzeDraft(enemyTeam, ownTeam) {
    const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            enemy_team: enemyTeam,
            own_team: ownTeam
        })
    });

   if (!response.ok) {
    const error = await response.json();

    console.error("Backend error:", error);

    throw new Error(
        typeof error.detail === "string"
            ? error.detail
            : JSON.stringify(error.detail)
    );
}

    return response.json();
}