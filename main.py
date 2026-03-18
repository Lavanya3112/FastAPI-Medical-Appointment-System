from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional
import math

app = FastAPI(
    title="MediCare Clinic - Medical Appointment System",
    description="A complete FastAPI backend for managing doctors, appointments, and consultations.",
    version="1.0.0"
)

# ─────────────────────────────────────────────
# DATA STORE
# ─────────────────────────────────────────────

doctors = [
    {"id": 1, "name": "Dr. Aisha Sharma",    "specialization": "Cardiologist",    "fee": 1200, "experience_years": 15, "is_available": True},
    {"id": 2, "name": "Dr. Rohan Mehta",     "specialization": "Dermatologist",   "fee": 800,  "experience_years": 8,  "is_available": True},
    {"id": 3, "name": "Dr. Priya Nair",      "specialization": "Pediatrician",    "fee": 600,  "experience_years": 10, "is_available": True},
    {"id": 4, "name": "Dr. Vikram Joshi",    "specialization": "General",         "fee": 400,  "experience_years": 5,  "is_available": True},
    {"id": 5, "name": "Dr. Sneha Kulkarni",  "specialization": "Cardiologist",    "fee": 1500, "experience_years": 20, "is_available": False},
    {"id": 6, "name": "Dr. Arjun Patel",     "specialization": "Dermatologist",   "fee": 950,  "experience_years": 12, "is_available": True},
]

appointments = []
appt_counter = 1
doctor_counter = 7


# ─────────────────────────────────────────────
# PYDANTIC MODELS
# ─────────────────────────────────────────────

class AppointmentRequest(BaseModel):
    patient_name: str = Field(..., min_length=2)
    doctor_id: int = Field(..., gt=0)
    date: str = Field(..., min_length=8)
    reason: str = Field(..., min_length=5)
    appointment_type: str = Field(default="in-person")
    senior_citizen: bool = Field(default=False)


class NewDoctor(BaseModel):
    name: str = Field(..., min_length=2)
    specialization: str = Field(..., min_length=2)
    fee: int = Field(..., gt=0)
    experience_years: int = Field(..., gt=0)
    is_available: bool = Field(default=True)


# ─────────────────────────────────────────────
# HELPER FUNCTIONS 
# ─────────────────────────────────────────────

def find_doctor(doctor_id: int):
    """Return the doctor dict if found, else None."""
    for d in doctors:
        if d["id"] == doctor_id:
            return d
    return None


def calculate_fee(base_fee: int, appointment_type: str, senior_citizen: bool) -> dict:
    """
    Calculate consultation fee based on appointment type and senior citizen status.
    - video       → 80 % of base fee
    - in-person   → 100 % of base fee
    - emergency   → 150 % of base fee
    Senior citizen discount: additional 15 % off after type adjustment.
    """
    type_multipliers = {"video": 0.80, "in-person": 1.0, "emergency": 1.50}
    multiplier = type_multipliers.get(appointment_type, 1.0)
    adjusted_fee = round(base_fee * multiplier)
    discount_amount = 0
    if senior_citizen:
        discount_amount = round(adjusted_fee * 0.15)
    final_fee = adjusted_fee - discount_amount
    return {
        "original_fee": base_fee,
        "type_adjusted_fee": adjusted_fee,
        "senior_discount": discount_amount,
        "final_fee": final_fee
    }


def filter_doctors_logic(
    specialization: Optional[str],
    max_fee: Optional[int],
    min_experience: Optional[int],
    is_available: Optional[bool]
) -> list:
    """Apply all active filters using is not None checks."""
    result = doctors[:]
    if specialization is not None:
        result = [d for d in result if d["specialization"].lower() == specialization.lower()]
    if max_fee is not None:
        result = [d for d in result if d["fee"] <= max_fee]
    if min_experience is not None:
        result = [d for d in result if d["experience_years"] >= min_experience]
    if is_available is not None:
        result = [d for d in result if d["is_available"] == is_available]
    return result


# ─────────────────────────────────────────────
# GET ENDPOINTS
# ─────────────────────────────────────────────

# Home route
@app.get("/")
def home():
    return {"message": "Welcome to MediCare Clinic"}


# List all doctors
@app.get("/doctors")
def get_all_doctors():
    available_count = sum(1 for d in doctors if d["is_available"])
    return {
        "total": len(doctors),
        "available_count": available_count,
        "doctors": doctors
    }


# List all appointments
@app.get("/appointments")
def get_all_appointments():
    return {
        "total": len(appointments),
        "appointments": appointments
    }


# Doctors summary  (FIXED route — must be above /doctors/{doctor_id})
@app.get("/doctors/summary")
def doctors_summary():
    if not doctors:
        return {"message": "No doctors available"}
    most_experienced = max(doctors, key=lambda d: d["experience_years"])
    cheapest_fee = min(d["fee"] for d in doctors)
    spec_count = {}
    for d in doctors:
        spec_count[d["specialization"]] = spec_count.get(d["specialization"], 0) + 1
    return {
        "total_doctors": len(doctors),
        "available_count": sum(1 for d in doctors if d["is_available"]),
        "most_experienced_doctor": most_experienced["name"],
        "most_experienced_years": most_experienced["experience_years"],
        "cheapest_consultation_fee": cheapest_fee,
        "doctors_per_specialization": spec_count
    }


# Filter doctors  (FIXED route)
@app.get("/doctors/filter")
def filter_doctors(
    specialization: Optional[str] = Query(default=None),
    max_fee: Optional[int] = Query(default=None),
    min_experience: Optional[int] = Query(default=None),
    is_available: Optional[bool] = Query(default=None)
):
    result = filter_doctors_logic(specialization, max_fee, min_experience, is_available)
    return {"total": len(result), "doctors": result}


# Search doctors  (FIXED route)
@app.get("/doctors/search")
def search_doctors(keyword: str = Query(...)):
    kw = keyword.lower()
    result = [
        d for d in doctors
        if kw in d["name"].lower() or kw in d["specialization"].lower()
    ]
    if not result:
        return {"message": f"No doctors found matching '{keyword}'", "total_found": 0, "doctors": []}
    return {"total_found": len(result), "doctors": result}


# Sort doctors  (FIXED route)
@app.get("/doctors/sort")
def sort_doctors(
    sort_by: str = Query(default="fee"),
    order: str = Query(default="asc")
):
    valid_sort = ["fee", "name", "experience_years"]
    valid_order = ["asc", "desc"]
    if sort_by not in valid_sort:
        return {"error": f"Invalid sort_by. Choose from: {valid_sort}"}
    if order not in valid_order:
        return {"error": f"Invalid order. Choose 'asc' or 'desc'"}
    sorted_list = sorted(doctors, key=lambda d: d[sort_by], reverse=(order == "desc"))
    return {"sort_by": sort_by, "order": order, "total": len(sorted_list), "doctors": sorted_list}


#  Paginate doctors  (FIXED route)
@app.get("/doctors/page")
def paginate_doctors(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=3, ge=1, le=10)
):
    start = (page - 1) * limit
    sliced = doctors[start: start + limit]
    total_pages = math.ceil(len(doctors) / limit)
    return {
        "page": page,
        "limit": limit,
        "total": len(doctors),
        "total_pages": total_pages,
        "doctors": sliced
    }


# Browse doctors (search + sort + paginate)  (FIXED route)
@app.get("/doctors/browse")
def browse_doctors(
    keyword: Optional[str] = Query(default=None),
    sort_by: str = Query(default="fee"),
    order: str = Query(default="asc"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=4, ge=1, le=20)
):
    valid_sort = ["fee", "name", "experience_years"]
    valid_order = ["asc", "desc"]
    if sort_by not in valid_sort:
        return {"error": f"Invalid sort_by. Choose from: {valid_sort}"}
    if order not in valid_order:
        return {"error": "Invalid order. Use 'asc' or 'desc'"}

    # Step 1: filter by keyword
    result = doctors[:]
    if keyword is not None:
        kw = keyword.lower()
        result = [d for d in result if kw in d["name"].lower() or kw in d["specialization"].lower()]

    # Step 2: sort
    result = sorted(result, key=lambda d: d[sort_by], reverse=(order == "desc"))

    # Step 3: paginate
    total = len(result)
    total_pages = math.ceil(total / limit) if total > 0 else 1
    start = (page - 1) * limit
    sliced = result[start: start + limit]

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total,
        "total_pages": total_pages,
        "doctors": sliced
    }


# Get doctor by ID 
@app.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: int):
    doctor = find_doctor(doctor_id)
    if not doctor:
        return {"error": "Doctor not found"}
    return doctor


# ─────────────────────────────────────────────
# APPOINTMENT — FIXED ROUTES
# ─────────────────────────────────────────────

# Search appointments by patient name
@app.get("/appointments/search")
def search_appointments(patient_name: str = Query(...)):
    result = [a for a in appointments if patient_name.lower() in a["patient_name"].lower()]
    return {"total_found": len(result), "appointments": result}


# Sort appointments
@app.get("/appointments/sort")
def sort_appointments(
    sort_by: str = Query(default="fee"),
    order: str = Query(default="asc")
):
    valid_sort = ["fee", "date"]
    valid_order = ["asc", "desc"]
    if sort_by not in valid_sort:
        return {"error": f"Invalid sort_by. Choose from: {valid_sort}"}
    if order not in valid_order:
        return {"error": "Invalid order. Use 'asc' or 'desc'"}
    sorted_list = sorted(appointments, key=lambda a: a[sort_by], reverse=(order == "desc"))
    return {"sort_by": sort_by, "order": order, "total": len(sorted_list), "appointments": sorted_list}


# Paginate appointments
@app.get("/appointments/page")
def paginate_appointments(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=5, ge=1, le=20)
):
    start = (page - 1) * limit
    sliced = appointments[start: start + limit]
    total_pages = math.ceil(len(appointments) / limit) if appointments else 1
    return {
        "page": page,
        "limit": limit,
        "total": len(appointments),
        "total_pages": total_pages,
        "appointments": sliced
    }


# Active appointments (status: scheduled or confirmed)  (FIXED route)
@app.get("/appointments/active")
def get_active_appointments():
    active = [a for a in appointments if a["status"] in ("scheduled", "confirmed")]
    return {"total": len(active), "appointments": active}


# Appointments by doctor  (FIXED prefix route)
@app.get("/appointments/by-doctor/{doctor_id}")
def get_appointments_by_doctor(doctor_id: int):
    doctor = find_doctor(doctor_id)
    if not doctor:
        return {"error": "Doctor not found"}
    result = [a for a in appointments if a["doctor_id"] == doctor_id]
    return {
        "doctor_name": doctor["name"],
        "total": len(result),
        "appointments": result
    }


# ─────────────────────────────────────────────
# POST /appointments 
# ─────────────────────────────────────────────

@app.post("/appointments")
def book_appointment(req: AppointmentRequest):
    global appt_counter

    # Check doctor exists
    doctor = find_doctor(req.doctor_id)
    if not doctor:
        return {"error": "Doctor not found"}

    # Check availability
    if not doctor["is_available"]:
        return {"error": f"{doctor['name']} is currently unavailable"}

    # Calculate fee using helper
    fee_info = calculate_fee(doctor["fee"], req.appointment_type, req.senior_citizen)

    appointment = {
        "appointment_id": appt_counter,
        "patient_name": req.patient_name,
        "doctor_id": req.doctor_id,
        "doctor_name": doctor["name"],
        "specialization": doctor["specialization"],
        "date": req.date,
        "reason": req.reason,
        "appointment_type": req.appointment_type,
        "senior_citizen": req.senior_citizen,
        "original_fee": fee_info["original_fee"],
        "type_adjusted_fee": fee_info["type_adjusted_fee"],
        "senior_discount": fee_info["senior_discount"],
        "fee": fee_info["final_fee"],
        "status": "scheduled"
    }
    appointments.append(appointment)
    appt_counter += 1
    return {"message": "Appointment booked successfully", "appointment": appointment}


# ─────────────────────────────────────────────
# CRUD: DOCTORS
# ─────────────────────────────────────────────

# Add new doctor
@app.post("/doctors", status_code=201)
def add_doctor(doc: NewDoctor):
    global doctor_counter
    # Reject duplicate names (case-insensitive)
    for existing in doctors:
        if existing["name"].lower() == doc.name.lower():
            return {"error": f"Doctor '{doc.name}' already exists"}
    new_doc = {
        "id": doctor_counter,
        "name": doc.name,
        "specialization": doc.specialization,
        "fee": doc.fee,
        "experience_years": doc.experience_years,
        "is_available": doc.is_available
    }
    doctors.append(new_doc)
    doctor_counter += 1
    return {"message": "Doctor added successfully", "doctor": new_doc}


# Update doctor
@app.put("/doctors/{doctor_id}")
def update_doctor(
    doctor_id: int,
    fee: Optional[int] = Query(default=None),
    is_available: Optional[bool] = Query(default=None)
):
    doctor = find_doctor(doctor_id)
    if not doctor:
        return {"error": "Doctor not found", "status_code": 404}
    if fee is not None:
        doctor["fee"] = fee
    if is_available is not None:
        doctor["is_available"] = is_available
    return {"message": "Doctor updated successfully", "doctor": doctor}


# Delete doctor
@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int):
    doctor = find_doctor(doctor_id)
    if not doctor:
        return {"error": "Doctor not found", "status_code": 404}
    # Cannot delete if doctor has active (scheduled) appointments
    active_appts = [a for a in appointments if a["doctor_id"] == doctor_id and a["status"] == "scheduled"]
    if active_appts:
        return {
            "error": f"Cannot delete '{doctor['name']}' — they have {len(active_appts)} active appointment(s)"
        }
    doctors.remove(doctor)
    return {"message": f"Doctor '{doctor['name']}' deleted successfully"}


# ─────────────────────────────────────────────
# MULTI-STEP WORKFLOW 
# ─────────────────────────────────────────────

# Confirm appointment
@app.post("/appointments/{appointment_id}/confirm")
def confirm_appointment(appointment_id: int):
    for appt in appointments:
        if appt["appointment_id"] == appointment_id:
            appt["status"] = "confirmed"
            return {"message": "Appointment confirmed", "appointment": appt}
    return {"error": "Appointment not found", "status_code": 404}


# Cancel appointment  (also marks doctor available again)
@app.post("/appointments/{appointment_id}/cancel")
def cancel_appointment(appointment_id: int):
    for appt in appointments:
        if appt["appointment_id"] == appointment_id:
            appt["status"] = "cancelled"
            # Mark the doctor available again
            doctor = find_doctor(appt["doctor_id"])
            if doctor:
                doctor["is_available"] = True
            return {"message": "Appointment cancelled and doctor is now available", "appointment": appt}
    return {"error": "Appointment not found", "status_code": 404}


# Complete appointment
@app.post("/appointments/{appointment_id}/complete")
def complete_appointment(appointment_id: int):
    for appt in appointments:
        if appt["appointment_id"] == appointment_id:
            appt["status"] = "completed"
            return {"message": "Appointment marked as completed", "appointment": appt}
    return {"error": "Appointment not found", "status_code": 404}