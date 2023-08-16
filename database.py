import mysql.connector as m
from dotenv import load_dotenv
import os
import uuid
import hashlib
import pickle

def hash_password_sha256(plain_password, salt=None):
    if salt is None:
        salt = os.urandom(32)

    password_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100000)
    hash_bytes = salt + password_hash

    return hash_bytes.hex()

def verify_password_sha256(plain_password, hashed_password):
    hash_bytes = bytes.fromhex(hashed_password)
    salt = hash_bytes[:32]

    rehashed_password = hash_password_sha256(plain_password, salt)
    return hashed_password == rehashed_password


def create_user(email,password):
    load_dotenv()
    mysql_user=os.environ.get("mysql_user")
    mysql_pass=os.environ.get("mysql_password")
    con=m.connect(user=mysql_user,password=mysql_pass,db="ai_chat",host="localhost")
    if con.is_connected():
        cursor=con.cursor()
        user_id=str(uuid.uuid4())
        search_id=f'select id from Users where id="{user_id}"'
        cursor.execute(search_id)
        row=cursor.fetchone()
        while row:
            user_id=str(uuid.uuid4())
            search_id=f'select id from Users where id="{user_id}"'
            cursor.execute(search_id)
            row=cursor.fetchone()
        search_email=f'select * from Users where email="{email}"'
        cursor.execute(search_email)
        row=cursor.fetchone()
        print(row)
        if row:
            return None
        password=hash_password_sha256(password)
        sql= "INSERT INTO Users (id, password, email) VALUES (%s, %s, %s)"
        cursor.execute(sql,(user_id,password,email))
        con.commit()
        con.close()
        return user_id

def validate_login(email,password):
    load_dotenv()
    mysql_user=os.environ.get("mysql_user")
    mysql_pass=os.environ.get("mysql_password")
    con=m.connect(user=mysql_user,password=mysql_pass,db="ai_chat",host="localhost")
    if con.is_connected():
        cursor=con.cursor()
        sql=f'''select * from Users where email="{email}"'''
        cursor.execute(sql)
        row=cursor.fetchone()
        if not row:
            return None 
        con.close()
        if verify_password_sha256(password,row[1]):
            return row[0]
        else:
            return False

def reset_password(userid,old_password,new_password):
    load_dotenv()
    mysql_user=os.environ.get("mysql_user")
    mysql_pass=os.environ.get("mysql_password")
    con=m.connect(user=mysql_user,password=mysql_pass,db="ai_chat",host="localhost")
    if con.is_connected():
        cursor=con.cursor()
        sql=f'''select * from Users where id="{userid}"'''
        cursor.execute(sql)
        row=cursor.fetchone()
        if verify_password_sha256(old_password,row[1]):
            sql=f'''update Users set password="{hash_password_sha256(new_password)}" where id="{userid}"'''
            cursor.execute(sql)
            con.commit()
            con.close()
            return True 
        else:
            con.close()
            return False
def delete(userid):
    load_dotenv()
    mysql_user=os.environ.get("mysql_user")
    mysql_pass=os.environ.get("mysql_password")
    con=m.connect(user=mysql_user,password=mysql_pass,db="ai_chat",host="localhost")
    if con.is_connected():
        cursor=con.cursor()
        cursor.execute(f'''delete from Users where id="{userid}"''')
        con.commit()
        con.close()
    with open("chats.bin","rb") as fh:
        d=pickle.load(fh)
        updated_d={}
        for key in d:
            if userid not in key:
                updated_d.update({key:d[key]})
    with open("chats.bin","wb") as fh:
        pickle.dump(updated_d,fh)

