from contextlib import closing

import psycopg2
from psycopg2 import sql


class DatabaseUtil:

    def __init__(self, db_config):
        self.db_config = db_config

    def schema_details(self,schema_name):

        schema_info_context = f"Database Schema: {schema_name}\n"

        with closing(psycopg2.connect(**self.db_config)) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = %s;",
                    (schema_name,),
                )
                tables_list = cursor.fetchall()

                for (table_name,) in tables_list:
                    schema_info_context += f"\nTable: {table_name}\n"

                    cursor.execute(
                        "SELECT column_name, data_type FROM information_schema.columns "
                        "WHERE table_schema = %s AND table_name = %s;",
                        (schema_name, table_name),
                    )
                    for column_name, data_type in cursor.fetchall():
                        schema_info_context += (
                            f"  Column: {column_name}, Data Type: {data_type}\n"
                        )

                    cursor.execute(
                        sql.SQL("SELECT * FROM {}.{} LIMIT 5").format(
                            sql.Identifier(schema_name),
                            sql.Identifier(table_name),
                        )
                    )
                    schema_info_context += "  Sample Data:\n"
                    for row in cursor.fetchall():
                        schema_info_context += f"    {row}\n"

        return schema_info_context

    def execute_sql(self, query):
        with closing(psycopg2.connect(**self.db_config)) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                if cursor.description is None:
                    result = f"Query executed successfully. {cursor.rowcount} rows affected."
                else:
                    result = str(cursor.fetchall())
            connection.commit()
            return result