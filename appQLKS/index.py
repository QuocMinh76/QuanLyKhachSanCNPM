from flask import render_template
from appQLKS import app


@app.route("/")
def index():
    return render_template('index.html')


if __name__ == '__main__':
    with app.app_context():
        from appQLKS import admin

        app.run(debug=True)
