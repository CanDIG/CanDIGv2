from dbtest import MyDatabase

DATABASE = 'sqlite'
sqlite = MyDatabase(DATABASE, dbname='test.db')

sqlite.create_db_table()
insert_query = "INSERT INTO files VALUES ( (:id), (:file_type), (:format) )"
insert_param = {'id': 'NA02102', 'file_type': '.bam', 'format': 'BAM'}
sqlite.execute(insert_query, insert_param)
sqlite.print_all_data()
query = """SELECT * FROM  files WHERE id = (:id) LIMIT 1"""
param_obj = {'id': 'NA02102'}
print(sqlite.get_data(query, param_obj))