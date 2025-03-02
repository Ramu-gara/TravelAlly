import requests
import os
from typing import Optional

class PlaceImageFetcher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place"
    
    def search_place(self, place_name: str, location: Optional[str] = None) -> Optional[str]:
        """Search for a place and return its place_id"""
        search_url = f"{self.base_url}/findplacefromtext/json"
        params = {
            "input": place_name,
            "inputtype": "textquery",
            "fields": "place_id,photos",
            "key": self.api_key
        }
        
        if location:
            params["locationbias"] = f"point:{location}"
            
        response = requests.get(search_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "OK" and data.get("candidates"):
                return data["candidates"][0].get("place_id")
        return None
    
    def get_place_photos(self, place_id: str, max_results: int = 1) -> list:
        """Get photos for a place using its place_id"""
        details_url = f"{self.base_url}/details/json"
        params = {
            "place_id": place_id,
            "fields": "photos",
            "key": self.api_key
        }
        
        response = requests.get(details_url, params=params)
        photo_urls = []
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "OK" and data.get("result", {}).get("photos"):
                photos = data["result"]["photos"][:max_results]
                for photo in photos:
                    if photo.get("photo_reference"):
                        photo_url = self.get_photo_url(photo["photo_reference"])
                        photo_urls.append(photo_url)
        
        return photo_urls
    
    def get_photo_url(self, photo_reference: str, max_width: int = 800) -> str:
        """Generate a URL for a place photo"""
        return f"{self.base_url}/photo?maxwidth={max_width}&photoreference={photo_reference}&key={self.api_key}"
    
    def get_image_for_place(self, place_name: str, location: Optional[str] = None) -> Optional[str]:
        """Get an image URL for a place by name"""
        place_id = self.search_place(place_name, location)
        if place_id:
            photo_urls = self.get_place_photos(place_id)
            if photo_urls:
                return photo_urls[0]
        return None
