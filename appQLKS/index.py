from flask import render_template
from appQLKS import app, login
import dao


@app.route("/")
def index():
    return render_template('index.html')


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


if __name__ == '__main__':
    with app.app_context():
        #from appQLKS import admin

        app.run(debug=True)
