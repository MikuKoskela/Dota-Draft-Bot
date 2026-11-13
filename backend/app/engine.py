
import json
from pathlib import Path
from statistics import mean

class DraftEngine:
    WEIGHTS = {
        "laning":0.20,"counter":0.20,"synergy":0.20,"composition":0.15,
        "itemization":0.10,"scaling":0.10,"reliability":0.05
    }
    COUNTER_RISK_MULTIPLIER = {"blind":1.5,"early":1.2,"mid":1.0,"late":0.8,"last_pick":0.6}
    TEAM_ATTRIBUTES = ["initiation","hard_disable","frontline","wave_clear","physical_damage",
                       "magic_damage","save","mobility","roshan","push","teamfight","scaling"]
    LANE_COMPONENT_WEIGHTS = {
        "last_hit":0.08,"deny":0.04,"harass":0.14,"trade":0.14,"kill_pressure":0.14,
        "survivability":0.10,"sustain":0.08,"wave_clear":0.07,"range_advantage":0.06,
        "level_2_spike":0.04,"level_3_spike":0.05,"level_6_spike":0.06
    }
    ROLE_MIN_CONFIDENCE = 0.45
    MATCHUP_CONFIDENCE = {"curated":0.95,"curated_inverse":0.85,"inferred":0.50}
    LANE_CONTEXT = {
        "pos1": {"enemy": (("pos3", .55), ("pos4", .35)), "ally": (("pos5", .10),)},
        "pos2": {"enemy": (("pos2", .75), ("pos4", .15)), "ally": (("pos4", .10),)},
        "pos3": {"enemy": (("pos1", .55), ("pos5", .35)), "ally": (("pos4", .10),)},
        "pos4": {"enemy": (("pos1", .30), ("pos5", .25), ("pos2", .15)), "ally": (("pos3", .30),)},
        "pos5": {"enemy": (("pos3", .35), ("pos4", .25), ("pos2", .10)), "ally": (("pos1", .30),)},
    }
    ITEM_PRESSURE_WEIGHTS = {
        "bkb": .08, "mobility": .06, "dispel": .05,
        "armor": .05, "survivability": .05, "mana": .04,
    }

    def __init__(self, data_dir=None):
        d = Path(data_dir or Path(__file__).parent/"data")
        self.heroes=self._load(d/"heroes.json")
        self.matchups=self._load(d/"matchups.json")
        self.synergies=self._load(d/"synergies.json")
        self.meta=self._load(d/"meta.json")
        self.knowledge=self._load(d/"knowledge_graph.json")
        profile_meta=d/"profile_build_meta.json"
        self.profile_meta=self._load(profile_meta) if profile_meta.exists() else {}

    def _load(self,p): return json.loads(p.read_text(encoding="utf-8"))
    @staticmethod
    def clamp(v,lo=0,hi=100): return max(lo,min(hi,v))
    @staticmethod
    def normalize(v,lo=-3,hi=3):
        v=max(lo,min(hi,v)); return ((v-lo)/(hi-lo))*100
    @staticmethod
    def known(team): return [x for x in team.values() if x]

    def hero(self,name): return self.heroes.get(name,{})
    def tags(self,name): return set(self.hero(name).get("tags",[]))
    def weaknesses(self,name): return set(self.hero(name).get("weaknesses",[]))
    def tag_weight(self,name,tag):
        h=self.hero(name)
        return float(h.get("tag_weights",{}).get(tag,1.0 if tag in h.get("tags",[]) else 0.0))
    def weakness_weight(self,name,weakness):
        h=self.hero(name)
        return float(h.get("weakness_weights",{}).get(
            weakness,1.0 if weakness in h.get("weaknesses",[]) else 0.0
        ))

    def lane_value(self,matchup):
        lane=matchup.get("lane",{})
        if isinstance(lane,(int,float)): return lane
        if isinstance(lane,dict):
            return sum(lane.get(k,0)*w for k,w in self.LANE_COMPONENT_WEIGHTS.items())
        return 0

    def infer_lane(self,candidate,enemy):
        # The 12-dimensional lane card is the primary fallback; tag interactions
        # add only small, weighted adjustments.
        candidate_lane=self.hero(candidate).get("lane_profile",{})
        enemy_lane=self.hero(enemy).get("lane_profile",{})
        lane_delta=sum(
            (float(candidate_lane.get(key,0))-float(enemy_lane.get(key,0)))*weight
            for key,weight in self.LANE_COMPONENT_WEIGHTS.items()
        )
        score=lane_delta*1.6; reasons=[]
        if abs(lane_delta) >= .08:
            direction="candidate" if lane_delta > 0 else "opponent"
            reasons.append(f"{direction} leads the weighted 12-part lane profile")

        range_edge=self.tag_weight(candidate,"ranged")*max(
            self.tag_weight(enemy,"melee"),self.weakness_weight(enemy,"low_range")
        )
        if range_edge:
            score += .22*range_edge; reasons.append("weighted range advantage")
        range_risk=self.tag_weight(candidate,"melee")*self.tag_weight(enemy,"ranged")*max(
            self.weakness_weight(candidate,"kiting"),self.weakness_weight(candidate,"low_range")
        )
        if range_risk:
            score -= .22*range_risk; reasons.append("weighted ranged-pressure risk")
        early_risk=self.weakness_weight(candidate,"early_pressure")*self.tag_weight(enemy,"lane_dominator")
        if early_risk:
            score -= .28*early_risk; reasons.append("early-pressure weakness is exposed")
        return max(-1.5,min(1.5,score)),reasons

    def graph_interactions(self,candidate,other,relation):
        total=0.0; reasons=[]
        for r in self.knowledge["rules"]:
            if r.get("effect") != relation: continue
            evidence=[]
            if "candidate_tag" in r: evidence.append(self.tag_weight(candidate,r["candidate_tag"]))
            if "candidate_weakness" in r: evidence.append(self.weakness_weight(candidate,r["candidate_weakness"]))
            if "enemy_tag" in r: evidence.append(self.tag_weight(other,r["enemy_tag"]))
            if "enemy_weakness" in r: evidence.append(self.weakness_weight(other,r["enemy_weakness"]))
            if "ally_tag" in r: evidence.append(self.tag_weight(other,r["ally_tag"]))
            strength=1.0
            for value in evidence: strength*=value
            if evidence and strength > 0:
                contribution=float(r["value"])*strength
                total += contribution
                reasons.append(f"{r['reason']} (evidence {strength:.2f}, value {contribution:+.2f})")
        return total,reasons

    @staticmethod
    def effective_matchup(matchup):
        confidence=float(matchup.get("confidence",0))
        return {
            "lane":float(matchup.get("lane",0))*confidence,
            "mid_game":float(matchup.get("mid_game",0))*confidence,
            "late_game":float(matchup.get("late_game",0))*confidence,
        }

    def infer_matchup(self,candidate,enemy):
        lane,lane_reasons=self.infer_lane(candidate,enemy)
        counter,counter_reasons=self.graph_interactions(candidate,enemy,"counter")
        risk,risk_reasons=self.graph_interactions(candidate,enemy,"risk")
        candidate_spikes=self.hero(candidate).get("power_spikes",{})
        enemy_spikes=self.hero(enemy).get("power_spikes",{})
        candidate_scaling=float(candidate_spikes.get("late",.5))
        enemy_scaling=float(enemy_spikes.get("late",.5))
        mid_delta=float(candidate_spikes.get("mid",.5))-float(enemy_spikes.get("mid",.5))

        mid=self.clamp(lane*.15+mid_delta*.65+counter*.45-risk*.45,-1.75,1.75)
        late=self.clamp((candidate_scaling-enemy_scaling)*1.2+counter*.25-risk*.25,-2.0,2.0)
        reasons=lane_reasons
        reasons += [f"counter: {reason}" for reason in counter_reasons]
        reasons += [f"risk: {reason}" for reason in risk_reasons]
        if candidate_scaling != enemy_scaling:
            direction="candidate" if candidate_scaling > enemy_scaling else "opponent"
            reasons.append(f"{direction} has the stronger baseline scaling profile")
        if not reasons:
            reasons=["neutral estimate from the two hero baseline profiles"]
        profile_confidence=(
            self.hero(candidate).get("profile_confidence",.6)*
            self.hero(enemy).get("profile_confidence",.6)
        )**.5
        result={
            "lane":lane,"mid_game":mid,"late_game":late,"reasons":reasons,
            "source":"inferred","confidence":round(self.MATCHUP_CONFIDENCE["inferred"]*profile_confidence,3)
        }
        result["effective"]=self.effective_matchup(result)
        return result

    def resolve_matchup(self,candidate,enemy):
        direct=self.matchups.get(candidate,{}).get(enemy)
        if direct:
            result={
                "lane":self.lane_value(direct),
                "mid_game":direct.get("mid_game",0),
                "late_game":direct.get("late_game",0),
                "reasons":direct.get("reasons",[]),
                "source":"curated",
                "confidence":self.MATCHUP_CONFIDENCE["curated"]
            }
            result["effective"]=self.effective_matchup(result)
            return result

        reverse=self.matchups.get(enemy,{}).get(candidate)
        if reverse:
            result={
                "lane":-self.lane_value(reverse),
                "mid_game":-reverse.get("mid_game",0),
                "late_game":-reverse.get("late_game",0),
                "reasons":[f"inverse of curated {enemy} vs {candidate}: {r}" for r in reverse.get("reasons",[])],
                "source":"curated_inverse",
                "confidence":self.MATCHUP_CONFIDENCE["curated_inverse"]
            }
            result["effective"]=self.effective_matchup(result)
            return result

        return self.infer_matchup(candidate,enemy)

    def lane_effective(self,candidate,enemy):
        return self.resolve_matchup(candidate,enemy)["effective"]["lane"]

    def matchup_coverage(self):
        total=len(self.heroes)*(len(self.heroes)-1)
        curated=sum(1 for candidate,enemies in self.matchups.items()
                    for enemy in enemies if candidate != enemy)
        curated_pairs={frozenset((candidate,enemy)) for candidate,enemies in self.matchups.items()
                       for enemy in enemies if candidate != enemy}
        inverse_only=len(curated_pairs)*2-curated
        return {
            "directed_matchups":total,
            "curated_matchups":curated,
            "curated_inverse_matchups":inverse_only,
            "inferred_matchups":max(0,total-curated-inverse_only),
            "role_min_confidence":self.ROLE_MIN_CONFIDENCE,
        }

    def scoring_configuration(self):
        return {
            "component_weights": self.WEIGHTS,
            "lane_component_weights": self.LANE_COMPONENT_WEIGHTS,
            "lane_role_context": {
                role:{side:{lane:weight for lane,weight in pairs} for side,pairs in context.items()}
                for role,context in self.LANE_CONTEXT.items()
            },
            "matchup_confidence_multipliers": self.MATCHUP_CONFIDENCE,
            "counter_risk_multipliers": self.COUNTER_RISK_MULTIPLIER,
            "item_pressure_weights": self.ITEM_PRESSURE_WEIGHTS,
            "role_min_confidence": self.ROLE_MIN_CONFIDENCE,
            "graph_rule_weighting": "rule_value × product of all matching tag/weakness weights",
        }

    def calculate_laning(self,candidate,own_team,enemy_team,target_role):
        context=self.LANE_CONTEXT[target_role]
        vals=[]; weights=[]
        for role,weight in context["enemy"]:
            enemy=enemy_team.get(role)
            if enemy:
                vals.append(self.lane_effective(candidate,enemy)); weights.append(weight)
        for role,weight in context["ally"]:
            ally=own_team.get(role)
            if ally:
                direct=self.synergies.get(candidate,{}).get(ally,{})
                lane_synergy=direct.get("lane_synergy",direct.get("lane",0))
                if not lane_synergy:
                    lane_synergy=self.graph_interactions(candidate,ally,"synergy")[0]*.70
                vals.append(lane_synergy); weights.append(weight)
        if vals:
            return self.normalize(sum(v*w for v,w in zip(vals,weights))/sum(weights))
        enemies=self.known(enemy_team)
        return self.normalize(mean([self.lane_effective(candidate,e) for e in enemies])) if enemies else 50.0

    def calculate_counter_value(self,candidate,enemy_team):
        vals=[]
        for e in self.known(enemy_team):
            m=self.resolve_matchup(candidate,e)
            effective=m["effective"]
            graph,_=self.graph_interactions(candidate,e,"counter")
            vals.append(effective["lane"]*.25+effective["mid_game"]*.35+
                        effective["late_game"]*.25+min(3,graph)*.15)
        return self.normalize(mean(vals)) if vals else 50.0

    def calculate_synergy(self,candidate,own_team):
        vals=[]
        for ally in self.known(own_team):
            d=self.synergies.get(candidate,{}).get(ally)
            direct=mean(d.values()) if d else 0
            graph,_=self.graph_interactions(candidate,ally,"synergy")
            vals.append(max(-3,min(3,direct*0.75+graph*0.25)))
        return self.normalize(mean(vals)) if vals else 50.0

    def calculate_team_needs(self,own_team):
        current={a:0 for a in self.TEAM_ATTRIBUTES}
        for h in self.known(own_team):
            for a,v in self.hero(h).get("team_contributions",{}).items():
                if a in current: current[a]+=v
        target={"initiation":3,"hard_disable":3,"frontline":3,"wave_clear":3,"physical_damage":3,
                "magic_damage":2,"save":2,"mobility":2,"roshan":2,"push":2,"teamfight":3,"scaling":2}
        return {a:max(0,target[a]-current[a]) for a in current}

    def calculate_team_composition(self,candidate,own_team):
        needs=self.calculate_team_needs(own_team)
        c=self.hero(candidate).get("team_contributions",{})
        total=sum(needs.values())
        if not total:return 50.0
        filled=sum(min(n,c.get(a,0)) for a,n in needs.items())
        return self.clamp(filled/total*100)

    def calculate_enemy_pressure(self,enemy_team):
        p={"bkb":0,"dispel":0,"mobility":0,"armor":0,"survivability":0,"mana":0}
        for e in self.known(enemy_team):
            p["bkb"] += .65*self.tag_weight(e,"hard_disable")+.35*self.tag_weight(e,"burst")
            p["armor"] += self.tag_weight(e,"physical_damage")
            p["mobility"] += max(self.tag_weight(e,"initiation"),self.tag_weight(e,"catch"))
            p["dispel"] += max(self.tag_weight(e,"silence"),self.tag_weight(e,"root"),self.tag_weight(e,"slow")*.5)
            p["survivability"] += self.tag_weight(e,"burst")
            p["mana"] += self.tag_weight(e,"mana_burn")
        return p

    def calculate_itemization(self,candidate,enemy_team):
        pr=self.hero(candidate).get("item_profile",{})
        p=self.calculate_enemy_pressure(enemy_team)
        dependencies={
            "bkb":pr.get("bkb_dependency",.5),
            "mobility":pr.get("mobility_dependency",.5),
            "dispel":pr.get("dispel_dependency",.5),
            "armor":pr.get("survivability_dependency",.5),
            "survivability":pr.get("survivability_dependency",.5),
            "mana":pr.get("mana_dependency",.5),
        }
        tax=sum(p[key]*self.ITEM_PRESSURE_WEIGHTS[key]*dependencies[key] for key in p)
        return self.clamp(100-tax*100)

    def calculate_scaling(self,candidate,own_team,enemy_team):
        candidate_late=float(self.hero(candidate).get("power_spikes",{}).get("late",.5))
        own_late=[float(self.hero(h).get("power_spikes",{}).get("late",.5)) for h in self.known(own_team)]
        enemy_late=[float(self.hero(h).get("power_spikes",{}).get("late",.5)) for h in self.known(enemy_team)]
        own_average=mean(own_late+[candidate_late])
        enemy_average=mean(enemy_late) if enemy_late else .5
        return self.clamp(50+(candidate_late-enemy_average)*45+(own_average-enemy_average)*20)

    def data_confidence(self,candidate):
        q=self.hero(candidate).get("data_quality","seed")
        mapped={"ability_enriched_v2":self.hero(candidate).get("profile_confidence",.85),
                "roster_curated_v1":.88,"curated_mvp":1.0,"migrated_mvp":.9,"seed":.55}
        return float(mapped.get(q,.6))

    def calculate_reliability(self,candidate,target_role):
        h=self.hero(candidate)
        role=h.get("roles",{}).get(target_role,0)
        execution=1-h.get("difficulty",.5)
        confidence=self.data_confidence(candidate)
        return self.clamp((role*.55+execution*.20+confidence*.25)*100)

    def calculate_counter_risk(self,candidate,enemy_team,draft_phase):
        vals=[]
        for e in self.known(enemy_team):
            m=self.resolve_matchup(candidate,e)
            negatives=[abs(v) for v in m["effective"].values() if v<0]
            graph,_=self.graph_interactions(candidate,e,"risk")
            base=(mean(negatives) if negatives else 0)+graph*.35
            if base:vals.append(base)
        if not vals:return 0
        base=min(15,(mean(vals)/3)*15)
        return min(15,base*self.COUNTER_RISK_MULTIPLIER.get(draft_phase,1))

    def calculate_item_tax(self,candidate,enemy_team):
        profile=self.hero(candidate).get("item_profile",{})
        return min(8,
            profile.get("farm_dependency",0)*3.0+
            profile.get("damage_item_dependency",0)*2.0+
            profile.get("survivability_dependency",0)*1.0+
            profile.get("mana_dependency",0)*.5
        )

    def calculate_role_conflict(self,candidate,target_role):
        conf=self.hero(candidate).get("roles",{}).get(target_role,0)
        return (1-conf)*8

    def calculate_redundancy(self,candidate,own_team):
        penalty=0
        meaningful={"carry","physical_damage","magic_damage","frontline"}
        for a in self.known(own_team):
            penalty += .8*sum(self.tag_weight(candidate,t)*self.tag_weight(a,t) for t in meaningful)
            penalty += .8*self.weakness_weight(candidate,"low_mobility")*self.weakness_weight(a,"low_mobility")
        return min(8,penalty)

    def calculate_data_uncertainty(self,candidate):
        # Explicit penalty for neutral seed heroes so incomplete data cannot outrank curated heroes too confidently.
        return round((1-self.data_confidence(candidate))*8,2)

    def interaction_reasons(self,candidate,own_team,enemy_team):
        out=[]
        for e in self.known(enemy_team):
            for rel in ("counter","risk"):
                _,rs=self.graph_interactions(candidate,e,rel)
                out += [f"{rel}: {r} ({e})" for r in rs]
        for a in self.known(own_team):
            _,rs=self.graph_interactions(candidate,a,"synergy")
            out += [f"synergy: {r} ({a})" for r in rs]
        return out[:8]


    def picked_heroes(self, own_team, enemy_team):
        return set(self.known(own_team)) | set(self.known(enemy_team))

    def build_available_heroes(self, own_team, enemy_team, target_role, available_heroes=None, banned_heroes=None):
        banned = set(banned_heroes or [])
        unavailable = self.picked_heroes(own_team, enemy_team) | banned

        if available_heroes is None:
            pool = list(self.heroes.keys())
        else:
            pool = [h for h in available_heroes if h in self.heroes]

        # Generic 0.2 role placeholders mean "not a real role" in the baseline data.
        # A 0.45 floor keeps genuine flex picks while removing placeholder roles.
        filtered = []
        for hero in pool:
            if hero in unavailable:
                continue
            role_conf = self.hero(hero).get("roles", {}).get(target_role, 0)
            if role_conf < self.ROLE_MIN_CONFIDENCE:
                continue
            filtered.append(hero)

        return filtered

    def evaluate_pick(self,candidate,own_team,enemy_team,target_role,draft_phase="mid"):
        scores={
            "laning":self.calculate_laning(candidate,own_team,enemy_team,target_role),
            "counter":self.calculate_counter_value(candidate,enemy_team),
            "synergy":self.calculate_synergy(candidate,own_team),
            "composition":self.calculate_team_composition(candidate,own_team),
            "itemization":self.calculate_itemization(candidate,enemy_team),
            "scaling":self.calculate_scaling(candidate,own_team,enemy_team),
            "reliability":self.calculate_reliability(candidate,target_role)
        }
        weighted={k:scores[k]*self.WEIGHTS[k] for k in scores}
        raw=sum(weighted.values())
        penalties={
            "counter_risk":self.calculate_counter_risk(candidate,enemy_team,draft_phase),
            "item_tax":self.calculate_item_tax(candidate,enemy_team),
            "role_conflict":self.calculate_role_conflict(candidate,target_role),
            "redundancy":self.calculate_redundancy(candidate,own_team),
            "data_uncertainty":self.calculate_data_uncertainty(candidate)
        }
        final=self.clamp(raw-sum(penalties.values()))
        breakdown={**{k:round(v,1) for k,v in weighted.items()},
                   **{k:round(-v,1) for k,v in penalties.items()}}
        positives=sorted([(k,v) for k,v in weighted.items()],key=lambda x:x[1],reverse=True)[:3]
        risks=sorted([(k,v) for k,v in penalties.items() if v>0],key=lambda x:x[1],reverse=True)
        explanation=", ".join([f"{k.replace('_',' ')} +{v:.1f}" for k,v in positives])
        if risks: explanation += f", suurin riski: {risks[0][0].replace('_',' ')} -{risks[0][1]:.1f}"
        matchup_details=[]
        for enemy in self.known(enemy_team):
            matchup=self.resolve_matchup(candidate,enemy)
            effective=matchup["effective"]
            matchup_score=self.normalize(
                effective["lane"]*.30+effective["mid_game"]*.40+effective["late_game"]*.30
            )
            matchup_details.append({
                "enemy":enemy,
                "lane":round(matchup["lane"],2),
                "mid_game":round(matchup["mid_game"],2),
                "late_game":round(matchup["late_game"],2),
                "score":round(matchup_score,1),
                "source":matchup["source"],
                "confidence":matchup["confidence"],
                "effective_lane":round(effective["lane"],2),
                "effective_mid_game":round(effective["mid_game"],2),
                "effective_late_game":round(effective["late_game"],2),
                "reasons":matchup["reasons"][:4],
            })
        matchup_confidence=mean([m["confidence"] for m in matchup_details]) if matchup_details else 0
        return {
            "hero":candidate,"score":round(final,1),"raw_score":round(raw,1),
            "patch":self.meta["game_patch"],"data_quality":self.hero(candidate).get("data_quality","seed"),
            "matchup_confidence":round(matchup_confidence,2),
            "matchup_details":matchup_details,
            "component_scores":{k:round(v,1) for k,v in scores.items()},
            "breakdown":breakdown,"knowledge_graph_reasons":self.interaction_reasons(candidate,own_team,enemy_team),
            "explanation":explanation
        }

    def rank_candidates(self,own_team,enemy_team,available_heroes,target_role,draft_phase="mid",banned_heroes=None):
        filtered = self.build_available_heroes(
            own_team=own_team,
            enemy_team=enemy_team,
            target_role=target_role,
            available_heroes=available_heroes,
            banned_heroes=banned_heroes,
        )
        results=[self.evaluate_pick(h,own_team,enemy_team,target_role,draft_phase)
                 for h in filtered]
        return sorted(results,key=lambda x:x["score"],reverse=True)
