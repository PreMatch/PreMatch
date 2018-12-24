from flask import *
import enstu

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('google-signin.html')
    else:
        token = request.form.get('id_token')
        session = enstu.login(token)
        return str(session.fetch_schedule(request.form.get('date', '12/5/2018')))


@app.route('/hello')
def say_hello():
    return 'hello!'