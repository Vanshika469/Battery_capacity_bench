import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import time
import io
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Battery Cell Simulation Dashboard",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .error-message {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .stSelectbox > div > div {
        background-color: #f8f9fa;
    }
    
    .task-card {
        border: 2px solid #e9ecef;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: linear-gradient(45deg, #f8f9fa 0%, #e9ecef 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "cells_data" not in st.session_state:
    st.session_state.cells_data = {}
if "tasks_data" not in st.session_state:
    st.session_state.tasks_data = {}
if "simulation_running" not in st.session_state:
    st.session_state.simulation_running = False
if "simulation_data" not in st.session_state:
    st.session_state.simulation_data = []

# Sidebar navigation
st.sidebar.markdown("## 🔋 Navigation")
page = st.sidebar.selectbox(
    "Select Page",
    ["🏠 Home", "⚡ Setup Cells", "📋 Add Tasks", "📊 Real-time Analysis", "📥 Data Export"],
    index=0
)

# Helper functions
def generate_cell_data(cell_type, cell_id):
    """Generate initial cell data based on type"""
    voltage = 3.2 if cell_type == "LFP" else 3.6
    min_voltage = 2.8 if cell_type == "LFP" else 3.2
    max_voltage = 3.6 if cell_type == "LFP" else 4.0
    current = 0.0
    temp = round(random.uniform(25, 40), 1)
    capacity = round(voltage * current, 2)
    
    return {
        "cell_id": cell_id,
        "cell_type": cell_type,
        "voltage": voltage,
        "current": current,
        "temperature": temp,
        "capacity": capacity,
        "min_voltage": min_voltage,
        "max_voltage": max_voltage,
        "status": "Active",
        "created_at": datetime.now()
    }

def simulate_real_time_data():
    """Simulate real-time data changes"""
    if st.session_state.cells_data:
        for cell_id, cell_data in st.session_state.cells_data.items():
            # Simulate small variations
            voltage_change = random.uniform(-0.1, 0.1)
            temp_change = random.uniform(-2, 2)
            
            # Update values within limits
            new_voltage = max(cell_data["min_voltage"], 
                            min(cell_data["max_voltage"], 
                                cell_data["voltage"] + voltage_change))
            new_temp = max(20, min(60, cell_data["temperature"] + temp_change))
            
            st.session_state.cells_data[cell_id]["voltage"] = round(new_voltage, 2)
            st.session_state.cells_data[cell_id]["temperature"] = round(new_temp, 1)
            st.session_state.cells_data[cell_id]["capacity"] = round(
                new_voltage * cell_data["current"], 2
            )

# HOME PAGE
if page == "🏠 Home":
    st.markdown('<h1 class="main-header">🔋 Battery Cell Simulation Dashboard</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>⚡ Setup Cells</h3>
            <p>Configure your battery cells with different types and parameters</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📋 Add Tasks</h3>
            <p>Define charging/discharging tasks for your battery cells</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Analytics</h3>
            <p>Monitor real-time performance and export data</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Cells", len(st.session_state.cells_data))
    
    with col2:
        st.metric("Active Tasks", len(st.session_state.tasks_data))
    
    with col3:
        lfp_count = sum(1 for cell in st.session_state.cells_data.values() if cell["cell_type"] == "LFP")
        st.metric("LFP Cells", lfp_count)
    
    with col4:
        nmc_count = sum(1 for cell in st.session_state.cells_data.values() if cell["cell_type"] == "NMC")
        st.metric("NMC Cells", nmc_count)
    
    if st.session_state.cells_data:
        st.markdown("### 📈 Quick Overview")
        
        # Create a quick overview chart
        df = pd.DataFrame(st.session_state.cells_data).T
        fig = px.bar(df, x=df.index, y="voltage", color="cell_type",
                    title="Cell Voltage Overview",
                    color_discrete_map={"LFP": "#2ecc71", "NMC": "#e74c3c"})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# SETUP CELLS PAGE
elif page == "⚡ Setup Cells":
    st.markdown('<h1 class="main-header">⚡ Setup Battery Cells</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<h3 class="sub-header">Add New Cell</h3>', unsafe_allow_html=True)
        
        with st.form("add_cell_form"):
            cell_type = st.selectbox("Cell Type", ["LFP", "NMC"])
            cell_name = st.text_input("Cell Name (optional)", placeholder="e.g., Cell_A1")
            
            submitted = st.form_submit_button("➕ Add Cell", use_container_width=True)
            
            if submitted:
                cell_id = cell_name if cell_name else f"cell_{len(st.session_state.cells_data) + 1}_{cell_type.lower()}"
                
                if cell_id not in st.session_state.cells_data:
                    st.session_state.cells_data[cell_id] = generate_cell_data(cell_type, cell_id)
                    st.success(f"✅ Cell '{cell_id}' added successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ Cell '{cell_id}' already exists!")
    
    with col2:
        st.markdown('<h3 class="sub-header">Current Cells</h3>', unsafe_allow_html=True)
        
        if st.session_state.cells_data:
            # Display cells in an editable format
            for cell_id, cell_data in st.session_state.cells_data.items():
                with st.expander(f"🔋 {cell_id} ({cell_data['cell_type']})", expanded=False):
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.metric("Voltage (V)", f"{cell_data['voltage']:.2f}")
                        st.metric("Current (A)", f"{cell_data['current']:.2f}")
                    
                    with col_b:
                        st.metric("Temperature (°C)", f"{cell_data['temperature']:.1f}")
                        st.metric("Capacity", f"{cell_data['capacity']:.2f}")
                    
                    with col_c:
                        st.metric("Min Voltage", f"{cell_data['min_voltage']:.1f}")
                        st.metric("Max Voltage", f"{cell_data['max_voltage']:.1f}")
                    
                    if st.button(f"🗑️ Remove {cell_id}", key=f"remove_{cell_id}"):
                        del st.session_state.cells_data[cell_id]
                        st.success(f"Cell {cell_id} removed!")
                        st.rerun()
        else:
            st.info("No cells configured yet. Add your first cell!")
    
    # Summary table
    if st.session_state.cells_data:
        st.markdown("---")
        st.markdown("### 📊 Cells Summary Table")
        
        df = pd.DataFrame(st.session_state.cells_data).T
        df = df[["cell_type", "voltage", "current", "temperature", "capacity", "min_voltage", "max_voltage", "status"]]
        st.dataframe(df, use_container_width=True)

# ADD TASKS PAGE
elif page == "📋 Add Tasks":
    st.markdown('<h1 class="main-header">📋 Add Battery Tasks</h1>', unsafe_allow_html=True)
    
    if not st.session_state.cells_data:
        st.warning("⚠️ Please setup cells first before adding tasks!")
        st.stop()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<h3 class="sub-header">Create New Task</h3>', unsafe_allow_html=True)
        
        with st.form("add_task_form"):
            task_type = st.selectbox("Task Type", ["CC_CV", "IDLE", "CC_CD"])
            task_name = st.text_input("Task Name", placeholder="e.g., Charge_Cycle_1")
            
            # Dynamic form fields based on task type
            if task_type == "CC_CV":
                st.markdown("**CC_CV Parameters:**")
                cc_input = st.text_input("CC/CP Value", placeholder="e.g., 5A or 10W")
                cv_voltage = st.number_input("CV Voltage (V)", min_value=0.0, value=4.0, step=0.1)
                current = st.number_input("Current (A)", min_value=0.0, value=1.0, step=0.1)
                capacity = st.number_input("Capacity", min_value=0.0, value=100.0, step=1.0)
                time_seconds = st.number_input("Time (seconds)", min_value=1, value=3600, step=1)
                
            elif task_type == "IDLE":
                st.markdown("**IDLE Parameters:**")
                time_seconds = st.number_input("Time (seconds)", min_value=1, value=1800, step=1)
                cc_input = cv_voltage = current = capacity = None
                
            elif task_type == "CC_CD":
                st.markdown("**CC_CD Parameters:**")
                cc_input = st.text_input("CC/CP Value", placeholder="e.g., 5A or 10W")
                voltage = st.number_input("Voltage (V)", min_value=0.0, value=3.0, step=0.1)
                capacity = st.number_input("Capacity", min_value=0.0, value=100.0, step=1.0)
                time_seconds = st.number_input("Time (seconds)", min_value=1, value=3600, step=1)
                cv_voltage = current = None
            
            submitted = st.form_submit_button("➕ Add Task", use_container_width=True)
            
            if submitted:
                task_id = task_name if task_name else f"task_{len(st.session_state.tasks_data) + 1}"
                
                if task_id not in st.session_state.tasks_data:
                    task_data = {
                        "task_id": task_id,
                        "task_type": task_type,
                        "time_seconds": time_seconds,
                        "status": "Pending",
                        "created_at": datetime.now()
                    }
                    
                    if task_type == "CC_CV":
                        task_data.update({
                            "cc_cp": cc_input,
                            "cv_voltage": cv_voltage,
                            "current": current,
                            "capacity": capacity
                        })
                    elif task_type == "CC_CD":
                        task_data.update({
                            "cc_cp": cc_input,
                            "voltage": voltage,
                            "capacity": capacity
                        })
                    
                    st.session_state.tasks_data[task_id] = task_data
                    st.success(f"✅ Task '{task_id}' added successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ Task '{task_id}' already exists!")
    
    with col2:
        st.markdown('<h3 class="sub-header">Current Tasks</h3>', unsafe_allow_html=True)
        
        if st.session_state.tasks_data:
            for task_id, task_data in st.session_state.tasks_data.items():
                with st.expander(f"📋 {task_id} ({task_data['task_type']})", expanded=False):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.write(f"**Type:** {task_data['task_type']}")
                        st.write(f"**Duration:** {task_data['time_seconds']} seconds")
                        st.write(f"**Status:** {task_data['status']}")
                    
                    with col_b:
                        if task_data['task_type'] == "CC_CV":
                            st.write(f"**CC/CP:** {task_data.get('cc_cp', 'N/A')}")
                            st.write(f"**CV Voltage:** {task_data.get('cv_voltage', 'N/A')} V")
                            st.write(f"**Current:** {task_data.get('current', 'N/A')} A")
                        elif task_data['task_type'] == "CC_CD":
                            st.write(f"**CC/CP:** {task_data.get('cc_cp', 'N/A')}")
                            st.write(f"**Voltage:** {task_data.get('voltage', 'N/A')} V")
                            st.write(f"**Capacity:** {task_data.get('capacity', 'N/A')}")
                    
                    if st.button(f"🗑️ Remove {task_id}", key=f"remove_task_{task_id}"):
                        del st.session_state.tasks_data[task_id]
                        st.success(f"Task {task_id} removed!")
                        st.rerun()
        else:
            st.info("No tasks configured yet. Add your first task!")
    
    # Tasks summary table
    if st.session_state.tasks_data:
        st.markdown("---")
        st.markdown("### 📊 Tasks Summary Table")
        
        df = pd.DataFrame(st.session_state.tasks_data).T
        display_cols = ["task_type", "time_seconds", "status"]
        if "cc_cp" in df.columns:
            display_cols.append("cc_cp")
        if "cv_voltage" in df.columns:
            display_cols.append("cv_voltage")
        if "voltage" in df.columns:
            display_cols.append("voltage")
        
        st.dataframe(df[display_cols], use_container_width=True)

# REAL-TIME ANALYSIS PAGE
elif page == "📊 Real-time Analysis":
    st.markdown('<h1 class="main-header">📊 Real-time Analysis Dashboard</h1>', unsafe_allow_html=True)
    
    if not st.session_state.cells_data:
        st.warning("⚠️ Please setup cells first!")
        st.stop()
    
    # Control panel
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ Start Simulation", use_container_width=True):
            st.session_state.simulation_running = True
    
    with col2:
        if st.button("⏸️ Stop Simulation", use_container_width=True):
            st.session_state.simulation_running = False
    
    with col3:
        auto_refresh = st.checkbox("🔄 Auto Refresh (2s)", value=True)
    
    # Auto refresh
    if auto_refresh and st.session_state.simulation_running:
        simulate_real_time_data()
        time.sleep(0.1)  # Small delay for smooth animation
        st.rerun()
    
    # Real-time metrics
    if st.session_state.cells_data:
        st.markdown("### 🔋 Live Cell Metrics")
        
        cols = st.columns(min(4, len(st.session_state.cells_data)))
        
        for idx, (cell_id, cell_data) in enumerate(st.session_state.cells_data.items()):
            with cols[idx % 4]:
                st.metric(
                    f"{cell_id}",
                    f"{cell_data['voltage']:.2f}V",
                    f"{cell_data['temperature']:.1f}°C"
                )
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.cells_data:
            # Voltage chart
            df = pd.DataFrame(st.session_state.cells_data).T
            fig1 = px.line(df, x=df.index, y="voltage", color="cell_type",
                          title="🔋 Cell Voltage Monitoring",
                          labels={"voltage": "Voltage (V)", "index": "Cell ID"})
            fig1.update_layout(height=400)
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        if st.session_state.cells_data:
            # Temperature chart
            fig2 = px.bar(df, x=df.index, y="temperature", color="cell_type",
                         title="🌡️ Cell Temperature Monitoring",
                         labels={"temperature": "Temperature (°C)", "index": "Cell ID"})
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)
    
    # Task progress
    if st.session_state.tasks_data:
        st.markdown("### 📋 Task Progress")
        
        for task_id, task_data in st.session_state.tasks_data.items():
            progress = random.randint(0, 100) if st.session_state.simulation_running else 0
            st.progress(progress / 100, text=f"{task_id}: {progress}%")
    
    # Combined analytics
    if st.session_state.cells_data:
        st.markdown("### 📈 Combined Analytics")
        
        # Create subplot
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Voltage vs Temperature", "Capacity Distribution", 
                          "Cell Type Distribution", "Voltage Range"),
            specs=[[{"secondary_y": True}, {"type": "pie"}],
                   [{"type": "pie"}, {"type": "bar"}]]
        )
        
        df = pd.DataFrame(st.session_state.cells_data).T
        
        # Scatter plot
        fig.add_trace(
            go.Scatter(x=df["voltage"], y=df["temperature"], 
                      mode="markers", name="Voltage vs Temp",
                      marker=dict(size=10, color=df["capacity"], colorscale="Viridis")),
            row=1, col=1
        )
        
        # Capacity pie chart
        fig.add_trace(
            go.Pie(labels=df.index, values=df["capacity"], name="Capacity"),
            row=1, col=2
        )
        
        # Cell type distribution
        cell_type_counts = df["cell_type"].value_counts()
        fig.add_trace(
            go.Pie(labels=cell_type_counts.index, values=cell_type_counts.values, 
                  name="Cell Types"),
            row=2, col=1
        )
        
        # Voltage range bar chart
        fig.add_trace(
            go.Bar(x=df.index, y=df["max_voltage"] - df["min_voltage"], 
                  name="Voltage Range"),
            row=2, col=2
        )
        
        fig.update_layout(height=800, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# DATA EXPORT PAGE
elif page == "📥 Data Export":
    st.markdown('<h1 class="main-header">📥 Data Export & Summary</h1>', unsafe_allow_html=True)
    
    # Summary statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔋 Cells Summary")
        if st.session_state.cells_data:
            df_cells = pd.DataFrame(st.session_state.cells_data).T
            st.dataframe(df_cells, use_container_width=True)
            
            # Export cells data
            csv_cells = df_cells.to_csv(index=True)
            st.download_button(
                label="📄 Download Cells Data (CSV)",
                data=csv_cells,
                file_name=f"battery_cells_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No cell data available")
    
    with col2:
        st.markdown("### 📋 Tasks Summary")
        if st.session_state.tasks_data:
            df_tasks = pd.DataFrame(st.session_state.tasks_data).T
            st.dataframe(df_tasks, use_container_width=True)
            
            # Export tasks data
            csv_tasks = df_tasks.to_csv(index=True)
            st.download_button(
                label="📄 Download Tasks Data (CSV)",
                data=csv_tasks,
                file_name=f"battery_tasks_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No task data available")
    
    # Combined export
    if st.session_state.cells_data or st.session_state.tasks_data:
        st.markdown("---")
        st.markdown("### 📊 Combined Export")
        
        # Create a comprehensive report
        report_data = {
            "Export_Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Total_Cells": len(st.session_state.cells_data),
            "Total_Tasks": len(st.session_state.tasks_data),
        }
        
        if st.session_state.cells_data:
            df_cells = pd.DataFrame(st.session_state.cells_data).T
            report_data.update({
                "Average_Voltage": df_cells["voltage"].mean(),
                "Average_Temperature": df_cells["temperature"].mean(),
                "LFP_Cells": sum(1 for cell in st.session_state.cells_data.values() if cell["cell_type"] == "LFP"),
                "NMC_Cells": sum(1 for cell in st.session_state.cells_data.values() if cell["cell_type"] == "NMC"),
            })
        
        # Create combined CSV
        combined_data = io.StringIO()
        combined_data.write("BATTERY CELL SIMULATION REPORT\n")
        combined_data.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        combined_data.write("=" * 50 + "\n\n")
        
        if st.session_state.cells_data:
            combined_data.write("CELLS DATA:\n")
            df_cells.to_csv(combined_data, index=True)
            combined_data.write("\n")
        
        if st.session_state.tasks_data:
            combined_data.write("TASKS DATA:\n")
            df_tasks.to_csv(combined_data, index=True)
        
        st.download_button(
            label="📦 Download Complete Report (CSV)",
            data=combined_data.getvalue(),
            file_name=f"battery_simulation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        # Display summary metrics
        st.markdown("### 📈 Summary Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Cells", len(st.session_state.cells_data))
        
        with col2:
            st.metric("Total Tasks", len(st.session_state.tasks_data))
        
        with col3:
            if st.session_state.cells_data:
                avg_voltage = pd.DataFrame(st.session_state.cells_data).T["voltage"].mean()
                st.metric("Avg Voltage", f"{avg_voltage:.2f}V")
        
        with col4:
            if st.session_state.cells_data:
                avg_temp = pd.DataFrame(st.session_state.cells_data).T["temperature"].mean()
                st.metric("Avg Temperature", f"{avg_temp:.1f}°C")

# Sidebar information
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Current Status")
st.sidebar.metric("Cells Configured", len(st.session_state.cells_data))
st.sidebar.metric("Tasks Added", len(st.session_state.tasks_data))

if st.session_state.simulation_running:
    st.sidebar.success("🟢 Simulation Running")
else:
    st.sidebar.info("🔴 Simulation Stopped")

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About")
st.sidebar.info("""
This application simulates battery cell behavior with different task types:
- **CC_CV**: Constant Current/Constant Voltage
- **IDLE**: Rest period
- **CC_CD**: Constant Current/Constant Discharge

Navigate through pages to set up cells, add tasks, monitor real-time data, and export results.
""")

# Add refresh button to sidebar for manual refresh
if st.sidebar.button("🔄 Refresh Data"):
    if st.session_state.cells_data:
        simulate_real_time_data()
    st.rerun()
