import csv
import io
from flask import Blueprint, render_template, request, redirect, flash
from werkzeug.utils import secure_filename
from sql.db import DB
import traceback
upload = Blueprint('upload', __name__, url_prefix='/upload')



@upload.route("/import", methods=["GET","POST"])
def importCSV():
    if request.method == "POST":
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file', "warning")
            return redirect(request.url)
        
        if ".csv" not in file.filename:
            flash('Select CSV file',"warning")
            return redirect(request.url)
        if file and secure_filename(file.filename):
            readers = []
            readers_query = """
            INSERT INTO READER (RID, RTYPE, RNAME, RADDRESS, PHONE_NO)
            VALUES (%(RID)s, %(RTYPE)s, %(RNAME)s, %(RADDRESS)s, %(PHONE_NO)s)
            ON DUPLICATE KEY UPDATE 
            RTYPE=VALUES(RTYPE),
            RNAME=VALUES(RNAME),
            RADDRESS=VALUES(RADDRESS),
            PHONE_NO=VALUES(PHONE_NO);
            """
            
            stream = io.TextIOWrapper(file.stream._file, "UTF8", newline=None)
            
            for row in csv.DictReader(stream):
                reader = {}
                reader['RID'] = row['RID']
                reader['RTYPE'] = row['RTYPE']
                reader['RNAME'] = row['RNAME']
                reader['RADDRESS'] = row['RADDRESS']
                reader['PHONE_NO'] = row['PHONE_NO']
                readers.append(reader)
                
            if len(readers) > 0:
                print(f"Inserting or updating {len(readers)} readers")
                try:
                    result = DB.insertMany(readers_query, readers)
                    Message = len(readers),"readers Inserted"
                    flash(Message,"success")
                except Exception as e:
                    traceback.print_exc()
                    flash("There was an error loading in the csv data", "danger")
            else:
                flash('No readers were loaded',"info")

            try:
                result = DB.selectOne("SHOW SESSION STATUS LIKE 'questions'")
                print(f"Result {result}")
            except Exception as e:
                    traceback.print_exc()
                    flash("There was an error counting session queries", "danger")
    return render_template("upload.html")

@upload.route("/upload_documents", methods=["GET","POST"])
def upload_documents():
    if request.method == "POST":
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file', "warning")
            return redirect(request.url)
        
        if ".csv" not in file.filename:
            flash('Select CSV file', "warning")
            return redirect(request.url)
        if file and secure_filename(file.filename):
            documents = []
            documents_query = """
            INSERT INTO DOCUMENT (DOCID, TITLE, PDATE, PUBLISHERID)
            VALUES (%(DOCID)s, %(TITLE)s, %(PDATE)s, %(PUBLISHERID)s)
            ON DUPLICATE KEY UPDATE 
            TITLE=VALUES(TITLE),
            PDATE=VALUES(PDATE),
            PUBLISHERID=VALUES(PUBLISHERID);
            """
            
            stream = io.TextIOWrapper(file.stream._file, "UTF8", newline=None)
            
            for row in csv.DictReader(stream):
                document = {
                    'DOCID': row['DOCID'],
                    'TITLE': row['TITLE'],
                    'PDATE': row['PDATE'],
                    'PUBLISHERID': row['PUBLISHERID']
                }
                documents.append(document)
                
            if len(documents) > 0:
                print(f"Inserting or updating {len(documents)} documents")
                try:
                    result = DB.insertMany(documents_query, documents)
                    message = f"{len(documents)} documents inserted or updated"
                    flash(message, "success")
                except Exception as e:
                    traceback.print_exc()
                    flash("There was an error loading in the csv data", "danger")
            else:
                flash('No documents were loaded', "info")

            try:
                result = DB.selectOne("SHOW SESSION STATUS LIKE 'questions'")
                print(f"Result {result}")
            except Exception as e:
                    traceback.print_exc()
                    flash("There was an error counting session queries", "danger")
    return render_template("upload.html")




@upload.route("/upload_publishers", methods=["GET", "POST"])
def upload_publishers():
    if request.method == "POST":
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file', "warning")
            return redirect(request.url)
        
        if ".csv" not in file.filename:
            flash('Select CSV file', "warning")
            return redirect(request.url)
        if file and secure_filename(file.filename):
            publishers = []
            publishers_query = """
            INSERT INTO PUBLISHER (PUBLISHERID, PUBNAME, ADDRESS)
            VALUES (%(PUBLISHERID)s, %(PUBNAME)s, %(ADDRESS)s)
            ON DUPLICATE KEY UPDATE 
            PUBNAME=VALUES(PUBNAME),
            ADDRESS=VALUES(ADDRESS);
            """
            
            stream = io.TextIOWrapper(file.stream._file, "UTF8", newline=None)
            
            for row in csv.DictReader(stream):
                publisher = {
                    'PUBLISHERID': row['PUBLISHERID'],
                    'PUBNAME': row['PUBNAME'],
                    'ADDRESS': row['ADDRESS']
                }
                publishers.append(publisher)
                
            if len(publishers) > 0:
                print(f"Inserting or updating {len(publishers)} publishers")
                try:
                    result = DB.insertMany(publishers_query, publishers)
                    message = f"{len(publishers)} publishers inserted or updated"
                    flash(message, "success")
                except Exception as e:
                    traceback.print_exc()
                    flash("There was an error loading in the csv data", "danger")
            else:
                flash('No publishers were loaded', "info")

            try:
                result = DB.selectOne("SHOW SESSION STATUS LIKE 'questions'")
                print(f"Result {result}")
            except Exception as e:
                traceback.print_exc()
                flash("There was an error counting session queries", "danger")
    return render_template("upload.html")

@upload.route("/upload_persons", methods=["GET", "POST"])
def upload_persons():
    if request.method == "POST":
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file', "warning")
            return redirect(request.url)
        
        if ".csv" not in file.filename:
            flash('Select CSV file', "warning")
            return redirect(request.url)
        if file and secure_filename(file.filename):
            persons = []
            persons_query = """
            INSERT INTO PERSON (PID, PNAME)
            VALUES (%(PID)s, %(PNAME)s)
            ON DUPLICATE KEY UPDATE 
            PNAME=VALUES(PNAME);
            """
            
            stream = io.TextIOWrapper(file.stream._file, "UTF8", newline=None)
            
            for row in csv.DictReader(stream):
                person = {
                    'PID': row['PID'],
                    'PNAME': row['PNAME']
                }
                persons.append(person)
                
            if len(persons) > 0:
                print(f"Inserting or updating {len(persons)} persons")
                try:
                    result = DB.insertMany(persons_query, persons)
                    message = f"{len(persons)} persons inserted or updated"
                    flash(message, "success")
                except Exception as e:
                    traceback.print_exc()
                    flash("There was an error loading in the csv data", "danger")
            else:
                flash('No persons were loaded', "info")
    return render_template("upload.html")
