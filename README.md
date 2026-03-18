# 💊 MediCare Clinic — Medical Appointment System

A production-style **FastAPI backend** simulating a real clinic appointment workflow.  
Built during the **Feb 2026 Innomatics Research Labs FastAPI Internship**.

---

## 🚀 Project Overview

This project implements a fully functional **Medical Appointment Management REST API** using FastAPI.

It demonstrates real-world backend capabilities including:

- Doctor management  
- Appointment booking lifecycle  
- Business logic & consultation fee calculation  
- Filtering and search systems  
- Sorting & pagination mechanisms  
- Multi-step workflow handling  

The system is designed to simulate how an actual **clinic backend service** operates.

---

## ✅ Core Features

### 🩺 Doctor Management

- View all doctors with availability status  
- Retrieve doctor details by ID  
- Add new doctors with validation  
- Update consultation fee & availability  
- Delete doctor with workflow safety checks  
- Filter doctors by specialization, fee and experience  
- Advanced keyword search  
- Sorting by fee, name or experience  
- Pagination support  
- Combined browsing (search + sort + pagination)

---

### 📅 Appointment Management

- Book appointments using validated request schema  
- Automatic doctor lookup & consultation fee calculation  
- Appointment type-based pricing (video / in-person / emergency)  
- Senior citizen discount handling  
- Confirm scheduled appointments  
- Cancel appointments with doctor availability restoration  
- Mark appointments as completed  
- View all appointments  
- View active appointments (scheduled + confirmed)  
- View appointments for a specific doctor  

---

### 🌟 Advanced Appointment Utilities

- Search appointments by patient name  
- Sort appointments by consultation fee or date  
- Paginate appointment records  

These utilities simulate real **healthcare dashboard backend features**.

---

## 🧠 Business Logic Implemented

### 💰 Fee Calculation Engine

- Video consultation → **80% of base fee**  
- In-person consultation → **100% of base fee**  
- Emergency consultation → **150% of base fee**  
- Senior citizen → **Additional 15% discount**

---

### 🔁 Appointment Lifecycle Workflow

```
Book → Confirm → Complete
        ↘ Cancel (restores doctor availability)
```

This models a real **state transition system** used in scheduling platforms.

---

## 📡 Tech Stack

- **FastAPI** — High-performance async API framework  
- **Pydantic v2** — Robust data validation  
- **Uvicorn** — ASGI production server  
- **Python 3.10+**

---

## 📁 Project Structure

```
fastapi-medical-appointment-system/
│
├── main.py
├── requirements.txt
├── README.md
└── screenshots/
```

---

## ▶️ Running the Project

```bash
git clone https://github.com/YOUR_USERNAME/fastapi-medical-appointment-system.git
cd fastapi-medical-appointment-system

pip install -r requirements.txt
uvicorn main:app --reload
```

Open Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

## 🏥 **Sample Dataset**

The system includes **pre-loaded doctors across multiple specializations**:

- Cardiologist  
- Dermatologist  
- Pediatrician  
- General Physician  

This allows immediate testing of **filtering and booking workflows**.

---

## 🎯 **Learning Outcomes**

Through this project, the following backend engineering skills were practiced:

- REST API design principles  
- Workflow-based state management  
- Structured validation using Pydantic  
- Query-parameter driven search systems  
- Pagination logic implementation  
- Clean API response structuring  
- Realistic business rule simulation  

---

## ⭐ **Built with dedication during the Innomatics Research Labs FastAPI Internship — Feb 2026**

---
