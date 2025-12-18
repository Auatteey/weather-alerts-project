import azure.functions as func
import json
import os
import requests

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        city = req.params.get("city")

        if not city:
            return func.HttpResponse(
                "Missing 'city' parameter",
                status_code=400
            )

        # OpenWeather API Key from Azure settings
        API_KEY = os.getenv("OPENWEATHER_KEY")
        if not API_KEY:
            return func.HttpResponse(
                "API key not configured",
                status_code=500
            )

        # Call OpenWeather API
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)

        if response.status_code != 200:
            return func.HttpResponse(
                f"City '{city}' not found",
                status_code=404
            )

        data = response.json()

        # Format useful weather data
        formatted = {
            "city": data.get("name"),
            "temp": data["main"].get("temp"),
            "humidity": data["main"].get("humidity"),
            "wind_speed": data["wind"].get("speed"),
            "condition": data["weather"][0].get("description"),
            "visibility": data.get("visibility", "N/A")
        }

        return func.HttpResponse(
            json.dumps(formatted),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            f"Server error: {str(e)}",
            status_code=500
        )
