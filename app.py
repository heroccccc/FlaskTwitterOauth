from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import tweepy
import re

CK = "******************************"
# Consumer Key
CS = "******************************"
# Consumer Secret

CALLBACK_URL = "******************************"



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(80), unique=True)

    def __init__(self, username):
        self.userName = username

@app.route("/")
def hello():
    if not session.get('now_user'):
        return render_template("main.html")
    else:
        print(session.get('now_user'))
        return render_template("main.html",username=session.get('now_user'))


@app.route("/loginpage")
def gologinpage():
    auth = tweepy.OAuthHandler(CK, CS, CALLBACK_URL)

    # 以下は、アクセストークンをもらいにいく場合のコード。
    # まず、認証コードを貰いに行くアドレスを取得する
    try:

        redirect_url = auth.get_authorization_url()
        #もうすでに一度認証しているか確認
        redirect_url = re.sub( 'authorize','authenticate', redirect_url )

        #認証して戻ってきた値をsessionに保存
        session['request_token'] = auth.request_token

    except tweepy.TweepError:
        print("Error! Failed to get request token.")

    #http://127.0.0.1:5000/ から
    return redirect(redirect_url)


@app.route("/login")
def login():
    session['verifier'] = request.args.get('oauth_verifier')

    #sessionを使って認証する
    verifier = session.get('verifier')

    auth = tweepy.OAuthHandler(CK, CS)
    auth.request_token = session.get('request_token')
    session.pop('request_token', None)

    # Access TokenとAccess Token Secretを取得してそれぞれオブジェクト
    auth.get_access_token(verifier)
    ACCESS_TOKEN = auth.access_token
    ACCESS_SECRET = auth.access_token_secret
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

    api = tweepy.API(auth)

    accountName = str(api.me().name)
    session['now_user'] = accountName

    #別に必要ない
    if not Account.query.filter_by(userName=accountName).first():
        newAccount = Account(username=accountName)
        db.session.add(newAccount)
        db.session.commit()

    return redirect(url_for('hello'))


@app.route("/logout")
def logout():
    session.pop('now_user', None)
    return redirect(url_for('hello'))


if __name__ == "__main__":
    db.create_all()
    app.secret_key = "******************************"
    app.run(host='0.0.0.0')
