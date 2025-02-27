from openai import OpenAI
import re
import google.generativeai as genai
from google.cloud import aiplatform
from django.conf import settings  # To use Django settings for API keys
from .forms import UserActivityForm, GreenActionSimulatorForm
import json
from datetime import timedelta
from django.utils import timezone
import openai
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Configure OpenAI API
def configure_openai():
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return client
    except Exception as e:
        raise ConnectionError(f"Failed to configure OpenAI API: {e}")

OPENAI_CLIENT = configure_openai()
MODEL_NAME = "gpt-4o-mini"  # Specify the model name

def calculate_carbon_footprint(user_input):
    """
    Uses OpenAI API to calculate carbon footprint based on user input.
    Parses the response into a structured format.
    """
    try:
        # Construct a refined prompt for OpenAI
        prompt = f"""
        Calculate the carbon footprint for the following activities: {user_input}.
        Provide ONLY the result as a numeric value followed by 'kg CO2e'. For example: '12.5 kg CO2e'.
        Do not include any additional explanations or text.
        """
        
        # Call OpenAI API using the updated method
        response = OPENAI_CLIENT.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an expert in environmental sustainability."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        # Extract the response text
        response_text = response.choices[0].message.content.strip()
        logging.debug(f"Raw OpenAI Response: {response_text}")  # Log the raw response for debugging
        
        # Parse the response to extract the numeric value
        match = re.search(r'(\d+(\.\d+)?)\s*kg\s*CO2e', response_text, re.IGNORECASE)
        if not match:
            # Fallback: Extract any numeric value if the format isn't strictly followed
            match = re.search(r'(\d+(\.\d+)?)', response_text)
            if not match:
                raise ValueError("Unable to parse carbon footprint from response.")
        
        # Extract the numeric value
        carbon_footprint = float(match.group(1))
        return carbon_footprint
    except Exception as e:
        logging.error(f"Error calculating carbon footprint: {str(e)}")
        raise ValueError(f"Error calculating carbon footprint: {e}")
    
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
   
def calculate_sustainability_score(user_activities):
    """
    Uses OpenAI API to calculate the sustainability score based on user activities.
    Parses the response into a structured format.
    """
    try:
        # Prepare input for OpenAI API
        activity_summary = "\n".join([
            f"Transportation: {activity.transportation}, Diet: {activity.diet}, Energy Usage: {activity.energy_usage}"
            for activity in user_activities
        ])
        
        prompt = (
            f"Calculate a sustainability score (0-100) for the following activities:\n{activity_summary}\n"
            "Provide a detailed breakdown of the score and suggestions for improvement."
        )
        
        # Call OpenAI API using the updated method
        response = OPENAI_CLIENT.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an expert sustainability analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        # Extract the response text
        response_text = response.choices[0].message.content.strip()
        
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
    except Exception as e:
        raise ValueError(f"Error calculating sustainability score: {e}")
    

# Initialize conversation history
conversation_history = []

def generate_chat_response(user_message):
    global conversation_history
    try:
        # Step 1: Add user message to history
        conversation_history.append({"role": "user", "content": user_message})
        
        # Step 2: Limit conversation history to the last 5 messages
        conversation_history = conversation_history[-5:]
        
        # Step 3: Build the conversation history
        messages = [{"role": "system", "content": "You are EcoMate Bot, an AI assistant focused on tackling climate change through innovation and collaboration."}]
        messages.extend(conversation_history)
        
        logging.debug(f"Sending prompt to OpenAI API: {messages}")
        
        # Step 4: Generate a response using OpenAI API
        response = OPENAI_CLIENT.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=100,
            temperature=0.7
        )
        
        # Extract the assistant's response
        assistant_response = response.choices[0].message.content.strip()
        
        # Step 5: Add assistant response to history
        conversation_history.append({"role": "assistant", "content": assistant_response})
        
        logging.debug(f"Received response from OpenAI API: {assistant_response}")
        return assistant_response
    except Exception as e:
        # Log the error and re-raise it
        logging.error(f"Error in generate_chat_response: {str(e)}")
        raise  # Re-raise the exception to propagate it to the view