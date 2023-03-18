import sqlite3

def create_table():
    connection = sqlite3.connect(f'data.db')
    cursor = connection.cursor()
    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_id
                      (user_id INTEGER, is_going , urls TEXT)''')
        cursor.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx ON user_id(user_id)''')
    except Exception as ex:
        print(ex)
    connection.commit()
    connection.close()

class Database:
    def __init__(self, Database):
        self.conn = sqlite3.connect(Database, timeout=22)
        self.cursor = self.conn.cursor()
    async def insert(self, user_id, going, urls):
        with self.conn:
            self.cursor.execute("""INSERT OR IGNORE INTO user_id VALUES(?,?,?)""", (user_id, going, urls, ))
    async def select_going(self, user_id):
        with self.conn:
            going = self.cursor.execute("""SELECT is_going FROM user_id WHERE user_id = ?""", (user_id,)).fetchall()[0][0]
        return going
    async def update(self, is_going, user_id):
        with self.conn:
            self.cursor.execute("""UPDATE user_id SET is_going = ? WHERE user_id = ?""", (is_going, user_id))
    async def get_domen(self, user_id):
        with self.conn:
            links = self.cursor.execute("""SELECT urls FROM user_id WHERE user_id = ?""", (user_id,)).fetchall()[0][0]
        return links
    async def update_donem(self, user_id, url):
        with self.conn:
            self.cursor.execute("""UPDATE user_id SET urls = ? WHERE user_id = ?""", (url, user_id))