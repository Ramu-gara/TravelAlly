import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

class WeatherInput(BaseModel):
    location: str = Field(description="The city or location to get weather for")
    date: str = Field(description="The date to get weather for (YYYY-MM-DD)")

class WeatherTool(BaseTool):
    name: str = "WeatherTool"
    description: str = "Gets weather forecast for a specific location and date"
    args_schema: type[BaseModel] = WeatherInput

    def _run(self, location: str, date: str):
        api_key = "0ece4f0f2d9c4112b1670813250203"
        
        # Ensure the date is not in the past
        input_date = datetime.strptime(date, "%Y-%m-%d")
        if input_date < datetime.now():
            date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&dt={date}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            data = response.json()
            forecast = data['forecast']['forecastday'][0]['day']
            return f"Weather in {location} on {date}: {forecast['condition']['text']}, High: {forecast['maxtemp_c']}°C, Low: {forecast['mintemp_c']}°C"
        except requests.exceptions.RequestException as e:
            return f"Error fetching weather data: {str(e)}"
        except (KeyError, IndexError) as e:
            return f"Error processing weather data: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
