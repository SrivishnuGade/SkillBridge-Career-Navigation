import json
import os
from .db import Neo4jConnection

def seed_db():
    conn = Neo4jConnection()
    print("Clearing database...")
    conn.query("MATCH (n) DETACH DELETE n") 
    
    data = {
        "roles": [
            {"title": "Machine Learning Engineer", "description": "Builds and deploys AI models"},
            {"title": "Full Stack Developer", "description": "Handles both frontend and backend development"},
            {"title": "Data Scientist", "description": "Analyzes complex datasets to drive decisions"},
            {"title": "Cloud Architect", "description": "Designs and manages scalable cloud infrastructure"},
            {"title": "DevOps Engineer", "description": "Bridges development and operations via CI/CD and automation"},
            {"title": "Cybersecurity Analyst", "description": "Protects systems and networks from threats"},
            {"title": "Data Engineer", "description": "Builds data pipelines and warehousing solutions"}
        ],
        "skills": [
            # Programming
            {"name": "Python", "category": "Programming"},
            {"name": "JavaScript", "category": "Programming"},
            {"name": "TypeScript", "category": "Programming"},
            {"name": "Java", "category": "Programming"},
            {"name": "Go", "category": "Programming"},
            # Math
            {"name": "Linear Algebra", "category": "Math"},
            {"name": "Statistics", "category": "Math"},
            {"name": "Calculus", "category": "Math"},
            # AI & Data
            {"name": "Machine Learning", "category": "AI"},
            {"name": "Deep Learning", "category": "AI"},
            {"name": "Natural Language Processing", "category": "AI"},
            {"name": "Pandas", "category": "Data"},
            {"name": "Spark", "category": "Data"},
            # Web
            {"name": "React", "category": "Frontend"},
            {"name": "Node.js", "category": "Backend"},
            {"name": "FastAPI", "category": "Backend"},
            {"name": "HTML/CSS", "category": "Frontend"},
            # Cloud/DevOps/DB
            {"name": "AWS", "category": "Cloud"},
            {"name": "Docker", "category": "DevOps"},
            {"name": "Kubernetes", "category": "DevOps"},
            {"name": "CI/CD", "category": "DevOps"},
            {"name": "Linux", "category": "OS"},
            {"name": "SQL", "category": "Database"},
            {"name": "Neo4j", "category": "Database"},
            # Cyber
            {"name": "Network Security", "category": "Security"},
            {"name": "Cryptography", "category": "Security"},
            {"name": "Ethical Hacking", "category": "Security"},
            # Advanced Curriculum Skills
            {"name": "C", "category": "Programming"},
            {"name": "C++", "category": "Programming"},
            {"name": "C#", "category": "Programming"},
            {"name": "Jupyter", "category": "Tools"},
            {"name": "IDLE", "category": "Tools"},
            {"name": "HackerRank", "category": "Tools"},
            {"name": "Icarus Verilog", "category": "Tools"},
            {"name": "GTK Wave", "category": "Tools"},
            {"name": "GCC Compiler", "category": "Tools"},
            {"name": "GDB Debugger", "category": "Tools"},
            {"name": "Matplotlib", "category": "Data"},
            {"name": "Scipy", "category": "Data"},
            {"name": "Seaborn", "category": "Data"},
            {"name": "BeautifulSoup", "category": "Data"},
            {"name": "Numpy", "category": "Data"},
            {"name": "Scikit learn", "category": "Data"},
            {"name": "MERN Technologies", "category": "Frontend"},
            {"name": "JFLAP", "category": "Tools"},
            {"name": "MySQL Workbench", "category": "Database"},
            {"name": "Pytorch", "category": "AI"},
            {"name": "GitHub", "category": "DevOps"},
            {"name": "MS Project", "category": "Tools"},
            {"name": "Jira", "category": "Tools"},
            {"name": "Jenkins", "category": "DevOps"},
            {"name": "Star UML", "category": "Tools"},
            {"name": "Tensorflow", "category": "AI"},
            {"name": "Solr", "category": "Data"},
            {"name": "Wireshark", "category": "Security"},
            {"name": "Cisco Packet Tracker", "category": "Security"},
            {"name": "Metasploit", "category": "Security"},
            {"name": "Arduino IDE", "category": "Tools"}
        ],
        "prerequisites": [
            {"skill": "Machine Learning", "prereq": "Python"},
            {"skill": "Machine Learning", "prereq": "Linear Algebra"},
            {"skill": "Machine Learning", "prereq": "Statistics"},
            {"skill": "Deep Learning", "prereq": "Machine Learning"},
            {"skill": "Deep Learning", "prereq": "Calculus"},
            {"skill": "Natural Language Processing", "prereq": "Deep Learning"},
            {"skill": "React", "prereq": "JavaScript"},
            {"skill": "React", "prereq": "HTML/CSS"},
            {"skill": "Node.js", "prereq": "JavaScript"},
            {"skill": "TypeScript", "prereq": "JavaScript"},
            {"skill": "FastAPI", "prereq": "Python"},
            {"skill": "Pandas", "prereq": "Python"},
            {"skill": "Spark", "prereq": "Python"},
            {"skill": "Spark", "prereq": "SQL"},
            {"skill": "Docker", "prereq": "Linux"},
            {"skill": "Kubernetes", "prereq": "Docker"},
            {"skill": "CI/CD", "prereq": "Docker"},
            # Conceptual Abstract Domain Aliasing (Tools depend on foundational concepts)
            {"skill": "Docker", "prereq": "Cloud"},
            {"skill": "Kubernetes", "prereq": "Cloud"},
            {"skill": "Machine Learning", "prereq": "Ai"},
            {"skill": "Machine Learning", "prereq": "AI"},
            {"skill": "Git", "prereq": "Version Control"},
            {"skill": "Jenkins", "prereq": "Ci/Cd"},
            {"skill": "Jenkins", "prereq": "CI/CD"},
            {"skill": "Jenkins", "prereq": "Sdlc"},
            {"skill": "Jenkins", "prereq": "SDLC"},
            {"skill": "Jenkins", "prereq": "Devops"},
            {"skill": "Jenkins", "prereq": "DevOps"},
            {"skill": "Ethical Hacking", "prereq": "Network Security"},
            {"skill": "Ethical Hacking", "prereq": "Linux"},
            # Advanced Subject Dependencies
            {"skill": "Data Structures & Algorithms", "prereq": "C"},
            {"skill": "Data Structures & Algorithms", "prereq": "C++"},
            {"skill": "Data Structures & Algorithms", "prereq": "Java"},
            {"skill": "Compiler Design", "prereq": "Data Structures & Algorithms"},
            {"skill": "Operating Systems", "prereq": "Data Structures & Algorithms"},
            {"skill": "Operating Systems", "prereq": "C"},
            {"skill": "Computer Networks", "prereq": "Operating Systems"},
            {"skill": "Network Security", "prereq": "Computer Networks"},
            {"skill": "DBMS", "prereq": "Data Structures & Algorithms"},
            {"skill": "DBMS", "prereq": "SQL"},
            {"skill": "Cryptography", "prereq": "Math"},
            {"skill": "Cryptography", "prereq": "Network Security"},
            # Application/Tool Dependencies
            {"skill": "Jupyter Notebook", "prereq": "Python"},
            {"skill": "Jupyter", "prereq": "Python"},
            {"skill": "IDLE", "prereq": "Python"},
            {"skill": "Python IDE", "prereq": "Python"},
            {"skill": "Matplotlib", "prereq": "Python"},
            {"skill": "Numpy", "prereq": "Python"},
            {"skill": "Scipy", "prereq": "Numpy"},
            {"skill": "Seaborn", "prereq": "Matplotlib"},
            {"skill": "Scikit learn", "prereq": "Python"},
            {"skill": "Scikit Learn", "prereq": "Python"},
            {"skill": "Pytorch", "prereq": "Machine Learning"},
            {"skill": "Pytorch", "prereq": "Python"},
            {"skill": "Tensorflow", "prereq": "Machine Learning"},
            {"skill": "Tensorflow", "prereq": "Python"},
            {"skill": "BeautifulSoup", "prereq": "Python"},
            {"skill": "Solr", "prereq": "Java"},
            {"skill": "C++", "prereq": "C"},
            {"skill": "GCC Compiler", "prereq": "C"},
            {"skill": "GDB Debugger", "prereq": "C"},
            {"skill": "Arduino IDE", "prereq": "C++"},
            {"skill": "Arduino Microcontroller", "prereq": "Arduino IDE"},
            {"skill": "Arduino", "prereq": "C++"},
            {"skill": "MERN Technologies", "prereq": "JavaScript"},
            {"skill": "MERN Technologies", "prereq": "React"},
            {"skill": "MERN Technologies", "prereq": "Node.js"},
            {"skill": "Jenkins", "prereq": "CI/CD"},
            {"skill": "Star UML", "prereq": "Object-Oriented Design"},
            {"skill": "Wireshark", "prereq": "Network Security"},
            {"skill": "Cisco Packet Tracker", "prereq": "Network Security"},
            {"skill": "Metasploit", "prereq": "Ethical Hacking"},
            {"skill": "Metasploit", "prereq": "Network Security"},
            {"skill": "MySQL Workbench", "prereq": "SQL"},
            {"skill": "MySQL", "prereq": "SQL"},
            {"skill": "OpenCV", "prereq": "Python"},
            {"skill": "Unity", "prereq": "C#"},
            {"skill": "Git", "prereq": "Linux/Unix OS"},
            {"skill": "GitHub", "prereq": "Git"},
            {"skill": "Solidity", "prereq": "JavaScript"},
            {"skill": "Remix", "prereq": "Solidity"},
            {"skill": "Lex/Flex", "prereq": "C"},
            {"skill": "Lex/flex", "prereq": "C"},
            {"skill": "YACC/Bison", "prereq": "C"},
            {"skill": "Linux/Unix OS", "prereq": "C"},
            {"skill": "Three.js", "prereq": "JavaScript"},
            {"skill": "Tkinter", "prereq": "Python"},
            {"skill": "HTML", "prereq": "Web Technologies"},
            {"skill": "CSS", "prereq": "HTML"},
            {"skill": "Embedded-C", "prereq": "C"},
            {"skill": "Single Board Computer", "prereq": "Embedded-C"},
            {"skill": "Cloud Platforms", "prereq": "Linux/Unix OS"},
            {"skill": "Amazon AWS", "prereq": "Cloud Platforms"},
            {"skill": "AWS", "prereq": "Cloud Platforms"},
            {"skill": "SEED labs", "prereq": "Linux/Unix OS"},
            {"skill": "OpenGL", "prereq": "C++"},
            {"skill": "CAD", "prereq": "Geometry"},
            {"skill": "Shapr3D", "prereq": "CAD"},
            {"skill": "CQL", "prereq": "Database"},
            {"skill": "GanttPro", "prereq": "Project Management"}
        ],
        "courses": [
            {"title": "Python for Beginners", "url": "https://example.com/python", "teaches": "Python"},
            {"title": "Linear Algebra Foundations", "url": "https://example.com/la", "teaches": "Linear Algebra"},
            {"title": "Statistics for Data Science", "url": "https://example.com/stats", "teaches": "Statistics"},
            {"title": "Intro to ML", "url": "https://example.com/ml", "teaches": "Machine Learning"},
            {"title": "Deep Learning Specialization", "url": "https://example.com/dl", "teaches": "Deep Learning"},
            {"title": "React Dev Course", "url": "https://example.com/react", "teaches": "React"},
            {"title": "FastAPI Masterclass", "url": "https://example.com/fastapi", "teaches": "FastAPI"},
            {"title": "SQL Bootcamp", "url": "https://example.com/sql", "teaches": "SQL"},
            {"title": "Docker for DevOps", "url": "https://example.com/docker", "teaches": "Docker"},
            {"title": "Kubernetes Mastery", "url": "https://example.com/k8s", "teaches": "Kubernetes"},
            {"title": "Network Security Fundamentals", "url": "https://example.com/netsec", "teaches": "Network Security"},
            {"title": "AWS Certified Solutions Architect", "url": "https://example.com/aws", "teaches": "AWS"}
        ],
        "role_skills": [
            # ML Engineer
            {"role": "Machine Learning Engineer", "skill": "Python"},
            {"role": "Machine Learning Engineer", "skill": "Deep Learning"},
            {"role": "Machine Learning Engineer", "skill": "Natural Language Processing"},
            {"role": "Machine Learning Engineer", "skill": "SQL"},
            # Full Stack
            {"role": "Full Stack Developer", "skill": "JavaScript"},
            {"role": "Full Stack Developer", "skill": "TypeScript"},
            {"role": "Full Stack Developer", "skill": "React"},
            {"role": "Full Stack Developer", "skill": "Node.js"},
            {"role": "Full Stack Developer", "skill": "SQL"},
            # Data Scientist
            {"role": "Data Scientist", "skill": "Python"},
            {"role": "Data Scientist", "skill": "Pandas"},
            {"role": "Data Scientist", "skill": "Machine Learning"},
            {"role": "Data Scientist", "skill": "SQL"},
            {"role": "Data Scientist", "skill": "Statistics"},
            # Cloud Architect
            {"role": "Cloud Architect", "skill": "AWS"},
            {"role": "Cloud Architect", "skill": "Linux"},
            {"role": "Cloud Architect", "skill": "Docker"},
            {"role": "Cloud Architect", "skill": "Kubernetes"},
            # DevOps
            {"role": "DevOps Engineer", "skill": "Linux"},
            {"role": "DevOps Engineer", "skill": "Docker"},
            {"role": "DevOps Engineer", "skill": "Kubernetes"},
            {"role": "DevOps Engineer", "skill": "CI/CD"},
            {"role": "DevOps Engineer", "skill": "Python"},
            # Cyber
            {"role": "Cybersecurity Analyst", "skill": "Network Security"},
            {"role": "Cybersecurity Analyst", "skill": "Linux"},
            {"role": "Cybersecurity Analyst", "skill": "Cryptography"},
            {"role": "Cybersecurity Analyst", "skill": "Ethical Hacking"},
            # Data Engineer
            {"role": "Data Engineer", "skill": "Python"},
            {"role": "Data Engineer", "skill": "SQL"},
            {"role": "Data Engineer", "skill": "Spark"},
            {"role": "Data Engineer", "skill": "AWS"}
        ]
    }

    print("Inserting Roles...")
    for r in data["roles"]:
        conn.query("CREATE (r:Role {title: $title, description: $description})", r)
        
    course_map = {c["teaches"]: c["url"] for c in data.get("courses", [])}
    print("Inserting Skills...")
    for s in data["skills"]:
        s["course"] = course_map.get(s["name"], f"https://www.coursera.org/search?query={s['name'].replace(' ', '%20')}")
        conn.query("CREATE (s:Skill {name: $name, category: $category, course: $course})", s)
        
    print("Linking Prerequisites...")
    for p in data["prerequisites"]:
        conn.query('''
        MATCH (s:Skill {name: $skill}), (pre:Skill {name: $prereq})
        MERGE (s)-[:HAS_PREREQUISITE]->(pre)
        ''', p)
        
    print("Linking Roles to Skills...")
    for rs in data["role_skills"]:
        conn.query('''
        MATCH (r:Role {title: $role}), (s:Skill {name: $skill})
        MERGE (r)-[:REQUIRES_SKILL]->(s)
        ''', rs)
        
    conn.close()
    print("Database seeded successfully.")
    
    # Save synthetic data to json in the root dir
    if "courses" in data:
        del data["courses"]
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), "synthetic_data.json")
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Synthetic data saved to {filepath}.")

if __name__ == "__main__":
    seed_db()
