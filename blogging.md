Here’s your content formatted in Markdown:  

```md
# How to Create a Virtual Environment in Linux

### Prerequisite
Install the required package:

```bash
sudo apt install python3.12-venv
```

### Command to Create Virtual Environment
```bash
python3 -m venv <environment_name>
```

## How to Start Virtual Environment
```bash
source <environment_name>/bin/activate
```

## How to Stop Virtual Environment
```bash
deactivate
```

---

# Installing Requirement Files from `requirements.txt`
```bash
pip install -r requirements.txt
```

### If There Is a Conflict in Dependencies  
If there is a conflict in module dependencies (e.g., Python 3.12 and `redis==4.6.0`):

#### Possible Fixes:
1️⃣ Use the latest version of `redis`  
   Try installing the latest version instead of `4.6.0`:

   ```bash
   pip install redis
   ```

2️⃣ Update `requirements.txt` with the installed version:

   ```bash
   pip freeze | grep redis >> requirements.txt
   ```

---

# How to Create a Django Project
```bash
django-admin startproject <project_name>
```

### Check Whether the Project is Created
```bash
python manage.py runserver
```

**Make sure that the present working directory (pwd) is `<project_name>`**  

---

# What is an App?
An app is a web application that has a specific meaning in your project, such as:
- A home page
- A contact form
- A members database

### How to Create an App
```bash
python manage.py startapp <app_name>
```

---

# Views in Django
Django views are Python functions that take HTTP requests and return HTTP responses, such as HTML documents.  

A web page that uses Django consists of multiple views, each performing different tasks.

Views are typically placed in a file named `views.py` inside your app’s folder.

---

# Routing in Django
The `urls.py` file inside the app is specific to that application. However, we also need to configure routing in the root directory (`my_tennis_club`).  

For now, simply follow the instructions to ensure proper routing.
```

This keeps everything structured and readable in Markdown. Let me know if you need any modifications! 🚀
