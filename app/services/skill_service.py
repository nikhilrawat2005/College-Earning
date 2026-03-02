# app/services/skill_service.py
import time
from typing import Dict, List, Any

from app.extensions import db
from app.models import User
from app.data.services_data import (
    SERVICES_DATA,
    ALL_SKILLS,
    SKILL_DESCRIPTION_MAP,
    SKILL_ICON_MAP,
    SKILL_IMAGE_MAP,
)


class SkillService:
    _cache: Dict[str, Any] = {}
    _cache_ttl = 60  # seconds

    @classmethod
    def get_skill_counts(cls) -> Dict[str, int]:
        """Returns a dictionary with skill names as keys and count of workers."""
        now = time.time()
        if 'counts' in cls._cache and (now - cls._cache.get('timestamp', 0) < cls._cache_ttl):
            return cls._cache['counts']

        counts = {skill: 0 for skill in ALL_SKILLS}
        users = db.session.query(User.skills).filter(
            User.is_verified == True,
            User.is_worker == True,
            User.skills.isnot(None)
        ).all()

        for (skills_str,) in users:
            user_skills = [s.strip().lower() for s in skills_str.split(',') if s.strip()]
            for skill in ALL_SKILLS:
                if skill.lower() in user_skills:
                    counts[skill] += 1

        cls._cache['counts'] = counts
        cls._cache['timestamp'] = now
        return counts

    @classmethod
    def get_categorized_skills(cls) -> List[Dict[str, Any]]:
        """Returns list of categories with enriched skills."""
        counts = cls.get_skill_counts()
        categorized = []
        for category_name, category_data in SERVICES_DATA.items():
            enriched_skills = []
            for skill_info in category_data["skills"]:
                skill_name = skill_info['name']
                enriched_skills.append({
                    'name': skill_name,
                    'icon': skill_info['icon'],
                    'description': skill_info['description'],
                    'count': counts.get(skill_name, 0),
                    'image': SKILL_IMAGE_MAP.get(skill_name, 'default.jpg')   # <-- added image filename
                })
            categorized.append({
                'name': category_name,
                'description': category_data["description"],
                'skills': enriched_skills
            })
        return categorized

    @staticmethod
    def get_all_skills() -> List[str]:
        return ALL_SKILLS.copy()

    @staticmethod
    def get_description(skill: str) -> str:
        return SKILL_DESCRIPTION_MAP.get(skill, "Talented students offering this service.")

    @staticmethod
    def get_icon(skill: str) -> str:
        return SKILL_ICON_MAP.get(skill, "fa-star")

    @classmethod
    def clear_cache(cls):
        cls._cache.clear()