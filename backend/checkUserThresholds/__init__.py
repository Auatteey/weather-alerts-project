import datetime
import logging
import os
import json
import requests
import azure.functions as func
from azure.storage.blob import BlobServiceClient


# ---------------------------------------------------------
#  MAILERSEND
# ---------------------------------------------------------
def send_email(to_email, subject, message):
    api_key = os.getenv("MAILERSEND_API_KEY")
    sender = os.getenv("ALERT_EMAIL_FROM")

    if not api_key or not sender:
        logging.error("❌ MailerSend configuration missing")
        return

    url = "https://api.mailersend.com/v1/email"
    payload = {
        "from": {"email": sender},
        "to": [{"email": to_email}],
        "subject": subject,
        "text": message
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    logging.info(f"[MAILERSEND] {response.status_code} {response.text}")


# ---------------------------------------------------------
#  Azure Function : Timer Trigger
# ---------------------------------------------------------
def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    logging.info(f"⏰ checkUserThresholds triggered at {utc_timestamp}")

    # Load subscriptions
    try:
        storage_conn = os.getenv("AzureWebJobsStorage")
        blob_service = BlobServiceClient.from_connection_string(storage_conn)
        container = blob_service.get_container_client("data")
        blob = container.get_blob_client("subscriptions.json")

        blob_data = blob.download_blob().readall()
        subscriptions_data = json.loads(blob_data)
        subscriptions = subscriptions_data.get("subscriptions", [])

        logging.info(f"📌 Loaded {len(subscriptions)} subscriptions")

    except Exception as e:
        logging.error(f"❌ Error loading subscriptions.json: {e}")
        return

    # OpenWeather API
    api_key = os.getenv("OPENWEATHER_KEY")
    if not api_key:
        logging.error("❌ OPENWEATHER_KEY missing")
        return

    # Check thresholds
    for sub in subscriptions:
        try:
            email = sub["email"]
            city = sub["city"]
            try:
                threshold = float(sub["threshold"])
            except ValueError:
                logging.error(f"❌ Invalid threshold for {city}: {sub['threshold']}")
                continue

            weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"
            response = requests.get(weather_url)

            if response.status_code != 200:
                logging.error(f"❌ Failed to fetch weather for {city}")
                continue

            weather = response.json()
            current_temp = weather["main"]["temp"]

            logging.info(f"🌡 {city} | Current: {current_temp}°C | Threshold: {threshold}°C")

            if current_temp >= threshold:
                message = (
                    f"🔥 Temperature alert for {city}\n\n"
                    f"Current temperature: {current_temp}°C\n"
                    f"Your threshold: {threshold}°C\n"
                    f"Condition: {weather['weather'][0]['description']}"
                )
                send_email(email, f"Temperature Alert – {city}", message)

        except Exception as e:
            logging.error(f"❌ Error processing subscription {sub}: {e}")

    logging.info("✔ checkUserThresholds completed.")
