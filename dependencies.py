from nameko.extensions import DependencyProvider

from nameko.web.handlers import http
from werkzeug.wrappers import Response
import redis
import pickle
import uuid


import mysql.connector
from mysql.connector import Error
from mysql.connector import pooling



class DatabaseWrapper:

    connection = None

    def __init__(self, connection):
        self.connection = connection
        self.default_expire = 60 * 60

    def add_user(self,username,password):
        cursor = self.connection.cursor(dictionary=True)
        sql = "INSERT INTO `user`(`id`, `username`, `password`) VALUES (NULL,%s,%s)"
        val = ([str(username),str(password)])
        cursor.execute(sql,val)
        self.connection.commit()
        cursor.close()
        return "success"

    def check_user(self,user_data):
        username = user_data['username']
        password = user_data['password']
        
        result1 = []
        cursor = self.connection.cursor(dictionary=True)
        sql = "select count(*) as hitung from user where username=%s and password=%s"
        val = ([str(username),str(password)])
        cursor.execute(sql,val)
        for row in cursor.fetchall():
            result1.append({
                'hitung': row['hitung']
            })
        status = row["hitung"]
        if status == 1:
            # key = str(uuid.uuid4())
            # response = Response(str(user_data))
            # response.set_cookie('SESSID', key)
            # return response
            # key = str(uuid.uuid4())
            # user_data = {
            #     'id': 1,
            #     'username': 'andre'
            # }
            # response = Response(str(user_data))
            # response.set_cookie('SESSID',key)
            # return response
            return 1
        elif status == 0:
            return 2
        cursor.close()
        
        connection = None


    def upload(self,arrnamafile,nama):
        cursor = self.connection.cursor(dictionary=True)
        sql = "SELECT * FROM `user` WHERE username=%s"
        val = ([str(nama)])
        cursor.execute(sql,val)
        row = cursor.fetchone()
        id = row['id']
        cursor.close()

        for i in range(len(arrnamafile)):
            cursor = self.connection.cursor(dictionary=True)
            sql = 'INSERT INTO `cloud`(`namafile`, `id_user`) VALUES (%s, %s)'
            cursor.execute(sql, [str(arrnamafile[i]),int(id)])
            self.connection.commit()

        cursor.close()
        return "upload success"

    def download(self,nama,id):
        cursor = self.connection.cursor(dictionary=True)
        sql = "SELECT * FROM `user` WHERE username=%s"
        val = ([str(nama)])
        cursor.execute(sql,val)
        row = cursor.fetchone()
        iduser = row['id']
        cursor.close()
        
        cursor = self.connection.cursor(dictionary=True)
        sql = "SELECT * FROM `cloud` WHERE id_user=%s and id=%s; "
        val = ([int(iduser),int(id)])
        cursor.execute(sql,val)
        row = cursor.fetchone()
        result = {
            "filename": row['namafile']
        }
        cursor.close()
        return result

    
    
   
class SessionWrapper:
    
    def __init__(self, connection):
        # Redis Connection
        self.redis = connection

        # 1 Hour Expire (in Second)
        self.default_expire = 60 * 60
        
    def set_session(self,user_data):
        key = str(uuid.uuid4())
        user_data_pickled = pickle.dumps(user_data)
        session_id = key
        self.redis.set(session_id, user_data_pickled, ex=self.default_expire)
        return session_id
   
    def get_session(self, session_id):
        # Get the Data from Redis
        result = self.redis.get(session_id)

        if result:
        # Unpack the user data from Redis
            user_data = pickle.loads(result)
        else:
            user_data = None

        return user_data

    def delete_session(self, session_id):
        result = self.redis.delete(session_id)
        return result

    
        
    
class Database(DependencyProvider):

    connection_pool = None

    def __init__(self):
        try:
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="database_pool",
                pool_size=5,
                pool_reset_session=True,
                host='localhost',
                database='register',
                user='root',
                password=''
            )
        except Error as e :
            print ("Error while connecting to MySQL using Connection pool ", e)
    
    def get_dependency(self, worker_ctx):
        return DatabaseWrapper(self.connection_pool.get_connection())

class SessionProvider(DependencyProvider):

    def setup(self):
        self.client = redis.Redis(host='127.0.0.1', port=16379, db=0)
    
    def get_dependency(self, worker_ctx):
        return SessionWrapper(self.client)
    
    



