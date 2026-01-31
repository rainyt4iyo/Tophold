import psycopg2
from contextlib import contextmanager   
from psycopg2.extras import RealDictCursor


@contextmanager
def get_db():

    conn = psycopg2.connect(
        host="localhost",
        dbname="tophold",
        user="t4",
        password="t4_password",
        cursor_factory=RealDictCursor,  # user['password_hash'] みたいに取れる
    )
    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()


def id2name(user_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT name FROM gym_login WHERE id = %s', (user_id,))
            result = cur.fetchone()
            if result:
                return result['name']
            else:
                return None
