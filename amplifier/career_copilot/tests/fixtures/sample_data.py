"""
Sample test data fixtures for AI Career Copilot tests.

This module provides realistic sample data for testing all components
of the career copilot service.
"""

from typing import Any

# Sample resume texts in different formats
SAMPLE_RESUME_TXT = """
John Anderson
San Francisco, CA | (415) 555-0123 | john.anderson@email.com | linkedin.com/in/johnanderson

PROFESSIONAL SUMMARY
Senior Software Engineer with 7+ years of experience in full-stack development,
cloud architecture, and team leadership. Proven track record of delivering
high-impact solutions in fast-paced environments.

WORK EXPERIENCE
Senior Software Engineer | TechCorp Solutions | San Francisco, CA
March 2020 - Present
• Lead development of microservices architecture serving 1M+ users
• Mentored team of 4 junior developers, improving team productivity by 35%
• Designed and implemented CI/CD pipeline reducing deployment time by 60%
• Optimized database queries improving application performance by 45%

Software Engineer | StartupHub | Palo Alto, CA
June 2018 - February 2020
• Developed RESTful APIs using Python, Django, and PostgreSQL
• Built responsive frontend applications with React and TypeScript
• Collaborated in Agile team of 6 developers using Scrum methodology
• Implemented automated testing suite achieving 85% code coverage

Junior Developer | Digital Innovations | San Jose, CA
August 2016 - May 2018
• Maintained and enhanced legacy web applications
• Participated in code reviews and pair programming sessions
• Assisted in migration from monolithic to microservices architecture

EDUCATION
Bachelor of Science in Computer Science
University of California, Davis | Davis, CA
September 2012 - June 2016
• GPA: 3.8/4.0, Magna Cum Laude
• Dean's List: 6 semesters
• Relevant Coursework: Data Structures, Algorithms, Database Systems,
  Software Engineering, Machine Learning

TECHNICAL SKILLS
Programming Languages: Python (Expert), JavaScript (Advanced), TypeScript (Advanced),
Java (Intermediate), Go (Beginner)
Frameworks & Libraries: React, Node.js, Django, Flask, Express.js, Spring Boot
Databases: PostgreSQL, MongoDB, Redis, MySQL
Cloud & DevOps: AWS, Docker, Kubernetes, Jenkins, GitLab CI
Tools & Technologies: Git, JIRA, Confluence, JUnit, Jest, Webpack

CERTIFICATIONS
• AWS Certified Solutions Architect - Professional (2023)
• Google Cloud Professional Developer (2022)
• Certified Kubernetes Administrator (CKA) (2022)

PROJECTS
E-commerce Platform Redesign
• Architected and led development of new microservices-based platform
• Technologies: React, Node.js, PostgreSQL, Docker, Kubernetes
• Result: 40% increase in conversion rate, 60% faster page load times

Real-time Analytics Dashboard
• Developed real-time data visualization platform for business metrics
• Technologies: Python, WebSockets, D3.js, Redis, Apache Kafka
• Result: Reduced decision-making time by 50% for executive team

Open Source Contributions
• Active contributor to Django REST Framework (50+ commits)
• Maintainer of popular React component library (2k+ stars)
• Technical blog writer: 50+ articles on Medium

LANGUAGES
English (Native), Spanish (Conversational), Mandarin (Basic)

INTERESTS
Machine Learning, Open Source, Technical Writing, Hiking, Photography
"""

SAMPLE_RESUME_JSON = {
    "personal_info": {
        "name": "Sarah Chen",
        "email": "sarah.chen@email.com",
        "phone": "(650) 555-0234",
        "location": "Mountain View, CA",
        "linkedin": "linkedin.com/in/sarahchen",
        "github": "github.com/sarahchen",
    },
    "summary": "Data Scientist with 5 years of experience in machine learning, statistical analysis, and data visualization. Passionate about leveraging data to drive business decisions and product innovation.",
    "work_experience": [
        {
            "company": "DataDrive Analytics",
            "position": "Senior Data Scientist",
            "location": "Mountain View, CA",
            "start_date": "2021-03-01",
            "end_date": None,
            "is_current": True,
            "description": "Lead data science initiatives for predictive analytics and machine learning projects.",
            "achievements": [
                "Developed customer churn prediction model with 89% accuracy",
                "Built A/B testing platform increasing conversion rates by 25%",
                "Led team of 3 data scientists in cross-functional projects",
            ],
            "skills_used": [
                {"name": "Python", "level": "advanced", "years_experience": 5.0},
                {"name": "Machine Learning", "level": "advanced", "years_experience": 4.0},
                {"name": "SQL", "level": "advanced", "years_experience": 5.0},
            ],
            "team_size": 3,
            "projects": ["Customer Segmentation Model", "Recommendation Engine"],
        }
    ],
    "education": [
        {
            "institution": "Stanford University",
            "degree": "Master of Science",
            "field_of_study": "Data Science",
            "location": "Stanford, CA",
            "start_date": "2018-09-01",
            "end_date": "2020-06-30",
            "gpa": 3.9,
            "honors": ["NSF Graduate Research Fellowship"],
            "relevant_coursework": ["Machine Learning", "Statistical Modeling", "Data Mining", "Deep Learning"],
        }
    ],
    "skills": [
        {"name": "Python", "level": "advanced", "years_experience": 5.0, "context": "Data analysis and ML"},
        {"name": "R", "level": "intermediate", "years_experience": 3.0, "context": "Statistical analysis"},
        {"name": "SQL", "level": "advanced", "years_experience": 5.0, "context": "Database queries"},
        {"name": "TensorFlow", "level": "advanced", "years_experience": 3.0, "context": "Deep learning"},
        {"name": "Tableau", "level": "intermediate", "years_experience": 2.0, "context": "Data visualization"},
    ],
    "certifications": [
        {
            "name": "TensorFlow Developer Certificate",
            "issuer": "Google",
            "date": "2022-01-15",
            "credential_id": "TF-2022-123456",
        }
    ],
}

# Sample job descriptions
SAMPLE_JOB_DESCRIPTIONS = [
    {
        "job_id": "job-001",
        "title": "Senior Software Engineer",
        "company": "TechCorp",
        "location": "San Francisco, CA",
        "remote": True,
        "salary_range": {"min": 160000, "max": 220000, "currency": "USD"},
        "description": "We are looking for a Senior Software Engineer to join our growing engineering team. You will work on building scalable web applications and mentor junior developers.",
        "requirements": [
            "5+ years of software development experience",
            "Strong proficiency in Python and JavaScript",
            "Experience with cloud platforms (AWS, GCP, or Azure)",
            "Experience with microservices architecture",
            "Strong problem-solving and communication skills",
        ],
        "skills": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "PostgreSQL"],
        "experience_level": "senior",
        "job_type": "full-time",
        "posted_date": "2024-01-15",
        "company_culture": "Innovative, collaborative, fast-paced environment with focus on work-life balance",
    },
    {
        "job_id": "job-002",
        "title": "Data Scientist",
        "company": "DataDriven Inc",
        "location": "New York, NY",
        "remote": False,
        "salary_range": {"min": 140000, "max": 190000, "currency": "USD"},
        "description": "Join our data science team to build machine learning models that drive business insights and product features.",
        "requirements": [
            "3+ years of data science experience",
            "Strong programming skills in Python or R",
            "Experience with machine learning frameworks",
            "Strong statistical and mathematical background",
            "Excellent communication and presentation skills",
        ],
        "skills": ["Python", "R", "Machine Learning", "SQL", "TensorFlow", "PyTorch", "Data Visualization"],
        "experience_level": "mid-senior",
        "job_type": "full-time",
        "posted_date": "2024-01-12",
        "company_culture": "Data-driven culture with emphasis on learning and development",
    },
    {
        "job_id": "job-003",
        "title": "Engineering Manager",
        "company": "StartupXYZ",
        "location": "Remote",
        "remote": True,
        "salary_range": {"min": 180000, "max": 250000, "currency": "USD"},
        "description": "Lead and grow our engineering team while maintaining high technical standards and shipping great products.",
        "requirements": [
            "8+ years of software development experience",
            "2+ years of management or technical leadership experience",
            "Experience with agile methodologies",
            "Strong communication and mentoring skills",
            "Experience with hiring and performance management",
        ],
        "skills": ["Leadership", "System Design", "Project Management", "Agile", "Mentoring", "Technical Strategy"],
        "experience_level": "senior",
        "job_type": "full-time",
        "posted_date": "2024-01-10",
        "company_culture": "Startup environment with flat hierarchy and rapid iteration",
    },
]

# Sample user preferences
SAMPLE_USER_PREFERENCES = {
    "career_goals": {
        "target_roles": ["Senior Software Engineer", "Engineering Manager", "Staff Engineer"],
        "target_industries": ["Technology", "FinTech", "E-commerce"],
        "target_companies": ["Google", "Stripe", "Airbnb", "Netflix", "Spotify"],
        "salary_range": {"min": 160000, "max": 250000, "currency": "USD"},
        "location_preferences": ["San Francisco", "Remote", "New York"],
        "work_style_preference": "hybrid",
        "career_timeline": "2-3 years",
        "growth_priorities": ["technical_leadership", "team_management", "system_architecture"],
    },
    "learning_preferences": {
        "learning_style": "hands_on",
        "time_commitment": 12,
        "learning_budget": 200,
        "preferred_formats": ["online_courses", "projects", "workshops", "mentoring"],
        "certification_goals": ["AWS Solutions Architect Professional", "Google Cloud Professional"],
        "difficulty_preference": "progressive",
        "group_learning": True,
    },
    "notification_settings": {
        "email_notifications": True,
        "job_alerts": True,
        "skill_updates": True,
        "career_insights": True,
        "networking_opportunities": False,
        "frequency": "weekly",
    },
    "privacy_settings": {
        "profile_visibility": "public",
        "data_sharing": True,
        "analytics_consent": True,
        "network_visibility": "limited",
    },
}

# Sample skill analysis results
SAMPLE_SKILL_ANALYSIS = {
    "skill_gaps": [
        {
            "skill_name": "System Design",
            "current_level": "intermediate",
            "required_level": "advanced",
            "priority": "high",
            "estimated_months": 6,
            "gap_description": "Need to improve ability to design large-scale distributed systems",
            "impact_on_career": "Critical for senior/staff level positions",
        },
        {
            "skill_name": "Leadership",
            "current_level": "beginner",
            "required_level": "advanced",
            "priority": "medium",
            "estimated_months": 12,
            "gap_description": "Limited experience leading teams or mentoring",
            "impact_on_career": "Important for engineering management track",
        },
        {
            "skill_name": "Kubernetes",
            "current_level": "beginner",
            "required_level": "intermediate",
            "priority": "medium",
            "estimated_months": 4,
            "gap_description": "Basic knowledge of container orchestration",
            "impact_on_career": "Valuable for modern cloud-native development",
        },
    ],
    "skill_development_plan": [
        {
            "skill_name": "System Design",
            "learning_resources": [
                {
                    "type": "course",
                    "title": "Grokking the System Design Interview",
                    "provider": "Educative",
                    "url": "https://educative.io/courses/grokking-the-system-design-interview",
                    "cost": "paid",
                    "time_commitment": "20 hours",
                    "quality_rating": 4.8,
                    "description": "Comprehensive guide to system design concepts and patterns",
                },
                {
                    "type": "book",
                    "title": "Designing Data-Intensive Applications",
                    "provider": "Martin Kleppmann",
                    "url": "https://amzn.com/book-id",
                    "cost": "paid",
                    "time_commitment": "40 hours",
                    "quality_rating": 4.7,
                    "description": "Fundamental concepts for distributed systems design",
                },
            ],
            "learning_methodology": {
                "approach": "project_based",
                "activities": [
                    "Complete design exercises",
                    "Build scalable projects",
                    "Participate in design discussions",
                    "Read case studies",
                ],
                "practice_opportunities": [
                    "Open source contributions",
                    "Personal projects",
                    "Internal system design reviews",
                    "Technical blog writing",
                ],
            },
            "timeline": {
                "phase_1": "Months 1-2: Study core concepts and patterns",
                "phase_2": "Months 3-4: Practice with real-world problems",
                "phase_3": "Months 5-6: Advanced topics and optimizations",
            },
            "validation_methods": [
                "System design mock interviews",
                "Peer design reviews",
                "Technical presentations",
                "Project implementations",
            ],
        }
    ],
    "market_readiness_score": 78,
    "strengths": [
        "Strong programming foundation in Python and JavaScript",
        "Good experience with modern web technologies",
        "Solid understanding of data structures and algorithms",
        "Experience with cloud platforms and DevOps practices",
    ],
    "improvement_areas": [
        "System design and architecture skills",
        "Leadership and mentoring experience",
        "Container orchestration (Kubernetes)",
        "Advanced distributed systems knowledge",
    ],
    "career_insights": {
        "current_level": "Senior Software Engineer",
        "next_level": "Staff Engineer / Engineering Manager",
        "readiness_for_next_level": 75,
        "time_to_promotion": "12-18 months",
        "market_demand": "high",
        "salary_potential": {"min": 180000, "max": 280000},
    },
}

# Sample coaching responses
SAMPLE_COACHING_RESPONSES = {
    "career_transition": {
        "response": "Based on your background in software engineering, transitioning to data science is definitely achievable with the right approach. Your strong programming foundation in Python gives you a significant advantage.",
        "action_items": [
            "Strengthen statistical and mathematical foundations",
            "Build portfolio of data science projects",
            "Take online courses in machine learning and statistics",
            "Network with data science professionals",
            "Consider internal transfer opportunities",
        ],
        "next_steps": "Would you like me to suggest specific learning resources for building your data science skills, or would you prefer to discuss how to leverage your existing engineering experience in data science roles?",
        "suggested_resources": [
            "Coursera's Machine Learning by Andrew Ng",
            "Kaggle competitions for practical experience",
            "Data Science community meetups and conferences",
        ],
    },
    "skill_development": {
        "response": "For advancing to senior/staff level positions, I recommend focusing on three key areas: system design, technical leadership, and cross-functional collaboration. Your current foundation is strong, so we can build upon it strategically.",
        "action_items": [
            "Practice system design interviews and concepts",
            "Take ownership of complex projects at work",
            "Mentor junior developers to build leadership skills",
            "Contribute to technical design discussions",
            "Write technical blog posts or give presentations",
        ],
        "next_steps": "Which of these areas feels most challenging to you right now? I can provide more specific guidance and resources for any of them.",
        "timeline_suggestion": "With consistent effort over 6-12 months, you should see significant improvement in these areas.",
    },
    "job_search_strategy": {
        "response": "Your profile is strong for senior engineering roles. Let's focus on targeting the right companies and preparing effectively for interviews. Your combination of technical skills and leadership potential makes you a valuable candidate.",
        "action_items": [
            "Update resume to highlight leadership and system design experience",
            "Prepare system design interviews with common patterns",
            "Research target companies' tech stacks and culture",
            "Network with engineers at target companies",
            "Practice behavioral interviews using STAR method",
        ],
        "next_steps": "Would you like help preparing your resume for senior roles, or should we focus on interview preparation first?",
        "company_suggestions": [
            "Consider fast-growing startups where you can have more impact",
            "Look at FAANG companies for structured growth paths",
            "Explore fintech companies for interesting technical challenges",
        ],
    },
}

# Sample job matches
SAMPLE_JOB_MATCHES = [
    {
        "job_id": "match-001",
        "title": "Senior Software Engineer",
        "company": "TechCorp",
        "location": "San Francisco, CA",
        "remote": True,
        "match_score": 92,
        "match_reasons": [
            "Strong alignment with Python and JavaScript skills",
            "Experience with microservices architecture",
            "Cloud platform experience matches requirements",
            "Leadership experience aligns with team culture",
        ],
        "salary_range": {"min": 160000, "max": 220000},
        "requirements_match": 95,
        "culture_fit": 88,
        "growth_potential": 90,
        "application_strategy": {
            "resume_highlights": ["Microservices leadership", "Performance optimization", "Team mentoring"],
            "cover_letter_points": ["Cloud architecture experience", "Team leadership", "Technical innovation"],
            "interview_prep": ["System design", "Leadership scenarios", "Technical deep-dive"],
        },
    },
    {
        "job_id": "match-002",
        "title": "Staff Software Engineer",
        "company": "StartupXYZ",
        "location": "Remote",
        "remote": True,
        "match_score": 87,
        "match_reasons": [
            "Advanced technical skills well-suited for staff level",
            "Experience with modern tech stack",
            "Self-starter attitude matches startup culture",
            "Cross-functional experience valuable",
        ],
        "salary_range": {"min": 180000, "max": 250000},
        "requirements_match": 85,
        "culture_fit": 92,
        "growth_potential": 95,
        "application_strategy": {
            "resume_highlights": ["End-to-end project ownership", "Technical innovation", "Problem-solving"],
            "cover_letter_points": ["Startup experience", "Technical leadership", "Business impact"],
            "interview_prep": ["Technical depth", "Business acumen", "Growth mindset"],
        },
    },
]

# Sample API responses
SAMPLE_API_RESPONSES = {
    "skill_analysis": SAMPLE_SKILL_ANALYSIS,
    "job_matches": {"matches": SAMPLE_JOB_MATCHES, "total_count": 25},
    "coaching_response": SAMPLE_COACHING_RESPONSES["career_transition"],
    "profile_analytics": {
        "profile_completion": 85,
        "skill_coverage": 78,
        "career_alignment": 82,
        "market_readiness": 78,
        "last_updated": "2024-01-15T10:30:00Z",
        "improvement_suggestions": [
            "Add more details to work experience achievements",
            "Include quantifiable impact metrics",
            "Expand technical skills documentation",
            "Add project portfolio links",
        ],
    },
}


def get_sample_resume_text(format_type: str = "txt") -> str:
    """Get sample resume text in specified format."""
    if format_type == "txt":
        return SAMPLE_RESUME_TXT
    if format_type == "json":
        return str(SAMPLE_RESUME_JSON)
    return SAMPLE_RESUME_TXT


def get_sample_job_description(job_type: str = "senior_engineer") -> dict[str, Any]:
    """Get sample job description by type."""
    job_mapping = {
        "senior_engineer": SAMPLE_JOB_DESCRIPTIONS[0],
        "data_scientist": SAMPLE_JOB_DESCRIPTIONS[1],
        "engineering_manager": SAMPLE_JOB_DESCRIPTIONS[2],
    }
    return job_mapping.get(job_type, SAMPLE_JOB_DESCRIPTIONS[0])


def get_sample_coaching_response(topic: str) -> dict[str, Any]:
    """Get sample coaching response by topic."""
    return SAMPLE_COACHING_RESPONSES.get(topic, SAMPLE_COACHING_RESPONSES["skill_development"])


def get_sample_api_response(response_type: str) -> dict[str, Any]:
    """Get sample API response by type."""
    return SAMPLE_API_RESPONSES.get(response_type, {})
