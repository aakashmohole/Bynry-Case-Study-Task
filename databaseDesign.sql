-- 1. Companies
CREATE TABLE company (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    -- Add fields like address, contact info, etc.
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 2. Warehouses
CREATE TABLE warehouse (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES company(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 3. Products
CREATE TABLE product (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES company(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(64) NOT NULL,
    price DECIMAL(12, 2) NOT NULL,
    is_bundle BOOLEAN NOT NULL DEFAULT FALSE,
    -- Additional fields: description, etc.
    UNIQUE (company_id, sku)  -- SKU unique within company
);

-- 4. Bundled Products (For bundles containing other products)
CREATE TABLE product_bundle (
    bundle_id INTEGER NOT NULL REFERENCES product(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES product(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (bundle_id, product_id)
);

-- 5. Suppliers
CREATE TABLE supplier (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_info VARCHAR(255),
    -- Add address, phone, etc.
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 6. Product - Supplier mapping (Products can have one or more suppliers)
CREATE TABLE product_supplier (
    product_id INTEGER NOT NULL REFERENCES product(id) ON DELETE CASCADE,
    supplier_id INTEGER NOT NULL REFERENCES supplier(id) ON DELETE CASCADE,
    PRIMARY KEY (product_id, supplier_id)
);

-- 7. Inventory (quantity per product per warehouse)
CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES product(id) ON DELETE CASCADE,
    warehouse_id INTEGER NOT NULL REFERENCES warehouse(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 0,
    UNIQUE (product_id, warehouse_id)
);

-- 8. Inventory Changes (Audit/history log)
CREATE TABLE inventory_change (
    id SERIAL PRIMARY KEY,
    inventory_id INTEGER NOT NULL REFERENCES inventory(id) ON DELETE CASCADE,
    change_amount INTEGER NOT NULL,
    reason VARCHAR(255),
    changed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    changed_by INTEGER -- Optionally FK to user table
);

