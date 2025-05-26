# Tutor AI – Multi-Agent System with Google Generative AI

A lightweight multi-agent tutor system built with Flask and Google's Generative AI. It leverages a custom agent framework (`google_adk`) and provides tutoring support via AI-driven agents.

# Features

- Multi-agent architecture ( Math Agent, Physics Agent)
- Google Generative AI (Gemini) integration
- Simple REST API with Flask
- Secure key management using `.env`

# Tech Stack

- Python 3.8+
- Flask
- google-generativeai
- Custom agent system via `google_adk`
- Web deployment ready (e.g., Render, Railway, etc.)

---

# Components:

1. Tutor Agent (Main) – Routes the user's question to the appropriate sub-agent.
2. Math Agent – Specialized in solving and explaining mathematics-related queries using the Gemini API and a built-in calculator tool.
3. Physics Agent – Handles physics-related questions with Gemini responses and a constant lookup tool.
4. Tools – Agents can invoke tools like calculators or constant fetchers to assist in generating grounded, accurate responses.

# Flow:
# 1. Clone the Repository


git clone https://github.com/mridukarir/Tutor_Agent_AI.git
cd tutor-ai

2. Create a Virtual Environment 
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

3. Install Dependencies
Make sure libs/google_adk-1.0.0-py3-none-any.whl exists. Then install:

bash
Copy code
pip install -r requirements.txt


4. Create a .env file in the root directory:

GOOGLE_API_KEY=your_google_genai_api_key




