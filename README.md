# Skill-Bridge Career Navigator

Candidate Name: Srivishnu Gade
Scenario Chosen: 2. Skill-Bridge Career Navigator
Estimated Time Spent: 4.5 hours
Video Presentation: https://vimeo.com/1175450813?share=copy&fl=sv&fe=ci

## Quick Start
### Prerequisites:
- Python 3.9+ (or `conda` environment)
- Neo4j Database (Local Desktop or AuraDB) running on `bolt://localhost:7687`
- Groq API Key

### Run Commands:
```bash
# Setup environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your Neo4j credentials and Groq API key

# Seed the database with synthetic data
python -m backend.seed

# Run the Streamlit Application
streamlit run app.py
```

### Test Commands:
```bash
pytest tests/
```

## AI Disclosure
- **Did you use an AI assistant (Copilot, ChatGPT, etc.)?** Yes
- **How did you verify the suggestions?** I verified AI-generated logic and dependencies. Streamlit commands were double-checked against the official documentation to handle state properly. Cypher queries were verified to ensure valid topological parsing for the prerequisite graphs.
- **Give one example of a suggestion you rejected or changed:** The AI initially suggested pulling the entire graph into memory via Python for prerequisite traversal. I rejected this and changed it to utilize Neo4j's native graph traversal `MATCH path = (s)-[:HAS_PREREQUISITE*]->(pre)` to leverage the Graph Database capabilities properly.

## Tradeoffs & Prioritization
- **What did you cut to stay within the 4–6 hour limit?**
  - Persistent User Database: Authentication and saving user history/roadmaps across sessions was skipped. The demo uses Streamlit's `session_state` to mock a logged-in user experience.
  - Complex NLP models locally: I routed resume parsing through the GroqAI API for speed instead of building a local NLP pipeline.
- **What would you build next if you had more time?**
  - Real-world ingestion pipeline pulling job postings directly from LinkedIn/Glassdoor to update the skill graph in real-time.
- **Known limitations:**
  - The AI mock interviewer generates questions but does not yet evaluate the user's answers.
  - AI extraction might hallucinate or miss niche tools if not explicitly prompted against an exhaustive dictionary.
