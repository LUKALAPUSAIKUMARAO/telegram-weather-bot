import os
import logging
import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from config import TELEGRAM_TOKEN, OPENWEATHER_API_KEY
from utils import get_weather_by_coords, format_weather_response, set_user_city, get_user_city

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[KeyboardButton("📍 Share Location", request_location=True)]]
    reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Hi! Send a city name or share your location to get weather updates.",
        reply_markup=reply_markup
    )

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    city = " ".join(context.args) if context.args else get_user_city(user_id)
    if not city:
        await update.message.reply_text("Please provide a city or set your default using /setcity <city>")
        return

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    res = requests.get(url).json()

    if res.get("cod") != 200:
        await update.message.reply_text("City not found!")
        return

    first_name = update.effective_user.first_name or "there"
    msg = format_weather_response(res, city=city, first_name=first_name)
    await update.message.reply_text(msg, parse_mode="MarkdownV2")

async def setcity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    city = " ".join(context.args)
    if city:
        set_user_city(user_id, city)
        await update.message.reply_text(f"✅ Default city set to: {city}")
    else:
        await update.message.reply_text("Usage: /setcity <city>")

async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location
    res = get_weather_by_coords(lat=loc.latitude, lon=loc.longitude)
    if res:
        first_name = update.effective_user.first_name or "user"
        city_name = res.get("name", "your location")
        msg = format_weather_response(res, city=city_name, first_name=first_name)
        await update.message.reply_text(msg, parse_mode="Markdown")
    else:
        await update.message.reply_text("Couldn't fetch weather for this location.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("setcity", setcity))
    app.add_handler(MessageHandler(filters.LOCATION, location_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
