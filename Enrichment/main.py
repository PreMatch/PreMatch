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
        date = request.form.get('date', '')
        return str(session.fetch_schedule('6/17/2019' if date in [None, ''] else date))


@app.route('/hello')
def say_hello():
    return 'hello!'


app.run()