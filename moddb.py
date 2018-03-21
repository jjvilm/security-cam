import sqlite3
import sqlite3
import Camara as cam
from Camara import db_file_name, save_folder_path


class db():
    def __init__(self):
        self.db_file = save_folder_path + db_file_name
        self.db_conn = self.create_conn()
        self.create_base_db()

    def create_conn(self):
        # dont forget to close connection from object.close()
        try:
            print("Connecting to: {}".format(self.db_file))
            db_conn = sqlite3.connect(self.db_file)
            print("Opened database successfulluly")
            return db_conn
        except:
            print('error loading database')

        return None


    def create_base_db(self):
        try:
            # create table
            self.db_conn.execute('''CREATE TABLE frames
                        (ID INT PRIMARY KEY NOT NULL,
                        DATE    TEXT    NOT NULL, 
                        TIME    TEXT    NOT NULL, 
                        PATH    TEXT    NOT NULL)''')
            print("Table created successfully")
            # insert a row of data
            #c.execute("INSERT INTO frames VALUES (0, '2006-01-05', '/home/pi/')")
            # Save
            #conn.commit()
        except Exception as e:
            print(e)

    def insert2db(self, ID, DATE, TIME, PATH):
        try:
            self.db_conn.execute('''INSERT INTO frames (ID, DATE, TIME, PATH) \
                    VALUES (?, ?, ?, ?)''', (ID, DATE, TIME, PATH))
            print("Row inserted successfully")
            self.db_conn.commit()
        except Exception as e:
            print(e)






if __name__ == '__main__':
    x = db()
    x.insert2db(1, '2018/03/20',"21:38:40", '/home/pi')
    x.db_conn.close()
