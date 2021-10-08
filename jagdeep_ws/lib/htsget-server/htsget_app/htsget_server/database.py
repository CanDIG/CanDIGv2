from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey

SQLITE = 'sqlite'

class MyDatabase:
    """
    Class that uses sqlalchemy and implements DB functionality
    """
    # http://docs.sqlalchemy.org/en/latest/core/engines.html
    # Main DB Connection Ref Obj
    db_engine = None
    def __init__(self, dbpath, username='', password=''):
        try:
            self.db_engine = create_engine(dbpath)
        except Exception as e:
            print("error occured while creating db engine")
            print(e)


    def create_db_table(self):
        metadata = MetaData()
        files = Table('files', metadata,
                        Column('id', String, primary_key=True),
                        Column('file_type', String),
                        Column('format', String)
                        )
        try:
            metadata.create_all(self.db_engine)
            print("Table created")
        except Exception as e:
            print("Error occurred during Table creation!")
            print(e)


    def execute(self, query, param):
        """
        Execute query to insert, update, or delete from DB

        :param query: desired query to be executed
        :param param: the param object to be passed in ( e.g. {'id': 'NA2102'})
        """
        if query == '' : return
        with self.db_engine.connect() as connection:
            try:
                result = connection.execute(query, param)
            except Exception as e:
                print(e)


    def get_data(self, query, param):
        """
        Generic function that executes a db query that expects data to return
        e.g. select * from files

        :param query: db query
        :param param: param object that is passed in ( e.g. {'id': 'NA2102'})

        returns an array of tuples
        """

        if query == '' : return
        with self.db_engine.connect() as connection:
            try:
                result = connection.execute(query, param)
            except Exception as e:
                print(e)
            else:
                res = []
                for row in result:
                    res.append(row)
                return res


    def print_all_data(self, table='', query=''):
        query = query if query != '' else "SELECT * FROM '{}';".format('files')
        print(query)
        with self.db_engine.connect() as connection:
            try:
                result = connection.execute(query)
            except Exception as e:
                print(e)
            else:
                for row in result:
                    print(row) # print(row[0], row[1], row[2])
                result.close()
        print("\n")
