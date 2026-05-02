# Team Task Manager

A simple full-stack task management web application where users can create accounts, manage projects, assign tasks, and track progress.

This project was built as part of a full-stack coding assignment to demonstrate backend development, authentication, database integration, and deployment.

## Features

**Authentication**

- User signup and login
- Password hashing using Bcrypt

**Project Management**

- Create projects
- Assign users to projects

**Task Management**

- Create tasks with title, description, and due date
- Assign tasks to users
- Update task status: To Do, In Progress, Done

**Dashboard**

- View task overview
- Track task status and assignments

## Tech Stack

**Backend**

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-Bcrypt

**Frontend**

- HTML
- CSS
- Jinja Templates

**Database**

- PostgreSQL

**Deployment**

- Railway

## Project Structure

```text
Ethara_AI_Task
│
├ main.py
├ routes.py
├ models.py
├ extensions.py
├ requirements.txt
│
├ templates
│   ├ base_auth.html
│   ├ login.html
│   ├ signup.html
│   └ dashboard.html
│
├ static
│   └ css
│       └ style.css
│
└ README.md
```

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/ShashankRajput90/Ethara_AI_Task.git
cd Ethara_AI_Task
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables

Create a `.env` file:

```env
SECRET_KEY=your_secret_key
DATABASE_URL=your_postgresql_database_url
```

### 5. Run the app

```bash
python main.py
```

Open:

```text
http://127.0.0.1:5000
```

## Deployment

The application is deployed using Railway with a PostgreSQL database service connected through environment variables.

## Author

Shashank Lodhi

GitHub: https://github.com/ShashankRajput90
LinkedIn: https://www.linkedin.com/in/shashank-lodhi-a93b2524b/
