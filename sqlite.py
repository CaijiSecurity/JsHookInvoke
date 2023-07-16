import sqlite3
import traceback

from threading import Lock
from utils import generate_id
from datetime import datetime

lock = Lock()
sqlite_conn = sqlite3.connect("data.db", check_same_thread=False)


def init_db():
    '''
    STATE 状态 0-未处理，1-已处理
    '''
    c = sqlite_conn.cursor()
    with lock:
        # 创建 CAIJIDATA 表
        try:
            c.execute(
                '''CREATE TABLE CAIJIDATA
                    (ID     TEXT     PRIMARY KEY     NOT NULL,
                    RAW_DATA    TEXT    NOT NULL,
                    RESULT_DATA     TEXT,
                    STATE       INT     NOT NULL,
                    RAW_INSERT_DATE      TIMESTAMP    NOT NULL,
                    RESULT_UPDATE_DATE      TIMESTAMP);
                '''
            )
            sqlite_conn.commit()
        except Exception as e:
            # traceback.print_exc()
            print(e)
            sqlite_conn.rollback()
        # 创建 AGENTS 表
        try:
            c.execute(
                '''CREATE TABLE AGENTS
                    (AGENTID     TEXT     PRIMARY KEY     NOT NULL,
                    DESCRIPTION    TEXT    NOT NULL);
                '''
            )
            sqlite_conn.commit()
        except Exception as e:
            # traceback.print_exc()
            print(e)
            sqlite_conn.rollback()


def insert_raw_data(raw_data):
    c = sqlite_conn.cursor()
    new_id = generate_id()
    with lock:
        try:
            c.execute(
                '''
                    INSERT INTO CAIJIDATA (ID, RAW_DATA, STATE, RAW_INSERT_DATE)
                    VALUES (?, ?, ?, ?);
                ''',
                (new_id, raw_data, 0, datetime.now())
            )
            sqlite_conn.commit()
            return new_id
        except Exception as e:
            traceback.print_exc()
            print(e)
            sqlite_conn.rollback()


def update_result_data(id, result_data):
    c = sqlite_conn.cursor()
    with lock:
        try:
            c.execute(
                '''
                    UPDATE 
                        CAIJIDATA 
                    set 
                        RESULT_DATA = ?,
                        STATE = ?,
                        RESULT_UPDATE_DATE = ?
                    WHERE 
                        ID = ?;
                ''',
                (result_data, 1, datetime.now(), id)
            )
            sqlite_conn.commit()
        except UnicodeError as e:
            print(e)
            c.execute(
                '''
                    UPDATE 
                        CAIJIDATA 
                    set 
                        RESULT_DATA = ?,
                        STATE = ?,
                        RESULT_UPDATE_DATE = ?
                    WHERE 
                        ID = ?;
                ''',
                ("编码异常，可能是数据中包含了Emoji之类的符号，JS处理后编码异常了", 1, datetime.now(), id)
            )
            sqlite_conn.commit()
        except Exception as e:
            print(e)
            traceback.print_exc()
            sqlite_conn.rollback()


def get_next_raw_data():
    c = sqlite_conn.cursor()
    with lock:
        try:
            cursor = c.execute(
                '''
                    SELECT  
                        ID, RAW_DATA 
                    FROM 
                        CAIJIDATA
                    WHERE 
                        STATE = 0
                    ORDER BY
                        RAW_INSERT_DATE asc;
                '''
            )
            all_rows = cursor.fetchall()
            if len(all_rows) > 0:
                id_and_raw_data = {
                    "id": all_rows[0][0],
                    "rawData": all_rows[0][1],
                }
                return id_and_raw_data
            else:
                return None 
        except Exception as e:
            print(e)
            traceback.print_exc()
            return None


def get_result(id):
    c = sqlite_conn.cursor()
    with lock:
        try:
            cursor = c.execute(
                '''
                    SELECT  
                        RESULT_DATA 
                    FROM 
                        CAIJIDATA
                    WHERE 
                        STATE = 1 and ID = ?
                ''',
                (id,)
            )
            all_rows = cursor.fetchall()
            if len(all_rows) > 0:
                return all_rows[0][0]
            else:
                return None 
        except Exception as e:
            print(e)
            traceback.print_exc()
            return None


def close_conn():
    with lock:
        sqlite_conn.close()


if __name__ == '__main__':
    '''
    测试
    '''
    import time
    test_id = insert_raw_data("testhahaha")
    print("插入数据", test_id)
    # 本地使用测试demo，延迟一秒左右才能查询到结果，根据实际场景，可能需要更久的延迟才能查询到结果
    time.sleep(1)
    print(get_result(test_id))
    