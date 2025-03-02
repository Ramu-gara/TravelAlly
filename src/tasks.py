from crewai import Task

def create_tasks(agents, trip_details):
    # Initial research task
    destination_research = Task(
        description=f"Research {trip_details['destination']} as a travel destination. Consider the best time to visit, general costs, safety, and major highlights.",
        expected_output="A comprehensive overview of the destination including seasonal considerations, general cost expectations, safety information, and major highlights.",
        agent=agents["local_culture_expert"]
    )
    
    # Accommodation planning
    accommodation_planning = Task(
        description=f"Find the best accommodation options in {trip_details['destination']} for a {trip_details['duration']} day trip with a budget of {trip_details['budget']}. Consider location, amenities, and reviews.",
        expected_output="A list of 3-5 recommended accommodations with details on location, price, amenities, and why they're recommended.",
        agent=agents["accommodation_specialist"],
        context=[destination_research]
    )

    
    # Transportation planning
    transportation_planning = Task(
        description=f"Plan transportation from {trip_details['origin']} to {trip_details['destination']} and local transportation during the {trip_details['duration']}-day stay.",
        expected_output="Transportation recommendations including flights/trains/etc. to the destination, and options for getting around locally (public transport, car rental, etc.).",
        agent=agents["transportation_expert"],
        context=[destination_research]
    )
    
    # Local tips and recommendations
    local_recommendations = Task(
        description=f"Provide insider tips for visiting {trip_details['destination']}. Include information on local customs, etiquette, food recommendations, and off-the-beaten-path experiences.",
        expected_output="A guide to local customs, recommended local dishes to try, phrases to know, and unique experiences that tourists might miss.",
        agent=agents["local_culture_expert"],
        context=[destination_research]
    )
    
    weather_forecast = Task(
        description=f"Get weather forecasts for {trip_details['destination']} for each day of the {trip_details['duration']}-day trip, starting from {trip_details['start_date']}. Use the WeatherTool for each day, incrementing the date.",
        expected_output="Daily weather forecasts for the entire trip duration.",
        agent=agents["weather_expert"]
    )

    # Attractions and activities planning
    attractions_planning = Task(
        description=f"""Plan a detailed itinerary for a {trip_details['duration']}-day trip to {trip_details['destination']} based on the interests: {', '.join(trip_details['interests'])}. For each day:
        1. Suggest 3-4 activities or attractions
        2. Provide a brief description (20-30 words) for each activity
        3. Estimate time needed and cost for each activity
        4. Recommend local restaurants or cafes for meals
        5. Include practical tips (e.g., best time to visit, what to wear)
        6. Suggest a photo opportunity or Instagram-worthy spot
        7. Include at least one off-the-beaten-path or unique local experience
        Ensure a balance of activities and rest time, and consider the traveler's budget of {trip_details['budget']}.
        """,
        expected_output="A comprehensive day-by-day itinerary with detailed descriptions, timings, costs, and insider tips for each recommended attraction and activity.",
        agent=agents["attractions_researcher"],
        context=[destination_research, weather_forecast]
    )

    weather_based_recommendations = Task(
        description=f"Based on the weather forecasts and traveler interests, provide daily recommendations for activities, clothing, and any necessary precautions or changes to the itinerary.",
        expected_output="Daily recommendations considering weather conditions and traveler preferences.",
        agent=agents["recommendation_expert"],
        context=[weather_forecast, attractions_planning]
    )

    # Final itinerary compilation
    final_itinerary = Task(
        description="""Create a comprehensive day-by-day travel itinerary combining all the research and recommendations. For each day, include:
        1. Detailed schedule with timings
        2. Specific activities and attractions with brief descriptions
        3. Estimated costs for each activity and cumulative daily cost
        4. Weather forecast and appropriate clothing recommendations
        5. Transportation details between locations
        6. Recommended restaurants or cafes for meals
        7. Any special local events or seasonal considerations
        Ensure the itinerary reflects the traveler's interests and budget constraints.""",
        expected_output="A highly detailed day-by-day itinerary including all aspects mentioned, with at least 300 words of description per day.",
        agent=agents["travel_planner"],
        context=[destination_research, accommodation_planning, attractions_planning, transportation_planning, local_recommendations, weather_forecast, weather_based_recommendations]
    )


    return [
        destination_research,
        weather_forecast,
        accommodation_planning,
        attractions_planning,
        transportation_planning,
        local_recommendations,
        weather_based_recommendations,
        final_itinerary
    ]
