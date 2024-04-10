# Administrative Functions Menu:
# - Add a document copy. (#Add Document 10/04/2024)
# - Search document copy and check its status.
# - Add new reader. (#Add READER 10/04/2024 /admin/add_reader)
# - Print branch information (name and location).(# with filter 10/04/2024)
# - Get number N and branch number I as input and print the top N most frequent borrowers (Rid and name) in branch I and the number of books each has borrowed.
# - Get number N as input and print the top N most frequent borrowers (Rid and name) in the library and the number of books each has borrowed.
# - Get number N and branch number I as input and print the N most borrowed books in branch I.
# - Get number N as input and print the N most borrowed books in the library.
# - Get a year as input and print the 10 most popular books of that year in the library.
# - Get a start date S and an end date E as input and print, for each branch, the branch
# Id and name and the average fine paid by the borrowers for documents borrowed
# from this branch during the corresponding period of time.

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
    print(query,args)
    try:
        result = DB.selectAll(query, args)
        branches = result.rows if result.status else []
    except Exception as e:
        flash(str(e), "danger")
        branches = []

    return render_template("list_branches.html", branches=branches)
