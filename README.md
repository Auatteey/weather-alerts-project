# 🌦️ Weather Alerts Cloud Project — Backend

## 📌 Project Overview

This project is a **cloud-based weather alert system** built on **Microsoft Azure**.  
The backend is responsible for collecting real-time weather data, analyzing it against predefined risk conditions, and automatically sending email alerts when dangerous weather situations are detected.

The project follows a **serverless architecture** and is designed to be scalable, reliable, and easy to monitor.

> ⚠️ This repository contains **only the backend part** of the project.  
> The frontend is developed and deployed separately by the other team member.

---

## 🎯 Objectives

- Retrieve real-time weather data for multiple cities
- Analyze weather conditions (temperature, wind, visibility, etc.)
- Detect potentially dangerous situations
- Automatically send email alerts to users
- Run fully in the cloud using Azure services
- Provide monitoring and logs for observability

---

## 🏗️ Cloud Architecture

The backend relies on the following Azure services:

- **Azure Functions**
  - `getWeather` (HTTP Trigger): returns real-time weather data
  - `checkAlerts` (Timer Trigger): periodically checks weather conditions and sends alerts

- **Azure Blob Storage**
  - Stores the list of monitored cities (`cities.json`)
  - Can store alert state data if needed

- **Application Insights**
  - Logs function executions
  - Monitors errors and dependencies
  - Confirms successful email delivery

The backend interacts with two external APIs:
- **OpenWeather API** (weather data)
- **MailerSend API** (email alerts)

---

## ⚙️ Backend Features

### 🔹 getWeather (HTTP Trigger)
- Input: city name
- Output: formatted weather data (temperature, humidity, wind, etc.)
- Used by the frontend to display real-time weather information

### 🔹 checkAlerts (Timer Trigger)
- Runs automatically at a fixed interval
- Loads the list of cities from Azure Blob Storage
- Calls the OpenWeather API for each city
- Applies alert rules
- Sends an email when a dangerous condition is detected

---

## 🚨 Alert Logic

Alerts are triggered when one or more of the following conditions are met:

- Temperature below a defined threshold
- Wind speed above a defined threshold
- Low visibility
- Storm or thunder conditions

When an alert is triggered:
- A clear alert message is generated
- An email is sent via MailerSend
- The execution is logged in Application Insights

---

## 🧪 Alert System Validation

The alert system was validated using a **controlled test**:
- A temporary forced condition was added to guarantee alert triggering
- Emails were successfully sent and received for all monitored cities
- Logs confirmed correct execution and email delivery (`202 Accepted`)

This test proves that the alert mechanism works independently of real weather conditions.


## 📦 Repository Scope

This repository contains **only the backend**:
- Azure Functions source code
- Configuration files
- Dependency definitions

The frontend is:
- Hosted separately on Azure Web App
- Maintained by the other project member
- Connected to this backend via HTTP APIs



---

## ✅ Conclusion

This backend demonstrates a **fully functional cloud-native alert system** using Azure serverless services.  
It integrates external APIs, automated tasks, secure configuration management, and monitoring, making it a complete and professional cloud project.
