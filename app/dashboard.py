import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import time
from datetime import datetime

st.set_page_config(page_title="GenomeGuard Dashboard", layout="wide")

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None

def make_authenticated_request(endpoint, method="GET", data=None, files=None):
    """Make authenticated API request"""
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    
    url = f"{API_BASE_URL}{endpoint}"
    
    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        if files:
            response = requests.post(url, headers=headers, files=files)
        else:
            response = requests.post(url, headers=headers, json=data)
    elif method == "DELETE":
        response = requests.delete(url, headers=headers)
    
    return response

def login_user(username, password):
    """Login user and store token"""
    data = {"username": username, "password": password}
    response = requests.post(f"{API_BASE_URL}/auth/token", data=data)
    
    if response.status_code == 200:
        token_data = response.json()
        st.session_state.token = token_data["access_token"]
        
        # Get user info
        user_response = make_authenticated_request("/auth/me")
        if user_response.status_code == 200:
            st.session_state.user = user_response.json()
            return True
    return False

def register_user(username, email, password, full_name):
    """Register new user"""
    data = {
        "username": username,
        "email": email,
        "password": password,
        "full_name": full_name
    }
    response = requests.post(f"{API_BASE_URL}/auth/register", json=data)
    return response.status_code == 200

st.title("🧬 GenomeGuard - Genetic Disease Risk Predictor")
st.markdown("AI-powered genetic analysis with secure backend")

# Authentication check
if not st.session_state.token:
    st.sidebar.header("Authentication")
    auth_mode = st.sidebar.selectbox("Choose action", ["Login", "Register"])
    
    if auth_mode == "Login":
        with st.sidebar.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if login_user(username, password):
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    else:  # Register
        with st.sidebar.form("register_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            full_name = st.text_input("Full Name")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Register")
            
            if submit:
                if register_user(username, email, password, full_name):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Registration failed")
    
    st.info("Please login or register to access GenomeGuard")
    st.stop()

# Sidebar for authenticated users
st.sidebar.header(f"Welcome, {st.session_state.user['username']}")
if st.sidebar.button("Logout"):
    st.session_state.token = None
    st.session_state.user = None
    st.rerun()

st.sidebar.header("Navigation")
page = st.sidebar.selectbox("Choose a page", ["Upload & Analyze", "Analysis History", "Results", "About"])

if page == "Upload & Analyze":
    st.header("Upload Genome Data")
    
    uploaded_file = st.file_uploader("Choose a VCF file", type=['vcf'])
    
    if uploaded_file:
        st.success(f"File selected: {uploaded_file.name}")
        
        if st.button("Analyze Genome"):
            with st.spinner("Uploading and processing genome data..."):
                # Upload file to backend
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/plain")}
                response = make_authenticated_request("/analysis/upload", method="POST", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"Analysis started! ID: {result['analysis_id']}")
                    st.session_state['current_analysis_id'] = result['analysis_id']
                    
                    # Poll for results
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i in range(30):  # Poll for 30 seconds
                        time.sleep(1)
                        progress_bar.progress((i + 1) / 30)
                        
                        # Check analysis status
                        analysis_response = make_authenticated_request(f"/analysis/results/{result['analysis_id']}")
                        if analysis_response.status_code == 200:
                            analysis_data = analysis_response.json()
                            status_text.text(f"Status: {analysis_data['status']}")
                            
                            if analysis_data['status'] == 'completed':
                                st.session_state['current_analysis'] = analysis_data
                                st.success("Analysis completed successfully!")
                                st.rerun()
                                break
                            elif analysis_data['status'] == 'failed':
                                st.error(f"Analysis failed: {analysis_data.get('error_message', 'Unknown error')}")
                                break
                    else:
                        st.warning("Analysis is taking longer than expected. Check the Analysis History page.")
                else:
                    st.error("Upload failed. Please try again.")

elif page == "Analysis History":
    st.header("Analysis History")
    
    # Get user's analysis history
    response = make_authenticated_request("/analysis/history")
    
    if response.status_code == 200:
        analyses = response.json()
        
        if analyses:
            for analysis in analyses:
                with st.expander(f"Analysis: {analysis['vcf_file']} - {analysis['status'].title()}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Created:** {analysis['created_at'][:19]}")
                        st.write(f"**Status:** {analysis['status'].title()}")
                    
                    with col2:
                        if analysis['status'] == 'completed':
                            st.write(f"**Risk Level:** {analysis['risk_classification'].title()}")
                            st.write(f"**Risk Probability:** {analysis['risk_probability']:.1%}")
                    
                    with col3:
                        if analysis['status'] == 'completed':
                            st.write(f"**Total Variants:** {analysis['total_variants']}")
                            st.write(f"**High Risk:** {analysis['high_risk_variants']}")
                    
                    if analysis['status'] == 'completed':
                        if st.button(f"View Details", key=f"view_{analysis['id']}"):
                            st.session_state['current_analysis'] = analysis
                            st.session_state['selected_page'] = "Results"
                            st.rerun()
                    
                    if st.button(f"Delete", key=f"delete_{analysis['id']}"):
                        delete_response = make_authenticated_request(f"/analysis/results/{analysis['id']}", method="DELETE")
                        if delete_response.status_code == 200:
                            st.success("Analysis deleted")
                            st.rerun()
        else:
            st.info("No analyses found. Upload a VCF file to get started.")
    else:
        st.error("Failed to load analysis history")

elif page == "Results":
    st.header("Analysis Results")
    
    if 'current_analysis' in st.session_state:
        analysis = st.session_state['current_analysis']
        
        # Risk overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Risk Classification", analysis['risk_classification'].title())
        
        with col2:
            st.metric("Risk Probability", f"{analysis['risk_probability']:.1%}")
        
        with col3:
            st.metric("Total Variants", analysis['total_variants'])
        
        # Risk visualization
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = analysis['risk_probability'] * 100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Disease Risk Score"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 30], 'color': "lightgreen"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        
        st.plotly_chart(fig)
        
        # Variant details
        st.subheader("Variant Summary")
        variant_data = {
            'Category': ['High Risk', 'Pathogenic', 'Total'],
            'Count': [analysis['high_risk_variants'], analysis['pathogenic_variants'], analysis['total_variants']]
        }
        
        fig_bar = px.bar(variant_data, x='Category', y='Count', 
                        title="Variant Categories")
        st.plotly_chart(fig_bar)
        
        # Detailed variant table
        if analysis.get('variants'):
            st.subheader("Detailed Variants")
            variants_df = pd.DataFrame(analysis['variants'])
            st.dataframe(variants_df)
        
    else:
        st.info("No analysis results selected. Please select an analysis from the History page.")

elif page == "About":
    st.header("About GenomeGuard")
    st.markdown("""
    **GenomeGuard** is an AI-powered genetic disease prediction system with secure backend infrastructure.
    
    ### Features:
    - 🔒 **Secure Backend**: User authentication and data protection
    - 🧬 **VCF Analysis**: Processes standard genomic variant files
    - 🤖 **AI Predictions**: Machine learning models for disease risk assessment
    - 📊 **Visual Reports**: Interactive dashboards and charts
    - 📱 **User Management**: Personal analysis history and results
    - 🗄️ **MongoDB Storage**: Scalable database for analysis results
    
    ### Supported Diseases:
    - Breast/Ovarian Cancer (BRCA1/BRCA2)
    - Alzheimer's Disease (APOE)
    - Li-Fraumeni Syndrome (TP53)
    
    ### Architecture:
    - **Frontend**: Streamlit dashboard
    - **Backend**: FastAPI with MongoDB
    - **Authentication**: JWT tokens with bcrypt hashing
    - **Processing**: Async background tasks
    - **Storage**: Secure file handling and database storage
    
    ### Workflow:
    1. Register/Login to secure account
    2. Upload VCF file through API
    3. Background processing and annotation
    4. ML model prediction
    5. Store results in database
    6. View interactive reports
    """)

# Footer
st.markdown("---")
st.markdown("GenomeGuard v2.0 - Secure Genetic Analysis Platform")