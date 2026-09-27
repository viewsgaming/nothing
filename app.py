from flask import Flask, render_template, request, jsonify
import json
import os
import requests
import re

app = Flask(__name__)

# JSON Data Load karna (Pehle check karega file hai ya nahi)
DATA_FILE = "genshin_wiki_data/Archon_Quests_data.json"
quest_data = {}

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        quest_data = json.load(f)
else:
    print(f"Warning: {DATA_FILE} nahi mila. Pehle data download script run karo.")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search")
def search():
    query = request.args.get("q", "").lower()
    results = []
    
    for title, content in quest_data.items():
        if query in title.lower():
            results.append({"title": title, "content": content})
            
    return jsonify(results)

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.json
    raw_text = data.get("text", "")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"error": "Gemini API key set nahi hai. Terminal me 'export GEMINI_API_KEY=...' run karo."})

    # Raw text ka sirf pehla 3000 characters bhejenge taaki API limit cross na ho
    clean_text = raw_text[:3000]
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    prompt = f"""
    You are an expert Genshin Impact lore master. 
    Summarize the following quest text in natural, conversational Hinglish (Hindi written in English alphabet). 
    Explain it like you are telling a story to a friend. 
    Do not translate fantasy terms like Teyvat, Archon, Abyss Order, etc.
    
    Quest Text:
    {clean_text}
    """
    
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code == 200:
            summary = res.json()["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"summary": summary})
        else:
            return jsonify({"error": f"API Error: {res.status_code}"})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
