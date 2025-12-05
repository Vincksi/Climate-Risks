import streamlit as st
import pandas as pd
import requests
import json
from typing import List, Dict

# --- Global Configuration ---
API_BASE_URL = "http://127.0.0.1:8000"

# Page config with custom theme
st.set_page_config(
    layout="wide", 
    page_title="GenAI Market Analyst",
    initial_sidebar_state="expanded"
)

# Custom CSS inspired by Ollama's design with white background
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background-color: #0f0f0f;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a;
        border-right: 1px solid #2a2a2a;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff;
        font-weight: 600;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
        margin: 4px 0;
    }
    
    .status-online {
        background-color: #10b981;
        color: white;
    }
    
    .status-offline {
        background-color: #ef4444;
        color: white;
    }
    
    /* Cards */
    .info-card {
        background-color: #1e1e1e;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
    }
    
    /* Model cards */
    .model-card {
        background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
        border: 1px solid #3a3a3a;
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
        transition: all 0.3s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }
    
    .model-card:hover {
        border-color: #4a4a4a;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
    }
    
    /* Text areas and inputs */
    .stTextArea textarea, .stTextInput input {
        background-color: #1e1e1e;
        border: 1px solid #3a3a3a;
        border-radius: 8px;
        color: #ffffff;
    }
    
    /* Selectbox and multiselect */
    .stSelectbox, .stMultiSelect {
        background-color: #1e1e1e;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #1e1e1e;
        border: 2px dashed #3a3a3a;
        border-radius: 8px;
        padding: 20px;
    }
    
    /* Divider */
    hr {
        border-color: #2a2a2a;
        margin: 20px 0;
    }
    
    /* Success/Error/Warning messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 8px;
        padding: 12px;
    }
    
    /* Text color adjustments */
    p, span, div {
        color: #e5e7eb;
    }
    </style>
""", unsafe_allow_html=True)

# --- Utility Functions ---

@st.cache_data
def get_roles_from_api():
    """Fetch predefined roles from FastAPI server."""
    try:
        response = requests.get(f"{API_BASE_URL}/roles")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching roles: Ensure FastAPI server ({API_BASE_URL}) is running. Error: {e}")
        return []

def display_server_health():
    """Display FastAPI and Ollama server health status."""
    is_ollama_ready = False
    available_models = []
    
    try:
        health_response = requests.get(f"{API_BASE_URL}/health")
        health_response.raise_for_status()
        data = health_response.json()
        
        # FastAPI Status
        st.markdown('<div class="status-badge status-online">FastAPI Online</div>', unsafe_allow_html=True)
        
        # Ollama Status
        if data.get('ollama_connection') == 'successful':
            available_models = data.get("available_models", [])
            st.markdown('<div class="status-badge status-online">Ollama Connected</div>', unsafe_allow_html=True)
            if available_models:
                st.markdown(f"**Available Models:** {len(available_models)}")
                for model in available_models:
                    st.markdown(f"• `{model}`")
            else:
                st.warning("No models installed. Use `ollama pull <model>`")
            is_ollama_ready = True
        else:
            error_detail = data.get('detail', "Check port 11434")
            st.markdown('<div class="status-badge status-offline">Ollama Offline</div>', unsafe_allow_html=True)
            st.error(f"Connection failed: {error_detail}")

    except requests.exceptions.ConnectionError:
        st.markdown('<div class="status-badge status-offline">Server Offline</div>', unsafe_allow_html=True)
        st.error("Server unreachable or not started")
    except Exception as e:
        st.warning(f"Unexpected health check error: {e}")
        
    return available_models, is_ollama_ready

# --- Main Application ---

# Header
st.markdown("# GenAI Market Analyst")
st.markdown("*Flexible Multi-Company Financial Analysis Platform*")
st.markdown("---")

# Sidebar Configuration
with st.sidebar:
    st.markdown("## Configuration")
    
    # Server Health Display
    with st.container():
        st.markdown("### Server Status")
        available_models, is_ollama_ready = display_server_health()
    
    st.markdown("---")

    # 1. Model Selection
    st.markdown("### LLM Models")
    selected_models = []

    if is_ollama_ready and available_models:
        selected_models = st.multiselect(
            "Select models to compare:",
            options=available_models,
            default=available_models[:1] if available_models else [],
            help="Choose one or more models for comparative analysis"
        )
        if selected_models:
            st.success(f"{len(selected_models)} model(s) selected")
    elif is_ollama_ready and not available_models:
        st.warning("Ollama is connected but no models are installed. Use `ollama pull <model>`")
    else:
        st.error("Cannot connect to API. Please start the FastAPI server")

    st.markdown("---")

    # 2. System Prompt Management
    st.markdown("### Analyst Role (System Prompt)")
    roles_data = get_roles_from_api()
    
    is_role_selection_active = bool(roles_data)
    role_options = [r['role_key'] for r in roles_data]
    
    role_choice = st.radio(
        "Choose role type:",
        ["Predefined", "Custom"],
        index=0,
        key='role_selector',
        disabled=not is_role_selection_active,
        help="Select a predefined analyst role or create your own"
    )
    
    final_system_prompt = ""
    
    if role_choice == "Predefined" and is_role_selection_active:
        selected_role_key = st.selectbox(
            "Analysis role:",
            options=role_options,
            index=0
        )
        
        role_info = next((r for r in roles_data if r['role_key'] == selected_role_key), None)
        if role_info:
            final_system_prompt = role_info['prompt']
            with st.expander("View prompt"):
                st.info(final_system_prompt)
    
    elif role_choice == "Custom":
        custom_prompt = st.text_area(
            "Enter your custom system prompt:",
            height=150,
            value="You are a cynical investor. Provide a pessimistic, yet grounded analysis.",
            help="Define the personality and focus of your analyst"
        )
        final_system_prompt = custom_prompt
        st.success("Using custom prompt")

# Main Content Area
col_file, col_question = st.columns([1, 1], gap="large")

rows_to_analyze: List[Dict] = []
df_combined: pd.DataFrame = pd.DataFrame()

with col_file:
    st.markdown("### Data Upload")
    st.markdown("*Support for multiple CSV files*")
    
    uploaded_files = st.file_uploader(
        "Choose one or more company CSV files:",
        type="csv",
        accept_multiple_files=True,
        help="Upload CSV files containing company financial data"
    )

    if uploaded_files:
        try:
            list_of_dfs = []
            for uploaded_file in uploaded_files:
                df_temp = pd.read_csv(uploaded_file)
                # Replace NaN values with None for JSON compatibility
                df_temp = df_temp.replace({pd.NA: None, pd.NaT: None})
                df_temp = df_temp.where(pd.notnull(df_temp), None)
                # Add source file identification
                df_temp['Source_File'] = uploaded_file.name
                list_of_dfs.append(df_temp)
            
            df_combined = pd.concat(list_of_dfs, ignore_index=True)
            st.success(f"{len(uploaded_files)} file(s) loaded successfully. Total: {len(df_combined)} rows")

            non_source_cols = [c for c in df_combined.columns if c != 'Source_File']
            if non_source_cols:
                company_col = non_source_cols[0]
                st.markdown(f"**Identification column:** `{company_col}`")
                
                company_list = df_combined[company_col].unique().tolist()
                
                selected_companies = st.multiselect(
                    "Select companies to analyze (for comparison):",
                    company_list,
                    default=company_list[:2] if len(company_list) >= 2 else company_list[:1],
                    help="Choose multiple companies to compare"
                )

                rows_to_analyze = df_combined[df_combined[company_col].isin(selected_companies)].to_dict('records')
                
                # Additional cleaning: ensure all NaN values are converted to None
                import math
                cleaned_rows = []
                for row in rows_to_analyze:
                    cleaned_row = {}
                    for key, value in row.items():
                        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                            cleaned_row[key] = None
                        else:
                            cleaned_row[key] = value
                    cleaned_rows.append(cleaned_row)
                rows_to_analyze = cleaned_rows
                
                if rows_to_analyze:
                    st.markdown("---")
                    with st.expander(f"View extracted data ({len(rows_to_analyze)} row(s))"):
                        st.json(rows_to_analyze)
            else:
                st.warning("No data columns found after loading")
                df_combined = pd.DataFrame()

        except Exception as e:
            st.error(f"Error processing CSV file(s): {e}")
            df_combined = pd.DataFrame()

with col_question:
    st.markdown("### Analysis Question")
    st.markdown("*Define your specific analysis query*")
    
    custom_question = st.text_area(
        "Enter your analysis question:",
        value="What is the company's valuation outlook based on the P/E ratio and recent revenue trends?",
        height=120,
        help="Be specific about what aspects you want to analyze"
    )

    is_ready = len(rows_to_analyze) > 0 and len(selected_models) > 0 and final_system_prompt

    if not is_ready:
        st.warning("Please: (1) Load and select companies, (2) Choose at least one model, (3) Define analyst role")

    # Analysis Button
    st.markdown("---")
    if st.button("Run Multi-Model Analysis", disabled=not is_ready, use_container_width=True):
        
        with st.spinner(f"Analyzing with {len(selected_models)} model(s)... (parallel execution)"):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/analyze",
                    json={
                        "models": selected_models,
                        "system_prompt": final_system_prompt,
                        "row": rows_to_analyze,
                        "question": custom_question
                    },
                    timeout=300
                )
                response.raise_for_status()
                
                analysis_results = response.json()["analysis_results"]

                st.markdown("---")
                st.markdown("## Analysis Results (Comparison)")
                
                num_results = len(analysis_results)
                
                cols = st.columns(num_results)

                for i, result in enumerate(analysis_results):
                    with cols[i]:
                        st.markdown(f'<div class="model-card">', unsafe_allow_html=True)
                        st.markdown(f"### {result['model']}")
                        
                        if result['status'] == 'success':
                            st.markdown('<div class="status-badge status-online">Success</div>', unsafe_allow_html=True)
                            st.markdown("---")
                            st.markdown(result['response'])
                        else:
                            st.markdown('<div class="status-badge status-offline">Failed</div>', unsafe_allow_html=True)
                            st.error(f"**Details:** {result['status'].replace('error: ', '')}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)

            except requests.exceptions.RequestException as e:
                st.error(f"Communication error with FastAPI server. Is it running on {API_BASE_URL}? Details: {e}")
            except Exception as e:
                st.exception(f"An unexpected error occurred: {e}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>GenAI Market Analyst | Powered by Ollama & FastAPI</p>
    </div>
    """,
    unsafe_allow_html=True
)
