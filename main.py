import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from data_processor import DataProcessor

# We'll use the processed data for all visualizations instead of loading a separate dataset

def main():
    st.set_page_config(page_title="COIQ",
                       page_icon="🚀",
                       layout="wide",
                       initial_sidebar_state="collapsed")
                       
    # Password protection
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        
    if not st.session_state.authenticated:
        # Add logo in top center for login page
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("attached_assets/c-star@1500x white.png", width=150)
            
        st.markdown("<h1 style='text-align: center;'>Welcome to COIQ Dashboard</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 18px; margin-bottom: 30px;'>Please enter the password to access the dashboard</p>", unsafe_allow_html=True)
        
        # Custom CSS for the login form
        st.markdown("""
        <style>
        div[data-testid="stTextInput"] {
            max-width: 400px;
            margin: 0 auto;
        }
        div.stButton > button {
            max-width: 400px;
            margin: 0 auto;
            display: block;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Center the input in the page
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            password = st.text_input("Password", type="password", placeholder="Enter password", label_visibility="collapsed")
            login_button = st.button("Login", use_container_width=True)
            
            if password or login_button:
                if password.lower() == "bismillah":
                    st.session_state.authenticated = True
                    st.success("Authentication successful!")
                    st.rerun()
                else:
                    st.error("Incorrect password. Please try again.")
                    return
                    
        return  # Stop execution until authenticated
        
    # Continue with the main app only if authenticated

    # Custom CSS for styling
    st.markdown("""
        <style>
        .logo-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 999;
        }
        .logo-image {
            width: 60px;
            height: auto;
        }
        .main-header {
            margin-bottom: 2rem;
            padding-top: 1rem;
        }
        .section-container {
            padding: 1.5rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

    # Add logo in top right corner
    # st.markdown("""
    #     <div class="logo-container">
    #         <img src="attached_assets/c-star@1500x%20white.png" class="logo-image">
    #     </div>
    # """, unsafe_allow_html=True)

    # Simple header with just COIQ
    st.markdown("<h1 class='main-header' style='text-align: center;'>C O I Q</h1>", unsafe_allow_html=True)
    st.markdown('###')

    # Define color scheme for rocket types
    color_scheme = {
        'W': '#8db3da',  # Soft blue
        'X': '#f4b183',  # Soft orange
        'Y': '#a8d5a7',  # Soft green
        'Z': '#f8a0a0'   # Soft red
    }

    # Simple header with minimal instructions
    st.markdown("### Please upload your data file below to begin analysis")
    
    # Create three columns for the top section
    upload_col, process_col, stats_col = st.columns([1, 1, 1])

    # File Upload Section (Left)
    with upload_col:
        st.subheader("📤 Upload Data")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv", 
                                        help="File should have columns: Name, Country, Gender, Region, Sector, 'MVP?', '<2 years?', Stage, 'Fund level', 'Have Traction?', Type, and 'rocket_type' (or 'Final Label')")
        
        # Provide information about the expected file format
        st.caption("Your file should contain columns for: Name, Country, Gender, Region, Sector, etc.")

    # Stats Summary Section (Right)
    with stats_col:
        st.subheader("📊 Key Stats")
        if 'processed_data' in st.session_state:
            df = st.session_state.processed_data
            st.metric("Total Startups", len(df))
            if 'Final Label' in df.columns:
                rocket_counts = df['Final Label'].value_counts().reindex(['W', 'X', 'Y', 'Z']).fillna(0).astype(int)

                # Display rocket types in pairs
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Type W", f"{rocket_counts['W']}")
                with col2:
                    st.metric("Type X", f"{rocket_counts['X']}")

                col3, col4 = st.columns(2)
                with col3:
                    st.metric("Type Y", f"{rocket_counts['Y']}")
                with col4:
                    st.metric("Type Z", f"{rocket_counts.get('Z', 0)}")
        else:
            st.info("Upload and process data to view statistics")

    # Process Button (Center)
    with process_col:
        st.subheader("🚀 Process Data")
        if uploaded_file is not None:
            if st.button("Process Uploaded File", use_container_width=True):
                with st.spinner("🔄 Processing your data..."):
                    # Load and process the uploaded data
                    try:
                        df = pd.read_csv(uploaded_file)
                        processed_df, stats = DataProcessor.process_csv(df)

                        # Store in session state
                        st.session_state.processed_data = processed_df
                        st.session_state.stats = stats
                        st.success("✅ Your data has been processed successfully!")
                    except Exception as e:
                        st.error(f"Error processing the file: {e}")
                        st.warning("Please make sure your file has the required format.")
        else:
            # No initial data loading - wait for user upload
            if 'processed_data' not in st.session_state:
                # Show guidance message
                st.info("Please upload a CSV file to begin analysis")

    # Visualization Section
    if 'processed_data' in st.session_state:
        st.markdown("<div class='section-container'>", unsafe_allow_html=True)
        st.subheader("📈 Rocket Type Distribution")
        viz_col1, viz_col2 = st.columns([2, 1])

        with viz_col1:
            if 'Final Label' in st.session_state.processed_data.columns:
                # Create bar chart with consistent colors
                df_counts = st.session_state.processed_data['Final Label'].value_counts().reset_index()
                df_counts.columns = ['Rocket Type', 'Count']

                fig = px.bar(df_counts,
                              x='Rocket Type',
                              y='Count',
                              title="Overall Rocket Type Distribution",
                              color='Rocket Type',
                              color_discrete_map=color_scheme)
                st.plotly_chart(fig, use_container_width=True)

        with viz_col2:
            if 'Final Label' in st.session_state.processed_data.columns:
                # Create pie chart with the same color scheme
                fig = px.pie(
                    values=st.session_state.processed_data['Final Label'].value_counts(),
                    names=st.session_state.processed_data['Final Label'].value_counts().index,
                    title="Rocket Type Breakdown",
                    color=st.session_state.processed_data['Final Label'].value_counts().index,
                    color_discrete_map=color_scheme)
                st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Global Map Visualization - Show this first
        st.subheader("🌍 Global Distribution")
        df = st.session_state.processed_data
        
        # Count startups per location
        location_counts = df.groupby(['latitude', 'longitude']).size().reset_index(name='count')

        fig = px.scatter_mapbox(
            location_counts,
            lat='latitude',
            lon='longitude',
            size='count',
            color_discrete_sequence=['red'],
            size_max=40,
            zoom=1.5,
            title="Startup Distribution"
        )
        
        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox=dict(
                center=dict(lat=20, lon=0),
                zoom=1.5
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # Country Distribution (Stacked Bar Chart) - Collapsed under the map
        st.subheader("📊 Country Analysis")
        with st.expander("View Country Distribution Chart & Table", expanded=False):
            # Create a pivot table for country and rocket type
            country_counts = df.groupby(['Country', 'Final Label']).size().reset_index(name='Count')
            
            # Sort countries by total count to show most frequent first
            country_totals = country_counts.groupby('Country')['Count'].sum().sort_values(ascending=False)
            top_countries = country_totals.head(15).index.tolist()
            
            # Filter for top countries only to keep chart readable
            filtered_counts = country_counts[country_counts['Country'].isin(top_countries)]
            
            # Create stacked bar chart
            fig = px.bar(
                filtered_counts,
                x='Country',
                y='Count',
                color='Final Label',
                title="Rocket Type Distribution by Country (Top 15)",
                color_discrete_map=color_scheme,
                category_orders={"Country": top_countries}
            )
            
            fig.update_layout(
                xaxis_title="Country",
                yaxis_title="Number of Startups",
                legend_title="Rocket Type"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Country Distribution Table
            st.subheader("📋 Frequency Table of Rockets by Country")
            
            # Create the frequency table
            pivot_table = df.pivot_table(
                index='Country', 
                columns='Final Label', 
                aggfunc='size', 
                fill_value=0
            ).reset_index()
            
            # Add total column
            if 'W' in pivot_table.columns:
                pivot_table['Total'] = pivot_table['W']
                if 'X' in pivot_table.columns:
                    pivot_table['Total'] += pivot_table['X']
                if 'Y' in pivot_table.columns:
                    pivot_table['Total'] += pivot_table['Y']
                if 'Z' in pivot_table.columns:
                    pivot_table['Total'] += pivot_table['Z']
            
            # Sort by total
            pivot_table = pivot_table.sort_values('Total', ascending=False)
            
            # Display the table
            st.dataframe(pivot_table, use_container_width=True)

        # Labeled Dataset View (Bottom)
        st.subheader("🔍 Detailed Results")
        with st.expander("View Processed Dataset", expanded=False):
            st.dataframe(st.session_state.processed_data,
                          use_container_width=True)

            # Download button for processed data
            csv = st.session_state.processed_data.to_csv(index=False)
            st.download_button(label="📥 Download Processed CSV",
                                data=csv,
                                file_name="processed_startups.csv",
                                mime="text/csv",
                                use_container_width=True)
                                
        # Additional Visualizations section
        st.subheader("📊 Additional Insights")
        with st.expander("View Additional Visualizations", expanded=False):
            # Use the same processed data
            df = st.session_state.processed_data
            
            # Overall statistics
            st.subheader("Overall Statistics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Organizations", len(df))
            with col2:
                st.metric("Countries", df['Country'].nunique())
            with col3:
                st.metric("Sectors", df['Sector'].nunique() if 'Sector' in df.columns else "N/A")
            with col4:
                st.metric("MVPs", len(df[df['MVP?'] == 'Yes']) if 'MVP?' in df.columns else "N/A")
            
            # If the data has the necessary columns, show the additional visualizations
            if 'Sector' in df.columns:
                # Sector distribution
                st.subheader("Sector Analysis")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Sector distribution
                    fig_sector = px.bar(
                        df['Sector'].value_counts().head(10),
                        title="Top 10 Sectors"
                    )
                    st.plotly_chart(fig_sector, use_container_width=True)
                
                with col2:
                    # Rocket Type distribution by Sector
                    if 'Final Label' in df.columns:
                        # Get top sectors
                        top_sectors = df['Sector'].value_counts().head(5).index.tolist()
                        # Filter for top sectors
                        sector_data = df[df['Sector'].isin(top_sectors)]
                        # Create grouped bar chart
                        fig_sector_rocket = px.histogram(
                            sector_data,
                            x='Sector', 
                            color='Final Label',
                            color_discrete_map=color_scheme,
                            title="Rocket Type Distribution by Top Sectors"
                        )
                        st.plotly_chart(fig_sector_rocket, use_container_width=True)
            
            # Funding and Gender Analysis
            if any(col in df.columns for col in ['Fund level', 'Gender']):
                st.subheader("Funding & Gender Analysis")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Funding distribution
                    if 'Fund level' in df.columns:
                        fig_funding = px.pie(
                            df,
                            names='Fund level',
                            title="Distribution of Funding Levels"
                        )
                        st.plotly_chart(fig_funding, use_container_width=True)
                    else:
                        st.info("Funding level data not available")
                
                with col2:
                    # Gender distribution
                    if 'Gender' in df.columns:
                        fig_gender = px.pie(
                            df,
                            names='Gender',
                            title="Gender Distribution"
                        )
                        st.plotly_chart(fig_gender, use_container_width=True)
                    else:
                        st.info("Gender data not available")
                
            # Rocket Type by Region if available
            if 'Region' in df.columns and 'Final Label' in df.columns:
                st.subheader("Regional Analysis")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Rocket Type Distribution by Region
                    fig_region = px.bar(
                        df.groupby(['Region', 'Final Label']).size().reset_index(name='count'),
                        x='Region',
                        y='count',
                        color='Final Label',
                        color_discrete_map=color_scheme,
                        title="Rocket Type Distribution by Region"
                    )
                    st.plotly_chart(fig_region, use_container_width=True)
                
                with col2:
                    # Rocket Type and Sector Distribution by Region
                    if 'Sector' in df.columns:
                        # Get top sectors to keep visualization readable
                        top_sectors = df['Sector'].value_counts().head(5).index.tolist()
                        # Filter data for top sectors
                        filtered_df = df[df['Sector'].isin(top_sectors)]
                        
                        fig_sector_region = px.bar(
                            filtered_df.groupby(['Region', 'Sector']).size().reset_index(name='count'),
                            x='Region',
                            y='count',
                            color='Sector',
                            title="Top Sectors Distribution by Region"
                        )
                        st.plotly_chart(fig_sector_region, use_container_width=True)
                
                # New visualization: Sector distribution by Rocket Type
                if 'Sector' in df.columns:
                    st.subheader("Sector & Rocket Type Analysis")
                    
                    # Get top sectors
                    top_sectors = df['Sector'].value_counts().head(10).index.tolist()
                    # Filter data for top sectors
                    filtered_df = df[df['Sector'].isin(top_sectors)]
                    
                    # Create grouped bar chart with Sectors on x-axis, counts as y-axis, and rocket types as colors
                    fig_sector_rocket = px.bar(
                        filtered_df.groupby(['Sector', 'Final Label']).size().reset_index(name='count'),
                        x='Sector',
                        y='count',
                        color='Final Label',
                        color_discrete_map=color_scheme,
                        title="Rocket Type Distribution by Sector",
                        labels={'count': 'Number of Startups', 'Sector': 'Sector', 'Final Label': 'Rocket Type'},
                        category_orders={"Sector": top_sectors}
                    )
                    
                    # Improve layout
                    fig_sector_rocket.update_layout(
                        legend_title="Rocket Type",
                        xaxis_tickangle=-45,  # Angle the x-axis labels for better readability
                        height=500
                    )
                    
                    st.plotly_chart(fig_sector_rocket, use_container_width=True)
                    
                    # Add a second visualization showing sectors by region and rocket type
                    st.subheader("Sector Analysis by Region")
                    
                    # Create a faceted chart with sectors on x-axis, grouped by region
                    regions = df['Region'].unique()
                    for region in regions:
                        region_df = filtered_df[filtered_df['Region'] == region]
                        
                        if len(region_df) > 0:
                            fig_region = px.bar(
                                region_df.groupby(['Sector', 'Final Label']).size().reset_index(name='count'),
                                x='Sector',
                                y='count',
                                color='Final Label',
                                color_discrete_map=color_scheme,
                                title=f"Rocket Type Distribution in {region}",
                                labels={'count': 'Number of Startups', 'Sector': 'Sector'},
                                category_orders={"Sector": top_sectors}
                            )
                            
                            fig_region.update_layout(
                                legend_title="Rocket Type",
                                xaxis_tickangle=-45,
                                height=400
                            )
                            
                            st.plotly_chart(fig_region, use_container_width=True)

    else:
        # Show placeholder when no file is uploaded
        st.info("👆 Please upload a CSV file to begin")

if __name__ == "__main__":
    main()
