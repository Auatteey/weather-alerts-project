# 🌦️ Weather Alerts Cloud Project — Backend

## 📌 Project Overview

This project implements a **cloud-based weather monitoring and alert system** using **Microsoft Azure**.
The backend is designed to retrieve real-time weather data, analyze it against predefined alert conditions, and automatically notify users via email when potentially dangerous weather events occur.

The system follows a **serverless, event-driven architecture**, ensuring scalability, reliability, and minimal operational overhead.

> ⚠️ This repository contains **only the backend component** of the project.
> The frontend application is developed and deployed separately by another team member and communicates with this backend via HTTP APIs.

---

## 🎯 Project Objectives

* Retrieve real-time weather data for multiple cities
* Analyze weather conditions automatically
* Detect hazardous or abnormal weather situations
* Send automated email alerts to subscribed users
* Run entirely in the cloud using serverless Azure services
* Provide logging, monitoring, and observability

---

## 🏗️ Cloud Architecture Overview

The backend relies on the following **Azure services**:

### ☁️ Core Azure Services

* **Azure Functions (Serverless Backend)**

  * `getWeather` *(HTTP Trigger)*
    Returns real-time weather data for a requested city
  * `checkAlerts` *(Timer Trigger)*
    Periodically checks weather conditions and triggers alerts
  * `checkUserThresholds` *(Timer Trigger)*
    Evaluates user-defined alert thresholds and sends personalized notifications

* **Azure Blob Storage**

  * Stores configuration and persistent data:

    * `cities.json` — list of monitored cities
    * `subscriptions.json` — user alert subscriptions

* **Azure Application Insights**

  * Logs executions and errors
  * Monitors API dependencies
  * Tracks alert processing and email delivery status

### 🌍 External APIs

* **OpenWeather API**

  * Provides real-time weather data (temperature, wind, visibility, etc.)

* **MailerSend API**

  * Sends alert emails to users
  * Provides delivery status and API-level feedback

---

## ⚙️ Backend Functionality

### 🔹 `getWeather` — HTTP Trigger

* **Input:** City name
* **Output:** Structured weather data (temperature, humidity, wind speed, visibility, conditions)
* **Purpose:** Supplies real-time weather data to the frontend interface

---

### 🔹 `checkAlerts` — Timer Trigger

* Executes automatically at a fixed interval
* Loads the list of monitored cities from Blob Storage
* Fetches weather data from OpenWeather API
* Applies predefined alert rules
* Sends alert emails when conditions are met

---

### 🔹 `checkUserThresholds` — Timer Trigger

* Evaluates **user-defined alert subscriptions**
* Compares real-time temperature values against custom thresholds
* Sends personalized alert emails when thresholds are crossed
* Prevents constant user polling by using background automation

---

## 🚨 Alert Logic

Alerts are generated when one or more of the following conditions occur:

* Temperature below or above defined thresholds
* Extreme cold or heat conditions
* Low visibility
* Strong wind or storm-related weather
* Custom user-defined temperature thresholds

When an alert is triggered:

1. A descriptive alert message is generated
2. An email is sent via **MailerSend**
3. The execution and result are logged in **Application Insights**

---

## 🧪 Alert System Validation

The alert system was validated through **controlled testing**:

* Forced threshold values were used to guarantee alert triggering
* Emails were successfully sent and received
* MailerSend responses (`202 Accepted`) confirmed delivery requests
* Azure logs confirmed correct execution of all timer functions

These tests demonstrate that the alert mechanism works independently of real-world weather conditions.

---

## 📦 Repository Scope

This repository contains **only the backend implementation**, including:

* Azure Functions source code
* Serverless configuration files
* Blob Storage access logic
* External API integrations
* Environment variable configuration

The frontend application:

* Is hosted separately on **Azure Web App**
* Is maintained by another project member
* Communicates with this backend via HTTP endpoints

---

## ✅ Conclusion

This backend represents a **complete cloud-native weather alert system** built with modern Azure services.
It demonstrates the use of serverless computing, event-driven execution, API integration, persistent cloud storage, automated notifications, and professional monitoring.

The project highlights how cloud technologies can be used to build **scalable, automated, and real-time alerting systems** with minimal infrastructure management.

