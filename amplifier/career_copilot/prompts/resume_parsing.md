# Resume Parsing Prompt Template

## System Prompt
You are an expert resume parser and career analyst. Your task is to extract structured information from resume text and organize it into a comprehensive, accurate resume data structure.

## Context
This prompt is used by the AI Career Copilot service to parse resumes in various formats (PDF, DOCX, TXT, etc.) and convert them into structured data that can be used for skill analysis, job matching, and career coaching.

## Variables
- `resume_text`: The raw text extracted from the resume file
- `filename`: The original filename (for context)
- `user_context`: Any additional context about the user's goals or preferences

## Prompt Template

```
Parse the following resume text and extract structured information. Return valid JSON that matches the ResumeData schema.

Resume text from {filename}:
{resume_text}

{user_context}

Extract and return JSON with this structure:
{
    "personal_info": {
        "name": "Full Name",
        "email": "email@example.com",
        "phone": "+1-555-0123",
        "location": "City, State",
        "linkedin": "linkedin.com/in/username",
        "github": "github.com/username"
    },
    "summary": "Professional summary or objective statement",
    "work_experience": [
        {
            "company": "Company Name",
            "position": "Job Title",
            "location": "City, State",
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD" or null if current,
            "is_current": true/false,
            "description": "Role description and responsibilities",
            "achievements": ["achievement 1", "achievement 2"],
            "skills_used": [
                {
                    "name": "Skill Name",
                    "level": "beginner|intermediate|advanced|expert",
                    "years_experience": 2.5
                }
            ],
            "team_size": 5,
            "projects": ["Project 1", "Project 2"]
        }
    ],
    "education": [
        {
            "institution": "University Name",
            "degree": "Degree Type",
            "field_of_study": "Major",
            "location": "City, State",
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD",
            "gpa": 3.5,
            "honors": ["Dean's List", "Magna Cum Laude"],
            "relevant_coursework": ["Course 1", "Course 2"],
            "thesis": "Thesis Title",
            "activities": ["Activity 1", "Activity 2"]
        }
    ],
    "skills": [
        {
            "name": "Skill Name",
            "level": "beginner|intermediate|advanced|expert",
            "years_experience": 3.0,
            "last_used": "YYYY-MM-DD",
            "context": "Context where skill was used",
            "certifications": ["Certification 1"]
        }
    ],
    "certifications": [
        {
            "name": "Certification Name",
            "issuer": "Issuing Organization",
            "date": "YYYY-MM-DD",
            "expiry_date": "YYYY-MM-DD",
            "credential_id": "ID123"
        }
    ],
    "languages": [
        {
            "language": "English",
            "proficiency": "native|fluent|proficient|conversational",
            "certifications": ["TOEFL score: 110"]
        }
    ],
    "projects": [
        {
            "name": "Project Name",
            "description": "Project description",
            "technologies": ["tech1", "tech2"],
            "url": "https://project-url.com",
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD",
            "highlights": ["Highlight 1", "Highlight 2"]
        }
    ],
    "publications": [
        {
            "title": "Publication Title",
            "authors": ["Author 1", "Author 2"],
            "journal": "Journal Name",
            "date": "YYYY-MM-DD",
            "doi": "DOI number",
            "url": "https://publication-url.com"
        }
    ],
    "volunteer_work": [
        {
            "organization": "Organization Name",
            "position": "Volunteer Role",
            "location": "City, State",
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD",
            "description": "Volunteer activities and impact",
            "achievements": ["Achievement 1"]
        }
    ],
    "interests": ["Interest 1", "Interest 2", "Interest 3"],
    "references_available": true,
    "last_updated": "YYYY-MM-DDTHH:MM:SS"
}

## Guidelines:

1. **Extract Only What's Present**: Only include information that is clearly stated in the resume. Do not invent or assume information.

2. **Date Format**: Always use YYYY-MM-DD format for dates. If only a year is provided, use YYYY-01-01.

3. **Current Positions**: For current employment, set is_current to true and end_date to null.

4. **Skill Levels**:
   - beginner: 0-1 year experience
   - intermediate: 1-3 years experience
   - advanced: 3-7 years experience
   - expert: 7+ years experience

5. **Years of Experience**: Calculate based on dates provided or use reasonable estimates.

6. **Contact Information**: Extract email, phone, LinkedIn, GitHub, and other professional profiles.

7. **Achievements**: Look for bullet points, metrics, and quantifiable results.

8. **Projects**: Include both professional and personal projects with technologies used.

9. **Education**: Extract degree type, field of study, dates, GPA, honors, and relevant coursework.

10. **Quality Assurance**: Ensure all extracted information is accurate and properly formatted.

## Error Handling:
- If the resume text is unclear or incomplete, do your best to extract what you can.
- If certain sections are missing, return empty arrays for those sections.
- Always return valid JSON even if some data is missing.

## Output Format:
Return only the JSON object without any additional text or markdown formatting.
```

## Usage Notes
- This prompt is designed to work with resumes in any text format
- The output should be compatible with the ResumeData Pydantic model
- Use this prompt with retry mechanisms and defensive parsing for best results
- Consider context about the user's career goals when available