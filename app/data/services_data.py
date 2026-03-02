"""
Centralized skill definitions with categories, icons, descriptions, and image filenames.
Used throughout the app for forms, services page, and skill counting.
"""

SERVICES_DATA = {
    "🎬 Creative & Media Services": {
        "description": "Edit, shoot, and design stunning visual content.",
        "skills": [
            {"name": "Video Editing", "icon": "fa-video", "description": "Edit reels, YouTube videos, cinematic edits, and college events."},
            {"name": "Videography", "icon": "fa-camera", "description": "Shoot campus events, short films, and promotional content."},
            {"name": "Photography", "icon": "fa-camera-retro", "description": "Portraits, events, and product shoots."},
            {"name": "Photo Editing", "icon": "fa-edit", "description": "Color grading, retouching, and enhancements."},
            {"name": "Poster & Social Media Design", "icon": "fa-paint-brush", "description": "Eye-catching posters and social media graphics."},
        ]
    },
    "📚 Academic & College Support": {
        "description": "Helping students complete academic work efficiently.",
        "skills": [
            {"name": "Assignment Writing", "icon": "fa-pencil", "description": "Well-researched assignments on any topic."},
            {"name": "Practical File Preparation", "icon": "fa-file", "description": "Neatly formatted practical files and lab records."},
            {"name": "Research Paper Assistance", "icon": "fa-search", "description": "Help with research, formatting, and citations."},
            {"name": "Project Development Help", "icon": "fa-code", "description": "Guidance and code for academic projects."},
            {"name": "DSA Guidance", "icon": "fa-sitemap", "description": "Data structures and algorithms tutoring."},
        ]
    },
    "🎨 Design & Digital Creation": {
        "description": "Turn ideas into digital visuals.",
        "skills": [
            {"name": "UI/UX Design", "icon": "fa-mobile", "description": "User‑friendly app and website designs."},
            {"name": "PPT & Presentation Design", "icon": "fa-file-powerpoint", "description": "Professional slide decks."},
            {"name": "Graphic Sheet Design", "icon": "fa-paint-brush", "description": "Creative graphic sheets for portfolios."},
            {"name": "Thumbnail & Banner Design", "icon": "fa-image", "description": "Click‑worthy YouTube thumbnails and banners."},
        ]
    },
    "💼 Career & Professional Growth": {
        "description": "Build skills that shape your future.",
        "skills": [
            {"name": "Resume / Portfolio / Online Profile Building", "icon": "fa-briefcase", "description": "Stand out with a polished resume or portfolio."},
            {"name": "Soft Skills Coaching", "icon": "fa-comments", "description": "Communication, leadership, and interview skills."},
            {"name": "Promotion", "icon": "fa-bullhorn", "description": "Market your events, gigs, or campaigns on campus."},
            {"name": "Personal Branding", "icon": "fa-id-badge", "description": "Build your online presence and personal brand."},
        ]
    },
    "🧠 Technical & Productivity Tools": {
        "description": "Work smarter with essential tools.",
        "skills": [
            {"name": "MS Excel Support", "icon": "fa-file-excel", "description": "Formulas, data analysis, and dashboards."},
            {"name": "MS Word Documentation", "icon": "fa-file-word", "description": "Formatting, templates, and document design."},
        ]
    },
    "🚀 Experience & Mentorship": {
        "description": "Collaborate, learn and grow together.",
        "skills": [
            {"name": "Hackathon Team Collaboration", "icon": "fa-users", "description": "Find teammates for hackathons and projects."},
        ]
    },
    "🏋️ Lifestyle & Other Services": {
        "description": "Balance skills with personal growth.",
        "skills": [
            {"name": "Fitness Guidance", "icon": "fa-heartbeat", "description": "Workout plans, diet advice, and fitness tips."},
            {"name": "Trading Basics Guidance", "icon": "fa-chart-line", "description": "Learn the basics of trading and investing."},
        ]
    },
}

# Flat list of all skill names for quick lookups
ALL_SKILLS = [skill["name"] for cat in SERVICES_DATA.values() for skill in cat["skills"]]

# Mapping from skill name to its icon
SKILL_ICON_MAP = {skill["name"]: skill["icon"] for cat in SERVICES_DATA.values() for skill in cat["skills"]}

# Mapping from skill name to its description
SKILL_DESCRIPTION_MAP = {skill["name"]: skill["description"] for cat in SERVICES_DATA.values() for skill in cat["skills"]}

# Mapping from skill name to its image filename (must match files in static/images/skills/)
SKILL_IMAGE_MAP = {
    "Video Editing": "video_editing.jpg",
    "Videography": "videography.jpg",
    "Photography": "photography.jpg",
    "Photo Editing": "photo_editing.jpg",
    "Poster & Social Media Design": "poster_and_social_media_design.jpg",
    "Assignment Writing": "assignment_writing.jpg",
    "Practical File Preparation": "practical_file_preparation.jpg",
    "Research Paper Assistance": "research_paper_assistance.jpg",
    "Project Development Help": "project_development_help.jpg",
    "DSA Guidance": "dsa_guidance.jpg",
    "UI/UX Design": "ui_ux_design.jpg",
    "PPT & Presentation Design": "ppt_and_presentation_design.jpg",
    "Graphic Sheet Design": "graphic_sheet_design.jpg",
    "Thumbnail & Banner Design": "thumbnail_and_banner_design.jpg",
    "Resume / Portfolio / Online Profile Building": "resume_portfolio_online_profile_building.jpg",
    "Soft Skills Coaching": "soft_skills_coaching.jpg",
    "Promotion": "promotion.jpg",
    "Personal Branding": "personal_branding.jpg",
    "MS Excel Support": "ms_excel_support.jpg",
    "MS Word Documentation": "ms_word_documentation.jpg",
    "Hackathon Team Collaboration": "hackathon_team_collaboration.jpg",
    "Fitness Guidance": "fitness_guidance.jpg",
    "Trading Basics Guidance": "trading_basics_guidance.jpg",
}