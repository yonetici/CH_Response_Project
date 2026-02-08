# CH-RIS: Cultural Heritage Response & Risk Management System

**CH-RIS** is a specialized Disaster Risk Management (DRM) platform designed to digitize damage assessment, inventory management, and logistics tracking for cultural heritage sites, historic buildings, and movable assets in post-disaster scenarios.

This system is fully aligned with the international **PROCULTHER-NET 2** methodology and templates.

## 🚀 Key Features

### 1. Field Operations Management

* 
**Hierarchical Data Structure:** Organizes operations from Sectors to Worksites, and down to specific Site Assessments, Buildings, and Assets.


* 
**Mission Assignment:** Assigns specialized teams to specific worksites and tracks mission status (Active/Completed/Cancelled).


* 
**Interactive Operational Map:** Visualizes sector boundaries and worksite points using JSON-based coordinate data.



### 2. Comprehensive Assessment Modules

* 
**Damage Assessment:** Specialized matrices for Seismic, Fire, and Hydrometeorological hazards, including structural and non-structural damage analysis.


* 
**Movable Cultural Heritage:** Cataloging of artifacts, including material analysis, damage condition, and evacuation priorities.


* 
**Logistics & Tracking:** End-to-end tracking of artifact transfers from damaged buildings to secure storage sites.


* 
**Intangible Heritage (ICH):** Assessment of risks to local traditions, rituals, and community social practices following a disaster.



### 3. Reporting & Security

* 
**Automated PDF Reporting:** Generates comprehensive Mission Reports in PDF format directly from field data for international stakeholders.


* **Role-Based Access Control (RBAC):** Distinct permissions for Administrators (Full Access) and Field Experts (Restricted to assigned tasks).
* **Secure Personnel Management:** Integrated system for managing expert profiles with automated secure password generation.

## 🛠️ Technology Stack

* 
**Backend:** Python 3.13+, Django 6.0 


* **Frontend:** HTML5, CSS3, Bootstrap 5, FontAwesome
* **Database:** SQLite (Development), PostgreSQL (Recommended for Production)
* 
**Reporting:** xhtml2pdf 



## 📋 Installation

1. **Clone the Repository:**
```bash
git clone https://github.com/yourusername/CH_Response_Project.git
cd CH_Response_Project

```


2. **Setup Virtual Environment:**
```bash
python -m venv env
# Windows:
.\env\Scripts\activate
# Linux/Mac:
source env/bin/activate

```


3. **Install Dependencies:**
```bash
pip install django xhtml2pdf

```


4. **Initialize Database:**
```bash
python manage.py makemigrations
python manage.py migrate

```


5. **Create Superuser:**
```bash
python manage.py createsuperuser

```


6. **Run Server:**
```bash
python manage.py runserver

```



## 📂 Project Architecture

* 
`core/models.py`: Database schemas following PROCULTHER standards (Site, Building, Damage, Movable, Intangible).


* 
`core/views.py`: Logic for the Command Center, field dashboard, and report generation.


* 
`core/forms.py`: Dynamic forms supporting JSONField for complex damage matrices.


* `templates/`: Responsive UI templates built with Bootstrap for field usage.

## 📄 License

Developed as an open-source tool within the framework of the PROCULTHER-NET 2 methodology.

---

**Developer Note:** This system was designed with the cooperation of AFAD (Disaster and Emergency Management Authority) and international cultural heritage protection standards in mind.