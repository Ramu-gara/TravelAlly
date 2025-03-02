from crewai import Agent
from src.tools import HotelSearchTool, AttractionSearchTool, FlightSearchTool, WeatherForecastTool
from crewai import LLM
from src.tools import PlaceImageSearchTool
from src.weather_tool import WeatherTool


def create_agents(api_key, model="gpt-4"):
    # Create LLM
    llm = LLM(api_key=api_key, model=model, temperature=0.7, max_tokens=1000)
    
    # Travel Planner - Oversees the entire planning process
    travel_planner = Agent(
        role="Travel Planning Coordinator",
        goal="Create a comprehensive travel plan based on the traveler's preferences",
        backstory="You are an experienced travel coordinator who has planned thousands of successful trips worldwide. You understand how to balance activities, rest, and exploration.",
        verbose=True,
        allow_delegation=True,
        tools=[],
        llm=llm
    )
    
    # Accommodation Specialist
    accommodation_specialist = Agent(
        role="Accommodation Specialist",
        goal="Find the best accommodation options that match the traveler's preferences and budget",
        backstory="You are an expert in finding the perfect places to stay. You consider location, amenities, reviews, and value for money to make recommendations.",
        verbose=True,
        tools=[HotelSearchTool()],
        llm=llm
    )
    
    # Attractions Researcher
    attractions_researcher = Agent(
        role="Attractions and Activities Specialist",
        goal="Discover and recommend the best attractions and activities, providing detailed descriptions, practical information, and personalized suggestions based on traveler preferences.",
        backstory="You are a world-renowned travel expert with encyclopedic knowledge of global attractions. You excel at creating personalized, detailed itineraries that perfectly match travelers' interests.",
        verbose=True,
        tools=[AttractionSearchTool()],
        llm=llm
    )

    
    # Transportation Expert
    transportation_expert = Agent(
        role="Transportation Logistics Expert",
        goal="Plan efficient transportation between locations and activities",
        backstory="You are a logistics wizard who knows how to optimize travel routes, find the best transportation options, and ensure smooth transitions between destinations.",
        verbose=True,
        tools=[FlightSearchTool()],
        llm=llm
    )
    
    # Local Culture Expert
    local_culture_expert = Agent(
        role="Local Culture and Customs Expert",
        goal="Provide insights on local culture, customs, and recommendations for an authentic experience",
        backstory="You have deep knowledge of cultures worldwide and can provide valuable insights on local customs, etiquette, and authentic experiences.",
        verbose=True,
        tools=[WeatherTool()],
        llm=llm
    )

    weather_expert = Agent(
        role="Weather Expert",
        goal="Provide accurate weather information for the trip dates",
        backstory="You are a meteorologist with years of experience in predicting weather patterns worldwide.",
        verbose=True,
        tools=[WeatherTool()],
        llm=llm
    )

    recommendation_expert = Agent(
        role="Travel Recommendation Specialist",
        goal="Provide tailored recommendations based on weather and traveler preferences",
        backstory="You are an expert at optimizing travel experiences, considering factors like weather, interests, and local events.",
        verbose=True,
        tools=[WeatherTool(), AttractionSearchTool()],
        llm=llm
    )

    return {
        "travel_planner": travel_planner,
        "accommodation_specialist": accommodation_specialist,
        "attractions_researcher": attractions_researcher,
        "transportation_expert": transportation_expert,
        "local_culture_expert": local_culture_expert,
        "weather_expert": weather_expert,
        "recommendation_expert":recommendation_expert
    }
