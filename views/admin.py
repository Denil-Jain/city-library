# Administrative Functions Menu:
# - Add a document copy. (#Add Document 10/04/2024)
# - Search document copy and check its status. (#DONE 23/04/2024)
# - Add new reader. (#Add READER 10/04/2024 /admin/add_reader)
# - Print branch information (name and location).(# with filter 10/04/2024)
# - Get number N and branch number I as input and print the top N most frequent borrowers (Rid and name) in branch I and the number of books each has borrowed. (#DONE 24-04-2024 route(/frequent_borrower))
# - Get number N as input and print the top N most frequent borrowers (Rid and name) in the library and the number of books each has borrowed. (#DONE 24-04-2024 route(/frequent_borrower))
# - Get number N and branch number I as input and print the N most borrowed books in branch I. (#DONE 24-04-2024 route(/branch_most_borrowed_books))
# - Get number N as input and print the N most borrowed books in the library. (#DONE 24-04-2024 route(/most_borrowed_books))
# - Get a year as input and print the 10 most popular books of that year in the library. (#DONE 28-04-2024 route(/books_of_year))
# - Get a start date S and an end date E as input and print, for each branch, the branch ($DONE 30-04-2024)
#       Id and name and the average fine paid by the borrowers for documents borrowed
#       from this branch during the corresponding period of time.

from flask import Blueprint, redirect, request, render_template, url_for, flash
import traceback
from sql.db import DB
admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route("/add_document", methods=["GET","POST"])
def add_document():
    if request.method == "POST":
        DOCID = request.form.get('DOCID')
        TITLE = request.form.get('TITLE')
        PDATE = request.form.get('PDATE')
        PUBLISHERID = request.form.get('PUBLISHERID')
        print(DOCID,TITLE,PDATE,PUBLISHERID)
        has_error = False

        if not DOCID:
            flash('DOCID is missing','danger')
            has_error = True

        if not TITLE:
            flash('TITLE is missing','danger')
            has_error = True

        if not PDATE:
            flash('PDATE is missing','danger')
            has_error = True

        if not PUBLISHERID:
            flash('PUBLISHERID is missing','danger')
            has_error = True

        if DOCID:
            result = DB.selectOne("SELECT DOCID FROM DOCUMENT WHERE DOCID = %(DOCID)s",{"DOCID":DOCID})
            # print(result)
            if result.row:
                flash("Document ID Aready Exists",'danger')
                has_error = True

        if not has_error:
            try:
                result = DB.insertOne("""
                INSERT INTO DOCUMENT (DOCID, TITLE, PDATE, PUBLISHERID)
                VALUES (%(DOCID)s, %(TITLE)s, %(PDATE)s, %(PUBLISHERID)s)
                """,{
                        'DOCID': DOCID,
                        'TITLE': TITLE,
                        'PDATE': PDATE,
                        'PUBLISHERID': PUBLISHERID
                    }
                )
                if result.status:
                    # print("DOCUMENT ADDED")
                    flash("DOCUMENT ADDED", "success")
            except Exception as e:
                flash(str(e), "danger")

    return render_template("manage_document.html",document = request.form)

# Search document copy
@admin.route("/document_copies", methods=["GET"])
def list_document_copies():
    doc_name_filter = request.args.get('doc_name')
    doc_id_filter = request.args.get('doc_id')
    bid_filter = request.args.get('bid')
    
    args = {}
    query = """
        SELECT C.COPYNO, D.DOCID, D.TITLE, D.PUBLISHERID, B.BID, B.BNAME, B.BLOCATION, CASE 
            WHEN (C.COPYNO, D.DOCID, B.BID) IN (SELECT COPYNO, DOCID, BID
                                                FROM BORROWS 
                                                NATURAL JOIN BORROWING
                                                WHERE RDTIME IS NULL)
            THEN 1
            ELSE 0 
        END AS STATUS
        FROM DOCUMENT D
        JOIN COPY C ON D.DOCID = C.DOCID
        JOIN BRANCH B ON C.BID = B.BID
        WHERE 1=1
    """
    if doc_name_filter:
        query += " AND D.TITLE LIKE %(doc_name)s "
        args["doc_name"] = f'%{doc_name_filter}%'
    if doc_id_filter:
        query += " AND D.DOCID = %(doc_id)s "
        args["doc_id"] = doc_id_filter
    if bid_filter:
        query += " AND B.BID = %(bid)s "
        args["bid"] = bid_filter
    
    try:
        result = DB.selectAll(query, args)
        copies = result.rows if result.status else []
    except Exception as e:
        flash(str(e), "danger")
        copies = []

    return render_template("list_document_copies_status.html", copies=copies)


@admin.route("/add_reader", methods=["GET","POST"])
def add_reader():
    if request.method == "POST":
        RID = request.form.get('RID')
        RTYPE = request.form.get('RTYPE')
        RNAME = request.form.get('RNAME')
        RADDRESS = request.form.get('RADDRESS')
        PHONE_NO = request.form.get('PHONE_NO')

        has_error = False

        if not RID:
            flash('Reader ID is missing','danger')
            has_error = True

        if not RTYPE:
            flash('Reader Type is missing','danger')
            has_error = True

        if not RNAME:
            flash('Reader Name is missing','danger')
            has_error = True

        if not RADDRESS:
            flash('Reader Address is missing','danger')
            has_error = True
        if not PHONE_NO:
            flash('Phone Number is missing','danger')
            has_error = True

        if RID:
            result = DB.selectOne("SELECT RID FROM READER WHERE RID = %(RID)s",{"RID":RID})
            # print(result)
            if result.row:
                flash("Reader ID Aready Exists",'danger')
                has_error = True

        if not has_error:
            try:
                result = DB.insertOne("""
                INSERT INTO READER (RID, RTYPE, RNAME, RADDRESS, PHONE_NO)
                VALUES (%(RID)s, %(RTYPE)s, %(RNAME)s, %(RADDRESS)s, %(PHONE_NO)s)
                """,{
                        'RID': RID,
                        'RTYPE': RTYPE,
                        'RNAME': RNAME,
                        'RADDRESS': RADDRESS,
                        'PHONE_NO': PHONE_NO
                    }
                )
                if result.status:
                    # print("Reader ADDED")
                    flash("READER ADDED", "success")
            except Exception as e:
                flash(str(e), "danger")

    return render_template("manage_reader.html",reader = request.form)


@admin.route("/branches", methods=["GET","POST"])
def list_branches():
    name_filter = request.args.get('bname')
    location_filter = request.args.get('blocation')
    limit = request.args.get('limit')
    args = {}
    query = """
        SELECT BID, BNAME, BLOCATION
        FROM BRANCH
        WHERE 1=1
    """
    if name_filter:
        query += " AND BNAME LIKE %(name)s "
        args["name"] = f'%{name_filter}%'
    if location_filter:
        query += " AND BLOCATION LIKE %(location)s "
        args["location"] = f'%{location_filter}%'
    
    if not limit:
        query += " LIMIT 10"
    else:
        query += " LIMIT %(limit)s"
        args['limit'] = int(limit)
    #print(query,args)
    try:
        result = DB.selectAll(query, args)
        branches = result.rows if result.status else []
    except Exception as e:
        flash(str(e), "danger")
        branches = []

    return render_template("list_branches.html", branches=branches)

# - Get number N as input and print the N most borrowed books in the library.
@admin.route("/most_borrowed_books", methods=["GET","POST"])
def most_borrowed_books():
    documents = []
    
    query = """
    SELECT DOCID, TITLE, PUBNAME, COUNT(DOCID) AS CONT
    FROM BORROWS NATURAL JOIN DOCUMENT NATURAL JOIN PUBLISHER
    GROUP BY DOCID, TITLE, PUBNAME
    ORDER BY COUNT(DOCID) DESC
    """
    args = {}
    
    TOP_B = request.args.get("TOP_B")
    
    if TOP_B:
        query += F" LIMIT {TOP_B}"
    else:
        query += F" LIMIT 10"
    
    try:
        result = DB.selectAll(query, args)
        if result.status:
            documents = result.rows
    except Exception as e:
        traceback.print_exc()
        flash("There was an error searching the documents", "danger")
    
    return render_template("most_borrowed_books.html", documents=documents)



# - Get number N and branch number I as input and print the N most borrowed books in branch I
@admin.route("/branch_most_borrowed_books", methods=["GET","POST"])
def branch_most_borrowed_books():
    documents = []
    
    query = """
    SELECT DOCID, TITLE, PUBNAME, COUNT(DOCID) AS CONT
    FROM BORROWS NATURAL JOIN DOCUMENT NATURAL JOIN PUBLISHER
    WHERE 1=1 
    """
    args = {}
    
    TOP_B = request.args.get("TOP_B")
    BID = request.args.get("BID")
    
    if BID:
        query += f" AND BID = {BID} "

    query+= '''GROUP BY DOCID, TITLE, PUBNAME
                ORDER BY COUNT(DOCID) DESC'''
    if TOP_B:
        query += F" LIMIT {TOP_B}"
    else:
        query += F" LIMIT 10"
    
    try:
        result = DB.selectAll(query, args)
        if result.status:
            documents = result.rows
    except Exception as e:
        traceback.print_exc()
        flash(f"There was an error searching the documents: {e}", "danger")
    
    return render_template("branch_most_borrowed_books.html", documents=documents)

# - Get number N and branch number I as input and print the top N most frequent borrowers (Rid and name) in branch I and the number of books each has borrowed.
@admin.route("/frequent_borrower", methods=["GET","POST"])
def frequent_borrower():
    reader = []
    
    query = """
    SELECT RID, RNAME, COUNT(DOCID) AS NBOOKS
    FROM BORROWS NATURAL JOIN READER
    WHERE 1=1 
    """
    args = {}
    
    TOP_B = request.args.get("TOP_B")
    BID = request.args.get("BID")
    
    if BID:
        query += f" AND BID = {BID} "

    query+= '''GROUP BY RID, RNAME
                ORDER BY COUNT(DOCID) DESC'''
    if TOP_B:
        query += F" LIMIT {TOP_B}"
    else:
        query += F" LIMIT 10"
    
    try:
        result = DB.selectAll(query, args)
        if result.status:
            reader = result.rows
    except Exception as e:
        traceback.print_exc()
        flash(f"There was an error searching the documents: {e}", "danger")
    
    return render_template("frequent_borrower.html", readers=reader)


# - Get a year as input and print the 10 most popular books of that year in the library.
@admin.route("/books_of_year", methods=["GET","POST"])
def books_of_year():
    documents = []
    YEAR = request.args.get("YEAR")
    query = f"""
    SELECT DOCID, TITLE, PUBNAME , COUNT(DOCID) AS COUNT
    FROM BORROWS NATURAL JOIN DOCUMENT NATURAL JOIN PUBLISHER NATURAL JOIN BORROWING
    WHERE YEAR(BDTIME) = {YEAR}
    GROUP BY DOCID, TITLE, PUBNAME
    ORDER BY COUNT(DOCID) DESC
    """
    if YEAR:
        try:
            result = DB.selectAll(query, {})
            if result.status:
                documents = result.rows
        except Exception as e:
            traceback.print_exc()
            flash("There was an error searching the documents", "danger")
    
    return render_template("books_of_year.html", documents=documents)


# - Get a start date S and an end date E as input and print, for each branch, the branch
#       Id and name and the average fine paid by the borrowers for documents borrowed
#       from this branch during the corresponding period of time.
@admin.route("/fine_paid", methods=["GET","POST"])
def fine_paid():
    branches = []
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    query = f"""
    SELECT BRANCH.BID, BNAME, 
        SUM(CASE WHEN fine IS NOT NULL THEN fine ELSE 0 END) AS FINE
    FROM BRANCH 
    LEFT JOIN BORROWS ON BORROWS.`BID` = BRANCH.BID 
    LEFT JOIN (SELECT `BOR_NO`,RDTIME,
                        (CASE
                            WHEN RDTIME IS NOT NULL THEN (CASE WHEN DATEDIFF(RDTIME, BDTIME) > 20 
                            THEN (DATEDIFF(RDTIME, BDTIME) - 20) * 0.20 ELSE 0 END) 
                            ELSE 0
                        END) AS fine
                    FROM BORROWING 
                    NATURAL JOIN BORROWS 
                    WHERE RDTIME BETWEEN '{start_date}' AND '{end_date}') AS BOR ON `BOR`.`BOR_NO` = BORROWS.`BOR_NO`
    GROUP BY BRANCH.BID, BNAME;
    """
    print(query)

    if start_date and end_date:
        try:
            result = DB.selectAll(query, {})
            if result.status:
                branches = result.rows
        except Exception as e:
            traceback.print_exc()
            flash("There was an error searching the documents", "danger")
    
    return render_template("fine_paid.html", branches=branches)