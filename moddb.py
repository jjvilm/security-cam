import sqlite3
import Camara as cam


class db():
    def __init__(self):
        self.db_file = cam.save_folder_path + cam.db_file_name
        self.create_base_db()

    def connect(self):
        # dont forget to close connection from object.close()
        try:
            db_conn = sqlite3.connect(self.db_file)
            return db_conn
        except:
            print('error loading database')
        return None


    def create_base_db(self):
        conn = self.connect()
        try:
            # create table
            conn.execute('''CREATE TABLE frames
                                (ID INT PRIMARY KEY NOT NULL,
                                DATE    TEXT    NOT NULL, 
                                TIME    TEXT    NOT NULL, 
                                PATH    TEXT    NOT NULL)''')
            print("Table created successfully")
            # Save
            conn.commit()
            conn.close()
        except Exception as e:
            print(e)

    def insert2db(self, ID, DATE, TIME, PATH):
        conn = self.connect()
        # DONT FORGET TO CLOSE
        try:
            conn.execute('''INSERT INTO frames (ID, DATE, TIME, PATH) \
                                    VALUES (?, ?, ?, ?)''', (ID, DATE, TIME, PATH,))
            conn.commit()
            conn.close()
        except Exception as e:
            print(e)






if __name__ == '__main__':
    x = db()
