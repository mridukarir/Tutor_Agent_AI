import os
import asyncio

from google.genai import types  

from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

import google.generativeai as genai

genai.configure(api_key=api_key)
import requests

def ask_gemini(prompt, model="gemini-2.0-flash"):
    try:
        model = genai.GenerativeModel(model)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini API Error: {e}"

# Tool: Calculator for Math Agent
import re

def calculate(expression: str):
    """
    Safely evaluate a basic math expression (supports +, -, *, /, parentheses).
    """ 
    try:
        # Only allow numbers, operators, and parentheses
        if not re.match(r'^[\d\s\+\-\*/\(\)\.]+$', expression):
            return "Invalid characters in expression."
        return eval(expression, {"__builtins__": {}})
    except Exception as e:
        return f"Error: {e}"

# Improved Physics constant lookup for flexible queries


def extract_constant_name(query: str):
    # Try to extract a known constant from the query, allowing for spaces or underscores
    keywords = [
        "speed of light", "speed_of_light",
        "planck constant", "planck_constant",
        "gravitational constant", "gravitational_constant",
        "elementary charge", "elementary_charge",
        "avogadro number", "avogadro_number",
        "boltzmann constant", "boltzmann_constant",
        "gas constant", "gas_constant",
        "electron mass", "electron_mass",
        "proton mass", "proton_mass"
    ]
    query_lower = query.lower().replace('-', ' ')
    for k in keywords:
        if k in query_lower:
            return k.replace(' ', '_')
    # fallback: extract last word if it matches a constant
    for k in keywords:
        if k.replace('_', ' ') in query_lower:
            return k
    return None

def get_physics_constant(constant_name: str):
    constants = {
        "speed_of_light": 299792458,  # m/s
        "planck_constant": 6.62607015e-34,  # J*s
        "gravitational_constant": 6.67430e-11,  # m^3 kg^-1 s^-2
        "elementary_charge": 1.602176634e-19,  # C
        "avogadro_number": 6.02214076e23,  # mol^-1
        "boltzmann_constant": 1.380649e-23,  # J/K
        "gas_constant": 8.314462618,  # J/(mol·K)
        "electron_mass": 9.10938356e-31,  # kg
        "proton_mass": 1.67262192369e-27,  # kg
    }
    return constants.get(constant_name, "Constant not found.")



class MathAgent:
    def handle(self, query):
        # Try to extract a math expression for calculation
        match = re.search(r"([-+*/().\d\s]+)", query)
        if match:
            expr = match.group(1)
            result = calculate(expr)
            if isinstance(result, (int, float)):
                return f"The result is: {result}"
        # Otherwise, use Gemini for open-ended math questions
        return ask_gemini(f"You are a math expert. Answer this question: {query}")

class PhysicsAgent:
    def handle(self, query):
        # Try to extract a physics constant request
        match = re.search(r"(speed of light|planck constant|gravitational constant|elementary charge|avogadro number|boltzmann constant|gas constant|electron mass|proton mass)", query, re.IGNORECASE)
        if match:
            constant_name = match.group(1).lower().replace(" ", "_")
            return get_physics_constant(constant_name)
        # Otherwise, use Gemini for open-ended physics questions
        return ask_gemini(f"You are a physics expert. Answer this question: {query}")

    tools=[get_physics_constant]

# Tutor Agent: Orchestrates and delegates queries
class TutorAgent:
    def __init__(self, math_agent, physics_agent):
        self.math_agent = MathAgent()
        self.physics_agent = PhysicsAgent()
    
    def classify(self, query):
        math_keywords = ["solve", "calculate", "add", "subtract", "multiply", "divide", "+", "-", "*", "/", "equation", "math"]
        physics_keywords = ["physics", "law", "constant", "speed of light", "planck", "gravitational", "force", "newton", "joule", "energy"]
        q = query.lower()
        if any(word in q for word in math_keywords):
            return "math"
        if any(word in q for word in physics_keywords):
            return "physics"
        return "other"
    
    def handle_query(self, query):
        subject = self.classify(query)
        if subject == "math":
            return self.math_agent.handle(query)
        elif subject == "physics":
            return self.physics_agent.handle(query)
        else:
            # Fallback: Use Gemini for general questions
            return ask_gemini(f"You are a helpful tutor. Answer this question: {query}")

from flask import Flask, request, jsonify
from flask import render_template_string

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Tutor Agent</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f7f7f7; margin: 0; padding: 0; }
        .container { max-width: 600px; margin: 40px auto; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px #ccc; padding: 32px; }
        h2 { color: #2c3e50; }
        label { font-weight: bold; }
        input[type=text] { width: 90%; padding: 10px; margin: 10px 0 20px 0; border: 1px solid #ccc; border-radius: 4px; }
        input[type=submit] { background: #007bff; color: #fff; border: none; padding: 10px 24px; border-radius: 4px; cursor: pointer; font-size: 16px; }
        input[type=submit]:hover { background: #0056b3; }
        .response-box { background: #f1f8e9; border: 1px solid #b2dfdb; border-radius: 4px; padding: 16px; margin-top: 24px; color: #222; }
        .footer { margin-top: 40px; color: #888; font-size: 13px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h2>AI Tutor Agent</h2>
        <form method="post">
            <label for="query">Ask a question:</label><br>
            <input type="text" id="query" name="query" placeholder="e.g. What is the speed of light?" required>
            <input type="submit" value="Ask">
        </form>
        {% if response %}
            <div class="response-box">
                <strong>Response:</strong><br>
                <div style="White-space: pre-wrap;">{{ response }}</div>
            </div>
        {% endif %}
        <div class="footer">&copy; 2025 AI Tutor Agent | Powered by Gemini &amp; Flask</div>
    </div>
</body>
</html>
"""
math_agent = MathAgent()
physics_agent = PhysicsAgent()
tutor = TutorAgent(math_agent, physics_agent)

app = Flask(__name__)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    query = data.get("query", "")
    response = tutor.handle_query(query)
    return jsonify({"response": response})

@app.route("/", methods=["GET", "POST"])
def home():
    response = None
    if request.method == "POST":
        query = request.form.get("query", "")
        response = tutor.handle_query(query)
    return render_template_string(HTML_PAGE, response=response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
