import uuid
import random
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# --- Configurations ---
app = FastAPI(
    title="Premium Doctor Booking API",
    description="Professional Backend for Flutter Training - Version 4.0",
    version="4.0.0"
)

security = HTTPBearer()

# Static Credentials
USER_DATA = {
    "id": "u-98754",
    "name": "Daniel Martinez",
    "phone": "+123 856479683",
    "email": "user@email.com",
    "password": "user123456"
}

active_tokens = set()

# --- Models ---
class Review(BaseModel):
    id: int # تم إضافة ID للريفيو
    username: str
    rating: int
    review_body: str

class Doctor(BaseModel):
    id: int
    name: str
    specialization: str
    image: str
    location: str
    patients_count: int
    experience_rate: int
    rating: int
    about: str
    working_time: str
    reviews: List[Review]

class Hospital(BaseModel):
    id: int
    name: str
    image: str
    location: str
    rating: int
    reviews_count: int
    distance: str

class LoginRequest(BaseModel):
    email: str
    password: str

# --- Data Generation Helpers ---

def get_realistic_review_body():
    # نصوص تم ضبطها لتكون بين 20 و 25 كلمة بالضبط
    options = [
        "Dr. Smith is an amazing professional who handled my case with extreme care and provided a very clear recovery plan for my health.",
        "The consultation was very detailed and informative. I appreciate the time spent explaining every single aspect of my current medical condition and treatment.",
        "I highly recommend this clinic to everyone seeking quality care. The staff is professional and the doctor is very knowledgeable about modern medical practices.",
        "The experience was outstanding from start to finish. I felt heard and respected during the entire process, making the recovery much easier than expected.",
        "A truly remarkable medical professional who genuinely cares about patient well-being and provides excellent follow-up support after every visit to the medical center."
    ]
    return random.choice(options)

def generate_doctors(count: int) -> List[Doctor]:
    docs = []
    # 20 اسم واقعي بدون أرقام
    names = [
        "David Patel", "Sarah Johnson", "Michael Chen", "Emily Davis", "James Wilson", 
        "Sophia Garcia", "Robert Miller", "Olivia Brown", "William Taylor", "Emma Anderson",
        "Christopher Thomas", "Isabella Moore", "Matthew Jackson", "Mia White", "Andrew Harris",
        "Charlotte Martin", "Joshua Thompson", "Amelia Garcia", "Nathan Robinson", "Grace Lewis"
    ]
    specs = ["Cardiologist", "Pediatrician", "Dermatologist", "Neurologist", "Orthopedic Surgeon"]
    cities = ["Medical Plaza, New York, NY", "Wellness Center, Los Angeles, CA", "Health Towers, Chicago, IL", "Unity Clinic, Houston, TX"]
    patient_names = ["Alice", "Mark", "Samer", "Sara", "John", "Elena", "Youssef", "Maria"]

    for i in range(count):
        name = f"Dr. {names[i]}" # استخدام الاسم من القائمة لضمان عدم وجود أرقام
        spec = random.choice(specs)
        docs.append(Doctor(
            id=101 + i,
            name=name,
            specialization=spec,
            image=f"https://i.pravatar.cc/150?u={uuid.uuid4().hex}", # صورة فريدة لكل دكتور
            location=random.choice(cities),
            patients_count=random.randint(5000, 10000),
            experience_rate=random.randint(7, 10),
            rating=random.randint(3, 5),
            about=f"{name} is a highly dedicated {spec.lower()} with a focus on modern diagnostic techniques. Bringing over 15 years of international experience to provide the best care.",
            working_time="Monday-Friday, 08.00 AM-18.00 PM",
            reviews=[
                Review(
                    id=i * 10 + 1,
                    username=random.choice(patient_names) + " " + random.choice(["K.", "M.", "A."]),
                    rating=random.randint(4, 5),
                    review_body=get_realistic_review_body()
                ),
                Review(
                    id=i * 10 + 2,
                    username=random.choice(patient_names) + " " + random.choice(["S.", "L.", "R."]),
                    rating=random.randint(4, 5),
                    review_body=get_realistic_review_body()
                )
            ]
        ))
    return docs

def generate_hospitals(count: int) -> List[Hospital]:
    hospitals = []
    # 10 أسماء مشافي واقعية بدون أرقام
    hospital_names = [
        "Sunrise Health Clinic", "City General Hospital", "Mercy Wellness Center", 
        "Green Valley Medical", "Saint Jude Hospital", "Metro Health Institute", 
        "North Star Medical", "Pacific Care Center", "Riverside General", "Unity Health Plaza"
    ]
    cities = ["Central Square, Boston, MA", "North District, Seattle, WA", "East Side Park, Miami, FL"]

    for i in range(count):
        hospitals.append(Hospital(
            id=501 + i,
            name=hospital_names[i],
            image=f"https://picsum.photos/seed/{uuid.uuid4().hex}/400/300", # صورة فريدة لكل مشفى
            location=random.choice(cities),
            rating=random.randint(3, 5),
            reviews_count=random.randint(50, 500),
            distance=f"{random.uniform(1.5, 10.0):.1f} km / {random.randint(15, 55)} min"
        ))
    return hospitals

# Pre-generate data
DOCTORS_DB = generate_doctors(20)
HOSPITALS_DB = generate_hospitals(10)

# --- Dependency ---
def verify_token(auth: HTTPAuthorizationCredentials = Depends(security)):
    token = auth.credentials
    if token not in active_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

# --- Endpoints ---

@app.post("/login", tags=["Auth"])
def login(request: LoginRequest):
    if request.email == USER_DATA["email"] and request.password == USER_DATA["password"]:
        token = uuid.uuid4().hex
        active_tokens.add(token)
        return {"status": "success", "token": token}
    raise HTTPException(status_code=401, detail="Invalid email or password")

@app.get("/doctors", response_model=List[Doctor], tags=["Data"])
def get_doctors(token: str = Depends(verify_token)):
    return DOCTORS_DB

@app.get("/hospitals", response_model=List[Hospital], tags=["Data"])
def get_hospitals(token: str = Depends(verify_token)):
    return HOSPITALS_DB

@app.get("/profile", tags=["User"])
def get_profile(token: str = Depends(verify_token)):
    return {
        "id": USER_DATA["id"],
        "name": USER_DATA["name"],
        "phone": USER_DATA["phone"],
        "email": USER_DATA["email"]
    }

@app.post("/logout", tags=["Auth"])
def logout(token: str = Depends(verify_token)):
    if token in active_tokens:
        active_tokens.remove(token)
    return {"message": "Successfully logged out"}