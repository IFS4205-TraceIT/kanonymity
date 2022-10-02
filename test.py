import os
import psycopg2
from prettytable import PrettyTable
import generate_anon_data
import sys
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

maindb = [os.environ['POSTGRES_HOST'],os.environ['POSTGRES_DB'],os.environ['POSTGRES_USER'],os.environ['POSTGRES_PASSWORD']]
researchdb = [os.environ['POSTGRES_HOST'],os.environ['POSTGRES_RESEARCH_DB'],os.environ['POSTGRES_RESEARCH_USER'],os.environ['POSTGRES_RESEARCH_PASSWORD']]
testdb = [os.environ['POSTGRES_HOST'],"anon_testdb",os.environ['POSTGRES_SUPER_USER'],os.environ['POSTGRES_SUPER_PASSWORD']]

def kanonymity_test(kvalue):
    statement = """
        select count(*) from (select dob,gender,postal_code, count(*) as total_records from researchdata group by (dob,gender,postal_code) having count(*) < %s) as t;
    """
    conn = db_con(researchdb)
    cur = conn.cursor()
    cur.execute(statement,(kvalue,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    if result[0][0] > 0:
        return False
    return True

def check_no_missing_records():
    main_statement = """
        select count(*) from users;
    """
    research_statement = """
        select count(*) from researchdata;
    """
    conn = db_con(maindb)
    cur = conn.cursor()
    cur.execute(main_statement)
    result1 = cur.fetchall()
    cur.close()
    conn.close()
    conn = db_con(researchdb)
    cur = conn.cursor()
    cur.execute(research_statement)
    result2 =  cur.fetchall()
    cur.close()
    conn.close()
    if result1[0][0] == result2[0][0]:
        return True
    return False

def handle_missing_result_data_researchdb():
    conn = db_con(testdb)
    try:
        generate_anon_data.db_import(conn, "1qwery124")
        generate_anon_data.db_import(conn, "")
    except IOError:
        return False
    return True

def handle_malform_insert_researchdb():
    statement = """
        select * from researchdata;
    """
    conn = db_con(testdb)
    malform_file = "./test_data/malform_insert.csv"
    try:
        generate_anon_data.db_import(conn,malform_file)
    except Exception as e:
        return False
    cur = conn.cursor()
    cur.execute(statement)
    result = cur.fetchall()
    if(len(result) == 1):
        return True
    return False

def print_result(lvalue):
    statement = """
        select total_a as "Needed L Diversity", total_b as "Total QI groups", total_c as "Total users" from 
        (select count(*) as total_a from (select dob,gender,postal_code from researchdata group by (dob,gender,postal_code) 
        having count(distinct row(list_of_vaccines,last_close_contact)) < %s) as a) as a, 
        (select count(distinct row(dob,gender,postal_code)) as total_b from researchdata) as b,
        (select count(*) as total_c from researchdata) as c;
    """
    v = PrettyTable(['Needed L Diversity', 'Total QI groups', 'Total users'])
    conn = db_con(researchdb)
    cur = conn.cursor()
    cur.execute(statement,(lvalue,))
    result =  cur.fetchall()
    v.add_row(result[0])
    print(v)

def db_con(dbargs):
    conn = None
    try:
        conn = psycopg2.connect(
            host=dbargs[0],
            database=dbargs[1],
            user=dbargs[2],
            password=dbargs[3]
        )
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return None

def setup_test_db(dbargs):
    statement = """
        create database {database_name};
    """
    conn = psycopg2.connect(host=dbargs[0],user=dbargs[2],password=dbargs[3])
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(
        sql.SQL(
            statement
        ).format(
            database_name = sql.Identifier(
                dbargs[1]
            )
        )
    )
    conn.commit()
    cur.close()
    conn.close()


def teardown(dbargs):
    statement = """
        drop database if exists {database_name};
    """
    conn = psycopg2.connect(host=dbargs[0],user=dbargs[2],password=dbargs[3])
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(
        sql.SQL(
            statement
        ).format(
            database_name = sql.Identifier(
                dbargs[1]
            )
        )
    )
    conn.commit()
    cur.close()
    conn.close()

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

def main():
    teardown(testdb)
    setup_test_db(testdb)
    #blockPrint()
    t = PrettyTable(['TestCases', 'PassedResult'])
    # t.add_row(['',])
    t.add_row(['handle_missing_result_data_researchdb',handle_missing_result_data_researchdb()])
    t.add_row(['handle_malform_insert_researchdb',handle_malform_insert_researchdb()])
    t.add_row(['check_no_missing_records',check_no_missing_records()])
    t.add_row(['kanonymity_test', kanonymity_test(sys.argv[1])])
    #enablePrint()
    print(t)

    print_result(sys.argv[2])
    teardown(testdb)

if __name__ == '__main__':
    main()