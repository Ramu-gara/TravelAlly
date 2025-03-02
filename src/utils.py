import re
from datetime import datetime
import folium
from streamlit_folium import folium_static

def parse_itinerary(raw_itinerary):
    """Parse the raw itinerary text into structured data"""
    # Check if raw_itinerary is a string, if not, try to extract the content
    if not isinstance(raw_itinerary, str):
        if hasattr(raw_itinerary, 'raw'):
            raw_itinerary = raw_itinerary.raw
        elif hasattr(raw_itinerary, 'output'):
            raw_itinerary = raw_itinerary.output
        else:
            raw_itinerary = str(raw_itinerary)
    
    # Continue with the existing parsing logic
    days = re.split(r'Day \d+:', raw_itinerary)
    days = [day.strip() for day in days if day.strip()]
    
    structured_itinerary = []
    day_count = 1
    
    for day in days:
        # Extract activities, meals, etc.
        activities = re.findall(r'- (.*?)(?=\n-|\n\n|$)', day)
        
        structured_itinerary.append({
            "day": day_count,
            "activities": activities,
            "raw": day
        })
        day_count += 1
    
    return structured_itinerary


def format_date(date_str):
    """Format date string to a standard format"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%B %d, %Y")

def create_interactive_map(itinerary):
    m = folium.Map(location=[0, 0], zoom_start=2)
    
    for day in itinerary:
        for activity in day.get('activities', []):
            if 'location' in activity and 'coordinates' in activity['location']:
                folium.Marker(
                    activity['location']['coordinates'],
                    popup=activity['name'],
                    tooltip=activity['name']
                ).add_to(m)
    
    return m
