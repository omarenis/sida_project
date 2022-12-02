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
                   "transmissibles MST, sont des infections pouvant être transmises lors des relations sexuelles, "
                   "avec ou sans pénétration"
    },
    {
        'question': 'Quel est le meilleur moyen de savoir si l&#39;on a une IST ?',
        'choix': ['Se renseigner sur des forums/internet', 'Se faire dépister',
                  'Acheter un test en pharmacie'],
        'correct': 1,
        'comment': "autotest VIH permet le dépistage du VIH, le virus du SIDA. Il est réalisé à partir "
                   "d'une goutte desang et grâce à un autopiqueur"
    },
    {
        'question': 'Le VIH se transmet uniquement par :',
        'choix': ["Les moustiques, l'urine", "La salive, les baisers, les larmes",
                  "Les liquides sexuels, le sang, le lait maternel, le sperme"],
        'correct': 1,
        'comment': "(Le VIH ne peut être transmis que lorsque le virus présent dans l’un de ces liquides organiques "
                   "entre en contact avec la circulation sanguine d’une personne séronégative pour le VIH, "
                   "soit par une lésion cutanée, soit par des muqueuses (les tissus «humides» tapissant les "
                   "orifices de l’organisme). "
    },
    {
        'question': "Une IST est-elle signe d'une mauvaise hygiène ?",
        'choix': ["Oui",
                  "Non ça n'a rien à voir",
                  "Cela dépend de l'IST"],
        'correct': 1,
        'comment': "Les Infections Sexuellement Transmissibles IST ne sont pas liées à une mauvaise hygiène, "
                   "ne sont pas héréditaires et nécessitent la consultation d'un médecin avant d'entreprendre "
                   "un traitement..."
    },
    {
        'question': 'Le résultat du centre de dépistage du VIH est certain :',
        'choix': ["48h après une prise de risque",
                  "15 jours après une prise de risque",
                  "6 semaines après une prise de risque"],
        'correct': 2,
        'comment': "(Le test de VIH est aussi appelé « test ou analyse de sérologie VIH (ou HIV) ». Sur le papier du "
                   "laboratoire qui vous sera remis en guise de résultat, il y aura aussi certainement le nom "
                   "commercial du test utilisé.) "
    },
    {
        'question': 'Considérez-vous que les maladies sexuellement transmissibles est un sujet tabou ?',
        'choix': ["Oui, c’est un sujet sensibles et personnels",
                  "Non, c’est un sujet comme un autre",
                  ],
        'correct': -1,
        'comment': "(En Afrique, parlez de sexe est considéré comme un sujet tabou parce que cela est considérez "
                   "comme étant à l’encontre des principes) "
    },
    {
        'question': 'La multiplication des partenaires est-elle risquée?',
        'choix': ["oui nous sommes exposé(e)s",
                  "Non, aucun soucis",
                  ],
        'correct': -1,
        'comment': "(Avoir plusieurs partenaires nous fait entrer dans un environnement instable ou on connait pas "
                   "forcément notre partenaire)"
    },
    {
        'question': 'Dois-je me tester ou demander à mon partenaire ?',
        'choix': ["oui si je suis sexuellement actif(ve)",
                  "non j'ai pas de symptômes",
                  ],
        'correct': -1,
        'comment': "(Avoir plusieurs partenaires nous fait entrer dans un environnement instable ou on connait pas "
                   "forcément notre partenaire ) "
    },
    {
        'question': 'Est-ce que les parents doivent avoir une discussion sur la santé sexuelle avec leurs enfant?',
        'choix': ["oui c'est à eux de prévenir",
                  "non, c’est pas un sujets à aborder avec ses enfants",
                  ],
        'correct': -1,
        'comment': "(Ne pas informer son enfant reste le meilleurs moyen pour le pousser à aller vers l’information, "
                   "ce qui reste assez risquer avec toutes les technologies en place) "
    },
    {
        'question': 'La santé sexuelle doit-il être un sujet pour les lycées ou/et dans les universités ?',
        'choix': ["oui, c’est le lieu le plus adapté pour l’apprentissage",
                  "non, cela n’est pas nécessaire"
                  ],
        'correct': -1,
        'comment': "(L’école reste le moyen le plus approprié pour parler de la santé sexuelle surtout à "
                   "l’adolescence apprendre à connaitre son corps, ses pulsions pour ne pas aller vers l’information) "
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
        if request.form.get('choix') == questions[numero].get('choix')[questions[numero].get('correct')]:
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
