# 🏠 PG and Hostel Management System

This project is a full-stack **PG and Hostel Management System** built using **Python, Django, HTML/CSS, JavaScript, Chart.js, scikit-learn, Pandas, and SQLite**. It is designed to streamline and automate hostel and PG management tasks, integrating both **web application features** and **machine learning capabilities**. Administrators can manage PG listings, tenant registrations, and complaint handling efficiently, while machine learning models provide predictive insights for better decision-making.

Key features include machine learning models for **rent prediction**, **occupancy forecasting**, **complaint resolution time estimation**, and **personalized PG recommendations**. These models are powered by **scikit-learn** and trained on structured datasets to enhance management accuracy and user experience. The application also integrates **Chart.js** for interactive and visually appealing analytics dashboards, enabling administrators to gain insights into occupancy trends, rental distributions, and complaint patterns.

The backend is powered by **Django** with **SQLite** as the database for managing tenant details, PG records, and complaint logs, while the frontend is built with **HTML, CSS, and JavaScript** for a user-friendly interface. Administrators can log in to view analytics dashboards and manage listings, while tenants can register, book rooms, and raise complaints seamlessly through the web interface. Data processing and predictive modeling are handled using **Pandas and scikit-learn**, with results visualized through graphs and charts for clarity. 

---

## 📂 Project Structure
media/
└── pg_images/
├── bornrich_pg.avif
├── hetal_pg_image.jpeg
└── Pearls_aatithya_PG.avif

ml_models/
├── complaint_model.pkl
├── occupancy_model.pkl
└── rent_model.pkl

models/
├── archive.zip
└── get_details.py

pg_project/
├── asgi.py
├── settings.py
├── urls.py
├── wsgi.py
├── init.py
└── pycache/
├── settings.cpython-312.pyc
├── urls.cpython-312.pyc
├── wsgi.cpython-312.pyc
└── init.cpython-312.pyc

db.sqlite3
generate_occupancy_csv.py
load_members.py
load_pg_data.py
manage.py
requirements.txt
train_complaints.py
train_occupancy.py
train_rent_model.py



---

## ⚙️ Installation & Setup

1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-username/pg-hostel-management.git
   cd pg-hostel-management
(Optional) Create and activate a virtual environment


python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate
Install dependencies from requirements.txt


pip install -r requirements.txt
Run database migrations


python manage.py migrate
Run the development server


python manage.py runserver
Access the app
Open http://127.0.0.1:8000/ in your browser.

🔄 Model Training
Since the trained ML models (.pkl files) are ignored in version control, they need to be regenerated after cloning. You can retrain them by running:


python train_rent_model.py
python train_occupancy.py
python train_complaints.py
This will create fresh models inside the ml_models/ folder.

📊 Features Recap (from Resume)
Built a full-stack web application using Django and Machine Learning to manage PG listings, tenant registrations, and complaint handling.

Integrated ML models for rent prediction, occupancy forecasting, complaint resolution time estimation, and PG recommendations.

Visualized analytics using Chart.js for admin insights.

📝 Notes
db.sqlite3 is a development database and is ignored in version control; users should generate their own locally.

Media files under media/pg_images/ are sample PG images and can be extended.

For production, environment variables (like secret keys) should be stored in a .env file, which is ignored in GitHub.
