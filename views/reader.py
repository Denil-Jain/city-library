# Search a document by ID, title, or publisher name.(#DONE/09/04/24)
# Document checkout. (#route(/list_document_copies)) (#route /checkout #DONE 23/04/24)
# Document return.
# Document reserve.
# Compute fine for a document copy borrowed by a reader based on the current date.
# Print the list of documents reserved by a reader and their status.
# Print the document id and document titles of documents published by a publisher. (#DONE 09/04/24 already added route('/reader/search_documents'))
# Quit.

from flask import Blueprint, redirect, request, render_template, url_for, flash
import traceback
from sql.db import DB
reader = Blueprint('reader', __name__, url_prefix='/reader')
import datetime


@reader.route("/search_documents", methods=["GET"])
def search_documents():
    documents = []
    
    query = """
    SELECT DOCID, TITLE, PUBNAME
    FROM DOCUMENT NATURAL JOIN PUBLISHER
    WHERE 1=1
    """
    args = {}
    
    doc_id = request.args.get("doc_id")
    title = request.args.get("title")
    publisher_name = request.args.get("publisher_name")
    
    if doc_id:
        query += " AND DOCID = %(doc_id)s"
        args["doc_id"] = doc_id
    
    if title:
        query += " AND TITLE LIKE %(title)s"
        args["title"] = f"%{title}%"
    
    if publisher_name:
        query += " AND PUBNAME LIKE %(publisher_name)s"
        args["publisher_name"] = f"%{publisher_name}%"
    
    try:
        result = DB.selectAll(query, args)
        if result.status:
            documents = result.rows
    except Exception as e:
        traceback.print_exc()
        flash("There was an error searching the documents", "danger")
    
    return render_template("search_documents.html", documents=documents)

@reader.route("/list_document_copies", methods=["GET"])
def list_document_copies():
    copies = []
    
    query = """
    SELECT C.COPYNO, C.DOCID, D.TITLE, D.PUBLISHERID, C.BID, B.BNAME, B.BLOCATION
    FROM COPY C
    INNER JOIN DOCUMENT D ON C.DOCID = D.DOCID
    LEFT JOIN BRANCH B ON C.BID = B.BID
    WHERE NOT EXISTS (
        SELECT 1
        FROM BORROWS BOR NATURAL JOIN BORROWING
        WHERE C.DOCID = BOR.DOCID
        AND C.COPYNO = BOR.COPYNO
        AND C.BID = BOR.BID
        AND BORROWING.RDTIME IS NULL
    )
    """
    
    try:
        result = DB.selectAll(query)
        if result.status:
            copies = result.rows
    except Exception as e:
        traceback.print_exc()
        flash("There was an error listing document copies", "danger")
    
    return render_template("list_document_copies.html", copies=copies)



@reader.route("/checkout", methods=["GET", "POST"])
def checkout():
    args = {}


    if request.method == "POST":
        # Handle form submission for checkout
        reader_id = request.form.get("reader_id")
        doc_id = request.form.get("doc_id")
        copy_no = request.form.get("copy_no")
        bid = request.form.get("bid")
        if not reader_id:
            flash("Reader ID is required", "danger")
            return redirect(url_for("reader.checkout"))

        # Perform the checkout process
        try:
            # Insert current time into BORROWING table
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            insert_borrowing_query = "INSERT INTO BORROWING (BDTIME) VALUES (%(current_time)s)"
            print(insert_borrowing_query)
            borrowing_result = DB.insertOne(insert_borrowing_query, {"current_time":current_time})
            print(borrowing_result)
            if not borrowing_result.status:
                flash("Error during checkout: Unable to insert into BORROWING table", "danger")
                return redirect(url_for("reader.checkout"))
            
            # Get the BOR_NO from the last insert operation
            bor_no = DB.selectOne("SELECT MAX(BOR_NO) FROM `BORROWING`",{}).row["MAX(BOR_NO)"]
            print(bor_no)
            # Insert checkout request into BORROWS table
            insert_borrows_query = "INSERT INTO BORROWS (BOR_NO, DOCID, COPYNO, BID, RID) VALUES (%(bor_no)s, %(doc_id)s, %(copy_no)s, %(bid)s, %(reader_id)s)"
            print(insert_borrows_query)
            borrows_result = DB.insertOne(insert_borrows_query, {"bor_no": bor_no, "doc_id": doc_id, "copy_no": copy_no, "bid": bid, "reader_id": reader_id})
            print(borrows_result)
            if not borrows_result.status:
                flash("Error during checkout: Unable to insert into BORROWS table", "danger")
                return redirect(url_for("reader.checkout", doc_id=doc_id, copy_no=copy_no, bid=bid))

            flash("Checkout successful", "success")
            return redirect(url_for("reader.list_document_copies"))
        except Exception as e:
            flash(f"Error during checkout: {e}", "danger")
            return redirect(url_for("reader.checkout", doc_id=doc_id, copy_no=copy_no, bid=bid))


    else:
        # Handle GET request to display checkout form
        bid = request.args.get("bid")
        copy_no = request.args.get("copy_no")
        doc_id = request.args.get("doc_id")

        if not bid or not copy_no or not doc_id:
            flash("Checkout Copy details are incorrect or not provided", "danger")
            return redirect(url_for("reader.list_document_copies"))

        args["bid"] = bid
        args["copy_no"] = copy_no
        args["doc_id"] = doc_id

        try:
            # Fetch copy information directly from the COPY table
            query = "SELECT * FROM COPY WHERE DOCID = %(doc_id)s AND COPYNO = %(copy_no)s AND BID = %(bid)s"
            result = DB.selectOne(query, args)
            if not result or not result.row:
                flash("Copy information not found", "danger")
                return redirect(url_for("reader.list_document_copies"))
            copy_info = result.row
        except Exception as e:
            flash(f"Error retrieving copy information: {e}", "danger")
            return redirect(url_for("reader.list_document_copies"))

        return render_template("checkout.html", copy_info=copy_info)