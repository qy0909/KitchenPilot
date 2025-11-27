import streamlit as st
from jamaibase import JamAI, protocol as p
import re
import os
from urllib.parse import unquote

# Configuration
st.set_page_config(page_title="Cikgu Compliance")

st.title("Cikgu Compliance Chat")
st.caption("Chat with our AI expert trained on Malaysian local laws regarding F&B business operation.")

# JamAI Configuration
ACTION_TABLE_ID = "Chat_Logs" 
PAT = st.secrets["PAT"]
PROJECT_ID = st.secrets["PROJECT_ID"]

jamai = JamAI(token=PAT, project_id=PROJECT_ID)

# Core Logic Function
def jamai_chat_query(question):
    """
    Sends data to JamAI with conversation history, retrieves the answer, 
    and selectively extracts references based on the [NO_RAG] tag.
    """
    try:
        history_block = ""
        
        # Check if we have history (needs to be > 1 because the last one is the current input)
        if "messages" in st.session_state and len(st.session_state.messages) > 1:
            
            # EXCLUDE the last message (current question) using [:-1]
            # Then take the last 2 items from that real history
            previous_msgs = st.session_state.messages[:-1]
            recent_msgs = previous_msgs[-2:] 
            
            history_lines = []
            for role, msg in recent_msgs:
                if role == "user":
                    history_lines.append(f"User asked: {msg}")
                elif role == "ai":
                    # Clean tags and truncate
                    clean_hist = msg.replace("[NO_RAG]", "").strip()
                    history_lines.append(f"AI answered: {clean_hist[:200]}...")
            
            if history_lines:
                history_block = "[HISTORY START]\n" + "\n".join(history_lines) + "\n[HISTORY END]\n\n"

        # Combine History + Current Question
        final_input = f"{history_block}[CURRENT QUESTION]\n{question}"

        # SEND TO JAMAI 
        row_data = [{"User_Input": final_input}]

        completion = jamai.table.add_table_rows(
            table_type=p.TableType.ACTION,
            request=p.RowAddRequest(
                table_id=ACTION_TABLE_ID,
                data=row_data,
                stream=False
            )
        )

        if completion.rows and len(completion.rows) > 0:
            response_col = completion.rows[0].columns["AI_Response"]
            raw_answer = response_col.text
            
            # IMPROVED FILTER LOGIC 
            references_data = []
            clean_answer = raw_answer
            
            # Define common greetings
            greeting_keywords = ["hi", "hello", "hey", "salam", "selamat pagi", "selamat petang", "good morning"]
            
            # Check if user input is a short greeting OR if AI used the tag
            is_short_greeting = any(k in question.lower() for k in greeting_keywords) and len(question.split()) < 5
            ai_signaled_no_rag = "[NO_RAG]" in raw_answer
            
            # Decision: Hide references if it's a greeting
            if ai_signaled_no_rag or is_short_greeting:
                # Remove tag if present
                clean_answer = raw_answer.replace("[NO_RAG]", "").strip()
                # FORCE EMPTY REFERENCES
                references_data = [] 
            
            else:
                # Standard RAG Response
                clean_answer = re.sub(r'\[@\d+\]', '', raw_answer)
                
                # Extract References
                if hasattr(response_col, "references") and response_col.references:
                    for ref_tuple in response_col.references:
                        if isinstance(ref_tuple, tuple) and len(ref_tuple) == 2:
                            key, value = ref_tuple
                            if key == 'chunks' and isinstance(value, list):
                                for chunk in value:
                                    fname = "Unknown File"
                                    if hasattr(chunk, 'file_name') and chunk.file_name:
                                        fname = chunk.file_name
                                    elif hasattr(chunk, 'document_id') and chunk.document_id:
                                        full_path = chunk.document_id
                                        fname = unquote(full_path.split('/')[-1])

                                    references_data.append({
                                        "file": fname,
                                        "page": chunk.page if hasattr(chunk, 'page') else "N/A",
                                        "text": chunk.text if hasattr(chunk, 'text') else "..."
                                    })
            
            return {
                "answer": clean_answer,
                "references": references_data 
            }

        else:
            return {
                "answer": "No response generated.",
                "references": []
            }

    except Exception as e:
        print(f"JamAI Error: {e}")
        return {
            "answer": f"Error interacting with Action Table: {str(e)}",
            "references": []
        }

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar Controls
with st.sidebar:
    if st.button("Start New Chat"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: grey; font-size: 12px;'>
            Kitchen Pilot © 2025 | By CodeFest2025 Hackathon Team AAA
        </div>
        """, 
        unsafe_allow_html=True
    )

# Display History Loop
for role, msg in st.session_state.messages:
    if role == "user":
        st.chat_message("user").write(msg)
    elif role == "ai":
        st.chat_message("assistant").write(msg)
    elif role == "ref_obj":
        # Only render if the list is NOT empty
        if msg and len(msg) > 0:
            with st.expander("Sources used in this reply"):
                for i, ref in enumerate(msg):
                    st.markdown(f"**{i+1}. {ref['file']} (Page {ref['page']})**")
                    st.caption(f"{ref['text'][:300]}...") 
                    
                    local_path = os.path.join("docs", ref['file'])
                    if os.path.exists(local_path):
                        with open(local_path, "rb") as f:
                            st.download_button(
                                label="Download",
                                data=f,
                                file_name=ref['file'],
                                key=f"hist_btn_{role}_{i}_{ref['page']}"
                            )

# Chat Input Logic
user_q = st.chat_input("Ask about F&B Compliance...")

if user_q:
    st.session_state.messages.append(("user", user_q))
    st.chat_message("user").write(user_q)

    with st.chat_message("assistant"):
        with st.spinner("Generating responses..."):
            rag_reply = jamai_chat_query(user_q)
            
            st.write(rag_reply["answer"])
            
            # If references exist (meaning NOT [NO_RAG]), show them
            if rag_reply["references"]:
                st.markdown("### References")
                for i, ref in enumerate(rag_reply["references"]):
                    label = f"{i+1}. {ref['file']} (Page {ref['page']})"
                    with st.expander(label):
                        st.markdown(f"> *\"{ref['text']}\"*")
                        local_path = os.path.join("docs", ref['file'])
                        if os.path.exists(local_path):
                            with open(local_path, "rb") as f:
                                st.download_button(
                                    label=f"Download {ref['file']}",
                                    data=f,
                                    file_name=ref['file'],
                                    mime="application/pdf",
                                    key=f"btn_{i}"
                                )
                        else:
                            st.caption(f"⚠️ File not found in 'docs' folder: {ref['file']}")

    # Save to history
    st.session_state.messages.append(("ai", rag_reply["answer"]))
    # Save references object (will be empty if NO_RAG)
    st.session_state.messages.append(("ref_obj", rag_reply["references"]))