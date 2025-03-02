import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time
import openai
import base64
from PIL import Image
import requests
from io import BytesIO
from streamlit_folium import folium_static

from src.crew import create_travel_crew
from src.utils import parse_itinerary, format_date, create_interactive_map

st.cache_data.clear()

# Page configuration
st.set_page_config(
    page_title="✈️ Travel Ally",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# Function to load CSS
def load_css(css_file):
    with open(css_file, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Function to get a background image
# Replace the current background image function with this:
# Option 1: Subtle blur effect on existing image
def add_bg_from_local(image_file):
    import base64
    from pathlib import Path
    
    # Read the image file
    img_path = Path(image_file)
    with open(img_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    # Create the CSS with the encoded image
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/{"png" if img_path.suffix == ".png" else "jpeg"};base64,{encoded_string});
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
        }}
        .stApp::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(255, 255, 255, 0.7);
            z-index: -1;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

progress_placeholder = st.empty()
output_placeholder = st.empty()

def update_progress(task_description):
    progress_placeholder.text(f"In progress: {task_description}")

def update_output(partial_result):
    current_output = output_placeholder.text()
    output_placeholder.text(current_output + "\n\n" + partial_result)



# Load CSS
load_css("style.css")

# Add a subtle background image
add_bg_from_local("image.jpg")

# Initialize session state
if "itinerary" not in st.session_state:
    st.session_state.itinerary = None
if "raw_output" not in st.session_state:
    st.session_state.raw_output = None
if "progress" not in st.session_state:
    st.session_state.progress = []

# Header with logo and title
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/201/201623.png", width=80)
with col2:
    st.markdown("<h1 style='color: #333333;'>✈️ Travel Ally - powered by AI </h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #000033;'>Let our AI agents create a personalized travel plan for your next adventure!</h3>", unsafe_allow_html=True)

# Add this after your background setting function to ensure all text is visible
st.markdown("""
    <style>
    .stApp {
        color: #000033;  /* Midnight blue for general text */
    }
    .stMarkdown, .stText {
        color: #000033 !important;  /* Ensure all markdown and text elements are visible */
    }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] .stText {
        color: #FFFFFF !important;  /* Keep sidebar text white */
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .stExpander {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)


# Sidebar for inputs
with st.sidebar:
    st.header("🗺️ Trip Details")
    
    # Origin and destination
    origin = st.text_input("🏠 Origin City/Country", "San Francisco")
    destination = st.text_input("🏝️ Destination", "Kyoto")
    
    # Trip dates
    st.subheader("📅 Travel Dates")
    col1, col2 = st.columns(2)
    with col1:
        today = datetime.today()
        start_date = st.date_input("Departure", today + timedelta(days=7))
    with col2:
        end_date = st.date_input("Return", today + timedelta(days=11))
    
    # Calculate duration
    duration = (end_date - start_date).days
    st.info(f"Trip Duration: {duration} days")
    
    # Budget
    st.subheader("💰 Budget")
    budget_options = ["Budget", "Moderate", "Luxury"]
    budget = st.select_slider("Budget Level", options=budget_options, value="Moderate")
    
    # Traveler information
    st.subheader("👥 Travelers")
    travelers = st.number_input("Number of Travelers", min_value=1, max_value=10, value=2)
    
    # Interests
    st.subheader("🎯 Interests")
    interests_col1, interests_col2 = st.columns(2)
    
    interests = []
    with interests_col1:
        if st.checkbox("History & Culture"):
            interests.append("History & Culture")
        if st.checkbox("Nature & Outdoors"):
            interests.append("Nature & Outdoors")
        if st.checkbox("Food & Cuisine"):
            interests.append("Food & Cuisine")
        if st.checkbox("Art & Museums"):
            interests.append("Art & Museums")
    
    with interests_col2:
        if st.checkbox("Shopping"):
            interests.append("Shopping")
        if st.checkbox("Nightlife"):
            interests.append("Nightlife")
        if st.checkbox("Relaxation"):
            interests.append("Relaxation")
        if st.checkbox("Adventure"):
            interests.append("Adventure")
    
    # Additional preferences
    st.subheader("✨ Additional Preferences")
    additional_notes = st.text_area("Special Requests or Notes", 
                                   "I prefer to avoid crowds. I'm interested in authentic local experiences.")
    
    # OpenAI settings
    st.subheader("⚙️ API Settings")
    openai_model = st.selectbox("Select OpenAI Model", [
        "gpt-3.5-turbo",
        "gpt-4-turbo",
        "gpt-4"
    ], index=0)
    
    # API Key
    api_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    
    # Create button
    create_button = st.button("✨ Create My Itinerary", type="primary", key="create_btn")

# Main content area
if create_button:
    if not api_key:
        st.error("Please enter your OpenAI API key")
    elif not interests:
        st.error("Please select at least one interest")
    else:
        # Set API key
        os.environ["OPENAI_API_KEY"] = api_key
        openai.api_key = api_key
        
        # Prepare trip details
        trip_details = {
            "origin": origin,
            "destination": destination,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "duration": duration,
            "budget": budget,
            "travelers": travelers,
            "interests": interests,
            "additional_notes": additional_notes
        }
        
        # Create progress display with animation
        progress_container = st.empty()
        progress_bar = st.progress(0)
        
        # Create and run crew
        with st.spinner("Our AI agents are planning your perfect trip..."):
            # Clear previous progress
            st.session_state.progress = []
            
            # Simulate progress for better UX
            for i in range(101):
                # Update progress bar
                progress_bar.progress(i)
                if i == 20:
                    progress_container.info("🔍 Researching destination information...")
                elif i == 40:
                    progress_container.info("🏨 Finding the best accommodations...")
                elif i == 60:
                    progress_container.info("🗿 Discovering attractions and activities...")
                elif i == 80:
                    progress_container.info("🚗 Planning transportation options...")
                
                time.sleep(0.05)
            
            # Create crew with OpenAI
            crew = create_travel_crew(api_key, openai_model, trip_details)
            
            # Run crew
            result = crew.kickoff(inputs=trip_details)

            # Check the type of result and extract the content if necessary
            if not isinstance(result, str):
                if hasattr(result, 'raw'):
                    result = result.raw
                elif hasattr(result, 'output'):
                    result = result.output
                else:
                    result = str(result)
            
            # Store results
            st.session_state.raw_output = result
            st.session_state.itinerary = parse_itinerary(result)
            
        # Clear progress elements
        progress_container.empty()
        progress_bar.empty()
        
        st.success("🎉 Your travel itinerary is ready!")

# Display itinerary if available
# In the section where you display the itinerary
if st.session_state.itinerary:
    st.markdown(f"## Your Personalized {duration}-Day Adventure in {destination}")
    
    # Trip overview with cards
    st.markdown("### Trip at a Glance")
    
    overview_cols = st.columns(4)
    with overview_cols[0]:
        st.metric("Destination", destination)
    with overview_cols[1]:
        st.metric("Duration", f"{duration} days")
    with overview_cols[2]:
        st.metric("Budget", budget)
    with overview_cols[3]:
        st.metric("Travelers", travelers)
    
    # Interactive day-by-day itinerary
    st.markdown("### Your Day-by-Day Journey")
    
    for i, day_data in enumerate(st.session_state.itinerary):
        with st.expander(f"Day {i+1}: {day_data.get('title', 'Explore ' + destination)}"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(day_data["raw"])
            with col2:
                if day_data.get("image"):
                    st.image(day_data["image"], caption=f"Day {i+1} Highlight")
                st.markdown(f"**Weather:** {day_data.get('weather', 'Information not available')}")

    st.markdown("### Your Day-by-Day Journey")

    for i, day_data in enumerate(st.session_state.itinerary):
        with st.expander(f"Day {i+1}: {day_data.get('title', 'Explore ' + destination)}"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(day_data["raw"])
            with col2:
                if day_data.get("image"):
                    st.image(day_data["image"], caption=f"Day {i+1} Highlight")
                st.markdown(f"**Weather:** {day_data.get('weather', 'Information not available')}")

    
    # Interactive map
    st.markdown("### Your Trip Map")
    trip_map = create_interactive_map(st.session_state.itinerary)
    folium_static(trip_map)



# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; padding: 20px;">
    <p>Built with ❤️ using CrewAI and Streamlit | AI Travel Planner</p>
</div>
""", unsafe_allow_html=True)
