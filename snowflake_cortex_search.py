from snowflake.core import Root
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
from snowflake.core import Root, CreateMode
from snowflake.core.database import Database
from snowflake.core.schema import Schema
from snowflake.core.table import Table, TableColumn, PrimaryKey

def snowflake_cortex_search(user_query):
    # Connection parameters for Snowflake
    CONNECTION_PARAMETERS = {
        "account": "HFGBXYS-OW03108",
        "user": "WINDJAMMER6",
        "password": "#Jetwei1217",
        "role": "ACCOUNTADMIN",
    }
    
    # Establish a session with Snowflake
    session = Session.builder.configs(CONNECTION_PARAMETERS).create()
    root = Root(session)
    
    # Create a database
    database = root.databases.create(
        Database(
            name="Computing"),
        mode=CreateMode.or_replace
    )
    
    # Create a schema
    schema = database.schemas.create(
        Schema(
            name="services"),
        mode=CreateMode.or_replace,
    )
    
    # Create a table to store assignments
    table = schema.tables.create(
        Table(
            name="assignments",
            columns=[
                TableColumn(
                    name="ASSIGNMENT_NAME",
                    datatype="string",
                    nullable=False,
                ),
                TableColumn(
                    name="ASSIGNMENT_NOTES",
                    datatype="string",
                    nullable=False,
                ),
            ],
        ),
        mode=CreateMode.or_replace
    )
    
    # # Insert data into the assignments table
    # insert_query = """
    #     INSERT INTO services.assignments (ASSIGNMENT_NAME, ASSIGNMENT_NOTES) VALUES 
    #     ('Calculate Factorial', 'Write a function `factorial(n)` that calculates the factorial of a non-negative integer `n`. The factorial of `n` is defined as `n! = n × (n-1) × ... × 1` with `0! = 1`.'),
    #     ('Check Prime Number', 'Write a function `is_prime(n)` that returns `True` if `n` is a prime number and `False` otherwise. A prime number is greater than 1 and divisible only by 1 and itself.');
    # """
    # session.sql(insert_query).collect()
    
    # Cortex Search Service Configuration
    transcript_search_service = (root
      .databases["Computing"]
      .schemas["services"]
      .cortex_search_services["search_service"]
    )
        
    # Search the assignments table based on the user input
    resp = transcript_search_service.search(
        query=user_query,
        columns=["ASSIGNMENT_NAME"],
    )
    
    # Convert the response to JSON for further processing
    output = resp.to_json()
    print(output)

    return resp[0]["ASSIGNMENT_NOTES"]
