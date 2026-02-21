import pyodbc


class SqlServerSrv:
    def __init__(self, server='localhost', database='YourDatabase', username='sa', password='sa'):
        """
        Initialize the connection to the SQL Server.
        """
        self.connection_string = f'DRIVER={{ODBC Driver 18 for SQL Server}};' \
                                 f'SERVER={server};DATABASE={database};' \
                                 f'UID={username};PWD={password};TrustServerCertificate=yes;'
        self.conn = None

    def connect(self):
        """
        Open the connection to the database.
        """
        try:
            self.conn = pyodbc.connect(self.connection_string)
            print("Connected to SQL Server successfully.")
        except Exception as e:
            print(f"Error connecting to SQL Server: {e}")
            raise

    def insert_with_stored_procedure(self, sp_name, param_value):
        """
        Call a stored procedure to insert data and return the new ID.

        Args:
            sp_name (str): The name of the stored procedure.
            param_value (str): The string value to insert.

        Returns:
            int: The ID of the inserted row.
        """
        if self.conn is None:
            self.connect()

        try:
            cursor = self.conn.cursor()

            # Assuming the stored procedure has one input parameter and returns the new ID as output
            # For example: CREATE PROCEDURE InsertData @InputValue NVARCHAR(100), @NewID INT OUTPUT
            new_id = cursor.execute(f"DECLARE @NewID INT; "
                                    f"EXEC {sp_name} @InputValue=?, @NewID=@NewID OUTPUT; "
                                    f"SELECT @NewID;", param_value).fetchone()[0]
            self.conn.commit()
            return new_id
        except Exception as e:
            print(f"Error executing stored procedure: {e}")
            self.conn.rollback()
            raise
        finally:
            cursor.close()

    def close(self):
        """
        Close the database connection.
        """
        if self.conn:
            self.conn.close()
            self.conn = None
            print("Connection closed.")