import datetime
import logging
import os
import json
import requests
import azure.functions as func
from azure.storage.blob import BlobServiceClient


# ---------------------------------------------------------
#  MAILERSEND : envoi d'e-mail via API REST
# ---------------------------------------------------------
def send_email(subject, message):
    api_key = os.getenv("MAILERSEND_API_KEY")
    sender = os.getenv("ALERT_EMAIL_FROM")
    recipient = os.getenv("ALERT_EMAIL")

    if not api_key:
        logging.error("❌ MAILERSEND_API_KEY is missing!")
        return

    url = "https://api.mailersend.com/v1/email"
    payload = {
        "from": {"email": sender},
        "to": [{"email": recipient}],
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
#  Weather Alert Logic
# ---------------------------------------------------------
def check_weather_alerts(city, weather):
    """Return an alert message if dangerous weather is detected."""

    temp = weather["main"]["temp"]
    wind = weather["wind"]["speed"]
    visibility = weather.get("visibility", 10000)
    condition = weather["weather"][0]["description"]

    alerts = []

# 🧪 TEST FORCÉ : déclenche toujours une alerte
  #  alerts.append(f" TEST ALERT for {city} – system working")
  #  return "\n".join(alerts)

    if temp < 3:
        alerts.append(f"❄️ Very cold temperature in {city}: {temp}°C")
    if wind > 15:
        alerts.append(f"🌬️ Strong wind in {city}: {wind} m/s")
    if visibility < 500:
        alerts.append(f"🌫️ Low visibility in {city}: {visibility} m")
    if "storm" in condition or "thunder" in condition:
        alerts.append(f"⛈️ Storm conditions detected in {city}: {condition}")

    

    if alerts:
        return "\n".join(alerts)
    return None


# ---------------------------------------------------------
#  Azure Function : checkAlerts (timer)
# ---------------------------------------------------------
def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    logging.info(f"⏰ checkAlerts triggered at {utc_timestamp}")

    # ---------------------------------------------------------
    # Load cities from Azure Blob Storage
    # ---------------------------------------------------------
    try:
        storage_conn = os.getenv("AzureWebJobsStorage")
        blob_service = BlobServiceClient.from_connection_string(storage_conn)
        container = blob_service.get_container_client("data")
        blob = container.get_blob_client("cities.json")

        data = blob.download_blob().readall()
        cities_data = json.loads(data)
        cities = cities_data.get("cities", [])

        logging.info(f"📌 Loaded {len(cities)} cities")

    except Exception as e:
        logging.error(f"❌ Error loading cities.json: {e}")
        return

    # ---------------------------------------------------------
    # Check alerts for each city
    # ---------------------------------------------------------
    api_key = os.getenv("OPENWEATHER_KEY")

    for city in cities:
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"
            response = requests.get(url)

            if response.status_code != 200:
                logging.error(f"❌ Failed to fetch weather for {city}: {response.text}")
                continue

            weather = response.json()
            alert_message = check_weather_alerts(city, weather)

            if alert_message:
                logging.info(f"⚠️ Alert triggered for {city}: {alert_message}")
                send_email(f"Weather Alert for {city}", alert_message)
            else:
                logging.info(f"✔ No alerts for {city}")

        except Exception as e:
            logging.error(f"❌ Error processing {city}: {e}")

    # ---------------------------------------------------------
    # Finished
    # ---------------------------------------------------------
    logging.info("✔ checkAlerts completed.")
