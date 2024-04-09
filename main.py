# from https://towardsdatascience.com/deploy-to-google-cloud-run-using-github-actions-590ecf957af0
import os
import sys
from flask import Flask, session, render_template, request, flash
from dotenv import load_dotenv
from sql.db import DB


load_dotenv()
# added so modules can be found between the two different lookup states:
# from tests and from regular running of the app
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
print(CURR_DIR)
sys.path.append(CURR_DIR)

# custom error pages
def page_not_found(e):
    return render_template('404.html'), 404

def permission_denied(e):
    return render_template("403.html"), 403

app = Flask(__name__)
app.register_error_handler(404, page_not_found)
app.register_error_handler(403, permission_denied)
app.secret_key = os.environ.get("SECRET_KEY", "missing_secret")

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
                # invalid user and invalid password together is too much info for a potential attacker
                # normally we return a single message for both "invalid username or password" so an attacker doens't know which part was correct
                flash("Invalid user", "warning")
        except Exception as e:
            flash(str(e), "danger")

    return render_template("home.html")
    # return 'Hello, World!'


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