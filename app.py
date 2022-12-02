from flask import Flask, request, render_template, flash, redirect, url_for, session
from flask_login import LoginManager, UserMixin, current_user, logout_user, login_user, login_required
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///players.sqlite3'
db = SQLAlchemy(app)
app.secret_key = 'hello world'
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    firstname = db.Column("firstname", db.String)
    lastname = db.Column("lastname", db.String)
    email = db.Column("email", db.String)
    password = db.Column("password", db.String)
    score = db.Column("score", db.Integer, default=0)

    def __init__(self, firstname, lastname, email, password, score=0, *args, **kwargs):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = password
        self.score = score


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') != request.form.get('retypePassword'):
            flash('tu n\'as pas retypé le mot de passe correctement', 'error')
        else:
            email = request.form.get('email')
            try:
                user = User.query.filter_by(email=email).first()
                if user is None:
                    flash('pas d\' utiliateur inscrit par cet email', 'error')
                elif user.password == request.form.get('password'):
                    login_user(user=user)
                    return redirect(url_for('quiz', numero=0))
            except Exception as exception:
                print(exception)
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('quiz'))
    if request.method == 'POST':
        if request.form.get('password') != request.form.get('retypePassword'):
            flash('tu n\'as pas retypé le mot de passe correctement', 'error')
        email = request.form.get('email')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        password = request.form.get('password')
        if User.query.filter_by(email=email).first() is None:
            user = User(firstname, lastname, email, password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            flash('cet email est déjà utilisé')
    return render_template('signup.html')


questions = [
    {
        'question': 'Que signifie le sigle IST ?',
        'choix': ['Infection sexuellement transmissible', 'Institut sexuel de Toulouse',
                  'Information scientifique et technique'],
        'correct': 0,
        'comment': "Les infections sexuellement transmissibles (IST), autrefois appelées maladies sexuellement "
                   "transmissibles (MST), sont des infections pouvant être transmises lors des relations sexuelles, "
                   "avec ou sans pénétration"
    },
    {
        'question': 'Quel est le meilleur moyen de savoir si l&#39;on a une IST ?',
        'choix': ['Se renseigner sur des forums/internet', 'Se faire dépister (V)',
                  'Acheter un test en pharmacie'],
        'correct': 1,
        'comment': "(L&#39;autotest VIH permet le dépistage du VIH, le virus du SIDA. Il est réalisé à partir "
                   "d&#39;une goutte desang et grâce à un autopiqueur) "
    },
    {
        'question': 'Le VIH se transmet uniquement par :',
        'choix': ['Les moustiques, l&#39;urine', 'La salive, les baisers, les larmes',
                  'Acheter un test en pharmacie'],
        'correct': 1,
        'comment': "(L&#39;autotest VIH permet le dépistage du VIH, le virus du SIDA. Il est réalisé à partir "
                   "d&#39;une goutte desang et grâce à un autopiqueur) "
    },

]


@app.route('/quiz/<numero>', methods=['GET', 'POST'])
@login_required
def quiz(numero):
    numero = int(numero) if numero is not None else 0
    if numero == 0:
        current_user.score = 0
        db.session.commit()
    if request.method == 'GET':
        return render_template('quiz.html', current_user=current_user, question=questions[numero],
                               correct=questions[numero].get('choix')[questions[numero].get('correct')],
                               numero=numero, comment=questions[numero].get('comment'))
    elif request.method == 'POST':
        if request.form.get('response') == questions[numero].get('choix')[questions[numero].get('correct')]:
            current_user.score += 1
            db.session.commit()
        numero += 1
        if numero == len(questions):
            return redirect('/result')
        else:
            return redirect(url_for('quiz', numero=numero))


@app.route('/result')
@login_required
def result():
    return render_template('result.html', current_user=current_user)


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
