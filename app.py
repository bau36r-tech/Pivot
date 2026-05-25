import streamlit as st
import pandas as pd
import plotly.express as px

# Web page appearance configuration
st.set_page_config(
    page_title="Web Pivot & Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-title { font-size:32px; font-weight:bold; color: #1E3A8A; margin-bottom: 5px; }
    .sub-title { font-size:16px; color: #4B5563; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">📊 Web-Based Pivot Table & Dashboard Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Upload your Excel or CSV file to dynamically analyze data and create instant web charts.</div>', unsafe_allow_html=True)

# File Uploader component on the web interface
uploaded_file = st.file_uploader("Drag and drop or click to upload your data file (.csv or .xlsx)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # Load the uploaded file dynamically
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"🎯 Successfully loaded: {uploaded_file.name}")
        
        # Expandable Raw Data View
        with st.expander("👀 View Raw Uploaded Data"):
            st.dataframe(df.head(20), use_container_width=True)
            
        # Sidebar Controls for Pivot Configurations
        st.sidebar.header("🛠️ Pivot Table Configurations")
        all_columns = df.columns.tolist()
        
        rows = st.sidebar.multiselect("Select Rows (Index Groups)", options=all_columns)
        cols = st.sidebar.multiselect("Select Columns (Optional)", options=all_columns)
        values = st.sidebar.selectbox("Select Numeric Value (Metrics)", options=all_columns)
        agg_func = st.sidebar.selectbox("Select Aggregation", options=["sum", "mean", "count", "max", "min"], index=0)
        
        # Generate Pivot Table if minimum criteria met
        if rows and values:
            pivot_table = pd.pivot_table(
                df, 
                values=values, 
                index=rows, 
                columns=cols if cols else None, 
                aggfunc=agg_func
            )
            
            # Flatten multi-level columns if columns are selected
            if isinstance(pivot_table.columns, pd.MultiIndex):
                pivot_table.columns = ['_'.join(str(s) for s in col if s).strip() for col in pivot_table.columns.values]
            
            pivot_df = pivot_table.reset_index()
            
            # Displaying the generated Pivot Table
            st.subheader("🎯 Generated Pivot Table Summary")
            st.dataframe(pivot_df, use_container_width=True)
            
            # Web Download Feature
            csv_pivot = pivot_df.to_csv(index=False).encode('utf-8')
            st.sidebar.download_button(
                label="📥 Download Summary as CSV",
                data=csv_pivot,
                file_name="web_pivot_summary.csv",
                mime="text/csv"
            )
            
            # Dynamic Chart Generation Section
            st.markdown("---")
            st.subheader("📈 Interactive Web Visualizations")
            
            layout_col1, layout_col2 = st.columns(2)
            with layout_col1:
                chart_type = st.selectbox("Choose Visual Chart Type", ["Bar Chart", "Line Chart", "Area Chart"])
            with layout_col2:
                x_axis = st.selectbox("Select X-Axis Data", options=rows)
                
            available_y = [c for c in pivot_df.columns if c != x_axis]
            y_axis = st.multiselect("Select Y-Axis Metrics", options=available_y, default=available_y[:1])
            
            if y_axis:
                if chart_type == "Bar Chart":
                    fig = px.bar(pivot_df, x=x_axis, y=y_axis, barmode="group", template="plotly_white")
                elif chart_type == "Line Chart":
                    fig = px.line(pivot_df, x=x_axis, y=y_axis, markers=True, template="plotly_white")
                elif chart_type == "Area Chart":
                    fig = px.area(pivot_df, x=x_axis, y=y_axis, template="plotly_white")
                    
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("💡 Please select at least one Y-Axis checkmark metric to view the graph.")
        else:
            st.info("💡 Side menu থেকে কমপক্ষে একটি Row এবং একটি Value সিলেক্ট করলেই আপনার ওয়েব পিভট টেবিল তৈরি হয়ে যাবে।")
            
    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("👋 Web App-টি ব্যবহারের জন্য আপনার এক্সেল বা সিএসভি ফাইলটি ওপরে ড্রপ করুন।")
