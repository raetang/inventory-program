import sqlite3
import sys
from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
from werkzeug.exceptions import abort

SORT_DEFAULT = 0
SORT_LOWEST_QUANTITY = 1
SORT_HIGHEST_QUANTITY = 2
SORT_LOWEST_PRICE = 3
SORT_HIGHEST_PRICE = 4

MONTH_LIST = [0, 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

# Database Helper Functions

def get_db_connection():
    """ Returns a connection to the database """
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home Page Helper Functions

def get_inventory_reminders():
    conn = get_db_connection()
    inventory_reminder = conn.execute('SELECT * FROM store_inventory WHERE quantity <= (SELECT quantity FROM settings WHERE name = ?)', ("Reminder Quantity", )).fetchall()
    conn.close()
    return inventory_reminder

def get_materials_reminders():
    conn = get_db_connection()
    materials_reminder = conn.execute('SELECT * FROM store_materials WHERE quantity <= (SELECT quantity FROM settings WHERE name = ?)', ("Reminder Quantity", )).fetchall()
    conn.close()
    return materials_reminder

# Inventory Helper Functions

def get_inventory_items():
    """ Returns all items in store inventory """
    conn = get_db_connection()
    inventory_items = conn.execute('SELECT * FROM store_inventory').fetchall()
    conn.close()
    return inventory_items

def get_inventory_item(item_id):
    """ Returns an item in store inventory given item id """
    conn = get_db_connection()
    cur = conn.cursor()
    inventory_item = cur.execute('SELECT * FROM store_inventory WHERE item_id = ?', (item_id,)).fetchone()
    conn.close()
    return inventory_item

def get_inventory_categories():
    """ Returns all store inventory categories """
    conn = get_db_connection()
    cur = conn.cursor()
    inventory_categories = cur.execute('SELECT * FROM inventory_categories').fetchall()
    conn.close()
    return inventory_categories

def get_inventory_categories_list():
    """ Returns a list of all store inventory categories """
    inventory_categories = get_inventory_categories()
    inventory_categories_list = []
    for category in inventory_categories:
        inventory_categories_list.append(category['tag_id'])
    return inventory_categories_list

def get_inventory_connections():
    """ Returns all connections of item and category in store inventory """
    conn = get_db_connection()
    cur = conn.cursor()
    inventory_connections = cur.execute('SELECT * FROM inventory_to_category').fetchall()
    conn.close()
    return inventory_connections

def get_inventory_item_connections_list(item_id):
    """ Returns a list of all connections to one store inventory item given item id """
    conn = get_db_connection()
    cur = conn.cursor()
    inventory_item_connections = cur.execute('SELECT * FROM inventory_to_category WHERE item_id = ?', (item_id, )).fetchall()
    conn.close()
    inventory_item_connections_list = []
    for connection in inventory_item_connections:
        inventory_item_connections_list.append(connection['tag_id'])
    return inventory_item_connections_list

def get_inventory_category_connections(category_id):
    """ Returns all connections to one store inventory category given category id """
    conn = get_db_connection()
    cur = conn.cursor()
    inventory_category_connections = cur.execute('SELECT * FROM inventory_categories WHERE tag_id = ?', (category_id, )).fetchone()
    conn.close()
    return inventory_category_connections

def create_inventory_item(name, quantity, cost, categories):
    conn = get_db_connection()
    cur = conn.cursor()
    item_id = cur.execute('INSERT INTO store_inventory (name, quantity, cost) VALUES (?, ?, ?)', (name, quantity, cost)).lastrowid
    assign_categories_to_inventory_item(cur, categories, item_id)
    conn.commit()
    conn.close()

def assign_categories_to_inventory_item(cur, categories, item_id):
    for category in categories:
        cur.execute('INSERT INTO inventory_to_category (tag_id, item_id) VALUES (?, ?)', (category, item_id))

# Materials Helper Functions

def get_materials_items():
    """ Returns all items in store materials """
    conn = get_db_connection()
    materials_items = conn.execute('SELECT * FROM store_materials').fetchall()
    conn.close()
    return materials_items

def get_materials_item(material_id):
    """ Returns an item in store materials given material id """
    conn = get_db_connection()
    cur = conn.cursor()
    materials_item = cur.execute('SELECT * FROM store_materials WHERE material_id = ?', (material_id,)).fetchone()
    conn.close()
    return materials_item

def get_materials_categories():
    """ Returns all store materials categories """
    conn = get_db_connection()
    cur = conn.cursor()
    materials_categories = cur.execute('SELECT * FROM materials_categories').fetchall()
    conn.close()
    return materials_categories

def get_materials_categories_list():
    """ Returns a list of all store materials categories """
    materials_categories = get_materials_categories()
    materials_categories_list = []
    for category in materials_categories:
        materials_categories_list.append(category['tag_id'])
    return materials_categories_list

def get_materials_connections():
    """ Returns all connections of item and category in store materials """
    conn = get_db_connection()
    cur = conn.cursor()
    materials_connections = cur.execute('SELECT * FROM material_to_category').fetchall()
    conn.close()
    return materials_connections

def get_materials_item_connections_list(material_id):
    """ Returns a list of all connections to one store materials item given material id """
    conn = get_db_connection()
    cur = conn.cursor()
    materials_item_connections = cur.execute('SELECT * FROM material_to_category WHERE material_id = ?', (material_id, )).fetchall()
    conn.close()
    materials_item_connections_list = []
    for connection in materials_item_connections:
        materials_item_connections_list.append(connection['tag_id'])
    return materials_item_connections_list

def get_materials_category_connections(category_id):
    """ Returns all connections to one store materials category given category id """
    conn = get_db_connection()
    cur = conn.cursor()
    materials_category_connections = cur.execute('SELECT * FROM materials_categories WHERE tag_id = ?', (category_id, )).fetchone()
    conn.close()
    return materials_category_connections

def create_materials_item(name, quantity, categories):
    conn = get_db_connection()
    cur = conn.cursor()
    material_id = cur.execute('INSERT INTO store_materials (name, quantity) VALUES (?, ?)', (name, quantity)).lastrowid
    assign_categories_to_materials_item(cur, categories, material_id)
    conn.commit()
    conn.close()

def assign_categories_to_materials_item(cur, categories, material_id):
    for category in categories:
        cur.execute('INSERT INTO material_to_category (tag_id, material_id) VALUES (?, ?)', (category, material_id))

# Income Helper Functions

def get_income_items():
    """ Returns all items in store income as a list of lists organized by year, then month and day"""
    return organize_income(0, 0)

def organize_income(category_id, search_date, search_by=None):
    """ Returns a list of lists of income items organized by year, then month and day """
    conn = get_db_connection()
    cur = conn.cursor()

    if search_by:
        # a search phrase
        if category_id == 0:
            # no category was selected
            if search_date == 0:
                # no date was selected
                income_items = cur.execute('SELECT * FROM store_income WHERE name LIKE "%"||?||"%" ORDER BY income_year, income_month, income_day',
                                           (search_by,)).fetchall()
            else:
                income_items = cur.execute(
                    'SELECT * FROM store_income WHERE (income_year = ?) AND (name LIKE "%"||?||"%") ORDER BY income_year, income_month, income_day',
                    (search_date, search_by)).fetchall()
        else:
            # a category was selected
            if search_date == 0:
                # no date was selected
                income_items = cur.execute(
                    'SELECT * FROM store_income WHERE income_id IN (SELECT income_id FROM income_to_category WHERE tag_id = ?) AND name LIKE "%"||?||"%" ORDER BY income_year, income_month, income_day',
                    (category_id, search_by)).fetchall()
            else:
                # a date was selected
                income_items = cur.execute(
                    'SELECT * FROM store_income WHERE income_id IN (SELECT income_id FROM income_to_category WHERE tag_id = ?) AND income_year = ? AND name LIKE "%"||?||"%" ORDER BY income_year, income_month, income_day',
                    (category_id, search_date, search_by)).fetchall()
    else:
        # no search phrase
        if category_id == 0:
            # no category was selected
            if search_date == 0:
                # no date was selected
                income_items = cur.execute('SELECT * FROM store_income ORDER BY income_year, income_month, income_day').fetchall()
            else:
                # a date was selected
                income_items = cur.execute('SELECT * FROM store_income WHERE income_year = ? ORDER BY income_year, income_month, income_day',
                                           (search_date,)).fetchall()
        else:
            # a category was selected
            if search_date == 0:
                # no date was selected
                income_items = cur.execute(
                    'SELECT * FROM store_income WHERE income_id IN (SELECT income_id FROM income_to_category WHERE tag_id = ?) ORDER BY income_year, income_month, income_day',
                    (category_id,)).fetchall()
            else:
                # a date was selected
                income_items = cur.execute(
                    'SELECT * FROM store_income WHERE (income_id IN (SELECT income_id FROM income_to_category WHERE tag_id = ?)) AND (income_year = ?) ORDER BY income_year, income_month, income_day',
                    (category_id, search_date)).fetchall()

    conn.close()

    income_list_by_year = []
    temp = []
    if income_items:
        year = income_items[0]['income_year']
        for item in income_items:
            if item['income_year'] == year:
                temp.append(item)
            else:
                income_list_by_year.append(temp)
                temp = []
                year = item['income_year']
                temp.append(item)
    if temp:
        income_list_by_year.append(temp)
    return income_list_by_year

def get_income_item(income_id):
    """ Returns an item in store income given income id """
    conn = get_db_connection()
    cur = conn.cursor()
    income_item = cur.execute('SELECT * FROM store_income WHERE income_id = ?', (income_id,)).fetchone()
    conn.close()
    return income_item

def get_income_categories():
    """ Returns all store income categories """
    conn = get_db_connection()
    cur = conn.cursor()
    income_categories = cur.execute('SELECT * FROM income_categories').fetchall()
    conn.close()
    return income_categories

def get_income_categories_list():
    """ Returns a list of all store income categories """
    conn = get_db_connection()
    cur = conn.cursor()
    income_categories = cur.execute('SELECT * FROM income_categories').fetchall()
    conn.close()
    income_categories_list = []
    for category in income_categories:
        income_categories_list.append(category['tag_id'])
    return income_categories_list

def get_income_connections():
    """ Returns all connections of item and category in store income """
    conn = get_db_connection()
    cur = conn.cursor()
    income_connections = cur.execute('SELECT * FROM income_to_category').fetchall()
    conn.close()
    return income_connections

def get_income_item_connections_list(income_id):
    """ Returns a list of all connections to one store income item given income id """
    conn = get_db_connection()
    cur = conn.cursor()
    income_connections = cur.execute('SELECT * FROM income_to_category WHERE income_id = ?', (income_id, )).fetchall()
    conn.close()
    income_connection_list = []
    for connection in income_connections:
        income_connection_list.append(connection['tag_id'])
    return income_connection_list

def get_income_category_connections(category_id):
    """ Returns all connections to one store income category given category id """
    conn = get_db_connection()
    cur = conn.cursor()
    income_category_connections = cur.execute('SELECT * FROM income_categories WHERE tag_id = ?', (category_id, )).fetchone()
    conn.close()
    return income_category_connections

def create_income_item(name, amount, income_year, income_month, income_day, categories):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO store_income (name, amount, income_year, income_month, income_day) VALUES (?, ?, ?, ?, ?)', (name, amount, income_year, income_month, income_day))
    income_id = cur.lastrowid
    assign_categories_to_income_item(cur, categories, income_id)
    conn.commit()
    conn.close()

def assign_categories_to_income_item(cur, categories, income_id):
    for category in categories:
        cur.execute('INSERT INTO income_to_category (tag_id, income_id) VALUES (?, ?)', (category, income_id))

# Expenses Helper Functions

def get_expenses_items():
    """ Returns all items in store expenses as a list of lists organized by year, then month and day"""
    return organize_expenses(0, 0)

def organize_expenses(category_id, search_date, search_by=None):
    """ Returns a list of lists of expenses items organized by year, then month and day """
    conn = get_db_connection()
    cur = conn.cursor()

    if search_by:
        # a search phrase
        if category_id == 0:
            # no category was selected
            if search_date == 0:
                # no date was selected
                expenses_items = cur.execute('SELECT * FROM store_expenses WHERE name LIKE "%"||?||"%" ORDER BY expense_year, expense_month, expense_day',
                                           (search_by,)).fetchall()
            else:
                expenses_items = cur.execute(
                    'SELECT * FROM store_expenses WHERE (expense_year = ?) AND (name LIKE "%"||?||"%") ORDER BY expense_year, expense_month, expense_day',
                    (search_date, search_by)).fetchall()
        else:
            # a category was selected
            if search_date == 0:
                # no date was selected
                expenses_items = cur.execute(
                    'SELECT * FROM store_expenses WHERE expense_id IN (SELECT expense_id FROM expense_to_category WHERE tag_id = ?) AND name LIKE "%"||?||"%" ORDER BY expense_year, expense_month, expense_day',
                    (category_id, search_by)).fetchall()
            else:
                # a date was selected
                expenses_items = cur.execute(
                    'SELECT * FROM store_expenses WHERE expense_id IN (SELECT expense_id FROM expense_to_category WHERE tag_id = ?) AND expense_year = ? AND name LIKE "%"||?||"%" ORDER BY expense_year, expense_month, expense_day',
                    (category_id, search_date, search_by)).fetchall()
    else:
        # no search phrase
        if category_id == 0:
            # no category was selected
            if search_date == 0:
                # no date was selected
                expenses_items = cur.execute('SELECT * FROM store_expenses ORDER BY expense_year, expense_month, expense_day').fetchall()
            else:
                # a date was selected
                expenses_items = cur.execute('SELECT * FROM store_expenses WHERE expense_year = ? ORDER BY expense_year, expense_month, expense_day',
                                           (search_date,)).fetchall()
        else:
            # a category was selected
            if search_date == 0:
                # no date was selected
                expenses_items = cur.execute(
                    'SELECT * FROM store_expenses WHERE expense_id IN (SELECT expense_id FROM expense_to_category WHERE tag_id = ?) ORDER BY expense_year, expense_month, expense_day',
                    (category_id,)).fetchall()
            else:
                # a date was selected
                expenses_items = cur.execute(
                    'SELECT * FROM store_expenses WHERE (expense_id IN (SELECT expense_id FROM expense_to_category WHERE tag_id = ?)) AND (expense_year = ?) ORDER BY expense_year, expense_month, expense_day',
                    (category_id, search_date)).fetchall()

    conn.close()

    expenses_list_by_year = []
    temp = []
    if expenses_items:
        year = expenses_items[0]['expense_year']
        for item in expenses_items:
            if item['expense_year'] == year:
                temp.append(item)
            else:
                expenses_list_by_year.append(temp)
                temp = []
                year = item['expense_year']
                temp.append(item)
    if temp:
        expenses_list_by_year.append(temp)
    return expenses_list_by_year

def get_expenses_item(expense_id):
    """ Returns an item in store expenses given expense id """
    conn = get_db_connection()
    cur = conn.cursor()
    expenses_item = cur.execute('SELECT * FROM store_expenses WHERE expense_id = ?', (expense_id,)).fetchone()
    conn.close()
    return expenses_item

def get_expenses_categories():
    """ Returns all store expenses categories """
    conn = get_db_connection()
    cur = conn.cursor()
    expenses_categories = cur.execute('SELECT * FROM expenses_categories').fetchall()
    conn.close()
    return expenses_categories

def get_expenses_categories_list():
    """ Returns a list of all store expenses categories """
    conn = get_db_connection()
    cur = conn.cursor()
    expenses_categories = cur.execute('SELECT * FROM expenses_categories').fetchall()
    conn.close()
    expenses_categories_list = []
    for category in expenses_categories:
        expenses_categories_list.append(category['tag_id'])
    return expenses_categories_list

def get_expenses_connections():
    """ Returns all connections of item and category in store expenses """
    conn = get_db_connection()
    cur = conn.cursor()
    expenses_connections = cur.execute('SELECT * FROM expense_to_category').fetchall()
    conn.close()
    return expenses_connections

def get_expenses_item_connections_list(expense_id):
    """ Returns a list of all connections to one store expenses item given expense id """
    conn = get_db_connection()
    cur = conn.cursor()
    expenses_connections = cur.execute('SELECT * FROM expense_to_category WHERE expense_id = ?', (expense_id, )).fetchall()
    conn.close()
    expenses_connection_list = []
    for connection in expenses_connections:
        expenses_connection_list.append(connection['tag_id'])
    return expenses_connection_list

def get_expenses_category_connections(category_id):
    """ Returns all connections to one store expenses category given category id """
    conn = get_db_connection()
    cur = conn.cursor()
    expenses_category_connections = cur.execute('SELECT * FROM expenses_categories WHERE tag_id = ?', (category_id, )).fetchone()
    conn.close()
    return expenses_category_connections

def create_expenses_item(name, amount, expense_year, expense_month, expense_day, categories):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO store_expenses (name, amount, expense_year, expense_month, expense_day) VALUES (?, ?, ?, ?, ?)', (name, amount, expense_year, expense_month, expense_day))
    expense_id = cur.lastrowid
    assign_categories_to_expenses_item(cur, categories, expense_id)
    conn.commit()
    conn.close()

def assign_categories_to_expenses_item(cur, categories, expense_id):
    for category in categories:
        cur.execute('INSERT INTO expense_to_category (tag_id, expense_id) VALUES (?, ?)', (category, expense_id))

# Helper functions

def str_to_int_list(list_of_str):
    list_of_int = []
    for item in list_of_str:
        list_of_int.append(int(item))
    return list_of_int


app = Flask(__name__)
app.config['SECRET_KEY'] = 'l\xc0q\x9b\xe9U\x86\xaf\xc4p\xc2W\xe1\xac\x0c\x0b\x986N\xa4\x97\x89\xe5\xf6b'

#Home Routes

@app.route('/', methods=('GET',))
def home():
    inventory_categories = get_inventory_categories()
    inventory_connections = get_inventory_connections()
    inventory_reminders = get_inventory_reminders()

    materials_categories = get_materials_categories()
    materials_connections = get_materials_connections()
    materials_reminders = get_materials_reminders()
    return render_template('home_view.html', inventory_reminders=inventory_reminders, inventory_categories=inventory_categories, inventory_connections=inventory_connections, materials_categories=materials_categories, materials_connections=materials_connections, materials_reminders=materials_reminders)

@app.route('/inventory_edit_item/<int:item_id>', methods=('GET', 'POST'))
def home_inventory_edit_item(item_id):
    item = get_inventory_item(item_id)
    inventory_categories = get_inventory_categories()
    inventory_item_category_connections = get_inventory_item_connections_list(item_id)
    inventory_categories_list = get_inventory_categories_list()

    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        cost = request.form['cost']
        categories = str_to_int_list(request.form.getlist('category-id'))

        if not name:
            flash('Name is required.')
        elif not quantity:
            flash('Quantity is required.')
        elif not cost:
            flash('Cost is required.')
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('UPDATE store_inventory SET name = ?, quantity = ?, cost = ? WHERE item_id = ?', (name, quantity, cost, item_id))
            # for categories, check that all connections for no longer checked categories are deleted, and create new connections for categories that have not been selected yet


            for category in inventory_categories_list:
                if category in categories and category not in inventory_item_category_connections:
                        cur.execute('INSERT INTO inventory_to_category (tag_id, item_id) VALUES (?, ?)',
                                    (category, item_id))
                elif category not in categories and category in inventory_item_category_connections:
                        cur.execute('DELETE FROM inventory_to_category WHERE tag_id = ? AND item_id = ?', (category, item_id))

            conn.commit()
            conn.close()
            return redirect(url_for('home'))

    return render_template('home_inventory_edit_item.html', item=item, inventory_categories=inventory_categories, inventory_item_category_connections=inventory_item_category_connections)

@app.route('/inventory_delete_item/<int:item_id>', methods=('POST', ))
def home_inventory_delete_item(item_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM store_inventory WHERE item_id = ?', (item_id, ))
    conn.commit()
    conn.close()
    flash('Successfully deleted')
    return redirect(url_for('home'))

@app.route('/materials_edit_item/<int:material_id>', methods=('GET', 'POST'))
def home_materials_edit_item(material_id):
    item = get_materials_item(material_id)
    materials_categories = get_materials_categories()
    materials_item_category_connections = get_materials_item_connections_list(material_id)
    materials_categories_list = get_materials_categories_list()

    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        categories = str_to_int_list(request.form.getlist('category-id'))

        if not name:
            flash('Name is required.')
        elif not quantity:
            flash('Quantity is required.')
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('UPDATE store_materials SET name = ?, quantity = ? WHERE material_id = ?', (name, quantity, material_id))
            # for categories, check that all connections for no longer checked categories are deleted, and create new connections for categories that have not been selected yet


            for category in materials_categories_list:
                if category in categories and category not in materials_item_category_connections:
                        cur.execute('INSERT INTO material_to_category (tag_id, material_id) VALUES (?, ?)',
                                    (category, material_id))
                elif category not in categories and category in materials_item_category_connections:
                        cur.execute('DELETE FROM material_to_category WHERE tag_id = ? AND material_id = ?', (category, material_id))

            conn.commit()
            conn.close()
            return redirect(url_for('home'))

    return render_template('home_materials_edit_item.html', item=item, materials_categories=materials_categories, materials_item_category_connections=materials_item_category_connections)

@app.route('/materials_delete_item/<int:material_id>', methods=('POST', ))
def home_materials_delete_item(material_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM store_materials WHERE material_id = ?', (material_id, ))
    conn.commit()
    conn.close()
    flash('Successfully deleted')
    return redirect(url_for('home'))

#Inventory Routes

@app.route('/inventory', methods=('POST', 'GET'))
def inventory():
    inventory_categories = get_inventory_categories()
    inventory_connections = get_inventory_connections()
    inventory_items = get_inventory_items()

    if request.method == 'POST':
        category_id = request.form['category-search']
        sort = request.form['sort-search']
        # search was clicked
        if request.form['search-by']:
            # search bar is not empty
            search_by = request.form['search-by']
            return redirect(url_for('inventory_search_phrase', category_id=category_id, sort=sort, search_by=search_by ))
        else:
            return redirect(url_for('inventory_search_all', category_id=category_id, sort=sort))

    return render_template('inventory_view.html', inventory_items=inventory_items, inventory_categories=inventory_categories, inventory_connections=inventory_connections, selected_inventory_category=0, sort_order=0)

# Search button was pressed and search bar was empty
@app.route('/inventory/search/<int:category_id>/<int:sort>', methods=('GET', 'POST'))
def inventory_search_all(category_id, sort):
    inventory_categories = get_inventory_categories()
    inventory_connections = get_inventory_connections()

    conn = get_db_connection()
    cur = conn.cursor()

    if category_id == 0:
        # no category was selected
        if sort == 0:
            inventory_items = cur.execute('SELECT * FROM store_inventory').fetchall()
        elif sort == 1:
            inventory_items = cur.execute('SELECT * FROM store_inventory ORDER BY quantity ASC').fetchall()
        elif sort == 2:
            inventory_items = cur.execute('SELECT * FROM store_inventory ORDER BY quantity DESC').fetchall()
        elif sort == 3:
            inventory_items = cur.execute('SELECT * FROM store_inventory ORDER BY cost ASC').fetchall()
        else:
            inventory_items = cur.execute('SELECT * FROM store_inventory ORDER BY cost DESC').fetchall()
    else:
        # a category was selected
        if sort == 0:
            inventory_items = cur.execute(
                'SELECT * FROM store_inventory WHERE item_id IN (SELECT item_id FROM inventory_to_category WHERE tag_id = ?)',
                (category_id,)).fetchall()
        elif sort == 1:
            inventory_items = cur.execute(
                'SELECT * FROM store_inventory WHERE item_id IN (SELECT item_id FROM inventory_to_category WHERE tag_id = ?) ORDER BY quantity ASC',
                (category_id,)).fetchall()
        elif sort == 2:
            inventory_items = cur.execute(
                'SELECT * FROM store_inventory WHERE item_id IN (SELECT item_id FROM inventory_to_category WHERE tag_id = ?) ORDER BY quantity DESC',
                (category_id,)).fetchall()
        elif sort == 3:
            inventory_items = cur.execute(
                'SELECT * FROM store_inventory WHERE item_id IN (SELECT item_id FROM inventory_to_category WHERE tag_id = ?) ORDER BY cost ASC',
                (category_id,)).fetchall()
        else:
            inventory_items = cur.execute(
                'SELECT * FROM store_inventory WHERE item_id IN (SELECT item_id FROM inventory_to_category WHERE tag_id = ?) ORDER BY cost DESC',
                (category_id,)).fetchall()

    conn.close()

    if request.method == 'POST':
        # search was clicked
        category_id = request.form['category-search']
        sort = request.form['sort-search']
        if request.form['search-by']:
            # search bar is not empty
            search_by = request.form['search-by']
            return redirect(url_for('inventory_search_phrase', category_id=category_id, sort=sort, search_by = search_by ))
        else:
            return redirect(url_for('inventory_search_all', category_id=category_id, sort=sort))

    return render_template('inventory_view.html', inventory_items=inventory_items, inventory_categories=inventory_categories,inventory_connections=inventory_connections, selected_inventory_category=category_id, sort_order=sort)

# Search button was pressed and search bar had a phrase
@app.route('/inventory/search/<int:category_id>/<int:sort>/<string:search_by>', methods=('GET', 'POST'))
def inventory_search_phrase(category_id, sort, search_by):
    inventory_categories = get_inventory_categories()
    inventory_connections = get_inventory_connections()

    conn = get_db_connection()
    cur = conn.cursor()

    if category_id == 0:
        # no category was selected
        if sort == 0:
            inventory_items = cur.execute('SELECT * FROM store_inventory WHERE name LIKE "%"||?||"%"', (search_by, )).fetchall()
        elif sort == 1:
            inventory_items = cur.execute('SELECT * FROM store_inventory WHERE name LIKE "%"||?||"%" ORDER BY quantity ASC', (search_by, )).fetchall()
        elif sort == 2:
            inventory_items = cur.execute('SELECT * FROM store_inventory WHERE name LIKE "%"||?||"%" ORDER BY quantity DESC', (search_by, )).fetchall()
        elif sort == 3:
            inventory_items = cur.execute('SELECT * FROM store_inventory WHERE name LIKE "%"||?||"%" ORDER BY cost ASC', (search_by, )).fetchall()
        else:
            inventory_items = cur.execute('SELECT * FROM store_inventory WHERE name LIKE "%"||?||"%" ORDER BY cost DESC', (search_by, )).fetchall()
    else:
        # a category was selected
        if sort == 0:
            inventory_items = cur.execute(
                'SELECT * FROM store_inventory WHERE item_id IN (SELECT item_id FROM inventory_to_category WHERE tag_id = ?) AND name LIKE "%"||?||"%" ',
                (category_id, search_by)).fetchall()
        elif sort == 1:
            inventory_items = cur.execute(
                'SELECT * FROM store_inventory WHERE item_id IN (SELECT item_id FROM inventory_to_category WHERE tag_id = ?) AND name LIKE "%"||?||"%" ORDER BY quantity ASC',
                (category_id, search_by)).fetchall()
        elif sort == 2:
            inventory_items = cur.execute(
                'SELECT * FROM store_inventory WHERE item_id IN (SELECT item_id FROM inventory_to_category WHERE tag_id = ?) AND name LIKE "%"||?||"%" ORDER BY quantity DESC',
                (category_id, search_by)).fetchall()
        elif sort == 3:
            inventory_items = cur.execute(
                'SELECT * FROM store_inventory WHERE item_id IN (SELECT item_id FROM inventory_to_category WHERE tag_id = ?) AND name LIKE "%"||?||"%" ORDER BY cost ASC',
                (category_id, search_by)).fetchall()
        else:
            inventory_items = cur.execute(
                'SELECT * FROM store_inventory WHERE item_id IN (SELECT item_id FROM inventory_to_category WHERE tag_id = ?) AND name LIKE "%"||?||"%" ORDER BY cost DESC',
                (category_id, search_by)).fetchall()

    conn.close()

    if request.method == 'POST':
        # search was clicked
        category_id = request.form['category-search']
        sort = request.form['sort-search']
        if request.form['search-by']:
            # search bar is not empty
            search_by = request.form['search-by']
            return redirect(url_for('inventory_search_phrase', category_id=category_id, sort=sort, search_by = search_by ))
        else:
            return redirect(url_for('inventory_search_all', category_id=category_id, sort=sort))

    return render_template('inventory_view.html', inventory_items=inventory_items, inventory_categories=inventory_categories, inventory_connections=inventory_connections, selected_inventory_category=category_id, sort_order=sort)

@app.route('/inventory/item_decrease_quantity', methods=('POST', ))
def inventory_item_decrease_quantity():

    item_id = request.form['item_id']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE store_inventory SET quantity = quantity - 1 WHERE item_id = ? AND quantity > 0', (item_id,))
    quantity = cur.execute('SELECT quantity FROM store_inventory WHERE item_id = ?', (item_id,)).fetchone()[0]
    conn.commit()
    conn.close()

    return jsonify({'quantity': quantity})

@app.route('/inventory/item_increase_quantity', methods=('POST', ))
def inventory_item_increase_quantity():
    item_id = request.form['item_id']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE store_inventory SET quantity = quantity + 1 WHERE item_id = ?', (item_id,))
    quantity = cur.execute('SELECT quantity FROM store_inventory WHERE item_id = ?', (item_id,)).fetchone()[0]
    conn.commit()
    conn.close()

    return jsonify({'quantity': quantity})

@app.route('/inventory/add_item', methods=('GET', 'POST'))
def inventory_add_item():
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        cost = request.form['cost']
        categories = str_to_int_list(request.form.getlist('category-id'))

        if not name:
            flash('Name is required.')
        elif not quantity:
            flash('Quantity is required.')
        elif not cost:
            flash('Cost is required.')
        else:
            create_inventory_item(name, quantity, cost, categories)
            return redirect(url_for('inventory'))

    inventory_categories = get_inventory_categories()

    return render_template('inventory_add_item.html', inventory_categories=inventory_categories)

@app.route('/inventory/edit_item/<int:item_id>', methods=('GET', 'POST'))
def inventory_edit_item(item_id):
    item = get_inventory_item(item_id)
    inventory_categories = get_inventory_categories()
    inventory_item_category_connections = get_inventory_item_connections_list(item_id)
    inventory_categories_list = get_inventory_categories_list()

    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        cost = request.form['cost']
        categories = str_to_int_list(request.form.getlist('category-id'))

        if not name:
            flash('Name is required.')
        elif not quantity:
            flash('Quantity is required.')
        elif not cost:
            flash('Cost is required.')
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('UPDATE store_inventory SET name = ?, quantity = ?, cost = ? WHERE item_id = ?', (name, quantity, cost, item_id))
            # for categories, check that all connections for no longer checked categories are deleted, and create new connections for categories that have not been selected yet


            for category in inventory_categories_list:
                if category in categories and category not in inventory_item_category_connections:
                        cur.execute('INSERT INTO inventory_to_category (tag_id, item_id) VALUES (?, ?)',
                                    (category, item_id))
                elif category not in categories and category in inventory_item_category_connections:
                        cur.execute('DELETE FROM inventory_to_category WHERE tag_id = ? AND item_id = ?', (category, item_id))

            conn.commit()
            conn.close()
            return redirect(url_for('inventory'))

    return render_template('inventory_edit_item.html', item=item, inventory_categories=inventory_categories, inventory_item_category_connections=inventory_item_category_connections)

@app.route('/inventory/delete_item/<int:item_id>', methods=('POST', ))
def inventory_delete_item(item_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM store_inventory WHERE item_id = ?', (item_id, ))
    conn.commit()
    conn.close()
    flash('Successfully deleted')
    return redirect(url_for('inventory'))

@app.route('/inventory/edit_categories', methods=('GET', 'POST'))
def inventory_edit_categories():
    inventory_categories = get_inventory_categories()
    if request.method == 'POST':
        if 'new_category' in request.form:
            new_category = request.form['new_category']
            if not new_category:
                flash('Category name is required')
            else:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute('INSERT INTO inventory_categories (name) VALUES (?)', (new_category, ))
                conn.commit()
                conn.close()

            return redirect(url_for('inventory_edit_categories'))

    return render_template('inventory_edit_categories.html', inventory_categories=inventory_categories)

@app.route('/inventory/edit_category/<int:category_id>', methods=('POST', 'GET'))
def inventory_edit_category(category_id):
    category = get_inventory_category_connections(category_id)

    if request.method == 'POST':
        name = request.form['name']

        if not name:
            flash('Name is required.')
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('UPDATE inventory_categories SET name = ? WHERE tag_id = ?',
                         (name, category_id ))
            conn.commit()
            conn.close()
            return redirect(url_for('inventory_edit_categories'))

    return render_template('inventory_edit_category.html', category=category)

@app.route('/inventory/delete_category/<int:category_id>', methods=('POST', ))
def inventory_delete_category(category_id):
    conn = get_db_connection()
    cur = conn.cursor()
    # Delete all connections to that category
    cur.execute('DELETE FROM inventory_to_category WHERE tag_id = ?', (category_id, ))
    cur.execute('DELETE FROM inventory_categories WHERE tag_id = ?', (category_id, ))
    conn.commit()
    conn.close()
    flash('Successfully deleted')
    return redirect(url_for('inventory_edit_categories'))

#Materials Routes

@app.route('/materials', methods=('POST', 'GET'))
def materials():
    materials_categories = get_materials_categories()
    materials_connections = get_materials_connections()
    materials_items = get_materials_items()

    if request.method == 'POST':
        category_id = request.form['category-search']
        sort = request.form['sort-search']
        # search was clicked
        if request.form['search-by']:
            # search bar is not empty
            search_by = request.form['search-by']
            return redirect(url_for('materials_search_phrase', category_id=category_id, sort=sort, search_by=search_by ))
        else:
            return redirect(url_for('materials_search_all', category_id=category_id, sort=sort))

    return render_template('materials_view.html', materials_items=materials_items, materials_categories=materials_categories, materials_connections=materials_connections, selected_materials_category=0, sort_order=0)

# Search button was pressed and search bar was empty
@app.route('/materials/search/<int:category_id>/<int:sort>', methods=('GET', 'POST'))
def materials_search_all(category_id, sort):
    materials_categories = get_materials_categories()
    materials_connections = get_materials_connections()

    conn = get_db_connection()
    cur = conn.cursor()

    if category_id == 0:
        # no category was selected
        if sort == 0:
            materials_items = cur.execute('SELECT * FROM store_materials').fetchall()
        elif sort == 1:
            materials_items = cur.execute('SELECT * FROM store_materials ORDER BY quantity ASC').fetchall()
        else:
            materials_items = cur.execute('SELECT * FROM store_materials ORDER BY quantity DESC').fetchall()
    else:
        # a category was selected
        if sort == 0:
            materials_items = cur.execute(
                'SELECT * FROM store_materials WHERE material_id IN (SELECT material_id FROM material_to_category WHERE tag_id = ?)',
                (category_id,)).fetchall()
        elif sort == 1:
            materials_items = cur.execute(
                'SELECT * FROM store_materials WHERE material_id IN (SELECT material_id FROM material_to_category WHERE tag_id = ?) ORDER BY quantity ASC',
                (category_id,)).fetchall()
        else:
            materials_items = cur.execute(
                'SELECT * FROM store_materials WHERE material_id IN (SELECT material_id FROM material_to_category WHERE tag_id = ?) ORDER BY quantity DESC',
                (category_id,)).fetchall()

    conn.close()

    if request.method == 'POST':
        # search was clicked
        category_id = request.form['category-search']
        sort = request.form['sort-search']
        if request.form['search-by']:
            # search bar is not empty
            search_by = request.form['search-by']
            return redirect(url_for('materials_search_phrase', category_id=category_id, sort=sort, search_by = search_by ))
        else:
            return redirect(url_for('materials_search_all', category_id=category_id, sort=sort))

    return render_template('materials_view.html', materials_items=materials_items, materials_categories=materials_categories,materials_connections=materials_connections, selected_materials_category=category_id, sort_order=sort)

# Search button was pressed and search bar had a phrase
@app.route('/materials/search/<int:category_id>/<int:sort>/<string:search_by>', methods=('GET', 'POST'))
def materials_search_phrase(category_id, sort, search_by):
    materials_categories = get_materials_categories()
    materials_connections = get_materials_connections()

    conn = get_db_connection()
    cur = conn.cursor()

    if category_id == 0:
        # no category was selected
        if sort == 0:
            materials_items = cur.execute('SELECT * FROM store_materials WHERE name LIKE "%"||?||"%"', (search_by, )).fetchall()
        elif sort == 1:
            materials_items = cur.execute('SELECT * FROM store_materials WHERE name LIKE "%"||?||"%" ORDER BY quantity ASC', (search_by, )).fetchall()
        else:
            materials_items = cur.execute('SELECT * FROM store_materials WHERE name LIKE "%"||?||"%" ORDER BY quantity DESC', (search_by, )).fetchall()
    else:
        # a category was selected
        if sort == 0:
            materials_items = cur.execute(
                'SELECT * FROM store_materials WHERE material_id IN (SELECT material_id FROM material_to_category WHERE tag_id = ?) AND name LIKE "%"||?||"%" ',
                (category_id, search_by)).fetchall()
        elif sort == 1:
            materials_items = cur.execute(
                'SELECT * FROM store_materials WHERE material_id IN (SELECT material_id FROM material_to_category WHERE tag_id = ?) AND name LIKE "%"||?||"%" ORDER BY quantity ASC',
                (category_id, search_by)).fetchall()
        else:
            materials_items = cur.execute(
                'SELECT * FROM store_materials WHERE material_id IN (SELECT material_id FROM material_to_category WHERE tag_id = ?) AND name LIKE "%"||?||"%" ORDER BY quantity DESC',
                (category_id, search_by)).fetchall()

    conn.close()

    if request.method == 'POST':
        # search was clicked
        category_id = request.form['category-search']
        sort = request.form['sort-search']
        if request.form['search-by']:
            # search bar is not empty
            search_by = request.form['search-by']
            return redirect(url_for('materials_search_phrase', category_id=category_id, sort=sort, search_by = search_by ))
        else:
            return redirect(url_for('materials_search_all', category_id=category_id, sort=sort))

    return render_template('materials_view.html', materials_items=materials_items, materials_categories=materials_categories, materials_connections=materials_connections, selected_materials_category=category_id, sort_order=sort)

@app.route('/materials/item_decrease_quantity', methods=('POST', ))
def materials_item_decrease_quantity():
    material_id = request.form['material_id']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE store_materials SET quantity = quantity - 1 WHERE material_id = ? AND quantity > 0', (material_id,))
    quantity = cur.execute('SELECT quantity FROM store_materials WHERE material_id = ?', (material_id,)).fetchone()[0]
    conn.commit()
    conn.close()

    return jsonify({'quantity': quantity})

@app.route('/materials/item_increase_quantity', methods=('POST', ))
def materials_item_increase_quantity():
    material_id = request.form['material_id']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE store_materials SET quantity = quantity + 1 WHERE material_id = ?', (material_id,))
    quantity = cur.execute('SELECT quantity FROM store_materials WHERE material_id = ?', (material_id,)).fetchone()[0]
    conn.commit()
    conn.close()

    return jsonify({'quantity': quantity})

@app.route('/materials/add_item', methods=('GET', 'POST'))
def materials_add_item():
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        categories = str_to_int_list(request.form.getlist('category-id'))

        if not name:
            flash('Name is required.')
        elif not quantity:
            flash('Quantity is required.')
        else:
            create_materials_item(name, quantity, categories)
            return redirect(url_for('materials'))

    materials_categories = get_materials_categories()

    return render_template('materials_add_item.html', materials_categories=materials_categories)

@app.route('/materials/edit_item/<int:material_id>', methods=('GET', 'POST'))
def materials_edit_item(material_id):
    item = get_materials_item(material_id)
    materials_categories = get_materials_categories()
    materials_item_category_connections = get_materials_item_connections_list(material_id)
    materials_categories_list = get_materials_categories_list()

    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        categories = str_to_int_list(request.form.getlist('category-id'))

        if not name:
            flash('Name is required.')
        elif not quantity:
            flash('Quantity is required.')
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('UPDATE store_materials SET name = ?, quantity = ? WHERE material_id = ?', (name, quantity, material_id))
            # for categories, check that all connections for no longer checked categories are deleted, and create new connections for categories that have not been selected yet


            for category in materials_categories_list:
                if category in categories and category not in materials_item_category_connections:
                        cur.execute('INSERT INTO material_to_category (tag_id, material_id) VALUES (?, ?)',
                                    (category, material_id))
                elif category not in categories and category in materials_item_category_connections:
                        cur.execute('DELETE FROM material_to_category WHERE tag_id = ? AND material_id = ?', (category, material_id))

            conn.commit()
            conn.close()
            return redirect(url_for('materials'))

    return render_template('materials_edit_item.html', item=item, materials_categories=materials_categories, materials_item_category_connections=materials_item_category_connections)

@app.route('/materials/delete_item/<int:material_id>', methods=('POST', ))
def materials_delete_item(material_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM store_materials WHERE material_id = ?', (material_id, ))
    conn.commit()
    conn.close()
    flash('Successfully deleted')
    return redirect(url_for('materials'))

@app.route('/materials/edit_categories', methods=('GET', 'POST'))
def materials_edit_categories():
    materials_categories = get_materials_categories()
    if request.method == 'POST':
        if 'new_category' in request.form:
            new_category = request.form['new_category']
            if not new_category:
                flash('Category name is required')
            else:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute('INSERT INTO materials_categories (name) VALUES (?)', (new_category, ))
                conn.commit()
                conn.close()

            return redirect(url_for('materials_edit_categories'))

    return render_template('materials_edit_categories.html', materials_categories=materials_categories)

@app.route('/materials/edit_category/<int:category_id>', methods=('POST', 'GET'))
def materials_edit_category(category_id):
    category = get_materials_category_connections(category_id)

    if request.method == 'POST':
        name = request.form['name']

        if not name:
            flash('Name is required.')
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('UPDATE materials_categories SET name = ? WHERE tag_id = ?',
                         (name, category_id ))
            conn.commit()
            conn.close()
            return redirect(url_for('materials_edit_categories'))

    return render_template('materials_edit_category.html', category=category)

@app.route('/materials/delete_category/<int:category_id>', methods=('POST', ))
def materials_delete_category(category_id):
    conn = get_db_connection()
    cur = conn.cursor()
    # Delete all connections to that category
    cur.execute('DELETE FROM material_to_category WHERE tag_id = ?', (category_id, ))
    cur.execute('DELETE FROM materials_categories WHERE tag_id = ?', (category_id, ))
    conn.commit()
    conn.close()
    flash('Successfully deleted')
    return redirect(url_for('materials_edit_categories'))

#Income Routes
@app.route('/income', methods=('POST', 'GET'))
def income():
    income_categories = get_income_categories()
    income_connections = get_income_connections()
    income_items = get_income_items()
    income_items_filtered = organize_income(0, 0)

    if request.method == 'POST':
        category_id = request.form['category-search']
        search_date = request.form['date-search']
        if request.form['search-by']:
            # search bar is not empty
            search_by = request.form['search-by']
            return redirect(url_for('income_search_phrase', category_id=category_id, search_date=search_date, search_by = search_by ))
        else:
            return redirect(url_for('income_search_all', category_id=category_id, search_date=search_date))

    return render_template('income_view.html', month_list=MONTH_LIST, income_items=income_items, income_categories=income_categories, income_connections=income_connections, income_items_filtered=income_items_filtered)

# Search button was pressed and search bar was empty
@app.route('/income/search/<int:category_id>/<int:search_date>', methods=('GET', 'POST'))
def income_search_all(category_id, search_date):
    income_categories = get_income_categories()
    income_connections = get_income_connections()
    income_items = get_income_items()
    income_items_filtered = organize_income(category_id, search_date)

    if request.method == 'POST':
        category_id = request.form['category-search']
        search_date = request.form['date-search']
        if request.form['search-by']:
            # search bar is not empty
            search_by = request.form['search-by']
            return redirect(url_for('income_search_phrase', category_id=category_id, search_date=search_date, search_by = search_by ))
        else:
            return redirect(url_for('income_search_all', category_id=category_id, search_date=search_date))

    return render_template('income_view.html', month_list=MONTH_LIST, income_items=income_items, income_categories=income_categories,income_connections=income_connections, income_items_filtered=income_items_filtered, selected_income_category=category_id, selected_income_date=search_date)

# Search button was pressed and search bar had a phrase
@app.route('/income/search/<int:category_id>/<int:search_date>/<string:search_by>', methods=('GET', 'POST'))
def income_search_phrase(category_id, search_date, search_by):
    income_categories = get_income_categories()
    income_connections = get_income_connections()
    income_items = get_income_items()
    income_items_filtered = organize_income(category_id, search_date, search_by)

    if request.method == 'POST':
        category_id = request.form['category-search']
        search_date = request.form['date-search']
        if request.form['search-by']:
            # search bar is not empty
            search_by = request.form['search-by']
            return redirect(url_for('income_search_phrase', category_id=category_id, search_date=search_date, search_by = search_by ))
        else:
            return redirect(url_for('income_search_all', category_id=category_id, search_date=search_date))

    return render_template('income_view.html', month_list=MONTH_LIST, income_items=income_items, income_categories=income_categories, income_connections=income_connections, income_items_filtered=income_items_filtered, selected_income_category=category_id, selected_income_date=search_date)

@app.route('/income/add_new_income', methods=('GET', 'POST'))
def income_add_item():
    if request.method == 'POST':
        name = request.form['name']
        amount = request.form['amount']
        income_year = request.form['income-year']
        income_month = MONTH_LIST.index(request.form['income-month'])
        income_day = request.form['income-day']
        categories = str_to_int_list(request.form.getlist('category-id'))

        if not name:
            flash("Name is required")
        elif not amount:
            flash("Amount is required")
        elif not income_year:
            flash("Year is required")
        elif not income_month:
            flash("Month is required")
        elif not income_day:
            flash("Day is required")
        else:
            create_income_item(name, amount, income_year, income_month, income_day, categories)
            return redirect(url_for('income'))

    income_categories = get_income_categories()

    return render_template('income_add_item.html', income_categories=income_categories)

@app.route('/income/edit_income/<int:income_id>', methods=('GET', 'POST'))
def income_edit_item(income_id):
    item = get_income_item(income_id)
    income_categories = get_income_categories()
    income_item_connections = get_income_item_connections_list(income_id)
    income_categories_list = get_income_categories_list()

    if request.method == 'POST':
        name = request.form['name']
        amount = request.form['amount']
        income_year = request.form['income-year']
        income_month = MONTH_LIST.index(request.form['income-month'])
        income_day = request.form['income-day']
        categories = str_to_int_list(request.form.getlist('category-id'))

        if not name:
            flash("Name is required")
        elif not amount:
            flash("Amount is required")
        elif not income_year:
            flash("Year is required")
        elif not income_month:
            flash("Month is required")
        elif not income_day:
            flash("Day is required")
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('UPDATE store_income SET name = ?, amount = ?, income_year = ?, income_month = ?, income_day = ? WHERE income_id = ?', (name, amount, income_year, income_month, income_day, income_id))
            # for categories, check that all connections for no longer checked categories are deleted, and create new connections for categories that have not been selected yet


            for category in income_categories_list:
                if category in categories and category not in income_item_connections:
                        cur.execute('INSERT INTO income_to_category (tag_id, income_id) VALUES (?, ?)',
                                    (category, income_id))
                elif category not in categories and category in income_item_connections:
                        cur.execute('DELETE FROM income_to_category WHERE tag_id = ? AND income_id = ?', (category, income_id))

            conn.commit()
            conn.close()
            return redirect(url_for('income'))

    return render_template('income_edit_item.html', item=item, income_categories=income_categories, income_item_connections=income_item_connections)

@app.route('/income/delete_item/<int:income_id>', methods=('POST', ))
def income_delete_item(income_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM store_income WHERE income_id = ?', (income_id, ))
    conn.commit()
    conn.close()
    flash('Successfully deleted')
    return redirect(url_for('income'))

@app.route('/income/edit_categories', methods=('GET', 'POST'))
def income_edit_categories():
    income_categories = get_income_categories()
    if request.method == 'POST':
        if 'new_category' in request.form:
            new_category = request.form['new_category']
            if not new_category:
                flash('Category name is required')
            else:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute('INSERT INTO income_categories (name) VALUES (?)', (new_category, ))
                conn.commit()
                conn.close()

            return redirect(url_for('income_edit_categories'))

    return render_template('income_edit_categories.html', income_categories=income_categories)

@app.route('/income/edit_category/<int:category_id>', methods=('POST', 'GET'))
def income_edit_category(category_id):
    category = get_income_category_connections(category_id)

    if request.method == 'POST':
        name = request.form['name']

        if not name:
            flash('Name is required.')
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('UPDATE income_categories SET name = ? WHERE tag_id = ?',
                         (name, category_id ))
            conn.commit()
            conn.close()
            return redirect(url_for('income_edit_categories'))

    return render_template('income_edit_category.html', category=category)

@app.route('/income/delete_category/<int:category_id>', methods=('POST', ))
def income_delete_category(category_id):
    conn = get_db_connection()
    cur = conn.cursor()
    # Delete all connections to that category
    cur.execute('DELETE FROM income_to_category WHERE tag_id = ?', (category_id, ))
    cur.execute('DELETE FROM income_categories WHERE tag_id = ?', (category_id, ))
    conn.commit()
    conn.close()
    flash('Successfully deleted')
    return redirect(url_for('income_edit_categories'))

#Expenses Routes

@app.route('/expenses', methods=('POST', 'GET'))
def expenses():
    expenses_categories = get_expenses_categories()
    expenses_connections = get_expenses_connections()
    expenses_items = get_expenses_items()
    expenses_items_filtered = organize_expenses(0, 0)

    if request.method == 'POST':
        category_id = request.form['category-search']
        search_date = request.form['date-search']
        if request.form['search-by']:
            # search bar is not empty
            search_by = request.form['search-by']
            return redirect(url_for('expenses_search_phrase', category_id=category_id, search_date=search_date, search_by = search_by ))
        else:
            return redirect(url_for('expenses_search_all', category_id=category_id, search_date=search_date))

    return render_template('expenses_view.html', month_list=MONTH_LIST, expenses_items=expenses_items, expenses_categories=expenses_categories, expenses_connections=expenses_connections, expenses_items_filtered=expenses_items_filtered)

# Search button was pressed and search bar was empty
@app.route('/expenses/search/<int:category_id>/<int:search_date>', methods=('GET', 'POST'))
def expenses_search_all(category_id, search_date):
    expenses_categories = get_expenses_categories()
    expenses_connections = get_expenses_connections()
    expenses_items = get_expenses_items()
    expenses_items_filtered = organize_expenses(category_id, search_date)

    if request.method == 'POST':
        category_id = request.form['category-search']
        search_date = request.form['date-search']
        if request.form['search-by']:
            # search bar is not empty
            search_by = request.form['search-by']
            return redirect(url_for('expenses_search_phrase', category_id=category_id, search_date=search_date, search_by = search_by ))
        else:
            return redirect(url_for('expenses_search_all', category_id=category_id, search_date=search_date))

    return render_template('expenses_view.html', month_list=MONTH_LIST, expenses_items=expenses_items, expenses_categories=expenses_categories, expenses_connections=expenses_connections, expenses_items_filtered=expenses_items_filtered, selected_expenses_category=category_id, selected_expenses_date=search_date)

# Search button was pressed and search bar had a phrase
@app.route('/expenses/search/<int:category_id>/<int:search_date>/<string:search_by>', methods=('GET', 'POST'))
def expenses_search_phrase(category_id, search_date, search_by):
    expenses_categories = get_expenses_categories()
    expenses_connections = get_expenses_connections()
    expenses_items = get_expenses_items()
    expenses_items_filtered = organize_expenses(category_id, search_date, search_by)

    if request.method == 'POST':
        category_id = request.form['category-search']
        search_date = request.form['date-search']
        if request.form['search-by']:
            # search bar is not empty
            search_by = request.form['search-by']
            return redirect(url_for('expenses_search_phrase', category_id=category_id, search_date=search_date, search_by = search_by ))
        else:
            return redirect(url_for('expenses_search_all', category_id=category_id, search_date=search_date))

    return render_template('expenses_view.html', month_list=MONTH_LIST, expenses_items=expenses_items, expenses_categories=expenses_categories, expenses_connections=expenses_connections, expenses_items_filtered=expenses_items_filtered, selected_expenses_category=category_id, selected_expenses_date=search_date)

@app.route('/expenses/add_new_expense', methods=('GET', 'POST'))
def expenses_add_item():
    if request.method == 'POST':
        name = request.form['name']
        amount = request.form['amount']
        expense_year = request.form['expense-year']
        expense_month = MONTH_LIST.index(request.form['expense-month'])
        expense_day = request.form['expense-day']
        categories = str_to_int_list(request.form.getlist('category-id'))

        if not name:
            flash("Name is required")
        elif not amount:
            flash("Amount is required")
        elif not expense_year:
            flash("Year is required")
        elif not expense_month:
            flash("Month is required")
        elif not expense_day:
            flash("Day is required")
        else:
            create_expenses_item(name, amount, expense_year, expense_month, expense_day, categories)
            return redirect(url_for('expenses'))

    expenses_categories = get_expenses_categories()

    return render_template('expenses_add_item.html', expenses_categories=expenses_categories)

@app.route('/expenses/edit_expense/<int:expense_id>', methods=('GET', 'POST'))
def expenses_edit_item(expense_id):
    item = get_expenses_item(expense_id)
    expenses_categories = get_expenses_categories()
    expenses_item_connections = get_expenses_item_connections_list(expense_id)
    expenses_categories_list = get_expenses_categories_list()

    if request.method == 'POST':
        name = request.form['name']
        amount = request.form['amount']
        expense_year = request.form['expense-year']
        expense_month = MONTH_LIST.index(request.form['expense-month'])
        expense_day = request.form['expense-day']
        categories = str_to_int_list(request.form.getlist('category-id'))

        if not name:
            flash("Name is required")
        elif not amount:
            flash("Amount is required")
        elif not expense_year:
            flash("Year is required")
        elif not expense_month:
            flash("Month is required")
        elif not expense_day:
            flash("Day is required")
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('UPDATE store_expenses SET name = ?, amount = ?, expense_year = ?, expense_month = ?, expense_day = ? WHERE expense_id = ?', (name, amount, expense_year, expense_month, expense_day, expense_id))
            # for categories, check that all connections for no longer checked categories are deleted, and create new connections for categories that have not been selected yet


            for category in expenses_categories_list:
                if category in categories and category not in expenses_item_connections:
                        cur.execute('INSERT INTO expense_to_category (tag_id, expense_id) VALUES (?, ?)',
                                    (category, expense_id))
                elif category not in categories and category in expenses_item_connections:
                        cur.execute('DELETE FROM expense_to_category WHERE tag_id = ? AND expense_id = ?', (category, expense_id))

            conn.commit()
            conn.close()
            return redirect(url_for('expenses'))

    return render_template('expenses_edit_item.html', item=item, expenses_categories=expenses_categories, expenses_item_connections=expenses_item_connections)

@app.route('/expenses/delete_expense/<int:expense_id>', methods=('POST', ))
def expenses_delete_item(expense_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM store_expenses WHERE expense_id = ?', (expense_id, ))
    conn.commit()
    conn.close()
    flash('Successfully deleted')
    return redirect(url_for('expenses'))

@app.route('/expenses/edit_categories', methods=('GET', 'POST'))
def expenses_edit_categories():
    expenses_categories = get_expenses_categories()
    if request.method == 'POST':
        if 'new_category' in request.form:
            new_category = request.form['new_category']
            if not new_category:
                flash('Category name is required')
            else:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute('INSERT INTO expenses_categories (name) VALUES (?)', (new_category, ))
                conn.commit()
                conn.close()

            return redirect(url_for('expenses_edit_categories'))

    return render_template('expenses_edit_categories.html', expenses_categories=expenses_categories)

@app.route('/expenses/edit_category/<int:category_id>', methods=('POST', 'GET'))
def expenses_edit_category(category_id):
    category = get_expenses_category_connections(category_id)

    if request.method == 'POST':
        name = request.form['name']

        if not name:
            flash('Name is required.')
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('UPDATE expenses_categories SET name = ? WHERE tag_id = ?',
                         (name, category_id ))
            conn.commit()
            conn.close()
            return redirect(url_for('expenses_edit_categories'))

    return render_template('expenses_edit_category.html', category=category)

@app.route('/expenses/delete_category/<int:category_id>', methods=('POST', ))
def expenses_delete_category(category_id):
    conn = get_db_connection()
    cur = conn.cursor()
    # Delete all connections to that category
    cur.execute('DELETE FROM expense_to_category WHERE tag_id = ?', (category_id, ))
    cur.execute('DELETE FROM expenses_categories WHERE tag_id = ?', (category_id, ))
    conn.commit()
    conn.close()
    flash('Successfully deleted')
    return redirect(url_for('expenses_edit_categories'))

# Settings Routes

@app.route('/settings', methods=('GET', 'POST'))
def settings():

    conn = get_db_connection()
    cur = conn.cursor()
    reminder_quantity = cur.execute('SELECT quantity FROM settings WHERE name = ?', ("Reminder Quantity", )).fetchone()
    conn.close()

    print(reminder_quantity[0], sys.stdout)

    if request.method == "POST":
        if 'reminder-quantity' in request.form:
            new_reminder_quantity = request.form['reminder-quantity']
            if not new_reminder_quantity:
                flash('Reminder quantity is required')
            else:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute('UPDATE settings SET quantity = ? WHERE name = ?', (new_reminder_quantity, "Reminder Quantity"))
                conn.commit()
                conn.close()
                return redirect(url_for('home'))

    return render_template('settings_view.html', reminder_quantity=reminder_quantity)

@app.route('/settings/manual', methods=('GET',))
def settings_manual():
    return render_template('settings_manual.html')

if __name__ == '__main__':
    app.run()
