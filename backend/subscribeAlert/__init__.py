import azure.functions as func
import json
import os
import requests
from azure.storage.blob import BlobServiceClient
import logging

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
#  HTTP Trigger: subscribeAlert
# ---------------------------------------------------------
def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # ----------------------------
        # Read parameters
        # ----------------------------
        email = req.params.get("email")
        city = req.params.get("city")
        threshold = req.params.get("threshold")

        if not email or not city or not threshold:
            return func.HttpResponse("Missing email, city, or threshold", status_code=400)

        try:
            threshold = float(threshold)
        except ValueError:
            return func.HttpResponse("Threshold must be a number", status_code=400)

        # ----------------------------
        # OpenWeather API
        # ----------------------------
        api_key = os.getenv("OPENWEATHER_KEY")
        if not api_key:
            return func.HttpResponse("OPENWEATHER_KEY not configured", status_code=500)

        weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"
        weather_response = requests.get(weather_url)

        if weather_response.status_code != 200:
            return func.HttpResponse(f"City '{city}' not found", status_code=404)

        weather = weather_response.json()
        current_temp = weather["main"]["temp"]

        # ----------------------------
        # Blob Storage: load subscriptions.json
        # ----------------------------
        storage_conn = os.getenv("AzureWebJobsStorage")
        blob_service = BlobServiceClient.from_connection_string(storage_conn)
        container = blob_service.get_container_client("data")
        blob = container.get_blob_client("subscriptions.json")

        try:
            blob_data = blob.download_blob().readall()
            subscriptions_data = json.loads(blob_data)
        except Exception:
            subscriptions_data = {"subscriptions": []}

        subscriptions = subscriptions_data.get("subscriptions", [])

        # ----------------------------
        # Avoid duplicates
        # ----------------------------
        for sub in subscriptions:
            if sub["email"].lower() == email.lower() and sub["city"].lower() == city.lower():
                return func.HttpResponse("You are already subscribed for this city", status_code=409)

        # ----------------------------
        # Add new subscription
        # ----------------------------
        new_subscription = {
            "email": email,
            "city": weather["name"],  # normalized city name
            "threshold": threshold
        }
        subscriptions.append(new_subscription)

        blob.upload_blob(json.dumps({"subscriptions": subscriptions}, indent=2), overwrite=True)

        # ----------------------------
        # Send email immediately if threshold exceeded
        # ----------------------------
        if current_temp >= threshold:
            message = (
                f"🔥 Temperature alert for {weather['name']}\n\n"
                f"Current temperature: {current_temp}°C\n"
                f"Your threshold: {threshold}°C\n"
                f"Condition: {weather['weather'][0]['description']}"
            )
            send_email(email, f"Temperature Alert – {weather['name']}", message)
            immediate_alert = "Email alert sent immediately."
        else:
            immediate_alert = "Subscription stored; email will be sent if threshold is exceeded."

        # ----------------------------
        # Response
        # ----------------------------
        response_data = {
            "message": "Subscription created successfully",
            "city": weather["name"],
            "current_temp": current_temp,
            "threshold": threshold,
            "condition": weather["weather"][0]["description"],
            "immediate_alert": immediate_alert
        }

        return func.HttpResponse(json.dumps(response_data), mimetype="application/json", status_code=200)

    except Exception as e:
        logging.error(f"❌ Server error: {e}")
        return func.HttpResponse(f"Server error: {str(e)}", status_code=500)
