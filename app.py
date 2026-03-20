import streamlit as st
import pandas as pd
from backend.db import Neo4jConnection
from backend.ai import extract_skills_from_resume, generate_mock_interview_question, generate_verification_question
import uuid

st.set_page_config(page_title="Skill-Bridge Career Navigator", layout="wide")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "user_skills" not in st.session_state:
    st.session_state.user_skills = []
if "target_role" not in st.session_state:
    st.session_state.target_role = "Machine Learning Engineer"
if "syllabus_skills" not in st.session_state:
    st.session_state.syllabus_skills = []

import os
import json

def load_cache(prefix, key):
    path = f"data/{prefix}_{key}.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None

def save_cache(prefix, key, data):
    os.makedirs("data", exist_ok=True)
    with open(f"data/{prefix}_{key}.json", "w") as f:
        json.dump(data, f)

@st.cache_resource
def get_db_connection():
    return Neo4jConnection()

conn = get_db_connection()

def read_pdf(file, max_pages=None):
    from pypdf import PdfReader
    reader = PdfReader(file)
    text = ""
    pages_to_read = reader.pages[:max_pages] if max_pages is not None else reader.pages
    for page in pages_to_read:
        text += page.extract_text() + "\n"
    return text

@st.cache_data
def get_canonical_skills():
    conn = get_db_connection()
    try:
        res = conn.query("MATCH (s:Skill) RETURN s.name AS name")
        return {r["name"].lower().strip(): r["name"] for r in res} if res else {}
    except:
        return {}

def normalize_skill(skill_str):
    if not skill_str: return ""
    canon = get_canonical_skills()
    return canon.get(skill_str.lower().strip(), skill_str)

def upsert_user_skill(skill, syllabus=False, liked=False, interest=False, rating=3):
    conn.query("""
    MERGE (u:User {id: $session_id})
    MERGE (s:Skill {name: $skill})
    MERGE (u)-[rel:HAS_SKILL]->(s)
    ON CREATE SET rel.in_syllabus = $syllabus, rel.owned = $syllabus, rel.liked = $liked, rel.learnt_by_interest = $interest, rel.rating = $rating
    ON MATCH SET 
        rel.in_syllabus = CASE WHEN $syllabus THEN true ELSE coalesce(rel.in_syllabus, false) END, 
        rel.owned = CASE WHEN $syllabus THEN true ELSE coalesce(rel.owned, false) END,
        rel.liked = CASE WHEN $liked THEN true ELSE coalesce(rel.liked, false) END,
        rel.learnt_by_interest = CASE WHEN $syllabus THEN false WHEN $interest THEN true ELSE coalesce(rel.learnt_by_interest, false) END
    """, {"session_id": st.session_state.session_id, "skill": skill, "syllabus": syllabus, "liked": liked, "interest": interest, "rating": rating})

def upsert_syllabus_data(subject_name, skills, liked=False, rating=3):
    conn.query("""
    MERGE (u:User {id: $session_id})
    MERGE (sub:Subject {name: $subject})
    MERGE (u)-[rel:TOOK_SUBJECT]->(sub)
    SET rel.liked = $liked
    """, {"session_id": st.session_state.session_id, "subject": subject_name, "liked": liked})
    
    for skill in skills:
        skill_name = skill.get("name")
        skill_tag = skill.get("tag", "tool")
        if not skill_name: continue
        
        conn.query("""
        MERGE (sub:Subject {name: $subject})
        MERGE (s:Skill {name: $skill})
        ON CREATE SET s.category = $tag
        MERGE (sub)-[:TEACHES_SKILL]->(s)
        
        MERGE (u:User {id: $session_id})
        MERGE (u)-[rel:HAS_SKILL]->(s)
        SET rel.owned = true, 
            rel.in_syllabus = true,
            rel.learnt_by_interest = false,
            rel.liked = CASE WHEN $liked THEN true ELSE coalesce(rel.liked, false) END, 
            rel.from_subject = CASE WHEN rel.rating IS NOT NULL AND rel.rating > $rating THEN coalesce(rel.from_subject, $subject) ELSE $subject END, 
            rel.preference_tag = coalesce(rel.preference_tag, $tag),
            rel.rating = CASE WHEN rel.rating IS NOT NULL AND rel.rating > $rating THEN rel.rating ELSE $rating END
        """, {"session_id": st.session_state.session_id, "subject": subject_name, "skill": skill_name, "tag": skill_tag, "liked": liked, "rating": rating})

def fetch_all_prerequisites(skills):
    if not skills: return []
    query = """
    UNWIND $skills AS skill_name
    MATCH (s:Skill {name: skill_name})-[:HAS_PREREQUISITE*1..5]->(pre:Skill)
    RETURN DISTINCT pre.name AS prereq
    """
    res = conn.query(query, {"skills": skills})
    return [r["prereq"] for r in res] if res else []

# --- PAGE 1: Academic Profile ---
def page_syllabus():
    st.title("🎓 Step 1: Academic Foundation")
    st.write("Let's map out your formal education. Upload your college syllabus to automatically add the core mandatory subjects to your profile.")
    
    uploaded_syl = st.file_uploader("Upload College Syllabus (PDF)", type=["pdf"])
    if st.button("Extract Mandatory Courses"):
        if uploaded_syl:
            with st.spinner("Parsing academic requirements..."):
                from backend.ai import extract_skills_from_syllabus
                syl_text = read_pdf(uploaded_syl, max_pages=10)
                
                # Fetch nested structural data: subject -> tools
                cache_key = uploaded_syl.name.replace(" ", "_")
                syl_data = load_cache("syl", cache_key)
                if not syl_data:
                    syl_data = extract_skills_from_syllabus(syl_text)
                    save_cache("syl", cache_key, syl_data)
                
                flat_skills = []
                subjects = []
                for item in syl_data:
                    subj = item.get("subject", "")
                    if subj:
                        subjects.append(subj)
                        upsert_syllabus_data(subj, item.get("skills", []), liked=False)
                        
                    for sk in item.get("skills", []):
                        name = sk.get("name", "")
                        if name: flat_skills.append(normalize_skill(name))
                        
                prereqs = fetch_all_prerequisites(flat_skills)
                all_academic = list(set(flat_skills + prereqs))
                
                st.session_state.syllabus_mapping = syl_data
                st.session_state.syllabus_subjects = subjects
                st.session_state.user_skills = list(set(st.session_state.user_skills + all_academic))
                for skill in prereqs: 
                    # Map implicit unowned prerequisites back
                    upsert_user_skill(skill, syllabus=True, liked=False, interest=False)
                st.success(f"Successfully mapped {len(subjects)} core subjects and {len(flat_skills)} discrete tools into your Profile!")

    if st.session_state.get("syllabus_subjects"):
        st.write("---")
        st.write("### ⭐ Subject Preferences")
        st.write("Categorize your core subjects to automatically configure your proficiency scale!")
        
        fav_subs = st.multiselect("❤️ Favorite Subjects (Sets tool rating to 5/5):", options=st.session_state.syllabus_subjects)
        av_options = [s for s in st.session_state.syllabus_subjects if s not in fav_subs]
        meh_subs = st.multiselect("👎 Not Interested Subjects (Sets tool rating to 0/5):", options=av_options)
        
        if st.button("Save Preferences & Continue"):
            fav_count, meh_count, norm_count = 0, 0, 0
            for item in st.session_state.get("syllabus_mapping", []):
                subj = item.get("subject")
                skills = item.get("skills", [])
                if subj in fav_subs:
                    upsert_syllabus_data(subj, skills, liked=True, rating=5)
                    fav_count += len(skills)
                elif subj in meh_subs:
                    upsert_syllabus_data(subj, skills, liked=False, rating=0)
                    meh_count += len(skills)
                else:
                    upsert_syllabus_data(subj, skills, liked=False, rating=3) # Standard
                    norm_count += len(skills)
            
            st.session_state.favorite_subjects = fav_subs
            st.success(f"Preferences applied! Boosted {fav_count} tools to Master (5/5). Dropped {meh_count} tools to None (0/5).")

# --- PAGE 2: Experience ---
def page_resume():
    st.title("💼 Step 2: Experience & Self-Teaching")
    st.write("Now, let's explore what you built outside of class. Upload your resume to extract the skills you learned by interest or on the job.")
    
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    if st.button("Extract Skills from Resume"):
        if uploaded_file is not None:
            with st.spinner("Analyzing Professional Experience..."):
                try:
                    resume_text = read_pdf(uploaded_file)
                    cache_key = uploaded_file.name.replace(" ", "_")
                    extracted = load_cache("res", cache_key)
                    if not extracted:
                        extracted = extract_skills_from_resume(resume_text)
                        save_cache("res", cache_key, extracted)
                    
                    extracted = [normalize_skill(s) for s in extracted]
                    
                    prereqs = fetch_all_prerequisites(extracted)
                    all_exp = list(set(extracted + prereqs))
                    
                    for skill in all_exp:
                        is_new = skill not in st.session_state.user_skills
                        upsert_user_skill(skill, syllabus=(not is_new), liked=False, interest=is_new, rating=4)
                        
                    st.session_state.user_skills = list(set(st.session_state.user_skills + all_exp))
                    st.success(f"Added {len(extracted)} new proprietary skills and {len(prereqs)} implicit prerequisites!")
                except Exception as e:
                    st.error(f"Error processing PDF: {e}")

# --- PAGE 3: My Skills Dashboard ---
def page_skills_dashboard():
    st.title("⭐ Step 3: My Skills Dashboard")
    st.write("This is your ultimate graph profile. Review, curate, and scale your confidence in each skill.")
    
    if not st.session_state.user_skills:
        st.info("Your graph is empty! Please complete Step 1 (Academic) or Step 2 (Experience).")
        return
        
    query = """
    MATCH (u:User {id: $session_id})-[r:HAS_SKILL]->(s:Skill)
    RETURN s.name AS skill, r.owned AS owned, r.from_subject AS subject, r.preference_tag AS tag, r.in_syllabus AS syllabus, r.learnt_by_interest AS interest, r.liked AS liked, r.rating AS rating
    ORDER BY r.liked DESC, r.rating DESC, s.name ASC
    """
    skill_data = conn.query(query, {"session_id": st.session_state.session_id})
    
    if skill_data:
        st.write("### 🕸️ Your Verified Skill Topology")
        try:
            from pyvis.network import Network
            import streamlit.components.v1 as components
            import tempfile
            
            owned_query = """
            MATCH (s1:Skill)-[:HAS_PREREQUISITE]->(s2:Skill)
            WHERE s1.name IN $user_skills AND s2.name IN $user_skills
            RETURN s1.name AS source, s2.name AS target
            """
            edges = conn.query(owned_query, {"user_skills": st.session_state.user_skills})
            if edges:
                net = Network(height="450px", width="100%", directed=True, bgcolor="#0E1117", font_color="white")
                nodes = set()
                for edge in edges:
                    nodes.add(edge["source"].title())
                    nodes.add(edge["target"].title())
                    
                for n in nodes:
                    net.add_node(n, label=n, title=n, color="#3498DB")
                    
                drawn_edges = set()
                for edge in edges:
                    src = edge["source"].title()
                    tgt = edge["target"].title()
                    edge_key = (tgt, src)
                    if edge_key not in drawn_edges:
                        # Reverse visual flow: Foundation -> Advanced
                        net.add_edge(tgt, src, color="#7F8C8D", width=2)
                        drawn_edges.add(edge_key)
                    
                net.set_options('''
                var options = {
                  "edges": {
                    "smooth": false
                  },
                  "layout": {
                    "hierarchical": {
                      "enabled": true,
                      "direction": "DU",
                      "sortMethod": "directed",
                      "nodeSpacing": 80,
                      "levelSeparation": 80
                    }
                  },
                  "physics": {
                    "hierarchicalRepulsion": {
                      "centralGravity": 0.0,
                      "nodeDistance": 100
                    },
                    "solver": "hierarchicalRepulsion"
                  },
                  "interaction": {
                    "zoomView": true,
                    "dragNodes": true,
                    "navigationButtons": false
                  }
                }
                ''')
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp_file:
                    net.save_graph(tmp_file.name)
                    
                with open(tmp_file.name, 'r', encoding='utf-8') as f: 
                    source_code = f.read() 
                
                source_code = source_code.replace("</script>", "network.fit();</script>")
                
                components.html(f"""
                <div style="display: flex; justify-content: center; width: 100%;">
                    {source_code}
                </div>
                """, height=470)
            else:
                st.info("You don't have enough interconnected prerequisite skills yet to form a topology.")
        except Exception as e:
            st.error(f"Graph rendering failed: {e}")
            
        st.write("---")
        st.write("### 📝 Interactive Inventory")
        with st.form("skill_ratings_form"):
            updates = {}
            for row in skill_data:
                skill_name = row['skill']
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    tags = []
                    if row['owned']: tags.append("💎 Owned from Syllabus")
                    elif row['syllabus']: tags.append("🎓 Prerequisite")
                    if row['interest']: tags.append("💡 Self-Taught")
                    if row['subject']: tags.append(f"📚 {row['subject']}")
                    if row['tag']: tags.append(f"🔧 {row['tag']}")
                    if row['liked']: tags.append("❤️ Liked")
                    tag_str = ' | '.join(tags)
                    st.markdown(f"**{skill_name}** <br> <small style='color: gray'>{tag_str}</small>", unsafe_allow_html=True)
                with col2:
                    r_val = row['rating'] if row['rating'] is not None else 3
                    updates[skill_name] = st.slider(f"Confidence Level", 0, 5, r_val, key=f"rate_{skill_name}", label_visibility="collapsed")
                with col3:
                    st.write("") # spacing
            
            if st.form_submit_button("Save Ratings into Graph"):
                for skill_name, rating in updates.items():
                    conn.query("""
                    MATCH (u:User {id: $session_id})-[r:HAS_SKILL]->(s:Skill {name: $skill})
                    SET r.rating = $rating
                    """, {"session_id": st.session_state.session_id, "skill": skill_name, "rating": rating})
                st.success("All ratings successfully synced with your Neo4j node!")

# --- PAGE 4: Career Navigator ---
def page_career_navigator():
    st.title("🗺️ Step 4: Intelligent Career Navigator")
    
    # Target Role Sidebar
    with st.sidebar:
        st.header("Graph Targeting")
        roles_query = conn.query("MATCH (r:Role) RETURN r.title AS title")
        roles = [r["title"] for r in roles_query] if roles_query else ["Machine Learning Engineer"]
        
        current_idx = roles.index(st.session_state.target_role) if st.session_state.target_role in roles else 0
        st.session_state.target_role = st.selectbox("Select Target Role:", options=roles, index=current_idx)
        
        st.write("---")
        st.write("Or import a custom Job Description:")
        uploaded_jd = st.file_uploader("Upload JD (PDF)", type=["pdf"])
        if st.button("Parse JD & Add Graph Node"):
            if uploaded_jd:
                with st.spinner("Running AI Parser..."):
                    from backend.ai import extract_role_from_jd
                    jd_text = read_pdf(uploaded_jd)
                    cache_key = uploaded_jd.name.replace(" ", "_")
                    jd_data = load_cache("jd", cache_key)
                    if not jd_data:
                        jd_data = extract_role_from_jd(jd_text)
                        save_cache("jd", cache_key, jd_data)
                    new_title = jd_data.get("title", "Custom Role")
                    raw_skills = jd_data.get("required_skills", [])
                    
                    # Programmatic safety net: aggressively strip any AI-hallucinated sentence fragments and arbitrarily vague domains
                    req_skills = [normalize_skill(s) for s in raw_skills if len(s.split()) <= 3 and s.lower() != "programming"]
                    
                    conn.query("MERGE (r:Role {title: $title}) SET r.description = $desc", {"title": new_title, "desc": jd_data.get("description", "")})
                    for s in req_skills:
                        conn.query("MERGE (s:Skill {name: $skill}) MERGE (r:Role {title: $title}) MERGE (r)-[:REQUIRES_SKILL]->(s)", {"skill": s, "title": new_title})
                    st.success(f"Added {new_title} to Neo4j Graph!")
                    st.session_state.target_role = new_title
                    st.rerun()
                    
    # The 5 Core Flow Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Role Recommendations", "📊 Gap Analysis", "📍 Learning Roadmap", "🎤 Mock Interview"])
    
    with tab1:
        st.header("🎯 AI Graph Recommendations")
        st.write("This query factors in your base skills, multiplies scores for your *Liked* subjects, and natively weights your self-reported *1-5 Rating Confidence*!")
        if not st.session_state.user_skills:
            st.info("Complete Steps 1-3 to get graph recommendations!")
        else:
            query = """
            MATCH (u:User {id: $session_id})-[r:HAS_SKILL]->(s:Skill)
            WITH u, collect({name: s.name, liked: coalesce(r.liked, false), rating: coalesce(r.rating, 3)}) as user_skill_data
            MATCH (role:Role)-[:REQUIRES_SKILL]->(req:Skill)
            WITH role, collect(req.name) AS required_skills, user_skill_data
            
            // Calculate matches and compute dynamic weight
            WITH role, required_skills, 
                 [uskill IN user_skill_data WHERE uskill.name IN required_skills] AS matching_uskills
            WITH role, required_skills, matching_uskills,
                 size(matching_uskills) AS base_match,
                 size(required_skills) AS req_count,
                 reduce(bonus = 0, uskill IN matching_uskills | 
                    bonus + (CASE WHEN uskill.liked THEN 3 ELSE 0 END) + (uskill.rating - 3)
                 ) AS dynamic_bonus
                 
            WITH role, required_skills, [u IN matching_uskills | u.name] AS matching_skills, req_count, base_match, (base_match + dynamic_bonus) AS match_score
            WHERE req_count > 0
            RETURN role.title AS role, role.description AS desc, match_score, req_count, required_skills, matching_skills, base_match
            ORDER BY match_score DESC, req_count ASC
            LIMIT 3
            """
            try:
                suggestions = conn.query(query, {"session_id": st.session_state.session_id})
                if suggestions:
                    for row in suggestions:
                        role_title = row['role']
                        match_pct = int((row['base_match'] / row['req_count']) * 100)
                        missing = [s for s in row['required_skills'] if s not in row['matching_skills']]
                        with st.expander(f"**{role_title}** - Dynamic Weight: {row['match_score']} ({row['base_match']}/{row['req_count']} skills)", expanded=True):
                            st.write(row['desc'])
                            if missing:
                                st.markdown(f"**Missing:** {', '.join(missing)}")
                            else:
                                st.success("You have all the required skills!")
                else:
                    st.write("No matching roles found.")
            except Exception as e:
                st.error(f"Error querying Neo4j: {e}")

    with tab2:
        st.header(f"Gap Analysis for {st.session_state.target_role}")
        if not st.session_state.target_role:
            st.warning("Please select a target role in the sidebar.")
        else:
            query = """
            MATCH (r:Role {title: $title})-[:REQUIRES_SKILL]->(s:Skill)
            RETURN s.name AS skill, s.category AS category
            """
            req_data = conn.query(query, {"title": st.session_state.target_role})
            # Retroactive string filter to hide polluted graph nodes containing AI-hallucinated descriptive sentences
            raw_req = [row["skill"] for row in req_data if len(row["skill"].split()) <= 3 and row["skill"].lower().strip() not in ["programming", "ai"]] if req_data else []
            required_skills = list(dict.fromkeys(raw_req))
            
            user_skills = st.session_state.user_skills
            # Dynamically infer foundation knowledge based on concrete tools owned
            implicit_prereqs = fetch_all_prerequisites(user_skills)
            full_user_skills = list(set(user_skills + implicit_prereqs))
            
            user_skills_lower = [s.lower() for s in full_user_skills]
            owned_skills = [s for s in required_skills if s.lower() in user_skills_lower]
            missing_skills = [s for s in required_skills if s.lower() not in user_skills_lower]
            
            st.metric("Total Required Skills", len(required_skills))
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("✅ Skills You Have")
                for s in owned_skills: st.write(f"- {s}")
            with col2:
                st.subheader("❌ Missing Gap")
                for s in missing_skills: st.write(f"- {s}")
            st.session_state.missing_skills = missing_skills
            
            st.write("---")
            st.subheader("🕸️ Prerequisite Network Graph")
            try:
                from pyvis.network import Network
                import streamlit.components.v1 as components
                import tempfile
                
                nodes_query = """
                MATCH (r:Role {title: $title})-[:REQUIRES_SKILL]->(req:Skill)
                OPTIONAL MATCH (req)-[:HAS_PREREQUISITE*1..5]->(pre:Skill)
                WITH collect(DISTINCT req.name) + collect(DISTINCT pre.name) AS all_skills
                UNWIND all_skills AS s
                RETURN DISTINCT s AS node_name
                """
                
                net_query = """
                MATCH (r:Role {title: $title})-[:REQUIRES_SKILL]->(req:Skill)
                OPTIONAL MATCH (req)-[:HAS_PREREQUISITE*1..5]->(pre:Skill)
                WITH collect(DISTINCT req.name) + collect(DISTINCT pre.name) AS all_skills
                UNWIND all_skills AS s
                MATCH (s1:Skill {name: s})-[rel:HAS_PREREQUISITE]->(s2:Skill)
                WHERE s2.name IN all_skills
                RETURN DISTINCT s1.name AS source, s2.name AS target
                """
                
                nodes_data = conn.query(nodes_query, {"title": st.session_state.target_role})
                
                if nodes_data:
                    net = Network(height="600px", width="100%", directed=True, bgcolor="#0E1117", font_color="white")
                    
                    all_graph_nodes = [row["node_name"] for row in nodes_data if row["node_name"]]
                    valid_nodes = set([n for n in all_graph_nodes if len(n.split()) <= 3 and n.lower().strip() not in ["programming", "ai"]])
                    
                    user_skills_lower = [s.lower() for s in user_skills]
                    
                    for n in valid_nodes:
                        color = "#3498DB" if n.lower() in user_skills_lower else "#E74C3C"
                        net.add_node(n, label=n, title=n, color=color)
                        
                    edges = conn.query(net_query, {"title": st.session_state.target_role})
                    if edges:
                        drawn_edges = set()
                        for edge in edges:
                            src = edge["source"]
                            tgt = edge["target"]
                            if src in valid_nodes and tgt in valid_nodes:
                                edge_key = (tgt, src)
                                if edge_key not in drawn_edges:
                                    # Reversing visual flow: foundation -> advanced
                                    net.add_edge(tgt, src, color="#7F8C8D", width=2)
                                    drawn_edges.add(edge_key)
                        
                    net.set_options('''
                    var options = {
                      "edges": {
                        "smooth": false
                      },
                      "physics": {
                        "barnesHut": {
                          "gravitationalConstant": -3000,
                          "centralGravity": 0.8,
                          "springLength": 150
                        },
                        "minVelocity": 0.75
                      },
                      "interaction": {
                        "zoomView": true,
                        "dragNodes": true,
                        "navigationButtons": false
                      }
                    }
                    ''')

                    with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp_file:
                        net.save_graph(tmp_file.name)
                        
                    with open(tmp_file.name, 'r', encoding='utf-8') as f: 
                        source_code = f.read() 
                    
                    # Force Vis.js to center the graph immediately after physics stabilization
                    source_code = source_code.replace(
                        "network = new vis.Network(container, data, options);",
                        "network = new vis.Network(container, data, options);\n"
                        "network.once('stabilizationIterationsDone', function() { network.fit(); });\n"
                    )

                    components.html(source_code, height=620)
                else:
                    st.info("No prerequisite chains defined for this role's specific skills.")
            except Exception as e:
                st.error(f"Graph visualization failed: {e}")

    with tab3:
        st.header("📍 Topological Roadmap")
        missing_skills = st.session_state.get("missing_skills", [])
        if not missing_skills:
            st.info("No missing skills! You're ready for this role.")
        else:
            query = """
            MATCH (s:Skill) WHERE s.name IN $missing
            OPTIONAL MATCH (s)-[:HAS_PREREQUISITE]->(pre:Skill)
            RETURN s.name AS skill, collect(DISTINCT pre.name) AS prereqs, s.course AS course
            """
            roadmap_data = conn.query(query, {"missing": missing_skills})
            if roadmap_data:
                for row in roadmap_data:
                    skill = row['skill']
                    prereqs = [p for p in row['prereqs'] if p in missing_skills]
                    course_url = row.get('course')
                    with st.expander(f"Learn: **{skill}**", expanded=True):
                        if prereqs:
                            st.warning(f"⚠️ Mandatory Prerequisite First: {', '.join(prereqs)}")
                        st.write("Resources:")
                        if course_url:
                            st.markdown(f"- [Recommended Course / Search]({course_url})")

    with tab4:
        st.header("🎤 Mock Interview")
        test_skill = st.selectbox("Select a missing skill to practice:", options=st.session_state.get("missing_skills", ["Python"]))
        if st.button("Generate Interview Question", key="mockbtn"):
            with st.spinner("Generating..."):
                question, answer = generate_mock_interview_question(test_skill)
                st.session_state.mock_q = question
                st.session_state.mock_a = answer
        if "mock_q" in st.session_state:
            st.success(f"{st.session_state.mock_q}")
            with st.expander("View AI Answer"):
                st.write(st.session_state.mock_a)

# --- Define Navigation ---
pg = st.navigation([
    st.Page(page_syllabus, title="1. Academic Profile", icon="🎓"),
    st.Page(page_resume, title="2. Experience", icon="💼"),
    st.Page(page_skills_dashboard, title="3. My Skills", icon="⭐"),
    st.Page(page_career_navigator, title="4. Career Navigator", icon="🗺️")
])
pg.run()
