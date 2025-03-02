from crewai.tools import BaseTool
import requests
import os
import json
from pydantic import BaseModel, Field
from typing import Optional
import openai
from src.place_image import PlaceImageFetcher
from typing import Optional, Dict

class WebSearchInput(BaseModel):
    query: str = Field(description="The search query to send")

class HotelSearchInput(BaseModel):
    location: str = Field(description="The city or location to search for hotels")
    check_in: str = Field(description="Check-in date in YYYY-MM-DD format")
    check_out: str = Field(description="Check-out date in YYYY-MM-DD format")
    budget: Optional[str] = Field(None, description="Budget level (e.g., Budget, Moderate, Luxury)")
    amenities: Optional[str] = Field(None, description="Desired amenities separated by commas")

class AttractionSearchInput(BaseModel):
    location: str = Field(description="The city or location to search for attractions")
    interests: Optional[str] = Field(None, description="Specific interests or categories of attractions")

class FlightSearchInput(BaseModel):
    origin: str = Field(description="Origin city or airport code")
    destination: str = Field(description="Destination city or airport code")
    departure_date: str = Field(description="Departure date in YYYY-MM-DD format")
    return_date: Optional[str] = Field(None, description="Return date in YYYY-MM-DD format")

class WeatherForecastInput(BaseModel):
    location: str = Field(description="The city or location to get weather forecast")
    start_date: str = Field(description="Start date in YYYY-MM-DD format")
    end_date: str = Field(description="End date in YYYY-MM-DD format")

class WebSearchTool(BaseTool):
    name: str = "WebSearchTool"
    description: str = "Searches the web for up-to-date information"
    args_schema: type[BaseModel] = WebSearchInput
    
    def _run(self, query: str):
        # Using OpenAI to simulate web search results
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful web search tool. Provide accurate and up-to-date information as if you were returning search results. Include relevant facts and details."},
                {"role": "user", "content": f"Search for: {query}"}
            ]
        )
        
        return response.choices[0].message.content

class HotelSearchTool(BaseTool):
    name: str = "HotelSearchTool"
    description: str = "Searches for hotels in a specific location with given criteria"
    args_schema: type[BaseModel] = HotelSearchInput
    
    def _run(self, location: str, check_in: str, check_out: str, budget: Optional[str] = None, amenities: Optional[str] = None):
        web_search = WebSearchTool()
        query = f"Find top hotels in {location} between {check_in} and {check_out}"
        if budget:
            query += f" with a budget of {budget}"
        if amenities:
            query += f" with amenities like {amenities}"
        
        return web_search._run(query=query)

class AttractionSearchTool(BaseTool):
    name: str = "AttractionSearchTool"
    description: str = "Searches for attractions and activities in a specific location"
    args_schema: type[BaseModel] = AttractionSearchInput
    
    def _run(self, location: str, interests: Optional[str] = None):
        web_search = WebSearchTool()
        query = f"What are the top attractions in {location}"
        if interests:
            query += f" related to {interests}"
        
        return web_search._run(query=query)

class FlightSearchTool(BaseTool):
    name: str = "FlightSearchTool"
    description: str = "Searches for flights between two locations on specific dates"
    args_schema: type[BaseModel] = FlightSearchInput
    
    def _run(self, origin: str, destination: str, departure_date: str, return_date: Optional[str] = None):
        web_search = WebSearchTool()
        query = f"Find flights from {origin} to {destination} on {departure_date}"
        if return_date:
            query += f" with return on {return_date}"
        
        return web_search._run(query=query)

class WeatherForecastTool(BaseTool):
    name: str = "WeatherForecastTool"
    description: str = "Gets weather forecast for a location on specific dates"
    args_schema: type[BaseModel] = WeatherForecastInput
    
    def _run(self, location: str, start_date: str, end_date: str):
        web_search = WebSearchTool()
        query = f"What is the weather forecast for {location} from {start_date} to {end_date}"
        
        return web_search._run(query=query)

class PlaceImageSearchInput(BaseModel):
    place_name: str = Field(description="The name of the place to find an image for")
    location: Optional[str] = Field(None, description="Optional location context (e.g., 'Tokyo, Japan')")

class PlaceImageSearchTool(BaseTool):
    name: str = "PlaceImageSearchTool"
    description: str = "Searches for images of specific places or attractions"
    args_schema: type[BaseModel] = PlaceImageSearchInput
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY", os.getenv("OPENAI_API_KEY"))
        self.image_fetcher = PlaceImageFetcher(self.api_key)
    
    def _run(self, place_name: str, location: Optional[str] = None) -> str:
        image_url = self.image_fetcher.get_image_for_place(place_name, location)
        if image_url:
            return f"Image found for {place_name}: {image_url}"
        else:
            return f"No image found for {place_name}"
