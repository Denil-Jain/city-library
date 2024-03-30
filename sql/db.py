from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the DB_URL environment variable
DB_URL = os.getenv("DB_URL")
from urllib.parse import urlparse, unquote
import mysql.connector

# Parse the DB_URL
result = urlparse(DB_URL)
username = result.username
password = unquote(result.password)
database = result.path[1:]  # Skipping the leading '/'
hostname = result.hostname
port = result.port

# Connect to the MySQL database
conn = mysql.connector.connect(
    host=hostname,
    user=username,
    passwd=password,
    database=database,
    port=port
)
c = conn.cursor()
