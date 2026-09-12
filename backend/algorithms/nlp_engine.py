import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class LocalNLPEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def calculate_similarity(self, text1, text2):
        """Calculates cosine similarity between two text strings."""
        if not text1 or not text2:
            return 0.0
        try:
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(sim)
        except Exception:
            # Fallback keyword overlap
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            if not words1 or not words2:
                return 0.0
            return len(words1.intersection(words2)) / float(len(words1.union(words2)))

    def is_duplicate_idea(self, candidate_idea, existing_ideas, threshold=0.75):
        """
        Checks if candidate idea problem/title exceeds similarity threshold with any existing idea.
        """
        cand_text = f"{candidate_idea.get('title', '')} {candidate_idea.get('problem', '')} {candidate_idea.get('solution', '')}"
        
        for item in existing_ideas:
            item_text = f"{item.get('title', '')} {item.get('problem', '')} {item.get('solution', '')}"
            sim = self.calculate_similarity(cand_text, item_text)
            if sim >= threshold:
                return True, sim, item.get('title', '')
        return False, 0.0, None


class RecommendationEngine:
    @staticmethod
    def rank_projects(student_profile, project_candidates):
        """
        Ranks project candidates for a student profile using multi-factor scoring:
        - Skill Match (25%)
        - Technology Match (25%)
        - Difficulty Match (15%)
        - Duration Match (15%)
        - Feasibility (10%)
        - Innovation (10%)
        """
        student_skills = set([s.lower() for s in student_profile.get_skills()])
        student_techs = set([t.lower() for t in student_profile.get_technologies()])
        student_pref_diff = student_profile.preferred_difficulty or 'Intermediate'
        student_hours = student_profile.available_time_hours_per_week or 10

        ranked_results = []
        for proj in project_candidates:
            # Tech match
            proj_techs = set([t.lower() for t in proj.get_tech_stack()])
            tech_match_pct = (len(student_techs.intersection(proj_techs)) / max(len(proj_techs), 1)) * 100
            
            # Skill match (estimate from features/techs)
            skill_match_pct = min(100.0, tech_match_pct + 15.0) if tech_match_pct > 0 else 50.0

            # Difficulty match
            diff_score = 100
            if proj.difficulty != student_pref_diff:
                diff_score = 75 if (proj.difficulty == 'Intermediate') else 60

            # Duration match
            dur_weeks = proj.estimated_duration_weeks or 8
            dur_score = 90 if dur_weeks <= 12 else 70

            # Feasibility
            feasibility_score = 95 if not proj.api_required else 75

            # Innovation
            innovation_score = 85

            # Overall Score calculation
            overall_score = round(
                (skill_match_pct * 0.25) +
                (tech_match_pct * 0.25) +
                (diff_score * 0.15) +
                (dur_score * 0.15) +
                (feasibility_score * 0.10) +
                (innovation_score * 0.10),
                1
            )

            ranked_results.append({
                "project": proj,
                "overall_match": overall_score,
                "breakdown": {
                    "skill_match": round(skill_match_pct, 1),
                    "technology_match": round(tech_match_pct, 1),
                    "difficulty_match": round(diff_score, 1),
                    "duration_match": round(dur_score, 1),
                    "feasibility": round(feasibility_score, 1),
                    "innovation": round(innovation_score, 1)
                }
            })

        # Sort descending by overall match score
        ranked_results.sort(key=lambda x: x["overall_match"], reverse=True)
        return ranked_results
