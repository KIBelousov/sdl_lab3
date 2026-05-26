import os
import psycopg
from psycopg import sql
from getpass import getpass
import logging
import sys


LOG_FILE = os.getenv("APP_LOG_FILE")

if LOG_FILE:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

handlers = [logging.StreamHandler(sys.stdout)]

if LOG_FILE:
    handlers.append(logging.FileHandler(LOG_FILE, mode="a"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=handlers,
    force=True
)

logging.info("APPLICATION STARTED")


def load_config():
    cfg = {
        "host": os.getenv("DB_HOST", "db"),
        "port": os.getenv("DB_PORT", "5432"),
        "database": os.getenv("DB_NAME", "petshop")
    }
    logging.info(f"Config loaded: {cfg}")
    return cfg


def get_credentials():
    user = input("Логин: ").strip()
    password = getpass("Пароль: ")
    logging.info(f"User login attempt: {user}")
    return user, password


ALLOWED_TABLES = {
    "customers": ["id", "full_name", "email", "phone"],
    "pet_categories": ["id", "name"],
    "products": ["id", "name", "price", "stock", "category_id"],
    "orders": ["id", "customer_id", "order_date"],
    "order_items": ["id", "order_id", "product_id", "quantity", "price"]
}

def safe_table(table):
    if table not in ALLOWED_TABLES:
        raise ValueError("Недопустимая таблица")
    return sql.Identifier(table)

def safe_column(table, column):
    if table not in ALLOWED_TABLES or column not in ALLOWED_TABLES[table]:
        raise ValueError("Недопустимая колонка")
    return sql.Identifier(column)


def connect(cfg, user, password):
    try:
        conninfo = psycopg.conninfo.make_conninfo(
            host=cfg["host"],
            port=cfg["port"],
            dbname=cfg["database"],
            user=user,
            password=password
        )
        conn = psycopg.connect(conninfo=conninfo)
        logging.info("Database connection successful")
        return conn
    except Exception as e:
        logging.error("Database connection failed")
        raise e


def select_all(cur):
    table = input("Таблица: ")
    query = sql.SQL("SELECT * FROM {}").format(safe_table(table))

    cur.execute(query)
    rows = cur.fetchall()

    logging.info(f"SELECT ALL from {table}")
    print(rows)

def select_where(cur):
    table = input("Таблица: ")
    column = input("Колонка: ")
    value = input("Значение: ")

    query = sql.SQL("SELECT * FROM {} WHERE {} = %s").format(
        safe_table(table),
        safe_column(table, column)
    )

    cur.execute(query, (value,))
    rows = cur.fetchall()

    logging.info(f"SELECT WHERE {table}.{column}={value}")
    print(rows)


def update_one(cur):
    table = input("Таблица: ")
    _id = input("ID: ")
    column = input("Колонка: ")
    value = input("Новое значение: ")

    query = sql.SQL("UPDATE {} SET {} = %s WHERE id = %s").format(
        safe_table(table),
        safe_column(table, column)
    )

    cur.execute(query, (value, _id))

    logging.info(f"UPDATE {table} id={_id} set {column}={value}")
    print("OK")


def update_many(cur):
    table = input("Таблица: ")
    column = input("Колонка: ")
    ids = input("ID через запятую: ").split(",")
    new_value = input("Новое значение: ")

    query = sql.SQL("UPDATE {} SET {} = %s WHERE id = ANY(%s)").format(
        safe_table(table),
        safe_column(table, column)
    )

    cur.execute(query, (new_value, ids))

    logging.info(f"UPDATE MANY {table} ids={ids} set {column}={new_value}")
    print("OK")


def insert_single(cur):
    name = input("Name: ")
    price = input("Price: ")
    stock = input("Stock: ")
    cat = input("Category ID: ")

    cur.execute(
        "INSERT INTO products(name, price, stock, category_id) VALUES (%s, %s, %s, %s)",
        (name, price, stock, cat)
    )

    logging.info(f"INSERT product {name}, price={price}")
    print("Добавлено")


def insert_many(cur):
    n = int(input("Сколько товаров?: "))
    data = []

    for i in range(n):
        print(f"\nТовар {i+1}")
        name = input("Name: ")
        price = input("Price: ")
        stock = input("Stock: ")
        cat = input("Category ID: ")

        data.append((name, price, stock, cat))

    cur.executemany(
        "INSERT INTO products(name, price, stock, category_id) VALUES (%s, %s, %s, %s)",
        data
    )

    logging.info(f"INSERT MANY products count={n}")
    print("OK")


def insert_order(cur):
    customer_id = input("Customer ID: ")

    cur.execute(
        "INSERT INTO orders(customer_id) VALUES (%s) RETURNING id",
        (customer_id,)
    )

    order_id = cur.fetchone()[0]

    n = int(input("Сколько товаров в заказе?: "))
    items = []

    for i in range(n):
        print(f"\nТовар {i+1}")
        product_id = input("Product ID: ")
        quantity = input("Quantity: ")
        price = input("Price: ")

        items.append((order_id, product_id, quantity, price))

    cur.executemany(
        "INSERT INTO order_items(order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
        items
    )

    logging.info(f"ORDER CREATED id={order_id}, items={n}")
    print("Заказ создан")


def main():
    cfg = load_config()
    user, password = get_credentials()

    try:
        conn = connect(cfg, user, password)
        cur = conn.cursor()

        while True:
            print("""
1 - SELECT *
2 - SELECT WHERE
3 - INSERT product
4 - INSERT many products
5 - UPDATE one
6 - UPDATE many
7 - INSERT order
0 - exit
""")

            cmd = input(">>> ")

            if cmd == "1":
                select_all(cur)

            elif cmd == "2":
                select_where(cur)

            elif cmd == "3":
                insert_single(cur)
                conn.commit()

            elif cmd == "4":
                insert_many(cur)
                conn.commit()

            elif cmd == "5":
                update_one(cur)
                conn.commit()

            elif cmd == "6":
                update_many(cur)
                conn.commit()

            elif cmd == "7":
                insert_order(cur)
                conn.commit()

            elif cmd == "0":
                logging.info("Application stopped by user")
                break

    except Exception as e:
        logging.error(f"Fatal error: {e}")

    finally:
        try:
            conn.close()
        except:
            pass

if __name__ == "__main__":
    main()
