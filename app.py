import streamlit as st
from chatbot import get_answer
import html

# ---------------- PAGE ----------------
st.set_page_config(page_title="SRMASC Assistant", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>

body {
    background: linear-gradient(135deg, #ffffff, #f7f3f0);
    font-family: 'Poppins', sans-serif;
}

/* Title */
.title {
    text-align:center;
    font-size:36px;
    font-weight:700;
    color:#6b1f2b;
}

/* Link */
.link {
    text-align:center;
    margin-bottom:20px;
}
.link a {
    color:#6b1f2b;
    text-decoration:none;
}

/* Chat container */
.chat-box {
    max-width:700px;
    margin:auto;
}

/* Messages */
.user {
    background:#7b2c3a;
    color:white;
    padding:10px 14px;
    border-radius:15px;
    margin:6px 0;
    width:fit-content;
    max-width:75%;
    margin-left:auto;
}

.bot {
    background:#ffffff;
    border:1px solid #eee;
    padding:10px 14px;
    border-radius:15px;
    margin:6px 0;
    width:fit-content;
    max-width:75%;
}

/* Input */
input {
    border-radius:20px !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown('<div class="title">SRM Arts and Science College</div>', unsafe_allow_html=True)
st.markdown('<div class="link"><a href="https://www.srmasc.ac.in/" target="_blank">Visit Official Website</a></div>', unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "chat" not in st.session_state:
    st.session_state.chat = []

# ---------------- DISPLAY CHAT ----------------
st.markdown('<div class="chat-box">', unsafe_allow_html=True)

for role, msg in st.session_state.chat:
    safe_msg = html.escape(msg).replace("\n", "<br>")
    
    if role == "user":
        st.markdown(f'<div class="user">{safe_msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot">{safe_msg}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- INPUT (ENTER FIX) ----------------
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("", placeholder="Type your message...")
    submit = st.form_submit_button("Send")

if submit and user_input:
    response = get_answer(user_input)

    st.session_state.chat.append(("user", user_input))
    st.session_state.chat.append(("bot", response))

    st.rerun()

# ---------------- FOOTER ----------------
st.markdown("""
<div style="text-align:center; margin-top:30px; color:#7b2c3a;">
Done by Rajalakshmi & Rubini <br>
Guided by Sangeetha Mam
</div>
""", unsafe_allow_html=True)