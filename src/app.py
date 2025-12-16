"""
MedVerify AI - Main Application Entry Point
Streamlit-based frontend for the Healthcare Provider Validation System
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys
import os
import time

# Add src to path to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents_phase1 import Agent1DataValidation
from src.orchestrator import MultiAgentOrchestrator

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="MedVerify AI | Healthcare Directory Validation",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        font-weight: 700;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        font-weight: 500;
    }
    .card {
        background-color: #f9f9f9;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #0D47A1;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3063/3063176.png", width=60)
    st.title("MedVerify AI")
    st.caption("Autonomous Validation System")
    
    st.markdown("---")
    
    menu = st.radio(
        "Navigation", 
        ["Dashboard", "Single Validator", "Batch Processing", "Analytics & Reports"]
    )
    
    st.markdown("---")
    st.info(
        "**System Status**\n\n"
        "✅ Agent 1: Active\n\n"
        "✅ Agent 2: Active\n\n"
        "✅ Agent 3: Active"
    )

# ============================================================================
# HOME DASHBOARD
# ============================================================================
if menu == "Dashboard":
    st.markdown('<p class="main-header">MedVerify AI Control Center</p>', unsafe_allow_html=True)
    st.markdown("### Intelligent Healthcare Provider Directory Validation")
    
    # Project Status Metrics (Static for now, dynamic later)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="System Accuracy", value="98.5%", delta="+45%")
    with col2:
        st.metric(label="Records Processed", value="12,450", delta="+120 today")
    with col3:
        st.metric(label="Fraud Detected", value="342", delta="2.7% rate", delta_color="inverse")
    with col4:
        st.metric(label="Cost Saved", value="₹4.2L", delta="Est.")

    st.markdown("---")
    
    # Workflow Visualization
    st.markdown("### 🤖 Autonomous Workflow")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
        <div class="card">
            <h4>1️⃣ Validation Agent</h4>
            <p>Checks format, compliance, and registration data against NMC/MCI standards.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown("""
        <div class="card">
            <h4>2️⃣ Enrichment Agent</h4>
            <p>Standardizes cities, specialties, and fills missing gaps using fuzzy logic.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown("""
        <div class="card">
            <h4>3️⃣ Cross-Validation</h4>
            <p>Detects duplicates, geolocation fraud, and anomalies in provider data.</p>
        </div>
        """, unsafe_allow_html=True)

    # Quick Actions
    st.markdown("### 🚀 Quick Actions")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Start New Validation Task", use_container_width=True):
            st.toast("Navigate to 'Single Validator' to begin!")
    with col_b:
        if st.button("Upload CSV Dataset", use_container_width=True):
            st.toast("Navigate to 'Batch Processing' to upload!")

# ============================================================================
# PLACEHOLDERS
# ============================================================================
# ============================================================================
# SINGLE RECORD VALIDATOR
# ============================================================================
elif menu == "Single Validator":
    st.markdown('<p class="main-header">Single Record Validator</p>', unsafe_allow_html=True)
    st.markdown("Manually validate a single healthcare provider record against the autonomous agent system.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📝 Provider Details")
        with st.form("single_validate_form"):
            name = st.text_input("Provider Name", placeholder="e.g., Dr. Rajesh Kumar")
            
            c1, c2 = st.columns(2)
            with c1:
                phone = st.text_input("Phone Number", placeholder="e.g., 9876543210")
            with c2:
                pincode = st.text_input("Pincode", placeholder="e.g., 560001")
                
            c3, c4 = st.columns(2)
            with c3:
                city = st.text_input("City", placeholder="e.g., Bangalore")
            with c4:
                specialty = st.text_input("Specialty", placeholder="e.g., Cardiology")
                
            reg_no = st.text_input("Registration Number", placeholder="e.g., MCI-12345")
            address = st.text_area("Clinic Address", placeholder="e.g., 123 MG Road, Indiranagar")
            
            submitted = st.form_submit_button("🚀 Validate Record", use_container_width=True)

    with col2:
        st.markdown("### 🔍 Validation Results")
        
        if submitted:
            if not name or not phone:
                st.error("Name and Phone are required fields!")
            else:
                # 1. Create Record Dictionary
                record = {
                    "name": name,
                    "phone": phone,
                    "city": city,
                    "specialty": specialty,
                    "registration_no": reg_no,
                    "clinic_address": address,
                    "pincode": pincode
                }
                
                # 2. Run Orchestrator
                with st.spinner("🤖 Agents working... Validating > Enriching > Cross-Checking..."):
                    try:
                        orchestrator = MultiAgentOrchestrator()
                        result = orchestrator.validate_provider(record)
                        
                        # 3. Display Decision Badge
                        decision = result['decision']
                        color = "green" if "APPROVE" in decision else "orange" if "REVIEW" in decision else "red"
                        st.markdown(f"""
                        <div style="background-color: {color}; color: white; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 20px;">
                            <h2 style="margin:0">{decision}</h2>
                            <p style="margin:0">Confidence: {result['combined_confidence_percentage']}% | Score: {result['combined_score']}/200</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 4. Display Agent Breakdown
                        t1, t2, t3 = st.tabs(["Agent 1 (Validation)", "Agent 2 (Enrichment)", "Agent 3 (Fraud)"])
                        
                        with t1:
                            s1 = result['agent1_validation']
                            st.metric("Validation Score", f"{s1.get('confidence_agent1', 0)}/100")
                            if s1.get('issues_validation'):
                                st.error("Issues Found:")
                                for issue in s1['issues_validation']:
                                    st.write(f"❌ {issue}")
                            else:
                                st.success("✅ No validation issues found.")
                                
                        with t2:
                            s2 = result['agent2_enrichment']
                            st.metric("Enrichment Score", f"{s2.get('confidence_agent2', 0)}/60")
                            if s2.get('enrichment_changes'):
                                st.info("Changes Applied:")
                                for change in s2['enrichment_changes']:
                                    st.write(f"✨ {change}")
                            
                            # Show before/after comparison
                            st.caption("Enriched Data:")
                            st.json(s2.get('record_enriched', {}))
                            
                        with t3:
                            s3 = result['agent3_cross_validation']
                            st.metric("Cross-Check Score", f"{s3.get('confidence_agent3', 0)}/40")
                            if s3.get('cross_validation_flags'):
                                st.warning("Fraud Flags:")
                                for flag in s3['cross_validation_flags']:
                                    st.write(f"⚠️ {flag}")
                            else:
                                st.success("✅ No fraud patterns detected.")

                    except Exception as e:
                        st.error(f"An error occurred during processing: {str(e)}")
        
        else:
            st.info("👈 Fill out the form and press 'Validate Record' to see the autonomous agents in action.")
            st.markdown("""
            **Try these test cases:**
            
            **1. Perfect Record:**
            - Phone: 9876543210
            - Pincode: 560001
            - City: Bangalore
            
            **2. Needs Enrichment (Typo):**
            - City: "Banaglore" (Typo)
            - Phone: "+91-98765-43210" (Format)
            """)


# ============================================================================
# BATCH PROCESSING
# ============================================================================
elif menu == "Batch Processing":
    st.markdown('<p class="main-header">Batch Data Processing</p>', unsafe_allow_html=True)
    st.markdown("Upload a CSV file containing multiple provider records for bulk validation.")
    
    # File Uploader
    uploaded_file = st.file_uploader("Upload CSV File", type=['csv'], help="Required columns: name, phone, city, specialty")
    
    if uploaded_file is not None:
        try:
            # 1. Read the file
            df = pd.read_csv(uploaded_file)
            st.info(f"✅ Loaded {len(df)} records successfully.")
            
            # Preview Data
            with st.expander("👀 View Raw Data"):
                st.dataframe(df.head())
            
            # Start Processing Button
            if st.button(f"🚀 Process {len(df)} Records", type="primary"):
                
                # Initialize result containers
                results_list = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Initialize Orchestrator
                orchestrator = MultiAgentOrchestrator()
                
                # Process Loop
                total_records = len(df)
                start_time_batch = time.time()
                
                # Create a tab for live logs
                log_container = st.container()
                
                for index, row in df.iterrows():
                    # Update status
                    status_text.text(f"Processing Record {index + 1}/{total_records}: {row.get('name', 'Unknown')}")
                    
                    # Convert row to dict
                    record = row.to_dict()
                    
                    # Run Validation Pipeline
                    result = orchestrator.validate_provider(record)
                    
                    # Store key results for the summary table
                    summary_row = {
                        "Name": record.get("name"),
                        "Phone": record.get("phone"),
                        "Decision": result['decision'],
                        "Confidence": f"{result['combined_confidence_percentage']}%",
                        "Score": result['combined_score'],
                        "Enriched City": result['enriched_record'].get('city'),
                        "Issues": len(result['agent1_validation'].get('issues_validation', [])) + 
                                  len(result['agent3_cross_validation'].get('cross_validation_flags', []))
                    }
                    results_list.append(summary_row)
                    
                    # Update progress
                    progress_bar.progress((index + 1) / total_records)
                
                # Processing Complete
                total_time = round(time.time() - start_time_batch, 2)
                st.success(f"🎉 Processing Complete! Processed {total_records} records in {total_time} seconds.")
                
                # Display Results Table
                results_df = pd.DataFrame(results_list)
                
                # Color coding function for the dataframe
                def color_decision(val):
                    color = 'green' if 'APPROVE' in val else 'orange' if 'REVIEW' in val else 'red'
                    return f'color: {color}; font-weight: bold'

                st.markdown("### 📊 Processing Results")
                st.dataframe(
                    results_df.style.applymap(color_decision, subset=['Decision']),
                    use_container_width=True
                )
                
                # Download Report Button
                csv = results_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Download Summary Report",
                    csv,
                    "validation_report.csv",
                    "text/csv",
                    key='download-csv'
                )
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            
    else:
        # Show Template Download
        st.info("👋 Don't have a file? Download our template.")
        
        # Create a sample template on the fly for them to download
        sample_data = pd.DataFrame([
            {"name": "Dr. Sample", "phone": "9876543210", "city": "Bangalore", "specialty": "Cardiology", "pincode": "560001", "registration_no": "MCI-123", "clinic_address": "MG Road"},
            {"name": "Dr. Test", "phone": "+91-98765-43210", "city": "Banaglore", "specialty": "CARDIO", "pincode": "560001", "registration_no": "MCI-456", "clinic_address": "Indiranagar"}
        ])
        csv_template = sample_data.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            "📄 Download CSV Template",
            csv_template,
            "medverify_template.csv",
            "text/csv"
        )

# ============================================================================
# ANALYTICS DASHBOARD
# ============================================================================
elif menu == "Analytics & Reports":
    st.markdown('<p class="main-header">Analytics Dashboard</p>', unsafe_allow_html=True)
    st.markdown("Visual insights into healthcare provider directory quality and validation performance.")
    
    # 1. Upload Data for Analysis
    uploaded_file = st.file_uploader("Upload Processed Report (CSV)", type=['csv'], help="Upload the 'validation_report.csv' generated from Batch Processing")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            # Key Metrics Row
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Total Records", len(df))
            with m2:
                approval_rate = (len(df[df['Decision'].str.contains('APPROVE')]) / len(df)) * 100
                st.metric("Approval Rate", f"{approval_rate:.1f}%")
            with m3:
                avg_score = df['Score'].mean()
                st.metric("Avg Quality Score", f"{avg_score:.1f}/200")
            with m4:
                fraud_count = len(df[df['Decision'] == 'REJECT'])
                st.metric("Potential Fraud", fraud_count, delta_color="inverse")
            
            st.markdown("---")
            
            # CHARTS ROW 1
            c1, c2 = st.columns(2)
            
            with c1:
                st.subheader("Validation Decisions")
                # Pie Chart for Decisions
                fig_pie = px.pie(
                    df, 
                    names='Decision', 
                    title='Distribution of Validation Decisions',
                    color='Decision',
                    color_discrete_map={
                        'AUTO_APPROVE': '#00CC96',
                        'CONDITIONAL_APPROVE': '#636EFA',
                        'MANUAL_REVIEW': '#FFA15A',
                        'REJECT': '#EF553B'
                    }
                )
                st.plotly_chart(fig_pie, use_container_width=True)
                
            with c2:
                st.subheader("Confidence Score Distribution")
                # Histogram for Scores
                fig_hist = px.histogram(
                    df, 
                    x='Score', 
                    nbins=20, 
                    title='Quality Score Distribution (0-200)',
                    color_discrete_sequence=['#636EFA']
                )
                fig_hist.add_vline(x=180, line_dash="dash", line_color="green", annotation_text="Auto Approve")
                fig_hist.add_vline(x=120, line_dash="dash", line_color="red", annotation_text="Reject")
                st.plotly_chart(fig_hist, use_container_width=True)
            
            # CHARTS ROW 2
            st.subheader("Geographic & Error Analysis")
            c3, c4 = st.columns(2)
            
            with c3:
                # Top Cities Bar Chart
                if 'Enriched City' in df.columns:
                    city_counts = df['Enriched City'].value_counts().head(10).reset_index()
                    city_counts.columns = ['City', 'Count']
                    fig_bar = px.bar(
                        city_counts, 
                        x='City', 
                        y='Count', 
                        title='Top 10 Cities Processed',
                        color='Count'
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("City data not available for visualization.")
            
            with c4:
                # Issues Analysis (if available)
                if 'Issues' in df.columns:
                    # FIX: Explicitly name the columns after reset_index
                    issues_data = df['Issues'].value_counts().reset_index()
                    issues_data.columns = ['Issue_Count', 'Record_Count']  # Rename columns clearly
                    
                    fig_issues = px.bar(
                        issues_data,
                        x='Issue_Count', 
                        y='Record_Count', 
                        labels={'Issue_Count': 'Number of Issues per Record', 'Record_Count': 'Count of Records'},
                        title='Data Quality Issues Frequency',
                        text='Record_Count'  # Add text labels on bars
                    )
                    st.plotly_chart(fig_issues, use_container_width=True)
                else:
                    st.info("Issue details not available for visualization.")

                    
        except Exception as e:
            st.error(f"Error analyzing file: {str(e)}")
            st.warning("Make sure you uploaded the 'validation_report.csv' generated by the Batch Processing module.")
            
    else:
        st.info("👆 Upload a processed validation report CSV to view analytics.")
        st.markdown("""
        **How to get a report:**
        1. Go to **Batch Processing**
        2. Upload your provider data
        3. Process the records
        4. Click **"Download Summary Report"**
        5. Upload that file here!
        """)

