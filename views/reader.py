# Search a document by ID, title, or publisher name.(#DONE/09/04/24)
# Document checkout.
# Document return.
# Document reserve.
# Compute fine for a document copy borrowed by a reader based on the current date.
# Print the list of documents reserved by a reader and their status.
# Print the document id and document titles of documents published by a publisher.
# Quit.

from flask import Blueprint, redirect, request, render_template, url_for, flash
import traceback
from sql.db import DB
reader = Blueprint('reader', __name__, url_prefix='/reader')


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