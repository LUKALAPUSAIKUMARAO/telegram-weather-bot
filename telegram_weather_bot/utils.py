import os
import requests
from config import OPENWEATHER_API_KEY

user_city_db = {}

def set_user_city(user_id, city):
    user_city_db[user_id] = city

def get_user_city(user_id):
    return user_city_db.get(user_id)

def get_weather_by_coords(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    res = requests.get(url).json()
    return res if res.get("cod") == 200 else None

def format_weather_response(res, city=None, first_name="User"):
    weather = res["weather"][0]
    main = res["main"]
    wind = res["wind"]
    weather_desc = weather["description"].capitalize()
    temp = main["temp"]
    humidity = main["humidity"]
    wind_speed = wind["speed"]
    feels_like = main["feels_like"]
    cloud_pct = res["clouds"]["all"]
    rain = res.get("rain", {}).get("1h", 0)
    emoji = "🌤️"

    advice = ""
    if "rain" in weather_desc.lower() or rain > 0:
        emoji = "🌧️"
        advice = "🌂 Advice: Carry an umbrella. It might rain."
    elif temp >= 35 and cloud_pct < 20:
        emoji = "☀️"
        advice = "🧢 Advice: It's very sunny. Wear a hat and stay hydrated."
    elif temp < 15:
        emoji = "🥶"
        advice = "🧥 Advice: It's cold. Wear warm clothes."
    elif humidity > 80 and temp > 30:
        emoji = "💧"
        advice = "💦 Advice: It's humid and hot. Drink water and stay indoors if possible."
    else:
        advice = "😊 Advice: Weather looks normal. Have a great day!"

    if not city:
        city = res.get("name", "your location")

    return (
        f"{emoji} *Hello {first_name}!* Here's the weather in *{city}*:\n\n"
        f"*{weather_desc}*\n"
        f"🌡️ Temperature: *{temp}°C* (Feels like *{feels_like}°C*)\n"
        f"💧 Humidity: *{humidity}%*\n"
        f"🌬️ Wind Speed: *{wind_speed} m/s*\n"
        f"☁️ Cloudiness: *{cloud_pct}%*\n\n"
        f"{advice}"
    )
   
