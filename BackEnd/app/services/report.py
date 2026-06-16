import json
from ..schemas.video import Scores



async def video_report(Groq_client,scores: Scores, analysis_data: dict) -> str:
    """Generates a personalized interview report for a single video."""
    scores_dict = scores.model_dump()
    
    prompt = f"""
    You are an expert Video interview analyzer and behavioral interview coach evaluating a candidate's video interview.
    Analyze the AI-extracted performance scores and raw model analysis data below.
    
    1. Candidate Scores (Scale: 0.0 to 1.0):
    {json.dumps(scores_dict, indent=2)}

    2. Detailed Model Outputs:
    {analysis_data}

    Required Output Format (Use Markdown):
    1. Performance Overview: A brief paragraph explaining what the candidate is doing based on the scores.
    2. Key Strengths: Highlight the areas where they scored the highest.
    3. Actionable Tips: Provide 3-4 specific, practical tips they can use to fix their weaknesses.

    don't add any symbols like # or * or - or 1. or 2. or emojis in the output, just plain text with newlines between sections.

    """

    try:
        response = await Groq_client.chat.completions.create(
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


async def compare_between_reports(Groq_client, comparison_data: dict) -> str:
    """Compares multiple interview videos and determines the best performance."""
    prompt = f"""
    You are an expert Video interview analyzer comparing a candidate's performance across multiple video interviews.
    
    Comparison Data:
    {json.dumps(comparison_data, indent=2)}

    Required Output Format (Use Markdown):
    2. Detailed Breakdown: Compare their energy, fluency, and facial expressions across the attempts.
    1. Comparison Summary: Briefly explain the main differences between the videos.
    3. The Winner: Explicitly state which video was better overall and justify why using the data.
    4. Next Steps: One final piece of advice for their next interview based on the comparison.

    don't add any symbols like # or * or - or 1. or 2. or emojis in the output, just plain text with newlines between sections.
    """

    try:
        response = await Groq_client.chat.completions.create(
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