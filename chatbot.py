import os
import re
from deep_translator import GoogleTranslator
from langdetect import detect

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# ---------------- LOAD ----------------
current_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(current_dir, "data")

files = [
    "syllabus.txt.pdf",
    "departments.txt.pdf",
    "scholarships.txt.pdf",
    "placements.txt.pdf",
    "admission.txt.pdf",
    "college.txt.pdf",
    "courses.txt.pdf"
]

documents = []
print("🔄 Loading documents...")

for file in files:
    path = os.path.join(data_folder, file)
    if os.path.exists(path):
        loader = PyPDFLoader(path)
        docs = loader.load()

        for d in docs:
            d.metadata["source"] = file

        documents.extend(docs)
        print(f"✅ {file}")

# ---------------- VECTOR DB ----------------
splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
texts = splitter.split_documents(documents)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = FAISS.from_documents(texts, embeddings)
print("✅ RAG Ready")

# ---------------- LANGUAGE ----------------
def detect_lang(text):
    try:
        return detect(text)
    except:
        return "en"

# ---------------- INTENT ----------------
def detect_intent(q):
    q = q.lower()

    if any(w in q for w in ["course", "program", "degree"]):
        return "courses"

    elif any(w in q for w in ["admission", "apply", "fee"]):
        return "admission"

    elif "scholarship" in q:
        return "scholarships"

    elif any(w in q for w in ["placement", "job", "training"]):
        return "placements"

    elif any(w in q for w in ["faculty","faculties","hod","staff","teacher","professor"]):
        return "faculty"

    return "general"

# ---------------- SMART RETRIEVE ----------------
def retrieve(query, intent):

    docs = db.similarity_search(query, k=15)

    # 🎯 FILTER BASED ON INTENT
    if intent == "faculty":
        filtered = [d for d in docs if "computer science" in d.page_content.lower()]
        return filtered if filtered else docs

    elif intent == "courses":
        return [d for d in docs if "course" in d.page_content.lower() or "b.sc" in d.page_content.lower()] or docs

    elif intent == "admission":
        return [d for d in docs if "admission" in d.page_content.lower()] or docs

    elif intent == "placements":
        return [d for d in docs if "placement" in d.page_content.lower()] or docs

    elif intent == "scholarships":
        return [d for d in docs if "scholarship" in d.page_content.lower()] or docs

    return docs

# ---------------- EXTRACT CS ----------------
def extract_cs(text):
    text_lower = text.lower()
    if "computer science" in text_lower:
        start = text_lower.find("computer science")
        return text[start:start+1200]
    return text

# ---------------- FORMAT FACULTY ----------------
def format_faculty(text):

    lines = text.split("\n")
    faculty = []

    for line in lines:
        line = line.strip()
        if any(w in line for w in ["Dr", "Mr", "Mrs", "Professor"]):
            faculty.append("• " + line)

    if faculty:
        return "Computer Science Faculty:\n\n" + "\n".join(faculty[:15])

    return "No faculty information found."

# ---------------- CLEAN ----------------
def clean(text, max_sent=5):
    text = text.replace("\n", " ").strip()
    sentences = re.split(r'(?<=[.!?]) +', text)
    return " ".join(sentences[:max_sent])

# ---------------- MAIN ----------------
def get_answer(user_input):

    if user_input.lower() in ["hi","hello","hey","helo"]:
        return "Hello. What would you like to know about SRM Arts and Science College?"

    # 🌍 detect language
    user_lang = detect_lang(user_input)

    # 🔁 translate to English
    if user_lang != "en":
        query = GoogleTranslator(source='auto', target='en').translate(user_input)
    else:
        query = user_input

    intent = detect_intent(query)

    docs = retrieve(query, intent)

    if not docs:
        return "No information found."

    raw = docs[0].page_content

    # 🎯 RESPONSE BASED ON INTENT
    if intent == "faculty":
        cs_text = extract_cs(raw)
        answer = format_faculty(cs_text)

    elif intent == "courses":
        answer = "Courses:\n\n" + clean(raw, 8)

    elif intent == "placements":
        answer = "Placements:\n\n" + clean(raw, 6)

    elif intent == "admission":
        answer = "Admission:\n\n" + clean(raw, 6)

    elif intent == "scholarships":
        answer = "Scholarships:\n\n" + clean(raw, 6)

    else:
        answer = clean(raw, 5)

    # 🔁 translate back
    if user_lang != "en":
        answer = GoogleTranslator(source='en', target=user_lang).translate(answer)

    return answer


# ---------------- TERMINAL MODE ----------------
if __name__ == "__main__":

    print("\nSRMASC Smart Assistant Ready")
    print("Ask in English, Tamil, Hindi, etc.")
    print("Type 'exit' to quit\n")

    while True:
        q = input("You: ")

        if q.lower() == "exit":
            print("Bye.")
            break

        print("Bot:", get_answer(q))