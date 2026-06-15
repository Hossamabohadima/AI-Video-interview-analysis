import os
import json
from dotenv import load_dotenv, find_dotenv
from openai import AsyncOpenAI
from ..schemas.video import Scores

# Automatically find and load the .env file
load_dotenv(find_dotenv())

# Initialize the Groq client
client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

async def video_report(scores: Scores, analysis_data: dict) -> str:
    """Generates a personalized interview report for a single video."""
    scores_dict = scores.model_dump()
    
    prompt = f"""
    You are an expert HR recruiter and behavioral interview coach evaluating a candidate's video interview.
    Analyze the AI-extracted performance scores and raw model analysis data below.
    
    ### 1. Candidate Scores (Scale: 0.0 to 1.0):
    {json.dumps(scores_dict, indent=2)}

    ### 2. Detailed Model Outputs:
    {json.dumps(analysis_data, indent=2)}

    ### Required Output Format (Use Markdown):
    1. **Performance Overview**: A brief paragraph explaining what the candidate is doing based on the scores.
    2. **Key Strengths**: Highlight the areas where they scored the highest.
    3. **Actionable Tips**: Provide 3-4 specific, practical tips they can use to fix their weaknesses.
    """

    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a professional, empathetic, and objective AI interview coach."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise ValueError(f"Failed to generate video report from LLM: {str(e)}")


async def compare_between_reports(comparison_data: dict) -> str:
    """Compares multiple interview videos and determines the best performance."""
    prompt = f"""
    You are an expert HR recruiter comparing a candidate's performance across multiple video interviews.
    
    ### Comparison Data:
    {json.dumps(comparison_data, indent=2)}

    ### Required Output Format (Use Markdown):
    1. **Comparison Summary**: Briefly explain the main differences between the videos.
    2. **Detailed Breakdown**: Compare their energy, fluency, and facial expressions across the attempts.
    3. **The Winner**: Explicitly state which video was better overall and justify *why* using the data.
    4. **Next Steps**: One final piece of advice for their next interview based on the comparison.
    """

    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an analytical and decisive HR recruiter."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise ValueError(f"Failed to generate comparison report from LLM: {str(e)}")