import streamlit as st
import pandas as pd
from db import load_data

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="TobuGo Analytics",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
def local_css():
    st.markdown("""
        <style>
            /* Main Content Background */
            .stApp {
                background-color: #F8FAFC;
            }
            
            /* Sidebar */
            [data-testid="stSidebar"] {
                background-color: #0F172A;
            }
            [data-testid="stSidebar"] * {
                color: #E2E8F0 !important;
            }
            
            /* Metric Cards */
            .metric-card {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                transition: transform 0.2s;
            }
            .metric-card:hover {
                transform: translateY(-2px);
            }
            .metric-title {
                color: #64748B;
                font-size: 0.875rem;
                font-weight: 500;
                margin-bottom: 0.5rem;
            }
            .metric-value {
                color: #0F172A;
                font-size: 1.5rem;
                font-weight: 700;
            }
            
            /* Table Styling */
            [data-testid="stDataFrame"] {
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                background-color: white;
                padding: 1rem;
            }
            
            /* Headers */
            h1, h2, h3 {
                color: #0F172A;
                font-family: 'Inter', sans-serif;
            }
        </style>
    """, unsafe_allow_html=True)

local_css()

# --- SIDEBAR ---
with st.sidebar:
    st.title("TobuGo Admin")
    st.markdown("---")
    st.markdown("### 📊 Analytics")
    st.markdown("Currently viewing: **Chat Prompts**")
    
    st.markdown("---")
    st.caption("v1.0.0 | TobuGo Inc.")

# --- MAIN CONTENT ---
st.title("🤖 Chat Prompts Dashboard")
st.markdown("Monitor and analyze user interactions with the Gemini AI agent.")

# --- DATA LOADING ---
with st.spinner("Loading data from remote database..."):
    # Updated query with JOIN to fetch user details
    query = """
        SELECT 
            cp.user_id,
            u.first_name as username,
            u.email,
            cp.prompt_text,
            cp.session_id,
            cp.created_at
        FROM chat_prompts cp
        JOIN users u ON cp.user_id = u.id
        ORDER BY cp.created_at DESC
        LIMIT 1000
    """
    df = load_data(query)

if df is not None and not df.empty:
    # --- METRICS SECTION ---
    col1, col2, col3 = st.columns(3)
    
    total_prompts = len(df)
    unique_users = df['user_id'].nunique()
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'])
        today_prompts = df[df['created_at'].dt.date == pd.Timestamp.now().date()].shape[0]
    else:
        today_prompts = "N/A"

    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Prompts (Recent)</div>
                <div class="metric-value">{total_prompts}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Active Users</div>
                <div class="metric-value">{unique_users}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Prompts Today</div>
                <div class="metric-value">{today_prompts}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📝 Recent Prompts")
    
    # Search filter
    search_term = st.text_input("Search prompts...", placeholder="Type to filter by prompt text, user or email...")
    
    if search_term:
        # Search in multiple columns
        mask = (
            df['prompt_text'].astype(str).str.contains(search_term, case=False, na=False) |
            df['username'].astype(str).str.contains(search_term, case=False, na=False) |
            df['email'].astype(str).str.contains(search_term, case=False, na=False)
        )
        filtered_df = df[mask]
    else:
        filtered_df = df

    # Requested order: User ID, username, email, Prompt, Session ID, Timestamp
    st.dataframe(
        filtered_df,
        column_order=("user_id", "username", "email", "prompt_text", "session_id", "created_at"),
        column_config={
            "user_id": st.column_config.TextColumn("User ID"),
            "username": st.column_config.TextColumn("Username"),
            "email": st.column_config.TextColumn("Email"),
            "prompt_text": st.column_config.TextColumn("Prompt", width="large"),
            "session_id": st.column_config.TextColumn("Session ID"),
            "created_at": st.column_config.DatetimeColumn(
                "Timestamp",
                format="D MMM YYYY, h:mm a",
            )
        },
        width="stretch",
        hide_index=True,
        height=600
    )

elif df is None:
    st.warning("Could not connect to the database. Please check your configuration.")
    st.info("💡 Tip: Make sure you have created a `.env` file with your `DATABASE_URL`.")

else:
    st.info("No chat prompts found in the database.")
