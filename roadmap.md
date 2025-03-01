## **Step-by-Step Development Roadmap**  

Since you're using an API for managing seat availability, it's best to develop the **backend first** so the frontend can consume the APIs during development. This will ensure smooth integration and reduce potential rework.  

---

# **🛠 Phase 1: Backend Development (Step-by-Step)**
### **Goal:** Build a Python-based backend that manages user authentication, booking system, seat availability, payments, and notifications.  

## **🔹 Step 1: Define Backend Requirements**
✅ **Core Features:**  
   - User authentication (Sign-up/Login).  
   - Ride management (Routes, time slots, seat availability).  
   - Booking system (Reserving/canceling seats).  
   - Payment integration (Stripe/Razorpay).  
   - Notifications (Email/SMS reminders).  
   - Admin dashboard APIs (for managing rides & users).  

---

## **🔹 Step 2: Set Up the Development Environment**  
✅ **Choose Stack:**  
   - **Framework:** Django (for full-stack) or FastAPI (for API-only).  
   - **Database:** PostgreSQL (main DB) + Redis (for caching seat availability).  
   - **Task Queue:** Celery + Redis (for async tasks like email/sms).  
   - **Hosting:** AWS EC2, Google Cloud, or Heroku.  

✅ **Install Required Packages:**  
```sh
pip install django djangorestframework django-cors-headers djangorestframework-simplejwt psycopg2-binary gunicorn celery redis stripe
```  
✅ **Create Project & App:**  
```sh
django-admin startproject backend  
cd backend  
django-admin startapp api  
```  

---

## **🔹 Step 3: Design Database Schema**  
✅ **Models for Users, Rides, Bookings, and Payments:**  

```python
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
    referral_code = models.CharField(max_length=10, unique=True, null=True, blank=True)

class Ride(models.Model):
    route = models.CharField(max_length=255)
    time_slot = models.TimeField()
    total_seats = models.IntegerField()
    available_seats = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE)
    num_seats = models.IntegerField()
    payment_status = models.CharField(max_length=10, choices=[('Pending', 'Pending'), ('Paid', 'Paid')])

class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=10, choices=[('Success', 'Success'), ('Failed', 'Failed')])
```  

✅ **Run Migrations:**  
```sh
python manage.py makemigrations  
python manage.py migrate  
```  

---

## **🔹 Step 4: Implement Authentication (JWT-Based)**
✅ **Install JWT Authentication:**  
```sh
pip install djangorestframework-simplejwt
```  
✅ **Modify `settings.py`:**  
```python
INSTALLED_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'api',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

AUTH_USER_MODEL = 'api.User'
```  
✅ **Create API Endpoints (`views.py`):**  

```python
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from .models import User

@api_view(['POST'])
def register(request):
    user = User.objects.create_user(
        username=request.data['email'],
        email=request.data['email'],
        password=request.data['password'],
        phone=request.data['phone']
    )
    return Response({'message': 'User registered successfully'})

@api_view(['POST'])
def login(request):
    user = authenticate(username=request.data['email'], password=request.data['password'])
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({'refresh': str(refresh), 'access': str(refresh.access_token)})
    return Response({'error': 'Invalid credentials'}, status=400)
```  

---

## **🔹 Step 5: Implement Booking Management**  
✅ **API Endpoints:**  

```python
@api_view(['GET'])
def get_rides(request):
    rides = Ride.objects.all()
    return Response([{"id": ride.id, "route": ride.route, "available_seats": ride.available_seats} for ride in rides])

@api_view(['POST'])
def create_booking(request):
    ride = Ride.objects.get(id=request.data['ride_id'])
    if ride.available_seats >= request.data['num_seats']:
        ride.available_seats -= request.data['num_seats']
        ride.save()
        booking = Booking.objects.create(
            user=request.user, ride=ride, num_seats=request.data['num_seats'], payment_status="Pending"
        )
        return Response({"message": "Booking created", "booking_id": booking.id})
    return Response({"error": "Not enough seats"}, status=400)
```  

---

## **🔹 Step 6: Implement Seat Availability API (Real-time Updates using Redis)**  
✅ **Install Redis:**  
```sh
sudo apt update && sudo apt install redis  
pip install django-redis
```  
✅ **Modify `settings.py`:**  
```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
    }
}
```  
✅ **Use Redis for Seat Availability Caching:**  

```python
from django.core.cache import cache

@api_view(['GET'])
def get_seat_availability(request, ride_id):
    available_seats = cache.get(f"ride_{ride_id}_seats")
    if available_seats is None:
        ride = Ride.objects.get(id=ride_id)
        available_seats = ride.available_seats
        cache.set(f"ride_{ride_id}_seats", available_seats, timeout=60)
    return Response({"available_seats": available_seats})
```  

---

## **🔹 Step 7: Integrate Payment System (Stripe API)**
✅ **Install Stripe:**  
```sh
pip install stripe
```  
✅ **Create Payment API:**  

```python
import stripe
from django.conf import settings

stripe.api_key = "YOUR_STRIPE_SECRET_KEY"

@api_view(['POST'])
def create_payment(request):
    booking = Booking.objects.get(id=request.data['booking_id'])
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': booking.ride.route},
                'unit_amount': int(booking.ride.price * 100),
            },
            'quantity': booking.num_seats,
        }],
        mode='payment',
        success_url=settings.SITE_URL + "/success",
        cancel_url=settings.SITE_URL + "/cancel",
    )
    return Response({"session_id": session.id})
```  

---

## **🔹 Step 8: Testing**
✅ **Test APIs using Postman**  
✅ **Write Unit Tests using Pytest**  

---

## **🔹 Step 9: Deploy Backend**  
✅ **Use Docker:**  
```sh
docker build -t my-backend .  
docker run -p 8000:8000 my-backend  
```  
✅ **Deploy on AWS/GCP/Heroku**  
✅ **Use CI/CD (GitHub Actions)**  

---

# **🚀 Phase 2: Frontend Development (Step-by-Step)**
## **Goal:** Build a responsive React frontend that interacts with the backend APIs for authentication, booking, seat availability, and payments.  

---

## **🔹 Step 1: Set Up React Development Environment**  

✅ **Install Node.js & Create React App:**  
```sh
npx create-react-app frontend  
cd frontend  
```

✅ **Install Dependencies:**  
```sh
npm install axios react-router-dom @mui/material @emotion/react @emotion/styled react-toastify redux react-redux @reduxjs/toolkit jwt-decode
```  

✅ **Project Structure:**  
```
frontend/
│── src/
│   ├── components/      # Reusable UI components
│   ├── pages/           # Page components
│   ├── store/           # Redux store
│   ├── services/        # API calls
│   ├── App.js           # Main application
│   ├── index.js         # Entry point
```

---

## **🔹 Step 2: Configure Routing (React Router)**  
✅ **Install React Router:**  
```sh
npm install react-router-dom
```

✅ **Update `App.js`:**  
```jsx
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Booking from "./pages/Booking";
import Dashboard from "./pages/Dashboard";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/booking" element={<Booking />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Router>
  );
}

export default App;
```

---

## **🔹 Step 3: Implement Authentication (JWT-Based)**
✅ **Create `services/authService.js`:**  
```jsx
import axios from "axios";

const API_URL = "http://localhost:8000/api";

export const login = async (email, password) => {
  const response = await axios.post(`${API_URL}/login/`, { email, password });
  localStorage.setItem("token", response.data.access);
  return response.data;
};

export const register = async (email, password, phone) => {
  return axios.post(`${API_URL}/register/`, { email, password, phone });
};

export const logout = () => {
  localStorage.removeItem("token");
};
```

✅ **Create `store/authSlice.js` for Redux State Management:**  
```jsx
import { createSlice } from "@reduxjs/toolkit";
import jwtDecode from "jwt-decode";

const token = localStorage.getItem("token");

const initialState = {
  user: token ? jwtDecode(token) : null,
  isAuthenticated: !!token,
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    loginSuccess: (state, action) => {
      state.user = action.payload;
      state.isAuthenticated = true;
    },
    logoutSuccess: (state) => {
      state.user = null;
      state.isAuthenticated = false;
    },
  },
});

export const { loginSuccess, logoutSuccess } = authSlice.actions;
export default authSlice.reducer;
```

✅ **Wrap App in Redux Provider (`index.js`):**  
```jsx
import { Provider } from "react-redux";
import { configureStore } from "@reduxjs/toolkit";
import authReducer from "./store/authSlice";

const store = configureStore({ reducer: { auth: authReducer } });

ReactDOM.render(
  <Provider store={store}>
    <App />
  </Provider>,
  document.getElementById("root")
);
```

---

## **🔹 Step 4: Implement UI Pages**
✅ **Login Page (`pages/Login.js`)**
```jsx
import { useState } from "react";
import { login } from "../services/authService";
import { useDispatch } from "react-redux";
import { loginSuccess } from "../store/authSlice";
import { useNavigate } from "react-router-dom";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const data = await login(email, password);
      dispatch(loginSuccess(data));
      navigate("/dashboard");
    } catch (error) {
      alert("Login failed!");
    }
  };

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        <button type="submit">Login</button>
      </form>
    </div>
  );
};

export default Login;
```

---

## **🔹 Step 5: Implement Booking System**
✅ **Fetch Available Rides (`services/bookingService.js`)**  
```jsx
import axios from "axios";

const API_URL = "http://localhost:8000/api";

export const getAvailableRides = async () => {
  return axios.get(`${API_URL}/rides/`);
};

export const bookRide = async (rideId, numSeats) => {
  const token = localStorage.getItem("token");
  return axios.post(
    `${API_URL}/bookings/`,
    { ride_id: rideId, num_seats: numSeats },
    { headers: { Authorization: `Bearer ${token}` } }
  );
};
```

✅ **Booking Page (`pages/Booking.js`)**  
```jsx
import { useEffect, useState } from "react";
import { getAvailableRides, bookRide } from "../services/bookingService";

const Booking = () => {
  const [rides, setRides] = useState([]);
  const [selectedRide, setSelectedRide] = useState(null);
  const [numSeats, setNumSeats] = useState(1);

  useEffect(() => {
    getAvailableRides().then((res) => setRides(res.data));
  }, []);

  const handleBooking = async () => {
    if (selectedRide) {
      await bookRide(selectedRide, numSeats);
      alert("Booking confirmed!");
    }
  };

  return (
    <div>
      <h2>Select a Ride</h2>
      <select onChange={(e) => setSelectedRide(e.target.value)}>
        {rides.map((ride) => (
          <option key={ride.id} value={ride.id}>{`${ride.route} - ${ride.available_seats} seats left`}</option>
        ))}
      </select>
      <input type="number" value={numSeats} onChange={(e) => setNumSeats(e.target.value)} />
      <button onClick={handleBooking}>Book Now</button>
    </div>
  );
};

export default Booking;
```

---

## **🔹 Step 6: Implement Payments (Stripe Checkout)**
✅ **Modify `bookingService.js`:**  
```jsx
export const createPayment = async (bookingId) => {
  return axios.post(`${API_URL}/payments/`, { booking_id: bookingId });
};
```

✅ **Update `Booking.js` to handle payments:**  
```jsx
const handlePayment = async () => {
  const response = await createPayment(selectedBookingId);
  window.location.href = response.data.session_url; // Redirect to Stripe checkout
};
```

---

## **🔹 Step 7: Responsive Design with Material UI**
✅ **Install Material UI:**  
```sh
npm install @mui/material @mui/icons-material
```

✅ **Use Material UI Components:**  
```jsx
import { Button, TextField, Card, CardContent } from "@mui/material";
```

---

## **🔹 Step 8: Testing & Deployment**
✅ **Test in Multiple Browsers (Chrome, Safari, Firefox)**  
✅ **Deploy Frontend on Vercel/Netlify**  
```sh
npm run build  
```
✅ **Connect Frontend to Backend & Run End-to-End Tests**  

---

🎉 **Final Step: Full System Integration!**  
✅ **Test the complete flow from user login → booking → payment → confirmation.** 🚀
