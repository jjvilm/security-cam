import sqlite3
from CamSettings import SAVE_PATH, DATABASE_FILE


class db():
    def __init__(self):
        self.db_file = SAVE_PATH + DATABASE_FILE

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
            # creates database in case non exists
            self.create_base_db()


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

    def get_rows(self, column_id='week'):
        try:
            conn = self.connect()
            c = conn.cursor()
            if column_id == 'week':
                c.execute('SELECT * FROM frames')
            else:
                c.execute('''SELECT * FROM frames WHERE DAY=?''', (column_id,))

            # closes connection 
            rows = c.fetchall()
            c.close()
            conn.close()
            # returns list of list [rowN, (valueA, valueB)]
            return rows

        except Exception as e:
            print(e)



    def retrieve_column(self, column_id='week'):
        """ Import frames by day specified, defualt is by week """
        try:
            conn = self.connect()
            c = conn.cursor()
            if column_id == 'week':
                c.execute('SELECT * FROM frames')
            else:
                c.execute('''SELECT * FROM frames WHERE DAY=?''', (column_id,))

            rows = c.fetchall()
            for i, row in enumerate(rows):
                yield i, row[0]


            # closes connection 
            c.close()
            conn.close()
        except Exception as e:
            print(e)

    def count_rows(self, column_id='week'):
        try:
            conn = self.connect()
            c = conn.cursor()
            if column_id == 'week':
                c.execute('SELECT * FROM frames')
            else:
                c.execute('''SELECT * FROM frames WHERE DAY=?''', (column_id,))

            rows = c.fetchall()
            print(len(rows))
            return
            for i, _ in enumerate(rows):
                continue
            c.close()
            conn.close()
            return i

        except Exception as e:
            print(e)



if __name__ == '__main__':
    x = db()
    #x.retrieve_column('Wednesday')
    x.count_rows('Wednesday')

