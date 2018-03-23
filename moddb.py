import sqlite3
import CamSettings as cam


class db():
    def __init__(self):
        self.db_file = cam.save_folder_path + cam.db_file_name

    def connect(self):
        # dont forget to close connection from object.close()
        try:
            db_conn = sqlite3.connect(self.db_file)
            return db_conn
        except:
            print('error loading database')
        return None


    def create_base_db(self):
        try:
            conn = self.connect()
            # create table
            conn.execute('''CREATE TABLE frames
                                (FILE   TEXT     PRIMARY KEY NOT NULL,
                                DAY    TEXT    NOT NULL)''')
            print("Table created successfully")
            # Save
            conn.commit()
            conn.close()
        except Exception as e:
            print(e)

    def insert2db(self, FILE, DAY):
        conn = self.connect()
        # DONT FORGET TO CLOSE
        try:
            conn.execute('''INSERT INTO frames (FILE, DAY) \
                            VALUES (?, ?)''', (FILE, DAY,))
            conn.commit()
            conn.close()
        except Exception as e:
            print(e)

    def yield_paths(self):
        try:
            # connectds and establishes a databse connection
            conn = self.connect()
            # get cursor ready to execute
            cur = conn.cursor()
            # gets all row values
            cur.execute('SELECT * FROM frames')
            rows = cur.fetchall()
            # iterates and yields through items
            for i, row in enumerate(rows):
                yield i, row[0]
            # closes connection 
            cur.close()
            conn.close()
        except Exception as e:
            print(e)

if __name__ == '__main__':
    x = db()
