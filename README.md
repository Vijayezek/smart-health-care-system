# Smart Health Care System

AI-powered healthcare system using data mining and sentiment analysis for disease prediction, medicine recommendations, and patient feedback analysis.

## Features

- **User Module**
  - Registration with unique validation (email, mobile, password strength)
  - Login/Logout
  - Symptom-based disease prediction using ML
  - Medicine recommendations
  - PDF prescription download
  - Feedback submission with sentiment analysis

- **Admin Module**
  - Pre-configured credentials (username: `admin`, password: `admin123`)
  - Real-time analytics dashboard
  - CRUD operations for:
    - Users
    - Doctors
    - Medicines
    - Feedbacks
  - Sentiment analysis charts

- **ML/AI Features**
  - Disease prediction using KNN and TF-IDF
  - Sentiment analysis using Naive Bayes
  - Automatic feedback categorization

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite3
- **ML Libraries**: scikit-learn, NLTK
- **PDF Generation**: ReportLab
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Chart.js
- **Timezone**: IST (Indian Standard Time)

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

## Installation & Setup for VS Code

### 1. Clone or Download the Project

```bash
# If you have the project as a zip, extract it
# Navigate to the project directory
cd SmartHealthCare
```

### 2. Create Virtual Environment (Recommended)

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download NLTK Data

Run this Python command to download required NLTK data:

```bash
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"
```

### 5. Set Environment Variables

**On Windows (PowerShell):**
```powershell
$env:SESSION_SECRET="your-super-secret-key-change-this-in-production"
```

**On Windows (Command Prompt):**
```cmd
set SESSION_SECRET=your-super-secret-key-change-this-in-production
```

**On macOS/Linux:**
```bash
export SESSION_SECRET="your-super-secret-key-change-this-in-production"
```

**Or create a `.env` file** (recommended for VS Code):

Create a file named `.env` in the project root:
```
SESSION_SECRET=your-super-secret-key-change-this-in-production
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

And add this to the top of `app.py` (after imports):
```python
from dotenv import load_dotenv
load_dotenv()
```

### 6. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### 7. Access the Application

- **Home Page**: http://localhost:5000
- **User Registration**: http://localhost:5000/register
- **User Login**: http://localhost:5000/login
- **Admin Login**: http://localhost:5000/admin/login

## Default Admin Credentials

- **Username**: `admin`
- **Password**: `admin123`

## Project Structure

```
SmartHealthCare/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── database/
│   └── smart_health.db        # SQLite database (auto-created)
├── static/
│   ├── css/
│   │   └── style.css          # Gradient UI styling
│   └── js/
│       └── dashboard.js       # Frontend scripts
├── templates/                  # HTML templates
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── admin_login.html
│   ├── user_dashboard.html
│   ├── admin_dashboard.html
│   ├── feedback.html
│   ├── manage_users.html
│   ├── manage_doctors.html
│   ├── manage_medicines.html
│   └── manage_feedbacks.html
└── utils/
    ├── db_helper.py           # Database operations
    ├── sentiment_model.py     # Sentiment analysis
    ├── symptom_predictor.py   # Disease prediction
    └── time_utils.py          # IST timezone
```

## Database Schema

The SQLite database includes the following tables:

- **users**: User accounts with unique email and mobile validation
- **admin**: Admin accounts (pre-seeded with admin/admin123)
- **doctors**: Doctor information
- **symptoms**: Symptom database
- **medicines**: Medicine database with disease mapping
- **feedbacks**: User feedback with sentiment analysis

## Validation Rules

### User Registration:
- **Email**: Must be unique and valid format
- **Mobile**: Must be unique, 10 digits, starting with 6-9
- **Password**: Minimum 8 characters with uppercase, lowercase, and number
- **Confirm Password**: Must match the password field

## Running in Production

For production deployment, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Important**: Always set a strong `SESSION_SECRET` environment variable in production!

## Troubleshooting

### NLTK Data Error
If you get NLTK errors, run:
```bash
python -c "import nltk; nltk.download('stopwords')"
```

### Database Not Found
The database is auto-created on first run. Ensure the `database/` folder exists.

### Port Already in Use
If port 5000 is busy, change the port in `app.py`:
```python
app.run(host='0.0.0.0', port=8080, debug=False)
```

### SESSION_SECRET Error
Make sure you've set the `SESSION_SECRET` environment variable before running the app.

## License

This project is for educational purposes.

## Support

For issues or questions, please check the code documentation or contact the development team.
