
# Inventory Management System for B2B SaaS - Task Documentation

## Overview

This project is a backend-focused take-home task for a B2B Inventory Management System ("StockFlow").  
It includes:  
- Debugged and optimized Flask API implementation for a **Low-Stock Alerts** endpoint.  
- Complete database schema design with PostgreSQL table creation scripts.  
- Swagger API endpoint documentation.  
- Data seeding and sample response illustration.  

This document summarizes all deliverables, instructions to setup, and usage.

## Folder Structure

```
/InventoryManagementTask
│
├── app/
│   ├── app.py                # Flask API implementation (Low-stock alerts)
│   ├── debuggedCode.py       # Corrected and debugged version of Part 1 code for product creation
│   ├── requirements.txt      # Python dependencies
│   └── endpointDoc.json      # Exported OpenAPI JSON specification from Swagger docs
│   |── .env                  # Add .env with credintial DATABASE_URL FLASK_ENV FLASK_APP you dont see this in repo i ignored this.
|── stockflowenv/
├── databaseDesign.sql        # SQL file containing all table creation queries for Postgres schema
├── response.png              # Screenshot of example API response output (low-stock alerts)
├── README.md                 # This documentation file
└── ...
```

## Setup Instructions

### 1. Clone or Download the repository

```bash
git clone https://github.com/aakashmohole/Bynry-Case-Study-Task.git
cd Bynry-Case-Study-Task
```

### 2. Create and Initialize PostgreSQL Database

- Use [NeonDB](https://neon.tech/) or your preferred PostgreSQL instance.

- Run the `databaseDesign.sql` to set up the schema:

```bash
psql -h  -U  -d  -f databaseDesign.sql
```

- The schema includes tables for `company`, `warehouse`, `product`, `product_bundle`, `supplier`, `product_supplier`, `inventory`, `inventory_change`, `sales`, and `product_type_threshold`.

### 3. Seed Sample Data

(Optionally, seed sample data with sample inserts for products, suppliers, warehouses, sales, and thresholds. This helps to test and see meaningful API output.)

### 4. Configure Flask App

- Navigate to the `app` folder:

```bash
cd app
```

- Create a Python virtual environment and activate it:

```bash
python -m venv env
# Linux/Mac
source env/bin/activate

# Windows
.\env\Scripts\activate
```

- Install dependencies:

```bash
pip install -r requirements.txt
```

- Open `app.py` and update the `SQLALCHEMY_DATABASE_URI` to your NeonDB or Postgres connection string:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://user:password@host/database?sslmode=require"
```

### 5. Run the Flask API

```bash
python app.py
```

- The API will be accessible at `http://localhost:5000`.

### 6. Test Low-Stock Alerts Endpoint

- Use curl, Postman, or browser:

```
GET http://localhost:5000/api/companies//alerts/low-stock
```

Example:

```bash
curl http://localhost:5000/api/companies/1/alerts/low-stock
```

## API Endpoint Summary

### GET `/api/companies/{company_id}/alerts/low-stock`

Return low-stock alerts for products owned by a company, filtered by:

- Low stock threshold (varies by product type — bundle or individual)
- Products with recent sales activity (last 30 days)
- Multiple warehouses per company
- Includes primary supplier info for reordering

#### Example Response
![resukt](response.png)


## Documentation

- The OpenAPI JSON documentation is provided as `endpointDoc.json` inside `/app`.
- You can use this file to import into SwaggerHub, Postman, or other API tools.
- Live Swagger UI will be available at `http://localhost:5000/apidocs/` when running the Flask app (with Flasgger enabled).

## Files Description

| File                  | Description                                          |
|-----------------------|-----------------------------------------------------|
| `databaseDesign.sql`  | All SQL DDL commands to create schema tables         |
| `response.png`        | Screenshot of a sample valid response from endpoint  |
| `app/app.py`          | Flask API implementation with low-stock alert logic  |
| `app/debuggedCode.py` | Debugged and improved product creation code (Part 1) |
| `app/requirements.txt`| Python dependencies needed to run the Flask app      |
| `app/endpointDoc.json`| Exported OpenAPI JSON file with endpoint documentation|

## Assumptions & Notes

- The system supports multi-tenant firms (companies), each with multiple warehouses.
- SKUs are unique per company.
- Sales data is tracked to identify recent sales activity.
- Stock thresholds differ between bundles and individual products.
- `product_type_threshold` uses `BOOLEAN` type matched with `Product.is_bundle`.
- Proper error handling and validation included in the API.
- For production deployments, use a WSGI server like Gunicorn.
- Sample data should be seeded for meaningful testing.


## Contact 
email - aakashmohole@gmail.com

**Thank you for reviewing my Inventory Management System implementation!**
