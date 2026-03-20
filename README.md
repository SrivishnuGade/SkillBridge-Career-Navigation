# Skill-Bridge Career Navigator

#### Candidate Name: Srivishnu Gade
#### Scenario Chosen: 2. Skill-Bridge Career Navigator
#### Estimated Time Spent: 4.5 hours
#### Video Presentation: https://vimeo.com/1175450813?share=copy&fl=sv&fe=ci

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



## Design Documentation

### 1. Data Modeling (Graph vs. Relational)
At the core of this project is a **Neo4j Graph Database**. We chose a graph structure over traditional SQL because career navigation is fundamentally a topological problem. Mapping academic prerequisites involves deep, multi-level traversing (e.g., finding the foundations of Machine Learning) which in SQL would require expensive, recursive Joins. Neo4j allows us to perform native **Transitive Traversal** with a single Cypher query.

**Node Schema:**
- **(Skill)**: The atomic unit of competence (contains `name`, `category`, `course_url`).
- **(User)**: Represents an individual (identified by session ID).
- **(Role)**: A job target (e.g., "Full Stack Developer").
- **(Subject)**: An academic course (e.g., "Data Structures").

**Relationship Schema:**
- `(Skill)-[:HAS_PREREQUISITE]->(Skill)`: Forms the prerequisite roadmap.
- `(User)-[:HAS_SKILL {rating, liked}]->(Skill)`: Tracks possession and confidence.
- `(Role)-[:REQUIRES_SKILL]->(Skill)`: Maps market requirements.

### 2. Core Data Flow
1. **Extraction (PDF -> AI)**: Unstructured syllabi/resumes are parsed via `LLaMA 3` (Groq AI).
2. **Normalization**: Extracted skills are normalized against a canonical Neo4j dictionary to prevent duplication and case-sensitivity bugs.
3. **Graph Analysis**: Cypher queries calculate the difference set between a `Role`’s required skills and a `User`’s owned skills.
4. **Interactive UI**: The gap is visualized through **PyVis Network Graphs** and actionable learning roadmaps.

### 3. AI Strategy & Resilience
- **LLM Selection**: We utilize `llama-3.1-8b` for speed and `llama-3.3-70b` for complex entity extraction.
- **Fail-Safe Mechanism**: Every AI call is wrapped in a robust fallback layer. If the API key is missing or the JSON is malformed, the system returns a rule-based dictionary of standard tech skills, ensuring zero downtime for the user.

## System Architecture & Tech Stack
- **Graph Database**: Neo4j (Topological prerequisite mapping and native graph gap analysis).
- **AI Integration**: Groq AI (LLaMA 3.1/3.3) for resume/syllabus/JD parsing and mock interviews.
- **Frontend / UI**: Streamlit with interactive PyVis network graph visualizations.

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
