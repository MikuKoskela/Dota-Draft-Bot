
import React, { useEffect, useState } from 'react'
import HeroCard from './HeroCard'
import { Plus } from 'lucide-react' 
import { heroData } from '../data/heroData.js';

export default function HeroGrid( { addEnemyHero, addOwnHero } ) {
    const [hoveredHero,setHoveredHero] = useState(null);

    function handleYourTeamPick(heroName){
        addOwnHero(heroName)
        console.log("Add to your team")
    }

    function handleEnemyTeamPick(heroName){
        addEnemyHero(heroName)
        console.log("Add to enemy team")
    }
  /* CHECK IF BACK AND FRONTEND NAMES MATCH
    useEffect(()=>{
       async function checkNames(){
            const response = await fetch("http://localhost:8000/api/heroes")
            const data = await response.json()

            const backendHeroes = data.heroes;

            const frontendHeroes = Object.values(heroData).map(
                hero => hero.displayName
            )
            
            const missingInFrontend = backendHeroes.filter(
                hero => !frontendHeroes.includes(hero)
            )

            const missingInBackend = frontendHeroes.filter(
                hero => !backendHeroes.includes(hero)
            )

                console.table({
                
                missingInFrontend,
            
                missingInBackend,
            
                });
        }
        checkNames()
    },[])
    */
    function getHeroImages(){
            let count = 0;
           return Object.entries(heroData).map(([heroId, hero]) => {
                const heroName = hero.displayName
                .replace(".png", "")
                .replace(/_/g, " ")
                .replace(/\b\w/g, char => char.toUpperCase()
            )

            
            
                return(       
                    <div
                    key={heroId}
                    className='relative mt-2 h-26 w-28'
                    onMouseEnter={() => setHoveredHero(heroId)}
                    onMouseLeave={() => setHoveredHero(null)}
                    >
                       
                <div 
                
                className='flex flex-col items-center justify-content h-26 w-28 bg-slate-950/80 shadow-sm shadow-red-700/40 hover:shadow-md hover:shadow-red-700/60 hover:scale-105 transition-transform duration-300  cursor-pointer  border border-red-500/60 rounded-2xl overflow-hidden'>
                <img
                    
                    src={`${hero.image}`}
                    alt={`${hero.displayName}`}
                    className='
                        w-full
                        h-16
                        bg-slate-700/20 
                        object-cover
                        rounded-t-2xl '
                />
                <span className='mt-2 text-xs bg-red-500 bg-clip-text text-transparent '>
                    {hero.displayName}
                </span>
                </div>
            
                   
                    <div className={`
                    absolute 
                    inset-0 
                    z-59 
                    flex 
                    flex-col 
                    items-center 
                    justify-center 
                    gap-2 
                    bg-slate-950/60 
                    shadow-sm 
                    shadow-red-700/40 
                    hover:shadow-md 
                    hover:shadow-red-700/60  
                    border 
                    border-red-500/60 
                    rounded-2xl
                    transition-all 
                    duration-300
                    ${hoveredHero === heroId ? "scale-105 opacity-100" : "opacity-0 pointer-events-none"}
                    `}
                    >
                       <button 
                       onClick={()=> handleYourTeamPick(hero.displayName)}
                       className='w-16 z-50 bg-green-500/90 border border-green-700 hover:scale-105 hover:shadow-sm hover:shadow-black rounded-2xl cursor-pointer'>
                        
                        <span className='mr-1 flex flex-row items-center justify-center text-xs bg-black bg-clip-text text-transparent leading-2.5'>
                           <Plus className='text-white'/>Your Team
                        </span>
                        </button>
                        <button 
                        onClick={()=> handleEnemyTeamPick(hero.displayName)}
                        className='w-16 z-50 bg-red-500/90 border border-red-700 hover:scale-105 hover:shadow-sm hover:shadow-black rounded-2xl cursor-pointer'>
                        
                        <span className='mr-1 flex flex-row items-center justify-center text-xs bg-black bg-clip-text text-transparent leading-2.5'>
                           <Plus className='text-white'/>Enemy Team
                        </span>
                        </button>
                    </div> 
                    
                </div>
            )}
        )
    }
  
  
    return (
    <div>
    <div className='p-3 pt-4 pb-4 bg-blue-800/5  border border-gray-500/25 rounded-2xl leading-tight'>
    <div className='flex items-center justify-center gap-15 p-4'>
        <p className='text-blue-500'>{"<<<<<"}</p>
        <h2 className='
            text-2xl
            font-black
            tracking-tight
            text-white
            sm:text-4xl
            border-b
            border-b-blue-600
            '
            >
                All Heroes </h2>
                <p className='text-blue-500'>{">>>>>"}</p>
    </div>
            <div className='grid grid-cols-4 sm:grid-cols-5 md:grid-cols-6  lg:grid-cols-7 xl:grid-cols-8 gap-1 '>
            {getHeroImages()}
             </div>
    </div>
    </div>
  )
}
