from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import func, Boolean
from flasgger import Swagger

from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
swagger = Swagger(app, config=None, template=None)


app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print("SQLALCHEMY_DATABASE_URI:", app.config.get('SQLALCHEMY_DATABASE_URI'))

db = SQLAlchemy(app)

# ENDPOINT DOCUMENTATION



####################################################
# Database models (reflect your schema exactly)
####################################################

class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

class Warehouse(db.Model):
    __tablename__ = 'warehouse'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(64), nullable=False)
    price = db.Column(db.Numeric(12, 2), nullable=False)
    is_bundle = db.Column(db.Boolean, nullable=False, default=False)  # use this for threshold join

class Supplier(db.Model):
    __tablename__ = 'supplier'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    contact_info = db.Column(db.String(255))  # used as contact_email in response
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

class ProductSupplier(db.Model):
    __tablename__ = 'product_supplier'
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id', ondelete='CASCADE'), primary_key=True)

class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)

class Sale(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    sale_date = db.Column(db.DateTime, nullable=False)

class ProductTypeThreshold(db.Model):
    __tablename__ = 'product_type_threshold'
    product_type = db.Column(Boolean, primary_key=True)  # BOOLEAN: True for bundles, False for others
    threshold = db.Column(db.Integer, nullable=False)

####################################################
# Low-stock alerts endpoint
####################################################

@app.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def get_low_stock_alerts(company_id):
    
    """
    Get low-stock alerts for a company.
    ---
    tags:
      - Alerts
    parameters:
      - name: company_id
        in: path
        type: integer
        required: true
        description: The ID of the company to get low stock alerts for
    responses:
      200:
        description: List of low-stock alerts with supplier information
        schema:
          type: object
          properties:
            alerts:
              type: array
              items:
                type: object
                properties:
                  product_id:
                    type: integer
                    example: 123
                  product_name:
                    type: string
                    example: "Widget A"
                  sku:
                    type: string
                    example: "WID-001"
                  warehouse_id:
                    type: integer
                    example: 456
                  warehouse_name:
                    type: string
                    example: "Main Warehouse"
                  current_stock:
                    type: integer
                    example: 5
                  threshold:
                    type: integer
                    example: 20
                  days_until_stockout:
                    type: integer
                    example: 12
                    nullable: true
                  supplier:
                    type: object
                    nullable: true
                    properties:
                      id:
                        type: integer
                        example: 789
                      name:
                        type: string
                        example: "Supplier Corp"
                      contact_email:
                        type: string
                        example: "orders@supplier.com"
            total_alerts:
              type: integer
              example: 1
      404:
        description: Company not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Company not found"
    """
    
    
    # Verify company exists
    company = Company.query.get(company_id)
    if not company:
        return jsonify({"error": "Company not found"}), 404

    # Define recent sales window (last 30 days)
    recent_period_start = datetime.utcnow() - timedelta(days=30)

    # 1. Products with recent sales in company
    recent_sales_subq = (
        db.session.query(Sale.product_id)
        .join(Product, Product.id == Sale.product_id)
        .filter(
            Product.company_id == company_id,
            Sale.sale_date >= recent_period_start
        )
        .distinct()
        .subquery()
    )

    # 2. Inventories with product info, warehouse info, and thresholds
    inventories = (
        db.session.query(
            Inventory.id.label("inventory_id"),
            Product.id.label("product_id"),
            Product.name.label("product_name"),
            Product.sku,
            Product.is_bundle,
            Warehouse.id.label("warehouse_id"),
            Warehouse.name.label("warehouse_name"),
            Inventory.quantity.label("current_stock"),
            ProductTypeThreshold.threshold
        )
        .join(Product, Inventory.product_id == Product.id)
        .join(Warehouse, Inventory.warehouse_id == Warehouse.id)
        .join(ProductTypeThreshold, Product.is_bundle == ProductTypeThreshold.product_type)  # Boolean join here
        .filter(
            Product.company_id == company_id,
            Warehouse.company_id == company_id,
            Inventory.quantity <= ProductTypeThreshold.threshold,
            Inventory.product_id.in_(recent_sales_subq)  # Only products with recent sales
        )
        .all()
    )

    # 3. Calculate average daily sales per product (last 30 days)
    sales_agg = (
        db.session.query(
            Sale.product_id,
            func.sum(Sale.quantity).label("total_quantity")
        )
        .join(Product, Product.id == Sale.product_id)
        .filter(
            Product.company_id == company_id,
            Sale.sale_date >= recent_period_start
        )
        .group_by(Sale.product_id)
        .all()
    )
    avg_daily_sales_map = {s.product_id: s.total_quantity / 30 for s in sales_agg}

    # 4. Prepare alert list
    alerts = []
    for inv in inventories:
        avg_daily_sales = avg_daily_sales_map.get(inv.product_id, 0)
        if avg_daily_sales > 0:
            days_until_stockout = int(inv.current_stock / avg_daily_sales)
        else:
            days_until_stockout = None

        # Fetch first linked supplier info (optional)
        supplier = (
            db.session.query(Supplier)
            .join(ProductSupplier, Supplier.id == ProductSupplier.supplier_id)
            .filter(ProductSupplier.product_id == inv.product_id)
            .first()
        )

        supplier_info = None
        if supplier:
            supplier_info = {
                "id": supplier.id,
                "name": supplier.name,
                "contact_email": supplier.contact_info or ""
            }

        alert = {
            "product_id": inv.product_id,
            "product_name": inv.product_name,
            "sku": inv.sku,
            "warehouse_id": inv.warehouse_id,
            "warehouse_name": inv.warehouse_name,
            "current_stock": inv.current_stock,
            "threshold": inv.threshold,
            "days_until_stockout": days_until_stockout,
            "supplier": supplier_info
        }
        alerts.append(alert)

    return jsonify({
        "alerts": alerts,
        "total_alerts": len(alerts)
    }), 200

####################################################
# Main entrypoint
####################################################

if __name__ == '__main__':
    # For production, use a WSGI server like gunicorn instead
    app.run(debug=True)
