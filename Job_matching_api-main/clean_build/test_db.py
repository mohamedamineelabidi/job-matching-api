from database.session import engine
from sqlalchemy import text

def test_database_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text('SELECT 1'))
            print('Database connection successful!')
            return True
    except Exception as e:
        print(f'Database connection failed: {str(e)}')
        return False

if __name__ == '__main__':
    test_database_connection()