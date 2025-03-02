from crewai import Crew
from src.agents import create_agents
from src.tasks import create_tasks

def create_travel_crew(api_key, model, trip_details):
    # Create agents with OpenAI
    agents = create_agents(api_key=api_key, model=model)
    
    # Create tasks
    tasks = create_tasks(agents, trip_details)
    
    # Create crew
    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        verbose=True
    )
    
    return crew
