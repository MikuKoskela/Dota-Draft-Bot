
const API_URL = "https://api.opendota.com/api/heroStats";

export async function getHeroes(){
    const response = await fetch(API_URL);
    if (!response.ok){
        throw new Error("Failed to fetch Dota heroes")
    }

    return response.json();

}

export async function getHeroMap(){
    const heroes = await getHeroes();

    return Object.fromEntries(
        heroes.map(hero => [
            hero.localized_name,
            hero
        ])
    );
}