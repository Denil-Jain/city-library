# Search a document by ID, title, or publisher name.(#DONE/09/04/24)
# Document checkout. (#route(/list_document_copies)) (#route /checkout #DONE 23/04/24)
# Document return. (#route(/return)) #DONE 24/04/24)
# Document reserve. (#route(/list_document_copies_reserve)) #DONE 30-04-2024
# Compute fine for a document copy borrowed by a reader based on the current date. (#While returning a document Fine is calculated. #24/04/24)
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
    args= {}
    query = """
    SELECT C.COPYNO, C.DOCID, D.TITLE, D.PUBLISHERID, C.BID, B.BNAME, B.BLOCATION
    FROM COPY C
    INNER JOIN DOCUMENT D ON C.DOCID = D.DOCID
    LEFT JOIN BRANCH B ON C.BID = B.BID
    NATURAL JOIN PUBLISHER
    WHERE NOT EXISTS (
        SELECT 1
        FROM BORROWS BOR NATURAL JOIN BORROWING
        WHERE C.DOCID = BOR.DOCID
        AND C.COPYNO = BOR.COPYNO
        AND C.BID = BOR.BID
        AND BORROWING.RDTIME IS NULL
    )
    """
    doc_id = request.args.get("doc_id")
    title = request.args.get("doc_name")
    publisher_name = request.args.get("publisher_name")
    
    if doc_id:
        query += " AND C.DOCID = %(doc_id)s"
        args["doc_id"] = doc_id
    
    if title:
        query += " AND D.TITLE LIKE %(title)s"
        args["title"] = f"%{title}%"
    
    if publisher_name:
        query += " AND PUBNAME LIKE %(publisher_name)s"
        args["publisher_name"] = f"%{publisher_name}%"
    
    try:
        result = DB.selectAll(query,args)
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
            check_limit_query = f'''
            SELECT COUNT(RID) AS VAL
            FROM BORROWING NATURAL JOIN BORROWS
            WHERE RDTIME IS NULL AND RID = {reader_id}
            '''
            check_limit_result = DB.selectOne(check_limit_query,args)
            print("check_limit_result",check_limit_result)
            if check_limit_result.row["VAL"] > 9:
                flash("Reader Limit: 10 Copies already taken", "warning")
                return redirect(url_for("reader.checkout", doc_id=doc_id, copy_no=copy_no, bid=bid))
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
    


@reader.route("/list_document_copies_reserve", methods=["GET"])
def list_document_copies_reserve():
    copies = []
    args= {}
    query = """
    SELECT C.COPYNO, C.DOCID, D.TITLE, D.PUBLISHERID, C.BID, B.BNAME, B.BLOCATION
    FROM COPY C
    INNER JOIN DOCUMENT D ON C.DOCID = D.DOCID
    LEFT JOIN BRANCH B ON C.BID = B.BID
    NATURAL JOIN PUBLISHER
    WHERE NOT EXISTS (
        SELECT 1
        FROM BORROWS BOR NATURAL JOIN BORROWING
        WHERE C.DOCID = BOR.DOCID
        AND C.COPYNO = BOR.COPYNO
        AND C.BID = BOR.BID
        AND BORROWING.RDTIME IS NULL
    )
    AND NOT EXISTS (
    SELECT 1
        FROM RESERVES RES JOIN RESERVATION ON RES.RESERVATION_NO = RES_NO
        WHERE C.DOCID = RES.DOCID
        AND C.COPYNO = RES.COPYNO
        AND C.BID = RES.BID
        AND  DATEDIFF(RESERVATION.DTIME,CURRENT_TIMESTAMP)=0
    )
    """
    doc_id = request.args.get("doc_id")
    title = request.args.get("doc_name")
    publisher_name = request.args.get("publisher_name")
    
    if doc_id:
        query += " AND C.DOCID = %(doc_id)s"
        args["doc_id"] = doc_id
    
    if title:
        query += " AND D.TITLE LIKE %(title)s"
        args["title"] = f"%{title}%"
    
    if publisher_name:
        query += " AND PUBNAME LIKE %(publisher_name)s"
        args["publisher_name"] = f"%{publisher_name}%"
    
    try:
        result = DB.selectAll(query,args)
        if result.status:
            copies = result.rows
    except Exception as e:
        traceback.print_exc()
        flash("There was an error listing document copies", "danger")
    
    return render_template("list_document_copies_reserve.html", copies=copies)



@reader.route("/reserve", methods=["GET", "POST"])
def reserve():
    args = {}
    if request.method == "POST":
        # Handle form submission for reserve
        reader_id = request.form.get("reader_id")
        doc_id = request.form.get("doc_id")
        copy_no = request.form.get("copy_no")
        bid = request.form.get("bid")
        if not reader_id:
            flash("Reader ID is required", "danger")
            return redirect(url_for("reader.checkout"))

        # Perform the reserve process
        try:
            check_limit_query_borrowing = f'''
            SELECT COUNT(RID) AS VAL
            FROM BORROWING NATURAL JOIN BORROWS
            WHERE RDTIME IS NULL AND RID = {reader_id}
            '''
            check_limit_query_reserve = f'''
            SELECT COUNT(RID) AS VAL
            FROM RESERVATION R JOIN RESERVES ON R.RES_NO = RESERVES.RESERVATION_NO
            WHERE DATEDIFF(DTIME,CURRENT_TIMESTAMP)=0 AND RID = {reader_id} 
            '''
            check_limit_result_borrowing = DB.selectOne(check_limit_query_borrowing,args)
            check_limit_result_reserve = DB.selectOne(check_limit_query_reserve,args)
            print("check_limit_result_borrowing",check_limit_result_borrowing)
            print("check_limit_result_reserve",check_limit_result_reserve)
            if check_limit_result_reserve.row["VAL"] + check_limit_result_borrowing.row["VAL"] > 9:
                flash("Reader Limit: 10 Copies already Borrowed or Reserved", "warning")
                return redirect(url_for("reader.reserve", doc_id=doc_id, copy_no=copy_no, bid=bid))
            # Insert current time into BORROWING table
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            insert_reservation_query = "INSERT INTO RESERVATION (DTIME) VALUES (%(current_time)s)"
            print(insert_reservation_query)
            reservation_result = DB.insertOne(insert_reservation_query, {"current_time":current_time})
            print(reservation_result)
            if not reservation_result.status:
                flash("Error during reserve: Unable to insert into RESERVATION table", "danger")
                return redirect(url_for("reader.reserve", doc_id=doc_id, copy_no=copy_no, bid=bid))
            
            # Get the RES_NO from the last insert operation
            res_no = DB.selectOne("SELECT MAX(RES_NO) FROM `RESERVATION`",{}).row["MAX(RES_NO)"]
            print(res_no)
            # Insert reserve request into RESERVES table
            insert_reserve_query = "INSERT INTO RESERVES (RESERVATION_NO, DOCID, COPYNO, BID, RID) VALUES (%(res_no)s, %(doc_id)s, %(copy_no)s, %(bid)s, %(reader_id)s)"
            print(insert_reserve_query)
            reserves_result = DB.insertOne(insert_reserve_query, {"res_no": res_no, "doc_id": doc_id, "copy_no": copy_no, "bid": bid, "reader_id": reader_id})
            print(reserves_result)
            if not reserves_result.status:
                flash("Error during Reservation: Unable to insert into RESERVES table", "danger")
                return redirect(url_for("reader.reserve", doc_id=doc_id, copy_no=copy_no, bid=bid))
            reader_name = DB.selectOne("SELECT RNAME FROM READER WHERE RID = %(reader_id)s",{"reader_id":reader_id})
            print(reader_name)
            flash(f"Reservation successful by {reader_name.row['RNAME']}", "success")
            return redirect(url_for("reader.list_document_copies_reserve"))
        except Exception as e:
            flash(f"Error during reservation: {e}", "danger")
            return redirect(url_for("reader.reserve", doc_id=doc_id, copy_no=copy_no, bid=bid))


    else:
        # Handle GET request to display checkout form
        bid = request.args.get("bid")
        copy_no = request.args.get("copy_no")
        doc_id = request.args.get("doc_id")

        if not bid or not copy_no or not doc_id:
            flash("Reservation Copy details are incorrect or not provided", "danger")
            return redirect(url_for("reader.list_document_copies_reserve"))

        args["bid"] = bid
        args["copy_no"] = copy_no
        args["doc_id"] = doc_id

        try:
            # Fetch copy information directly from the COPY table
            query = "SELECT * FROM COPY WHERE DOCID = %(doc_id)s AND COPYNO = %(copy_no)s AND BID = %(bid)s"
            result = DB.selectOne(query, args)
            if not result or not result.row:
                flash("Copy information not found", "danger")
                return redirect(url_for("reader.list_document_copies_reserve"))
            copy_info = result.row
        except Exception as e:
            flash(f"Error retrieving copy information: {e}", "danger")
            return redirect(url_for("reader.list_document_copies_reserve"))

        return render_template("reserve.html", copy_info=copy_info)
    
@reader.route("/return_copy", methods=["GET", "POST"])
def return_copy():
    RID = request.args.get("RID")
    if not RID:
        return render_template("return_copy.html")
    DOCID = request.args.get("DOCID")
    COPYNO = request.args.get("COPYNO")
    BID = request.args.get("BID")
    BOR_NO = request.args.get("BOR_NO")
    
    if RID and not DOCID:
        try:
            query = """ SELECT * 
                        FROM COPY C JOIN BORROWS B ON C.`DOCID` = B.`DOCID`AND C.`COPYNO` = B.`COPYNO` AND C.BID = B.`BID`  
                            JOIN BORROWING ON `BORROWING`.`BOR_NO` = B.`BOR_NO` 
                            NATURAL JOIN READER 
                            JOIN DOCUMENT ON DOCUMENT.`DOCID` = C.`DOCID` 
                        WHERE RID = %(RID)s AND RDTIME IS NULL"""
            result = DB.selectAll(query,{"RID":RID})
            if result.status and len(result.rows)>0:
                # print(result.rows)
                return render_template("return_copy.html",copies=result.rows,reader_name=result.rows[0]["RNAME"])
            else:
                flash("Nothing to Return","warning")
                return render_template("return_copy.html",copies=result.rows)
        except Exception as e:
            flash(f"Error retrieving borrowed copy inforamtion: {e}", "danger")
            return render_template("return_copy.html")
    else:
        try:
            query = """
                    SELECT RNAME,
                        CASE
                            WHEN RDTIME IS NULL THEN DATEDIFF(CURRENT_DATE(), BDTIME) - 20
                            ELSE DATEDIFF(RDTIME, BDTIME) - 20
                        END AS days_overdue,
                        CASE
                            WHEN RDTIME IS NULL THEN (CASE WHEN DATEDIFF(CURRENT_DATE(), BDTIME) > 20 THEN (DATEDIFF(CURRENT_DATE(), BDTIME) - 20) * 0.20 ELSE 0 END)
                            ELSE (CASE WHEN DATEDIFF(RDTIME, BDTIME) > 20 THEN (DATEDIFF(RDTIME, BDTIME) - 20) * 0.20 ELSE 0 END)
                        END AS fine
                    FROM BORROWING NATURAL JOIN BORROWS NATURAL JOIN READER
                    WHERE BOR_NO = %(BOR_NO)s
                    AND DOCID = %(DOCID)s
                    AND COPYNO = %(COPYNO)s
                    AND BID = %(BID)s;
                    """
            print(BOR_NO,DOCID,COPYNO,BID)
            print(query)
            result = DB.selectAll(query,{"BOR_NO" : BOR_NO , "DOCID" : DOCID, "COPYNO": COPYNO, "BID":BID})
            print(result.status)
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            result_update = DB.update("UPDATE BORROWING SET RDTIME = %(current_time)s WHERE BOR_NO = %(BOR_NO)s", {"BOR_NO" : BOR_NO, "current_time" : current_time})
            if result.status:
                flash(f"{result.rows[0]['RNAME']}'s Document Returned AND Fine: {result.rows[0]['fine']}","success")
                return render_template(f"return_copy.html",RID=RID)
        except Exception as e:
            flash(f"Error {e}", "danger")
            return render_template("return_copy.html")
        

@reader.route("/reserved_copy", methods=["GET", "POST"])
def reserved_copy():
    RID = request.args.get("RID")
    if not RID:
        return render_template("reserved_copy.html")
    
    if RID:
        try:
            query = """ SELECT * , CASE
                                    WHEN (C.DOCID,C.COPYNO,C.BID,READER.RID) IN (SELECT B2.DOCID,B2.COPYNO,B2.BID,B2.RID
                                                                    FROM BORROWS B2 NATURAL JOIN BORROWING WHERE B2.RID = %(RID)s AND BDTIME>DTIME AND RDTIME IS NULL) 
                                        THEN 1 
                                    WHEN (C.DOCID,C.COPYNO,C.BID,READER.RID) IN (SELECT B2.DOCID,B2.COPYNO,B2.BID,B2.RID
                                                                    FROM BORROWS B2 NATURAL JOIN BORROWING WHERE B2.RID = %(RID)s AND BDTIME>DTIME AND RDTIME IS NOT NULL) 
                                        THEN 2
                                    ELSE 0 END AS STATUS
                        FROM COPY C JOIN RESERVES R ON C.`DOCID` = R.`DOCID`AND C.`COPYNO` = R.`COPYNO` AND C.BID = R.`BID`  
                            JOIN RESERVATION ON `RESERVATION`.`RES_NO` = R.`RESERVATION_NO` 
                            JOIN READER ON R.RID = READER.RID
                            JOIN DOCUMENT ON DOCUMENT.`DOCID` = C.`DOCID` 
                        WHERE R.RID = %(RID)s """
            result = DB.selectAll(query,{"RID":RID})
            if result.status and len(result.rows)>0:
                # print(result.rows)
                return render_template("reserved_copy.html",copies=result.rows,reader_name=result.rows[0]["RNAME"])
            else:
                flash("Nothing Reserved","warning")
                return render_template("reserved_copy.html",copies=result.rows)
        except Exception as e:
            flash(f"Error retrieving reserved copy inforamtion: {e}", "danger")
            return render_template("reserved_copy.html")
    else:
        return render_template("return_copy.html")
        
