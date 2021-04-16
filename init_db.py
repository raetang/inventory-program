import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Populate database
# Settings

cur.execute("INSERT INTO settings (name, quantity) VALUES (?, ?)", ('Reminder Quantity', 10))
# Inventory

cur.execute("INSERT INTO store_inventory (name, quantity, cost) VALUES (?, ?, ?)",
            ('Flower Pin', 50, 15.00)
            )
cur.execute("INSERT INTO store_inventory (name, quantity, cost) VALUES (?, ?, ?)",
            ('Flower Earrings', 23, 20.99)
            )
cur.execute("INSERT INTO store_inventory (name, quantity, cost) VALUES (?, ?, ?)",
            ('Leaf Pin', 52, 15.00)
            )
cur.execute("INSERT INTO store_inventory (name, quantity, cost) VALUES (?, ?, ?)",
            ('Starry Patch', 45, 7.50)
            )
cur.execute("INSERT INTO store_inventory (name, quantity, cost) VALUES (?, ?, ?)",
            ('Starry Plush', 30, 45.99)
            )
cur.execute("INSERT INTO store_inventory (name, quantity, cost) VALUES (?, ?, ?)",
            ('Starry Notepad', 5, 8.99)
            )
cur.execute("INSERT INTO store_inventory (name, quantity, cost) VALUES (?, ?, ?)",
            ('Moon Notepad', 8, 8.99)
            )
cur.execute("INSERT INTO store_inventory (name, quantity, cost) VALUES (?, ?, ?)",
            ('Flower Set', 18, 30.00)
            )

cur.execute("INSERT INTO inventory_categories (name) VALUES (?)", ('Pin', ))
cur.execute("INSERT INTO inventory_categories (name) VALUES (?)", ('Patch', ))
cur.execute("INSERT INTO inventory_categories (name) VALUES (?)", ('Jewellery', ))
cur.execute("INSERT INTO inventory_categories (name) VALUES (?)", ('Stationery', ))

cur.execute("INSERT INTO inventory_to_category (tag_id, item_id) VALUES (?, ?)", (1, 1))
cur.execute("INSERT INTO inventory_to_category (tag_id, item_id) VALUES (?, ?)", (1, 3))
cur.execute("INSERT INTO inventory_to_category (tag_id, item_id) VALUES (?, ?)", (2, 4))
cur.execute("INSERT INTO inventory_to_category (tag_id, item_id) VALUES (?, ?)", (3, 2))
cur.execute("INSERT INTO inventory_to_category (tag_id, item_id) VALUES (?, ?)", (4, 6))
cur.execute("INSERT INTO inventory_to_category (tag_id, item_id) VALUES (?, ?)", (4, 7))
cur.execute("INSERT INTO inventory_to_category (tag_id, item_id) VALUES (?, ?)", (1, 8))
cur.execute("INSERT INTO inventory_to_category (tag_id, item_id) VALUES (?, ?)", (3, 8))

# Materials

cur.execute("INSERT INTO store_materials (name, quantity) VALUES (?, ?)",
            ('Earring Hooks', 90)
            )
cur.execute("INSERT INTO store_materials (name, quantity) VALUES (?, ?)",
            ('Backing Cards', 50)
            )
cur.execute("INSERT INTO store_materials (name, quantity) VALUES (?, ?)",
            ('Stamps', 32)
            )
cur.execute("INSERT INTO store_materials (name, quantity) VALUES (?, ?)",
            ('Envelopes', 3)
            )

cur.execute("INSERT INTO materials_categories (name) VALUES(?)", ('Mailing', ))

cur.execute("INSERT INTO material_to_category (tag_id, material_id) VALUES (?, ?)", (1, 3))
cur.execute("INSERT INTO material_to_category (tag_id, material_id) VALUES (?, ?)", (1, 4))

# Income

cur.execute("INSERT INTO store_income (name, amount, income_year, income_month, income_day) VALUES (?, ?, ?, ?, ?)",
            ('Etsy', 139.22, 2018, 4, 30)
            )
cur.execute("INSERT INTO store_income (name, amount, income_year, income_month, income_day) VALUES (?, ?, ?, ?, ?)",
            ('Etsy', 234.52, 2018, 6, 30)
            )
cur.execute("INSERT INTO store_income (name, amount, income_year, income_month, income_day) VALUES (?, ?, ?, ?, ?)",
            ('Artist Con', 3210.14, 2018, 6, 5)
            )
cur.execute("INSERT INTO store_income (name, amount, income_year, income_month, income_day) VALUES (?, ?, ?, ?, ?)",
            ('ABC Company', 420.90, 2018, 9, 21)
            )

cur.execute("INSERT INTO income_categories (name) VALUES(?)", ('Online Store', ))
cur.execute("INSERT INTO income_categories (name) VALUES(?)", ('Convention', ))
cur.execute("INSERT INTO income_categories (name) VALUES(?)", ('Wholesale Order', ))

cur.execute("INSERT INTO income_to_category (tag_id, income_id) VALUES (?, ?)", (1, 1))
cur.execute("INSERT INTO income_to_category (tag_id, income_id) VALUES (?, ?)", (1, 2))
cur.execute("INSERT INTO income_to_category (tag_id, income_id) VALUES (?, ?)", (2, 3))
cur.execute("INSERT INTO income_to_category (tag_id, income_id) VALUES (?, ?)", (3, 4))

# Expenses

cur.execute("INSERT INTO store_expenses (name, amount, expense_year, expense_month, expense_day) VALUES (?, ?, ?, ?, ?)",
            ('Artist Con Spot', 120.00, 2018, 1, 2)
            )
cur.execute("INSERT INTO store_expenses (name, amount, expense_year, expense_month, expense_day) VALUES (?, ?, ?, ?, ?)",
            ('Stamps', 50.99, 2018, 1, 5)
            )
cur.execute("INSERT INTO store_expenses (name, amount, expense_year, expense_month, expense_day) VALUES (?, ?, ?, ?, ?)",
            ('Flower Pins', 220.19, 2017, 3, 16)
            )

cur.execute("INSERT INTO expenses_categories (name) VALUES(?)", ('Mailing', ))
cur.execute("INSERT INTO expenses_categories (name) VALUES(?)", ('Stock', ))
cur.execute("INSERT INTO expenses_categories (name) VALUES(?)", ('Conventions', ))

cur.execute("INSERT INTO expense_to_category (tag_id, expense_id) VALUES (?, ?)", (3, 1))
cur.execute("INSERT INTO expense_to_category (tag_id, expense_id) VALUES (?, ?)", (1, 2))
cur.execute("INSERT INTO expense_to_category (tag_id, expense_id) VALUES (?, ?)", (2, 3))


connection.commit()
connection.close()
