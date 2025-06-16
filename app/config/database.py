from mysql.connector import connect
from mysql.connector.pooling import MySQLConnectionPool

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",  # Update with your MySQL password
    "database": "hearme_learning",  # Update with your database name
}

def get_db_connection():
    try:
        connection = connect(**db_config)
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise e

def get_connection_pool(pool_name="mypool", pool_size=5):
    try:
        connection_pool = MySQLConnectionPool(
            pool_name=pool_name,
            pool_size=pool_size,
            **db_config
        )
        return connection_pool
    except Exception as e:
        print(f"Error creating connection pool: {e}")
        raise e 