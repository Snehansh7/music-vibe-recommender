import os
import json
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv # to protect your api key, allows us to store that sensistive info in a separate hidden file

load_dotenv() # this looks for .env file and loads the variable
app = Flask(__name__)

# Essential: This specific import allows us to use Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('models/gemini-3-flash-preview')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_music():
    data = request.json
    
    # We tell Gemini exactly how to act and what format to use
    system_prompt = (
        "You are an elite music scout. Your goal is to find songs that match a specific vibe. "
        "IMPORTANT: You must respond ONLY with a JSON array of 4 objects. "
        "Format: [{\"title\": \"...\", \"artist\": \"...\", \"vibe_desc\": \"...\"}]"
    )

    user_filters = (
        f"Find songs with these traits: "
        f"Genre: {data.get('genre')}, "
        f"Popularity Level: {data.get('streams')} (If 'Underground', find songs with very low play counts), "
        f"Energy: {data.get('energy')}, "
        f"Mood: {data.get('mood')}. "
        "Make the vibe_desc poetic and short."
    )

    try:
        response = model.generate_content(f"{system_prompt}\n\n{user_filters}")
        
        # This cleans up any extra text the AI might accidentally add
        text_response = response.text.strip()
        if text_response.startswith("```json"):
            text_response = text_response.replace("```json", "").replace("```", "").strip()
        elif text_response.startswith("```"):
            text_response = text_response.replace("```", "").strip()
        
        recommendations = json.loads(text_response)
        return jsonify({"recommendations": recommendations})
    
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return jsonify({"error": "The music gods are silent. Check your API key."}), 500

if __name__ == '__main__':
    app.run(debug=True)