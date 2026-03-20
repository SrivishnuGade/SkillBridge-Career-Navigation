import pytest
from backend.ai import extract_skills_from_resume, generate_mock_interview_question, FALLBACK_SKILLS
import os

def test_extract_skills_fallback():
    """
    Edge case: If the resume text is complete garbage or AI fails, 
    the system should gracefully fallback to the hardcoded list without crashing.
    """
    # Force fallback by manipulating key if needed, or by sending garbage 
    # if the key is invalid in the CI environment, it naturally falls back.
    skills = extract_skills_from_resume("This is not a resume.")
    
    # Assert returning list of skills
    assert isinstance(skills, list)
    assert len(skills) > 0

def test_mock_interview_generation():
    """
    Happy Path / Edge Path: Generating an interview question.
    """
    skill = "Python"
    question, answer = generate_mock_interview_question(skill)
    
    assert isinstance(question, str)
    assert isinstance(answer, str)
    assert len(question) > 10 # Should be a reasonably sized question
    assert len(answer) > 5
