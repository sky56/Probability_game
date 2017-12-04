from flask import Flask, render_template, request
import psycopg2
from flask_sqlalchemy import SQLAlchemy
from random import randint

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:123456@localhost/betgame'
db = SQLAlchemy(app)

#The Database Model with table name and column name
class Data(db.Model):
    __tablename__ = "bettrans"
    id = db.Column(db.Integer,primary_key=True)
    user_id_ = db.Column(db.Integer)
    bet_user_id_ = db.Column(db.Integer)
    bet_amount_ = db.Column(db.Integer)
    current_amount_ = db.Column(db.Integer)
    bet_win_ = db.Column(db.Integer)

def __init__(self,user_id_,user_bet_id_,bet_amount_,current_amount_,bet_win_):
    self.user_id_ = user_id_
    self.bet_user_id_ = bet_user_id_
    self.bet_amount_ = bet_amount_
    self.current_amount_ = current_amount_
    self.bet_win_ = bet_win_


@app.route("/",methods=['GET','POST'])
def users():
    if request.method=='POST':
        user_id = request.form["user_id"]
        conn = psycopg2.connect("dbname='betgame' user='postgres' password='123456' host='localhost' port='5432'")
        cur = conn.cursor()
        #Checks in database whether user is present
        cur.execute("select count(*) from bettrans where user_id_=%s",(user_id,))
        count=cur.fetchall()
        average_bet_size = ""
        win_percent = ""
        current_amount = ""
        if count[0][0] == 0:
            #Inserts the user ID if not present
            cur.execute("insert into bettrans(user_id_,bet_user_id_,current_amount_) values (%s,%s,%s)",(user_id,0,1000))
            conn.commit()
        else:
            #Selects last transaction of the user and fetches details
            cur.execute("select * from bettrans where user_id_=%s AND bet_user_id_=( select max(bet_user_id_) from bettrans where user_id_=%s)",(user_id,user_id))
            rows=cur.fetchall()
            bet_id = rows[0][2]
            #If no transaction, then average_bet_size and win_percent will be null
            if bet_id == 0:
                average_bet_size = ""
                win_percent = ""
            #Else computes average_bet_size and win_percent from previous transactions
            else:
                cur.execute("select sum(bet_amount_) from bettrans where user_id_=%s",(user_id,))
                sum_bet_rows = cur.fetchall()
                sum_bet = sum_bet_rows[0][0]
                average_bet_size = sum_bet/(count[0][0]-1)
                average_bet_size = round(average_bet_size,2)

                cur.execute("select sum(bet_win_) from bettrans where user_id_=%s",(user_id,))
                win_bet_rows = cur.fetchall()
                win_bet = win_bet_rows[0][0]
                win_percent = win_bet*100/(count[0][0]-1)
                win_percent = round(win_percent,2)

            current_amount = rows[0][4]
        conn.close()
        #Renders betgame.html with all the field values
        return render_template("betgame.html",user_id = user_id,average_bet_size=average_bet_size,win_percent=win_percent,current_amount=current_amount)
    return render_template("users.html")

@app.route("/bet",methods=['POST','GET'])
def bet():
    if request.method=='POST':
        bet_amount = request.form["bet_amount"]
        user_id = request.form["user_id"]
        average_bet_size = ""
        win_percent = ""
        current_amount = ""
        success = ""
        failure = ""
        conn = psycopg2.connect("dbname='betgame' user='postgres' password='123456' host='localhost' port='5432'")
        cur = conn.cursor()
        #Checks the last transaction of the user
        cur.execute("select * from bettrans where user_id_=%s AND bet_user_id_=( select max(bet_user_id_) from bettrans where user_id_=%s)",(user_id,user_id))
        rows=cur.fetchall()
        previous_amount = rows[0][4]
        bet_id = rows[0][2]

        cur.execute("select sum(bet_amount_) from bettrans where user_id_=%s",(user_id,))
        sum_bet_rows = cur.fetchall()
        sum_bet = sum_bet_rows[0][0]

        cur.execute("select sum(bet_win_) from bettrans where user_id_=%s",(user_id,))
        win_bet_rows = cur.fetchall()
        win_bet = win_bet_rows[0][0]

        #Since biasness is 60%, so below 60 is a success
        toss = randint(1,100)
        if toss <= 60:
            isWin = 1
            success = "Congrats! You won"
            failure = ""
            win_value = 1
        else:
            isWin = -1
            failure = "Sorry, you lost."
            success = ""
            win_value = 0

        current_amount = previous_amount + int(bet_amount)*isWin
        #If there is no previous transaction
        if bet_id == 0:
            average_bet_size = float(bet_amount)
            win_percent = win_value*100
        #Computes the result from previous transaction
        else:
            sum_bet = sum_bet + int(bet_amount)
            average_bet_size = sum_bet/(bet_id + 1)
            win_bet = win_bet + win_value
            win_percent = win_bet*100/(bet_id + 1)

        average_bet_size = round(average_bet_size,2)
        win_percent = round(win_percent,2)
        win_percent = str(win_percent)+'%'
        #Inserts the Current transaction values in the database
        cur.execute("insert into bettrans(user_id_,bet_user_id_,bet_amount_,current_amount_,bet_win_) values (%s,%s,%s,%s,%s)",(user_id,(bet_id+1),bet_amount,current_amount,win_value))
        conn.commit()
        conn.close()
        return render_template("betgame.html",user_id=user_id,bet_amount=bet_amount,success=success,failure=failure,current_amount=current_amount,average_bet_size=average_bet_size,win_percent=win_percent)
    return render_template("users.html")

if __name__ == "__main__":
    app.run(debug=True)
