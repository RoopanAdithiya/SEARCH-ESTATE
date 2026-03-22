# 🏙 Chennai Rental Intelligence Platform

> AI-powered rental decision system with explainable ML and geospatial insights

---

## 🚀 Overview

A full-stack web application that helps:

* 🧑‍💼 Tenants evaluate affordability and rent fairness
* 🏢 Landlords optimize pricing and listing decisions
* 🏘 Users explore properties through AI + map-based insights

The system combines:

* Machine Learning (rent prediction)
* Explainable AI (SHAP)
* Marketplace listings
* Geospatial visualization (Leaflet)

---

## 🔥 Key Features

### 🧠 AI Rent Prediction

* Predicts fair rent using XGBoost
* Detects overpriced properties
* Provides decision-ready insights

---

### 📊 Explainable AI (SHAP)

* Shows *why* a rent was predicted
* Displays top contributing factors
* Visual bar-based explanation

---

### 🧑‍💼 Tenant Decision Engine

* Calculates rent stress
* Provides human-readable verdicts:

  * 🟢 Affordable
  * ⚠️ Moderate Strain
  * 🔴 High Stress

---

### 🏢 Landlord Optimization

* Add property listings
* Analyze pricing before listing
* Get AI-based feedback

---

### 🏘 Marketplace + Filters

* Browse properties
* Apply filters (BHK, locality, price)
* Instant AI verdict on each listing

---

### 🗺 Geospatial Visualization

* Map-based property browsing
* Marker → property interaction
* Map and list fully synchronized

---

## 🖼 Screenshots

*(Add these)*

* Home page
* Tenant analysis
* SHAP explanation
* Listings + map

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

## 🧠 How It Works

1. User inputs property details or selects a listing
2. ML model predicts fair rent
3. System calculates:

   * overpricing
   * rent stress
4. SHAP explains prediction
5. Results shown via UI + charts + map

---

## 📊 Core Logic

* **Overpricing**
  `(listed - predicted) / predicted`

* **Rent Stress**
  `rent / income`

---

## 🧭 Project Highlights

* Full-stack ML system (not just model)
* Explainable AI integration (SHAP)
* Real-world product design
* Map-based UX (spatial intelligence)
* Database-agnostic backend

---

## ⚙️ Setup Instructions

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

## 🎯 Future Improvements

* Vacancy prediction model
* Advanced filtering
* Real dataset integration
* Deployment

---

## 💡 Author

Built as a full-stack + ML portfolio project demonstrating:

* system design
* AI integration
* product thinking

---
