import mysql.connector
from fastapi import HTTPException
from app.config.settings import DB_CONFIG

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

def execute_query(query, params=None, fetch_one=False):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        
        # Check if this is a SELECT query
        is_select = query.strip().upper().startswith('SELECT')
        
        if is_select:
            if fetch_one:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
        else:
            # For INSERT, UPDATE, DELETE operations
            conn.commit()
            result = cursor.rowcount
            
        return result
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")
    finally:
        cursor.close()
        conn.close() 