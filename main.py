import os
import sys
from flask import Flask, session, render_template, request, flash
from dotenv import load_dotenv
from sql.db import DB
from views.upload import upload
from views.reader import reader
from views.admin import admin
from flask_caching import Cache

load_dotenv()
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
print(CURR_DIR)
sys.path.append(CURR_DIR)

def page_not_found(e):
    return render_template('404.html'), 404

def permission_denied(e):
    return render_template("403.html"), 403

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
def create_app():
    app = Flask(__name__)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(403, permission_denied)
    app.secret_key = os.environ.get("SECRET_KEY", "missing_secret")
    app.register_blueprint(upload)
    app.register_blueprint(reader)
    app.register_blueprint(admin)

    @app.route('/', methods = ["GET","POST"])
    def hello_world():
        if request.method == "POST":
            id = request.form.get('ReaderId')
            print(id)

            try:
                print("I am here")
                result = DB.selectOne("SELECT * FROM READER where RID= %(id)s", {"id":id})
                print(result)
                if result.status and result.row:
                    name = result.row['RNAME']
                    return render_template('reader.html',name = name)
                else:
                    flash("Invalid user", "warning")
            except Exception as e:
                flash(str(e), "danger")

        return render_template("home.html")
        # return 'Hello, World!'

    cache.init_app(app)
    with app.app_context():
        @app.template_global()
        @cache.cached(timeout=30) # cache for 30 seconds since this is expensive
        def get_publishers():
            from sql.db import DB
            try:
                print("get publisher")
                result = DB.selectAll("SELECT PUBLISHERID, PUBNAME FROM PUBLISHER ORDER BY PUBNAME")
                if result.status:
                    return result.rows or []
            except Exception as e:
                print(e)
            return []
        # DON'T DELETE, this cleans up the DB connection after each request
        # this avoids sleeping queries
        @app.teardown_request 
        def after_request_cleanup(ctx):
            from sql.db import DB
            DB.close()
        return app
app = create_app()



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))


# from flask import Flask, render_template
# import os
# app = Flask(__name__)

# @app.route('/')
# def hello_world():
#     return render_template("home.html")
#     # return 'Hello, World!'

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))