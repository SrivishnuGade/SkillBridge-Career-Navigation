from fpdf import FPDF
import os

def create_pdf(text, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Using encode/decode to avoid character mapping issues in fpdf
    for line in text.split('\n'):
         pdf.multi_cell(0, 10, txt=line.encode('latin-1', 'replace').decode('latin-1'))
    pdf.output(filename)

def main():
    os.makedirs("data", exist_ok=True)

    jd_ml = """Job Title: Lead ML Engineer

About the Role:
We are looking for a Senior ML Engineer to build scalable AI solutions.

Required Skills:
- Proficiency in Python and C++
- Deep understanding of Deep Learning, PyTorch, and TensorFlow
- Strong mathematical foundations in Calculus and Linear Algebra
- Experience with MLOps and Kubernetes
"""

    jd_web = """Job Title: Senior Frontend React Developer

About the Role:
Looking for a UI expert to build beautiful interfaces.

Requirements:
- Expert in JavaScript, TypeScript, and React
- Experience with Next.js and TailwindCSS
- Understanding of UI/UX principles
"""

    syllabus = """Computer Science Undergraduate Syllabus

Core Mandatory Subjects:
1. Data Structures and Algorithms - Focuses on trees, graphs, and dynamic programming.
2. Database Management Systems - SQL architectures, normal forms, transaction management.
3. Operating Systems - Process scheduling, memory management, Linux basics.
4. Computer Networks - OSI model, TCP/IP, Network Security.

Electives available next semester:
- Deep Learning
- Cryptography
"""

    create_pdf(jd_ml, "data/jd_ml_engineer.pdf")
    create_pdf(jd_web, "data/jd_frontend.pdf")
    create_pdf(syllabus, "data/cs_syllabus.pdf")
    print("Synthetic PDFs generated successfully in data/ folder.")

if __name__ == "__main__":
    main()
