from sqlalchemy.engine.url import URL, make_url
from starlette.datastructures import Secret, CommaSeparatedStrings


SECRET_KEY = "69bf038c4ed9c0f7ece92f1c840d25b94a3a82317de502ccdfb0222a9ecf9ada"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

DB_DRIVER = "postgresql"
DB_HOST = '127.0.0.1'
DB_PORT = 5432
DB_USER = "auction"
DB_PASSWORD = "auction"
DB_DATABASE = "auction"
DB_DSN = URL(drivername=DB_DRIVER,username=DB_USER,password=DB_PASSWORD,host=DB_HOST,port=DB_PORT,database=DB_DATABASE,)
DB_POOL_MIN_SIZE = 1
DB_POOL_MAX_SIZE = 16
DB_ECHO = False
DB_SSL = None
DB_USE_CONNECTION_FOR_REQUEST = True
DB_RETRY_LIMIT = 1
DB_RETRY_INTERVAL = 1