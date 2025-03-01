# **Containerizing Your Full-Stack Application with Docker**

Containerizing your project ensures that it runs consistently across different operating systems and environments. In this guide, we will containerize both the **backend (Django)** and **frontend (React)** using **Docker** and manage them using **Docker Compose**.

---

## **Step 1: Create a `Dockerfile` for the Backend**

Inside your **backend** directory, create a file named `Dockerfile` with the following content:

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend project into the container
COPY . .

# Expose the port that Django runs on
EXPOSE 8000

# Run database migrations and start the Django server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
```

---

## **Step 2: Create a `Dockerfile` for the Frontend**

Inside your **frontend** directory, create another file named `Dockerfile`:

```dockerfile
# Use an official Node.js runtime as a parent image
FROM node:18

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to leverage Docker caching
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy the entire frontend project into the container
COPY . .

# Expose the port that React runs on
EXPOSE 3000

# Start the React app
CMD ["npm", "start"]
```

---

## **Step 3: Create a `docker-compose.yml` File**

At the **root directory** of your project, create a file named `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DEBUG=True
      - DATABASE_URL=postgres://user:password@db:5432/app_db
      - REDIS_URL=redis://redis:6379

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: app_db
    ports:
      - "5432:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  pg_data:
```

---

## **Step 4: Build and Run the Containers**

Navigate to the **root directory** of your project and run the following commands:

1. **Build the containers:**
   ```sh
   docker-compose build
   ```

2. **Start all services:**
   ```sh
   docker-compose up
   ```

Your services should now be running:
✅ **Backend on** `http://localhost:8000`
✅ **Frontend on** `http://localhost:3000`
✅ **PostgreSQL database inside a container**
✅ **Redis caching system inside a container**

---

## **Step 5: Verify and Access the App**

### **Check Running Containers**
Run the following command to list all running containers:
```sh
docker ps
```

### **Access Django Admin Panel**
To create a Django superuser, execute:
```sh
docker exec -it <backend-container-id> python manage.py createsuperuser
```

### **Access PostgreSQL Database**
To connect to the PostgreSQL database inside the container:
```sh
docker exec -it <db-container-id> psql -U user -d app_db
```

---

## **Step 6: Stop and Remove Containers**

To **stop all running containers**, use:
```sh
docker-compose down
```

To **remove containers and associated volumes**, run:
```sh
docker-compose down --volumes
```

---

## **Conclusion** 🎉

Your full-stack project is now **fully containerized**, making it easy to run on any OS with Docker installed. Anyone can now start the project with:
```sh
docker-compose up --build
```

Let me know if you need modifications or additional features! 🚀

