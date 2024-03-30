import mysql.connector
from dotenv import load_dotenv
import os
from urllib.parse import urlparse, unquote

# Load environment variables
load_dotenv()
DB_URL = os.getenv("DB_URL")

# Parse the database URL
parsed_url = urlparse(DB_URL)
username = parsed_url.username
password = unquote(parsed_url.password)  # Decode URL-encoded password
database = parsed_url.path[1:]  # Remove the leading slash
hostname = parsed_url.hostname
port = parsed_url.port if parsed_url.port else 3306  # Default MySQL port is 3306

# Establish connection to the MySQL database
conn = mysql.connector.connect(
    host=hostname,
    user=username,
    passwd=password,
    database=database,
    port=port
)

def validate_reader(conn, reader_id):
    cursor = conn.cursor()
    query = "SELECT RNAME FROM READER WHERE RID = %s"
    cursor.execute(query, (reader_id,))
    result = cursor.fetchone()
    if result:
        print(f"Welcome, {result[0]}")
        return True
    return False


def main_menu(conn):
    while True:
        print("\nMain Menu:")
        print("1. Reader Functions")
        print("2. Administrative Functions")
        print("3. Quit")
        choice = input("Enter choice (1-3): ")

        if choice == "1":
            reader_id = input("Enter Reader ID: ")
            if validate_reader(conn, reader_id):
                reader_menu(conn, reader_id)
            else:
                print("Invalid Reader ID.")
        elif choice == "2":
            admin_id = input("Enter Admin ID: ")
            password = input("Enter Password: ")
            if validate_admin(conn, admin_id, password):
                admin_menu(conn)
            else:
                print("Invalid Admin ID or Password.")
        elif choice == "3":
            print("Exiting the system.")
            break
        else:
            print("Invalid choice, please try again.")


def reader_menu(conn):
    while True:
        print("\nReader Functions Menu:")
        print("1. Search a document by title")
        print("2. Document checkout (Placeholder)")
        print("3. Document return (Placeholder)")
        print("4. Document reserve (Placeholder)")
        print("5. Compute fine (Placeholder)")
        print("6. Print reserved documents (Placeholder)")
        print("7. Print documents by publisher (Placeholder)")
        print("8. Quit to Main Menu")
        choice = input("Enter choice: ")

        if choice == "1":
            search_document_by_title(conn)
        elif choice == "8":
            break  # Exiting the reader_menu
        else:
            print("Functionality coming soon...")

def admin_menu(conn):
    while True:
        print("\nAdministrative Functions Menu:")
        print("1. Add a document copy (Placeholder)")
        print("2. Search document copy (Placeholder)")
        print("3. Add new reader")
        print("4. Print branch information (Placeholder)")
        print("5. Top N frequent borrowers in a branch (Placeholder)")
        print("6. Top N frequent borrowers in the library (Placeholder)")
        print("7. N most borrowed books in a branch (Placeholder)")
        print("8. N most borrowed books in the library (Placeholder)")
        print("9. 10 most popular books of the year (Placeholder)")
        print("10. Average fine paid by branch (Placeholder)")
        print("11. Quit to Main Menu")
        choice = input("Enter choice: ")

        if choice == "3":
            add_new_reader(conn)
        elif choice == "11":
            break  # Exiting the admin_menu
        else:
            print("Functionality coming soon...")

def search_document_by_title(conn):
    title = input("Enter document title to search: ")
    cursor = conn.cursor()
    query = "SELECT DOCID, TITLE, PDATE FROM DOCUMENT WHERE TITLE LIKE %s"
    cursor.execute(query, ("%"+title+"%",))
    results = cursor.fetchall()
    if results:
        for doc in results:
            print(f"DOCID: {doc[0]}, Title: {doc[1]}, Published Date: {doc[2]}")
    else:
        print("No documents found.")

def add_new_reader(conn):
    rid = input("Enter reader ID: ")
    name = input("Enter reader name: ")
    type = input("Enter reader type: ")
    address = input("Enter reader address: ")
    phone_no = input("Enter reader phone number: ")
    cursor = conn.cursor()
    query = "INSERT INTO READER (RID, RNAME, RTYPE, RADDRESS, PHONE_NO) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (rid, name, type, address, phone_no))
    conn.commit()
    print("New reader added successfully.")

# Start the application from the entry point
if __name__ == "__main__":
    try:
        main_menu(conn)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()
