# climate_tracker/utils.py
import re
import google.generativeai as genai
from google.cloud import aiplatform
from django.conf import settings  # To use Django settings for API keys
from .forms import UserActivityForm, GreenActionSimulatorForm
import json
from datetime import timedelta
from django.utils import timezone

# Configure Gemini API
def configure_gemini():
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        return genai.GenerativeModel('gemini-2.0-flash')
    except Exception as e:
        raise ConnectionError(f"Failed to configure Gemini API: {e}")

model = configure_gemini()

def calculate_carbon_footprint(user_input):
    """
    Uses Google Gemini API to calculate carbon footprint based on user input.
    Parses the response into a structured format.
    """
    try:
        # Construct the prompt for Gemini
        prompt = f"Calculate the carbon footprint for the following activities: {user_input}. Provide the result as a numeric value in kg CO2e."

        # Simulate Gemini API response (replace this with actual API call)
        response = model.generate_content(prompt)

        # Parse the response to extract the numeric value
        match = re.search(r'(\d+(\.\d+)?)\s*kg\s*CO2e', response.text, re.IGNORECASE)
        if not match:
            raise ValueError("Unable to parse carbon footprint from response.")

        # Extract the numeric value
        carbon_footprint = float(match.group(1))
        return carbon_footprint

    except Exception as e:
        raise ValueError(f"Error calculating carbon footprint: {e}")


def calculate_sustainability_score(user_activities):
    """
    Uses Google Gemini API to calculate the sustainability score based on user activities.
    Parses the response into a structured format.
    """
    # Prepare input for Gemini API
    activity_summary = "\n".join([
        f"Transportation: {activity.transportation}, Diet: {activity.diet}, Energy Usage: {activity.energy_usage}"
        for activity in user_activities
    ])
    prompt = (
        f"Calculate a sustainability score (0-100) for the following activities:\n{activity_summary}\n"
        "Provide a detailed breakdown of the score and suggestions for improvement."
    )

    # Simulate Gemini API response (replace this with actual API call)
    response = model.generate_content(prompt)  # This returns an object
    response_text = response.text if hasattr(response, "text") else str(response)  # Extract text

    # Parse the response
    parsed_data = {
        'score': None,
        'breakdown': [],
        'suggestions': []
    }

    # Extract the sustainability score
    score_match = re.search(r'score\s*:\s*(\d+)', response_text, re.IGNORECASE)
    if score_match:
        parsed_data['score'] = int(score_match.group(1))

    # Extract the breakdown
    breakdown_matches = re.findall(r'(\w+)\s*:\s*(\d+)', response_text, re.IGNORECASE)
    if breakdown_matches:
        parsed_data['breakdown'] = [{'category': match[0], 'value': int(match[1])} for match in breakdown_matches]

    # Extract suggestions
    suggestion_matches = re.findall(r'-\s*(.+)', response_text, re.IGNORECASE)
    if suggestion_matches:
        parsed_data['suggestions'] = suggestion_matches

    return parsed_data

def format_chart_data(user_activities):
    """
    Formats historical data into a structure suitable for a usage vs. score line graph.
    Limits the data to the most recent 30 days or 50 activities.
    """
    # Filter activities to the last 30 days
    cutoff_date = timezone.now().date() - timedelta(days=30)
    recent_activities = user_activities.filter(date__gte=cutoff_date).order_by('-date')[:50]

    chart_data = [
        {
            'date': activity.date.strftime('%Y-%m-%d'),
            'energy_usage': activity.energy_usage,
            'score': calculate_sustainability_score([activity])['score'] or 0  # Default to 0 if no score is available
        }
        for activity in recent_activities
    ]
    return json.dumps(chart_data)

import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize conversation history
conversation_history = []

def generate_chat_response(user_message):
    global conversation_history

    try:
        # Step 1: Configure the API
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')

        # Step 2: Add user message to history
        conversation_history.append(f"User: {user_message}")

        # Step 3: Limit conversation history to the last 5 messages
        conversation_history = conversation_history[-5:]

        # Step 4: Build the prompt with history
        prompt = f"""
        You are EcoMate Bot, an AI assistant focused on tackling climate change through innovation and collaboration.
        Below is the conversation history:
        {'\n'.join(conversation_history)}
        Now, respond to the following user query:
        User: {user_message}
        """

        logging.debug(f"Sending prompt to Gemini API: {prompt}")

        # Step 5: Generate a response
        response = model.generate_content(prompt)
        assistant_response = response.text

        # Step 6: Add assistant response to history
        conversation_history.append(f"{assistant_response}")

        logging.debug(f"Received response from Gemini API: {assistant_response}")
        return assistant_response

    except Exception as e:
        # Log the error and re-raise it
        logging.error(f"Error in generate_chat_response: {str(e)}")
        raise  # Re-raise the exception to propagate it to the view