DROP TABLE IF EXISTS store_inventory;
DROP TABLE IF EXISTS inventory_categories;
DROP TABLE IF EXISTS inventory_to_category;

DROP TABLE IF EXISTS store_materials;
DROP TABLE IF EXISTS materials_categories;
DROP TABLE IF EXISTS material_to_category;

DROP TABLE IF EXISTS store_income;
DROP TABLE IF EXISTS income_categories;
DROP TABLE IF EXISTS income_to_category;

DROP TABLE IF EXISTS store_expenses;
DROP TABLE IF EXISTS expenses_categories;
DROP TABLE IF EXISTS expense_to_category;

DROP TABLE IF EXISTS settings;

CREATE TABLE store_inventory (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    cost DECIMAL(10, 2) NOT NULL
);

CREATE TABLE inventory_categories (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE inventory_to_category (
    tag_to_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_id INTEGER,
    item_id INTEGER
);


CREATE TABLE store_materials (
    material_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL
);

CREATE TABLE materials_categories (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE material_to_category (
    tag_to_material_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_id INTEGER,
    material_id INTEGER
);


CREATE TABLE store_income (
    income_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    income_year INTEGER,
    income_month INTEGER,
    income_day INTEGER
);

CREATE TABLE income_categories (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE income_to_category (
    tag_to_income_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_id INTEGER,
    income_id INTEGER
);


CREATE TABLE store_expenses (
    expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    expense_year INTEGER,
    expense_month INTEGER,
    expense_day INTEGER
);

CREATE TABLE expenses_categories (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE expense_to_category (
    tag_to_expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_id INTEGER,
    expense_id INTEGER
);

CREATE TABLE settings (
    name TEXT NOT NULL,
    quantity INTEGER
);
