# 🏙 SearchEstate — AI-Powered Rental Intelligence Platform

> Know the real price of rent. Stop guessing.

---

## 🚀 Overview

**SearchEstate** is a full-stack AI-powered platform that helps:

* 🧑‍💼 **Tenants** evaluate rent affordability and avoid overpaying
* 🏢 **Landlords** optimize pricing before listing
* 🏘 **Users** explore properties through intelligent insights + maps

It combines:

* Machine Learning (rent prediction)
* Explainable AI (SHAP)
* Marketplace listings
* Geospatial visualization

---

## 🔥 Key Features

### 🧠 AI Rent Prediction

* Predicts fair rent using ML (XGBoost)
* Detects overpriced listings
* Provides decision-ready insights

---

### 📊 Explainable AI (SHAP)

* Shows **why** a price is predicted
* Displays feature contributions
* Visual bar-based explanation

---

### 🧑‍💼 Tenant Decision Engine

* Calculates rent stress (% of income)
* Human-friendly verdicts:

  * 🟢 Affordable
  * ⚠️ Moderate Strain
  * 🔴 High Stress

---

### 🏢 Landlord Listing System

* Add property details
* Instantly list in marketplace
* AI-ready listings for tenants

---

### 🏘 Marketplace + Filters

* Browse all listings
* Filter by locality, BHK, rent
* AI verdict directly on listings

---

### 🗺 Geospatial Visualization

* Map-based browsing (Leaflet)
* Click marker → highlight listing
* Fully synced map + list experience

---

## 🖼 Screenshots

### 🏠 Home Page

![Home](./assert/home.png)

---

### 🏢 Landlord Listing Page

![Landlord](./assert/landlord.png)

---

### 🔍 Property Analysis (AI + SHAP)

![Analysis](./assert/analysis.png)

---

### 🗺 Listings + Map View

![Map](./assert/map.png)

---

### 🧠 Interactive Map + Selection

![Map Interaction](./assert/map2.png)

---

### 🧠 Deep Property Analysis (AI + SHAP)

![Deep Analysis](./assert/deep-analysis.png)

This view provides a complete breakdown of a property:

- 📍 Property details (location, size, furnishing, water, age)
- 💰 Predicted fair rent using ML
- 📉 Overpricing analysis vs market
- 📊 Visual comparison (predicted vs listed)
- 🧠 SHAP-based explanation:
  - Shows which features increased or decreased rent
  - Human-readable feature impact
  - Color-coded contribution bars

👉 This transforms raw predictions into **transparent, explainable decisions**

## 🧠 How It Works

1. User inputs property details or selects a listing
2. ML model predicts fair rent
3. System calculates:

   * overpricing
   * affordability
   * rent stress
4. SHAP explains the prediction
5. Results displayed via UI + charts + map

---

## 📊 Core Logic

**Overpricing**

```text
(listed_rent - predicted_rent) / predicted_rent
```

**Rent Stress**

```text
rent / income
```

---

## 🏗 Tech Stack

### Frontend

* React (Vite)
* Tailwind CSS
* Recharts
* React Leaflet

### Backend

* FastAPI
* SQLAlchemy

### Database

* PostgreSQL (production-ready)
* SQLite (development)

### Machine Learning

* XGBoost
* SHAP
* Scikit-learn
* Pandas / NumPy

---

## ⚙️ Setup Instructions

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 🧭 Project Highlights

* Full-stack ML system (not just a model)
* Explainable AI integration (SHAP)
* Real-world product UX (map + insights)
* Database-agnostic architecture
* Clean UI with decision-focused design

---

## 🚀 Future Improvements

* Vacancy prediction model
* Advanced filters
* Real dataset integration
* Deployment (cloud)

---

## 💡 Author

Built as a full-stack + ML portfolio project demonstrating:

* system design
* AI integration
* product thinking

---
