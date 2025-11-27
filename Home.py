import streamlit as st

st.set_page_config(
    page_title="Kitchen Pilot",
    layout="wide"
)

# CSS 
st.markdown("""
<style>
    /* Main Background adjustments */
    .main {
        background-color: #FAFAFA;
    }

    /* Hero Title Styling */
    h1 {
        color: #1E1E1E;
        font-family: 'Helvetica Neue', sans-serif;
    }

    /* Feature Cards (Containers) */
    .feature-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        height: 220px; /* Slight height increase to fit text */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    /* Ensure text fits nicely */
    .feature-card h3 {
        margin-top: 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Controls
with st.sidebar:
    st.markdown(
        """
        <div style='text-align: center; color: grey; font-size: 12px;'>
            Kitchen Pilot © 2025 | By CodeFest2025 Hackathon Team AAA
        </div>
        """, 
        unsafe_allow_html=True
    )

st.title("Kitchen Pilot")
st.markdown("### Your AI compliance partner for Malaysian F&B.")
st.markdown("""
Running a restaurant is hard. Dealing with permits shouldn't be. 
**Kitchen Pilot** streamlines your permits and simplifies regulations so you can focus on the food.
""")

st.divider()

# FEATURES SECTION
st.subheader("Features")

# Columns
c1, c2, c3 = st.columns(3)


# AI CHAT 
with c1:
    with st.container():
        st.markdown("""
            <div class="feature-card">
                <div>
                    <h3>Cikgu Compliance</h3>
                    <p>Chat with our AI expert trained on Malaysian local laws regarding F&B business operation.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Start Chat ➜", key="btn_chat"):
            st.switch_page("pages/1_Cikgu_ Compliance.py")

# PERMIT GUIDE 
with c2:
    with st.container():
        st.markdown("""
            <div class="feature-card">
                <div>
                    <h3>Permit Guide</h3>
                    <p>A quick compliance check for Malaysian F&B owners. Find out if you are missing any required permits or licenses.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Open Permit Guide ➜", key="btn_permit"):
            st.switch_page("pages/2_Permit_Checker.py") 

# SMART AUDITOR
with c3:
    with st.container():
        st.markdown("""
            <div class="feature-card">
                <div>
                    <h3>Smart Auditor</h3>
                    <p>Upload your SOPs or compliance logs. AI will analyze them and detect gaps automatically.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    
        if st.button("Start Audit ➜", key="btn_audit"):
            st.switch_page("pages/3_Smart_Auditor.py") 