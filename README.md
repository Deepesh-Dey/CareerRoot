# 🎓 CareerRoot - Placement Portal Application

A comprehensive Flask-based placement portal designed for educational institutions to streamline the placement process with dedicated portals for **Admins**, **Companies**, and **Students**.

## 🌐 Live Demo
**[https://careerroot.onrender.com](https://careerroot.onrender.com)**

---

## ✨ Features

### For Students 🎓
- Create and manage student profiles
- Browse and apply for placement drives
- Track application status in real-time
- View detailed company information
- Download placement offers

### For Companies 🏢
- Register and manage company profiles
- Create and manage placement drives
- View student applications
- Schedule interviews
- Post job requirements and eligibility criteria

### For Admins 👨‍💼
- Approve/reject company and student registrations
- Manage all placement drives
- Monitor applications and placements
- Generate analytics and reports
- View platform-wide statistics with charts

---

## 🛠️ Tech Stack

- **Backend**: Flask 2.3.3
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, Bootstrap
- **Authentication**: Flask-Login
- **Server**: Gunicorn
- **Deployment**: Render
- **Data Visualization**: Matplotlib
- **Form Validation**: WTForms

---

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment (optional but recommended)

---

## 🚀 Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/Deepesh-Dey/CareerRoot.git
cd CareerRoot
```

### 2. Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```

The app will be available at `http://localhost:5000`

---

## 🔐 Getting Started

### Admin Login
Use the default admin credentials to access the admin dashboard:

| Field | Value |
|-------|-------|
| **Username** | `admin` |
| **Password** | `Admin@123` |

### Register as Student or Company
- Navigate to the respective login page
- Click on **"Register"** or **"Sign Up"**
- Fill in the registration form with your details
- Use any valid email format (dummy emails work: `student@example.com`, `company@test.com`)
- Once registered, log in with your credentials
- Admin approval may be required for company registrations

---

## 📸 Screenshots

### 🏠 Landing Page
The welcoming home page with navigation to all three portals.
![Landing Page](./static/images/landing_page.png)

### 👨‍💼 Admin Dashboard
Admin panel with complete statistics, analytics charts, and management controls.
![Admin Dashboard](./static/images/admin_dashboard.png)

### 🏢 Company Registration
Company registration form for new recruitment partners.
![Company Registration](./static/images/company_registration.png)

### 🏢 Company Dashboard
Company dashboard showing jobs posted, applications, and analytics.
![Company Dashboard](./static/images/company_dashboard.png)

### 🎓 Student Registration
Student registration form for placement candidates.
![Student Registration](./static/images/student_registration.png)

### 🎓 Student Dashboard
Student dashboard with profile, available drives, and application tracking.
![Student Dashboard](./static/images/student_dashboard.png)

---

## 📁 Project Structure

```
CareerRoot/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── core/
│   ├── database/
│   │   ├── models.py          # SQLAlchemy models
│   │   └── __init__.py
│   ├── routes/
│   │   ├── auth.py            # Authentication routes
│   │   ├── admin.py           # Admin routes
│   │   ├── company.py         # Company routes
│   │   ├── student.py         # Student routes
│   │   └── __init__.py
│   ├── utils/
│   │   └── chart_data.py      # Analytics and charting
│   └── __init__.py
├── templates/
│   ├── base.html              # Base template
│   ├── Admin.html             # Admin dashboard
│   ├── Company.html           # Company dashboard
│   ├── Student.html           # Student dashboard
│   └── ...
├── static/
│   ├── css/                   # Stylesheets
│   ├── js/                    # JavaScript
│   ├── images/                # Screenshots and assets
│   └── ...
├── render.yaml                # Render deployment config
└── README.md                  # This file
```

---

## 🎯 Key Features Breakdown

### Authentication System
- Secure role-based login
- Session management
- Password hashing
- Account registration workflows

### Placement Drive Management
- Create and schedule drives
- Set eligibility criteria
- Manage applications
- Track placement status

### Dashboard & Analytics
- Real-time statistics
- Visual charts and graphs
- Application tracking
- Performance metrics

---

## 🌐 Deployment

This project is deployed on **Render** and automatically deploys on every push to the `main` branch.

### Deploy your own:
1. Fork this repository
2. Create a Render account at [render.com](https://render.com)
3. Connect your GitHub repository
4. Set environment variables: `SECRET_KEY`, `FLASK_ENV=production`
5. Deploy!

---

## 📝 Environment Variables

Create a `.env` file (not committed to repo):
```
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 👨‍💻 Author

**Deepesh Dey**
- GitHub: [@Deepesh-Dey](https://github.com/Deepesh-Dey)
- Project Repo: [CareerRoot](https://github.com/Deepesh-Dey/CareerRoot)

---

## 📞 Support

If you have any questions or issues, please open an [issue](https://github.com/Deepesh-Dey/CareerRoot/issues) on GitHub.

---

## 🙏 Acknowledgments

- Flask and Flask extensions community
- SQLAlchemy ORM
- Bootstrap for UI components
- Render for free hosting

---

## 📚 Academic Project

This project is developed as a course assignment for:

- **Institution**: IIT Madras
- **Program**: Bachelor of Science in Data Science and Applications (IITM BS DS)
- **Course**: Modern Application Development 1 (MAD 1) - Project
- **Term**: January 2026

**Made with ❤️ for educational institutions**
