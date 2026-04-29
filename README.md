# Zentory

![Zentory Logo](static/Logo.png)

**Zentory** is a lightweight, free, and open-source all-in-one business management system designed for small and medium-sized enterprises (SMEs).

It solves the common business problem of using multiple expensive and fragmented tools by combining **Inventory, Sales, CRM, and Accounting** into a single easy-to-use web application.

##  Features

- **Modern Dashboard** with iteractive charts:
  - Stock Value by Product (Bar Chart)
  - Recent Sales Trend (Line Chart)
  - Income vs Expenses (Doughnut Chart)
- **Inventory Management** – Add, view and delete products with stock tracking
- **Sales Management** – Record sales with automatic stock deduction
- **CRM** – Manage customer information
- **Accounting** – Track income and expenses with real-time balance
- Responsive and clean user interface built with Bootstrap 5
- Simple demo login system (`admin` / `1234`)
- Fully documented and ready for contributions

## Tech Stack

- **Backend**: Python + Flask
- **Database**: SQLite (with Flask-SQLAlchemy)
- **Frontend**: Bootstrap 5 + Chart.js
- **Deployment**: Easy to run locally or deploy on Render, Railway, etc.

## How to start Start

1. **Clone the repository**
  
2. Create a virtual environment
   python -m venv venv
   
3. Activate the virtual environment
   venv\Scripts\activate
   
4. Install dependencies
   pip install flask flask-sqlalchemy
   
5. Run the application
   python app.py


zentory/
├── app.py                # Main Flask application
├── static/
│   Logo.png              # Project logo
├── templates/            # All HTML templates
│   base.html
│   login.html
│   dashboard.html
│   inventory.html
│   sales.html
│   crm.html
│   accounting.html
├── README.md
└── LICENSE

License

This project is licensed under the MIT License - see the LICENSE file for details.
