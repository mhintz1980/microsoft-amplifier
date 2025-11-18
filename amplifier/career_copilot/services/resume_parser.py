"""
Resume Parser Service

Handles parsing of resumes from various formats (PDF, DOCX, TXT, JSON)
and extracts structured resume data using AI-powered analysis.
"""

import json
import logging
import re
from datetime import UTC
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Union

import pdfplumber
from docx import Document

from ...ccsdk_toolkit.defensive.llm_parsing import parse_llm_json
from ...ccsdk_toolkit.defensive.retry_patterns import retry_with_feedback
from ..models.resume_data import ResumeData

logger = logging.getLogger(__name__)


class ResumeParseError(Exception):
    """Custom exception for resume parsing errors."""

    pass


class ResumeParser:
    """Service for parsing resumes from various formats into structured data."""

    def __init__(self, claude_client=None):
        """Initialize resume parser with optional Claude client for AI analysis."""
        self.claude_client = claude_client
        self.supported_formats = {".pdf", ".docx", ".txt", ".json", ".md"}

    async def parse_resume(self, file_path: Union[str, Path]) -> ResumeData:
        """Parse resume from file and return structured ResumeData.

        Args:
            file_path: Path to resume file

        Returns:
            ResumeData: Structured resume information

        Raises:
            ResumeParseError: If parsing fails
            ValueError: If file format is not supported
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise ResumeParseError(f"Resume file not found: {file_path}")

        if file_path.suffix.lower() not in self.supported_formats:
            raise ValueError(
                f"Unsupported file format: {file_path.suffix}. Supported formats: {self.supported_formats}"
            )

        try:
            # Extract raw text based on file format
            raw_text = await self._extract_text(file_path)

            # Parse structured data from text
            if self.claude_client:
                resume_data = await self._ai_parse_resume(raw_text, file_path.name)
            else:
                resume_data = await self._rule_based_parse_resume(raw_text, file_path.name)

            # Validate and return
            return ResumeData(**resume_data)

        except Exception as e:
            logger.error(f"Failed to parse resume {file_path}: {e}")
            raise ResumeParseError(f"Resume parsing failed: {str(e)}")

    async def _extract_text(self, file_path: Path) -> str:
        """Extract text from resume file based on format."""
        try:
            if file_path.suffix.lower() == ".pdf":
                return await self._extract_pdf_text(file_path)
            if file_path.suffix.lower() == ".docx":
                return await self._extract_docx_text(file_path)
            if file_path.suffix.lower() in [".txt", ".md"]:
                return await self._extract_text_text(file_path)
            if file_path.suffix.lower() == ".json":
                return await self._extract_json_text(file_path)
            raise ValueError(f"Unsupported format: {file_path.suffix}")
        except Exception as e:
            raise ResumeParseError(f"Failed to extract text from {file_path}: {str(e)}")

    async def _extract_pdf_text(self, file_path: Path) -> str:
        """Extract text from PDF file using pdfplumber."""
        text_parts = []

        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
        except Exception as e:
            raise ResumeParseError(f"Failed to extract PDF text: {str(e)}")

        return "\n\n".join(text_parts)

    async def _extract_docx_text(self, file_path: Path) -> str:
        """Extract text from DOCX file using python-docx."""
        try:
            # type: ignore[arg-type]
            # type: ignore[arg-type]
            doc = Document(file_path)  # type: ignore[arg-type]
            text_parts = []

            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text.strip())

            return "\n\n".join(text_parts)
        except Exception as e:
            raise ResumeParseError(f"Failed to extract DOCX text: {str(e)}")

    async def _extract_text_text(self, file_path: Path) -> str:
        """Extract text from plain text or markdown file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, encoding="latin-1") as f:
                    return f.read()
            except Exception as e:
                raise ResumeParseError(f"Failed to read text file: {str(e)}")

    async def _extract_json_text(self, file_path: Path) -> str:
        """Extract and format text from JSON resume format."""
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            # Convert JSON to readable format for AI parsing
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ResumeParseError(f"Failed to read JSON file: {str(e)}")

    async def _ai_parse_resume(self, raw_text: str, filename: str) -> dict[str, Any]:
        """Parse resume text using AI (Claude) for intelligent extraction."""
        if not self.claude_client:
            logger.warning("Claude client not available, falling back to rule-based parsing")
            return await self._rule_based_parse_resume(raw_text, filename)

        prompt = f"""
Parse the following resume text and extract structured information. Return valid JSON that matches the ResumeData schema.

Resume text:
{raw_text}

Extract and return JSON with this structure:
{{
    "personal_info": {{
        "name": "Full Name",
        "email": "email@example.com",
        "phone": "+1-555-0123",
        "location": "City, State",
        "linkedin": "linkedin.com/in/username",
        "github": "github.com/username"
    }},
    "summary": "Professional summary or objective statement",
    "work_experience": [
        {{
            "company": "Company Name",
            "position": "Job Title",
            "location": "City, State",
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD" or null if current,
            "is_current": true/false,
            "description": "Role description",
            "achievements": ["achievement 1", "achievement 2"],
            "skills_used": [
                {{
                    "name": "Skill Name",
                    "level": "beginner|intermediate|advanced|expert",
                    "years_experience": 2.5
                }}
            ]
        }}
    ],
    "education": [
        {{
            "institution": "University Name",
            "degree": "Degree Type",
            "field_of_study": "Major",
            "location": "City, State",
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD",
            "gpa": 3.5
        }}
    ],
    "skills": [
        {{
            "name": "Skill Name",
            "level": "beginner|intermediate|advanced|expert",
            "years_experience": 3.0
        }}
    ],
    "certifications": [
        {{
            "name": "Certification Name",
            "issuer": "Issuing Organization",
            "date": "YYYY-MM-DD",
            "expiry_date": "YYYY-MM-DD"
        }}
    ],
    "languages": [
        {{
            "language": "English",
            "proficiency": "native|fluent|proficient|conversational"
        }}
    ],
    "projects": [
        {{
            "name": "Project Name",
            "description": "Project description",
            "technologies": ["tech1", "tech2"],
            "url": "https://project-url.com"
        }}
    ]
}}

Important guidelines:
1. Use null for missing dates or current positions
2. Estimate dates if not clearly specified (use reasonable defaults)
3. Infer skill levels from context and experience descriptions
4. Extract only information that is clearly present in the resume
5. Ensure all dates are in YYYY-MM-DD format
6. Make reasonable estimates for years of experience based on job dates
"""

        try:
            # Use retry with feedback for robust AI parsing
            result = await retry_with_feedback(
                func=lambda: self._call_claude_for_parsing(prompt), prompt=prompt, max_retries=3
            )

            if not result:
                raise ResumeParseError("AI parsing returned empty result")

            # Parse the JSON response
            parsed_data = parse_llm_json(result)
            if not parsed_data:
                raise ResumeParseError("Failed to parse AI response as JSON")

            return parsed_data

        except Exception as e:
            logger.error(f"AI parsing failed: {e}")
            logger.info("Falling back to rule-based parsing")
            return await self._rule_based_parse_resume(raw_text, filename)

    async def _call_claude_for_parsing(self, prompt: str) -> str:
        """Call Claude API for resume parsing."""
        try:
            response = await self.claude_client.query(prompt)  # type: ignore[assignment]

            # Collect response content
            result = ""
            async for message in response:
                if hasattr(message, "content") and isinstance(message.content, list):
                    for block in message.content:
                        if hasattr(block, "text"):
                            result += block.text
                elif hasattr(message, "text"):
                    result += message.text

            return result
        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            raise

    async def _rule_based_parse_resume(self, raw_text: str, filename: str) -> dict[str, Any]:
        """Parse resume using rule-based extraction as fallback."""
        logger.info("Using rule-based resume parsing")

        # Initialize result structure
        result = {
            "personal_info": {},
            "summary": None,
            "work_experience": [],
            "education": [],
            "skills": [],
            "certifications": [],
            "languages": [],
            "projects": [],
            "volunteer_work": [],
            "interests": [],
            "publications": [],
            "last_updated": datetime.now().isoformat(),
        }

        # Split text into lines for processing
        lines = raw_text.split("\n")

        # Extract basic information using patterns
        result["personal_info"] = self._extract_personal_info(lines)
        result["summary"] = self._extract_summary(lines)
        result["work_experience"] = self._extract_work_experience(lines)
        result["education"] = self._extract_education(lines)
        result["skills"] = self._extract_skills(lines)

        return result

    def _extract_personal_info(self, lines: list[str]) -> dict[str, Any]:
        """Extract personal information from resume lines."""
        personal_info = {}

        # Look for email patterns
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        for line in lines:
            email_match = re.search(email_pattern, line)
            if email_match:
                personal_info["email"] = email_match.group()
                break

        # Look for phone patterns
        phone_pattern = r"(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})"
        for line in lines:
            phone_match = re.search(phone_pattern, line)
            if phone_match:
                personal_info["phone"] = phone_match.group()
                break

        # Look for LinkedIn
        linkedin_pattern = r"linkedin\.com/in/[\w-]+"
        for line in lines:
            linkedin_match = re.search(linkedin_pattern, line.lower())
            if linkedin_match:
                personal_info["linkedin"] = "https://" + linkedin_match.group()
                break

        # Look for GitHub
        github_pattern = r"github\.com/[\w-]+"
        for line in lines:
            github_match = re.search(github_pattern, line.lower())
            if github_match:
                personal_info["github"] = "https://" + github_match.group()
                break

        # First non-empty line is likely the name
        for line in lines:
            name = line.strip()
            if name and len(name.split()) >= 2 and len(name) < 50:
                # Likely a name (has at least first and last name)
                personal_info["name"] = name
                break

        return personal_info

    def _extract_summary(self, lines: list[str]) -> str | None:
        """Extract professional summary or objective."""
        summary_keywords = ["summary", "objective", "profile", "about", "overview"]

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in summary_keywords):
                # Collect next few lines as summary
                summary_lines = []
                for j in range(i + 1, min(i + 4, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and not next_line.lower().startswith(("experience", "education", "skills", "work")):
                        summary_lines.append(next_line)
                    elif next_line and next_line.lower().startswith(("experience", "education", "skills", "work")):
                        break

                if summary_lines:
                    return " ".join(summary_lines)

        return None

    def _extract_work_experience(self, lines: list[str]) -> list[dict[str, Any]]:
        """Extract work experience using pattern matching."""
        experience = []
        current_exp = None
        exp_counter = 0

        for line in lines:
            line = line.strip()

            # Look for experience patterns (dates indicate new experience)
            date_pattern = r"(\d{4}|\d{1,2}/\d{4})"
            if re.search(date_pattern, line):
                if current_exp:
                    experience.append(current_exp)

                # Extract dates from the line
                dates = self._extract_dates_from_line(line)

                current_exp = {
                    "company": "",
                    "position": "",
                    "start_date": dates.get("start_date", datetime(2020, 1, 1, tzinfo=UTC)),  # Default to 2020-01-01
                    "end_date": dates.get("end_date", None),
                    "is_current": dates.get("is_current", False),
                    "description": "",
                    "achievements": [],
                    "skills_used": [],
                }
                exp_counter += 1

            # Try to extract position and company
            if current_exp and not current_exp["position"]:
                # This is likely the position and company line
                parts = line.split("|")
                if len(parts) >= 2:
                    current_exp["position"] = parts[0].strip()
                    current_exp["company"] = parts[1].strip()
                else:
                    # Use the line as position if no clear separator
                    current_exp["position"] = line

            # Look for bullet points or achievements
            if current_exp and line.startswith(("•", "-", "*", "·")):
                achievement = line.lstrip("•-*·").strip()
                if achievement:
                    current_exp["achievements"].append(achievement)

        # If no experience was found but we have some work-related content, create a default entry
        if not experience and any("experience" in line.lower() or "work" in line.lower() for line in lines):
            # Create a default experience entry
            default_exp = {
                "company": "Company Name",
                "position": "Position Title",
                "start_date": datetime(2020, 1, 1, tzinfo=UTC),
                "end_date": None,
                "is_current": True,
                "description": "Role description",
                "achievements": [],
                "skills_used": [],
            }
            experience.append(default_exp)

        # Add the last experience if exists
        if current_exp:
            experience.append(current_exp)

        return experience

    def _extract_education(self, lines: list[str]) -> list[dict[str, Any]]:
        """Extract education information."""
        education = []
        current_edu = None

        for line in lines:
            line = line.strip()
            line_lower = line.lower()

            # Look for education indicators
            edu_keywords = ["university", "college", "bachelor", "master", "phd", "degree", "diploma"]
            if any(keyword in line_lower for keyword in edu_keywords):
                if current_edu:
                    education.append(current_edu)

                current_edu = {
                    "institution": line,
                    "degree": "",
                    "field_of_study": "",
                    "start_date": None,
                    "end_date": None,
                    "gpa": None,
                }

        # Add the last education if exists
        if current_edu:
            education.append(current_edu)

        return education

    def _extract_skills(self, lines: list[str]) -> list[dict[str, Any]]:
        """Extract skills from resume."""
        skills = []
        skills_section = False

        for line in lines:
            line_lower = line.lower().strip()

            # Check if we're in the skills section
            if "skills" in line_lower:
                skills_section = True
                continue

            if skills_section and line:
                # Split by common separators
                skill_list = re.split(r"[,;|]", line)
                for skill in skill_list:
                    skill = skill.strip()
                    if skill and len(skill) > 1:
                        skills.append(
                            {
                                "name": skill,
                                "level": "intermediate",  # Default level
                                "years_experience": None,
                            }
                        )

        return skills

    def _extract_dates_from_line(self, line: str) -> dict[str, Any]:
        """Extract start and end dates from a line containing date information."""
        import calendar
        from datetime import datetime

        result = {
            "start_date": datetime(2020, 1, 1, tzinfo=UTC),  # Default start date
            "end_date": None,
            "is_current": False,
        }

        # Common patterns for date ranges
        patterns = [
            r"(\d{1,2})/(\d{4})\s*-\s*(Present|Current|至今)",  # MM/YYYY - Present
            r"(\d{4})\s*-\s*(Present|Current|至今)",  # YYYY - Present
            r"(\d{1,2})/(\d{4})\s*-\s*(\d{1,2})/(\d{4})",  # MM/YYYY - MM/YYYY
            r"(\d{4})\s*-\s*(\d{4})",  # YYYY - YYYY
            r"(\w+)\s+(\d{4})\s*-\s*(Present|Current)",  # Month YYYY - Present
            r"(\w+)\s+(\d{4})\s*-\s*(\w+)\s+(\d{4})",  # Month YYYY - Month YYYY
        ]

        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                groups = match.groups()

                if len(groups) >= 3:
                    # Handle range patterns
                    if groups[2] and groups[2].lower() in ["present", "current", "至今"]:
                        # Current position
                        result["is_current"] = True
                        result["end_date"] = None

                        # Parse start date
                        if "/" in groups[0]:  # MM/YYYY format
                            month, year = int(groups[0]), int(groups[1])
                            result["start_date"] = datetime(year, month, 1, tzinfo=UTC)
                        else:  # YYYY format or Month YYYY
                            if groups[0].isdigit():  # YYYY format
                                result["start_date"] = datetime(int(groups[0]), 1, 1, tzinfo=UTC)
                            else:  # Month YYYY format
                                month_name, year = groups[0], int(groups[1])
                                month_num = list(calendar.month_name).index(month_name.capitalize())
                                if month_num == 0:
                                    month_num = 1  # Default to January if month not found
                                result["start_date"] = datetime(year, month_num, 1, tzinfo=UTC)
                    else:
                        # Completed position with start and end dates
                        start_parts = [groups[0], groups[1]] if "/" in groups[0] else [groups[0]]
                        end_parts = [groups[2], groups[3]] if len(groups) > 3 and "/" in groups[2] else [groups[2]]

                        # Parse start date
                        if len(start_parts) == 2:  # MM/YYYY
                            month, year = int(start_parts[0]), int(start_parts[1])
                            result["start_date"] = datetime(year, month, 1, tzinfo=UTC)
                        else:  # YYYY or Month YYYY
                            if start_parts[0].isdigit():  # YYYY
                                result["start_date"] = datetime(int(start_parts[0]), 1, 1, tzinfo=UTC)
                            else:  # Month YYYY
                                month_name, year = start_parts[0], int(groups[1])
                                month_num = list(calendar.month_name).index(month_name.capitalize())
                                if month_num == 0:
                                    month_num = 1
                                result["start_date"] = datetime(year, month_num, 1, tzinfo=UTC)

                        # Parse end date
                        if len(end_parts) == 2:  # MM/YYYY
                            month, year = int(end_parts[0]), int(end_parts[1])
                            result["end_date"] = datetime(year, month, 1, tzinfo=UTC)
                        else:  # YYYY
                            result["end_date"] = datetime(int(end_parts[0]), 12, 31, tzinfo=UTC)  # End of year

                        result["is_current"] = False

                    break

        return result

    def validate_parsed_data(self, data: dict[str, Any]) -> bool:
        """Validate that parsed data meets minimum requirements."""
        if not data:
            return False

        # Check for at least some basic information
        has_personal_info = bool(data.get("personal_info", {}).get("name"))
        has_experience = bool(data.get("work_experience"))
        has_education = bool(data.get("education"))
        has_skills = bool(data.get("skills"))

        return has_personal_info and (has_experience or has_education or has_skills)

    async def parse_resume_text(self, resume_text: str, filename: str = "resume.txt") -> ResumeData:
        """Parse resume from text content and return structured ResumeData.

        Args:
            resume_text: Raw text content of resume
            filename: Original filename for reference

        Returns:
            ResumeData: Structured resume information

        Raises:
            ResumeParseError: If parsing fails
        """
        if not resume_text or not resume_text.strip():
            raise ResumeParseError("Resume text is empty")

        try:
            if self.claude_client:
                parsed_data = await self._ai_parse_resume(resume_text, filename)
            else:
                parsed_data = await self._rule_based_parse_resume(resume_text, filename)

            if not self.validate_parsed_data(parsed_data):
                raise ResumeParseError("Parsed data validation failed")

            # Convert to ResumeData object
            return ResumeData(**parsed_data)

        except Exception as e:
            logger.error(f"Resume parsing failed: {e}")
            raise ResumeParseError(f"Failed to parse resume: {str(e)}")
