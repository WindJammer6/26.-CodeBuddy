
from snowflake.core import Root
from snowflake.snowpark import Session

CONNECTION_PARAMETERS = {
    "account": "PCQBTTO-VK19305",
    "user": "MEGIE",
    "password": "M1stral!h4ck!",
    "role": "ACCOUNTADMIN",
}   


from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
from snowflake.core import Root, CreateMode
from snowflake.core.database import Database
from snowflake.core.schema import Schema
from snowflake.core.table import Table, TableColumn, PrimaryKey


connection_params = {
    "connection_name": "default"
}

session = Session.builder.configs(CONNECTION_PARAMETERS).create()
root = Root(session)

database = root.databases.create(
  Database(
    name="Computing"),
    mode=CreateMode.or_replace
  )

schema = database.schemas.create(
  Schema(
    name="Computing"),
    mode=CreateMode.or_replace,
  )


# create table to store data 
# contents in table can be customized according to the professor

table = schema.tables.create(
  Table(
    name="Computing",
    columns=[
      TableColumn(
        name="WEEK",
        datatype="int",
        nullable=False,
      ),
      TableColumn(
        name="QUESTION",
        datatype="int",
        nullable=False,
      ),
      TableColumn(
        name="DESCRIPTION",
        datatype="string",
      ),
      TableColumn(
        name="TESTCASES",
        datatype="string",
      ),
      TableColumn(
        name="NOTES",
        datatype="string",
      ),
    ],
  ),
mode=CreateMode.or_replace
)


transcript_search_service = (root
  .databases["Computing"]
  .schemas["services"]
  .cortex_search_services["search_service"]
)

# edit to fetch user input from streamlit
user_input = input("Enter your query: ")


resp = transcript_search_service.search(
  query = user_input,
  columns=["DESCRIPTION", "TESTCASES", "NOTES"],
)

output = resp.to_json()
