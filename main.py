from flask import Flask, render_template, request, json, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import math
import json
import datetime
now = datetime.datetime.now()

import calculate

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:postgres@localhost/hcm'
app.config['SQLALCHEMY_DATABASE_URI']='postgres://ujsecbijerrvjy:6f902fcecbd65d98af03b8afe6e8f1db91d68dc7802eeb4ef5b7fcfa77d7ac42@ec2-107-21-224-76.compute-1.amazonaws.com:5432/d9c9ung4cv9io3?sslmode=require'
db = SQLAlchemy(app)

class Payment(db.Model):
    __tablename__ = "payment"
    pay_id = db.Column(db.Integer, primary_key = True)
    pay_name = db.Column(db.String(120))
    reg_dm = db.Column(db.String(120))

    def __init__(self, pay_name, reg_dm):
        self.pay_name = pay_name
        self.reg_dm = reg_dm

class Member(db.Model):
    __tablename__ = "member"
    pay_member_id = db.Column(db.Integer, primary_key = True)
    pay_id = db.Column(db.Integer)
    pay_member_nm = db.Column(db.String(120))
    reg_dm = db.Column(db.String(120))

    def __init__(self, pay_id, pay_member_nm, reg_dm):
        self.pay_id = pay_id
        self.pay_member_nm = pay_member_nm
        self.reg_dm = reg_dm

class Round(db.Model):
    __tablename__ = "round"
    round_id = db.Column(db.Integer, primary_key = True)
    round_nm = db.Column(db.String(120))
    round_price = db.Column(db.Integer)
    pay_id = db.Column(db.Integer)
    pay_round_mst = db.Column(db.Integer)
    pay_round_member = db.Column(db.String(120))
    reg_dm = db.Column(db.String(120))

    def __init__(self, round_nm, round_price, pay_id, pay_round_mst, pay_round_member, reg_dm):
        self.round_nm = round_nm
        self.round_price = round_price
        self.pay_id = pay_id
        self.pay_round_mst = pay_round_mst
        self.pay_round_member = pay_round_member
        self.reg_dm = reg_dm




@app.route("/")
def index():
    return render_template("index.html")

################ pay.html ################
def get_member_id_list(pay_id):
    pay_member_db = db.session.query(Member).filter(Member.pay_id == pay_id).order_by(Member.pay_member_id).all()
    pay_member_id = []
    pay_member_list = []
    for member in pay_member_db:
        pay_member_id.append(member.pay_member_id)
        pay_member_list.append(member.pay_member_nm)

    return [pay_member_id, pay_member_list]


@app.route('/pay_register', methods=['POST'])
def pay_register():
    pay_name = request.form['pay_name']
    reg_dm = str(now)[:19]

    payment = Payment(pay_name, reg_dm)

    db.session.add(payment)
    db.session.commit()
    pay_id = db.session.query(func.max(Payment.pay_id)).scalar()

    params = {'pay_id' : pay_id}

    return jsonify(params)


@app.route('/pay/<pay_id>')
def pay(pay_id):
    pay_id = pay_id
    pay_name = db.session.query(Payment).filter(Payment.pay_id == pay_id).first().pay_name
    
    #화면에서 새로고침 할 수 있으니 리스트 전달해줘야한다.
    pay_member_id = get_member_id_list(pay_id)[0]
    pay_member_list = get_member_id_list(pay_id)[1]

    return render_template("pay.html", pay_id=pay_id, pay_name=pay_name, pay_member_id=pay_member_id, pay_member_list=pay_member_list)


@app.route('/select_member_nm')
def select_member_nm():
    pay_member_id = request.args.get('pay_member_id')

    pay_member_nm = db.session.query(Member).filter(Member.pay_member_id == pay_member_id).first().pay_member_nm

    return jsonify(pay_member_nm=pay_member_nm)


@app.route('/add_pay_member')
def add_pay_member():
    pay_id = request.args.get('pay_id')
    pay_member_nm = request.args.get('pay_member_nm')
    reg_dm = str(now)[:19]

    member = Member(pay_id, pay_member_nm, reg_dm)
    db.session.add(member)
    db.session.commit()

    pay_member_id = get_member_id_list(pay_id)[0]
    pay_member_list = get_member_id_list(pay_id)[1]

    return jsonify(pay_member_id=pay_member_id, pay_member_list=pay_member_list)


@app.route('/delete_pay_member')
def delete_pay_member():
    pay_id = request.args.get('pay_id')
    pay_member_id = request.args.get('pay_member_id')
    deleteVal = "%" + str(pay_member_id) + "%"

    #1. member 테이블에서 삭제
    db.session.query(Member).filter(Member.pay_member_id == pay_member_id).delete()
    #2. round 테이블에서 mst인 경우
    db.session.query(Round).filter(Round.pay_round_mst == pay_member_id).delete(synchronize_session='fetch')
    #3. round 테이블에서 member에 포함된 경우
    db.session.query(Round).filter(Round.pay_round_member.like(deleteVal)).delete(synchronize_session='fetch')

    db.session.commit()

    pay_member_id = get_member_id_list(pay_id)[0]
    pay_member_list = get_member_id_list(pay_id)[1]

    return jsonify(pay_member_id=pay_member_id, pay_member_list=pay_member_list)


@app.route('/update_pay_member')
def update_pay_member():
    pay_id = request.args.get('pay_id')
    pay_member_id = request.args.get('pay_member_id')
    pay_member_nm = request.args.get('pay_member_nm')
    reg_dm = str(now)[:19]

    member = Member(pay_id, pay_member_nm, reg_dm)

    db.session.query(Member).filter(Member.pay_member_id == pay_member_id).update({"pay_member_nm": pay_member_nm}, synchronize_session='evaluate')

    db.session.commit()

    pay_member_id = get_member_id_list(pay_id)[0]
    pay_member_list = get_member_id_list(pay_id)[1]

    return jsonify(pay_member_id=pay_member_id, pay_member_list=pay_member_list)

################ pay.html END ############


################ round.html ##############
def get_review_list(pay_round_list):
    #이름을 한 줄로 보여주기 위해 만드는 리스트 -> 이름1, 이름2, 이름3
    pay_round_member_nm = []
    for i in range(0, len(pay_round_list)):
        tempstr = "'"
        for j in range(0, len((pay_round_list[i].pay_round_member.split(",")))):
            if j == 0:
                tempstr = tempstr + db.session.query(Member).filter(Member.pay_member_id == (pay_round_list[i].pay_round_member.split(","))[j]).scalar().pay_member_nm
            else:
                tempstr = tempstr + "," + db.session.query(Member).filter(Member.pay_member_id == (pay_round_list[i].pay_round_member.split(","))[j]).scalar().pay_member_nm
        tempstr = tempstr + "'"
        pay_round_member_nm.append(tempstr)

    #round_nm, round_price, round_member, round_id(나중 추가) 형태로 리턴
    pay_review_list = []
    for i in range(0, len(pay_round_list)):
        pay_review_list.append([pay_round_list[i].round_nm
        , pay_round_list[i].round_price
        , db.session.query(Member).filter(Member.pay_member_id == pay_round_list[i].pay_round_mst).scalar().pay_member_nm
        , pay_round_member_nm[i].replace("'", "")
        , pay_round_list[i].round_id])

    return pay_review_list


@app.route('/round_enter', methods=['POST'])
def round_enter():
    pay_id = request.form['pay_id']

    params = {'pay_id' : pay_id}

    return jsonify(params)


@app.route('/round/<pay_id>')
def round(pay_id):
    pay_id = pay_id
    pay_name = db.session.query(Payment).filter(Payment.pay_id == pay_id).first().pay_name
    
    pay_member_list = db.session.query(Member).filter(Member.pay_id == pay_id).order_by(Member.pay_member_id).all()

    #화면에서 새로고침 할 수 있으니 리스트 전달해줘야한다.
    pay_round_list = db.session.query(Round).filter(Round.pay_id == pay_id).order_by(Round.round_id).all()

    pay_review_list = get_review_list(pay_round_list)

    return render_template("round.html"
        , pay_id=pay_id, pay_name=pay_name, pay_member_list=pay_member_list, pay_review_list=pay_review_list)


@app.route('/select_round_info')
def select_round_info():
    round_id = request.args.get('round_id')

    pay_round_info = db.session.query(Round).filter(Round.round_id == round_id).all()[0]
    pay_round_mst_nm = db.session.query(Member).filter(Member.pay_member_id == pay_round_info.pay_round_mst).all()[0].pay_member_nm

    return jsonify(round_nm=pay_round_info.round_nm, round_price=pay_round_info.round_price, pay_round_member=pay_round_info.pay_round_member
        , pay_round_mst=pay_round_info.pay_round_mst, pay_round_mst_nm=pay_round_mst_nm)


@app.route('/add_pay_round')
def add_pay_round():
    #신규 회차 내용 add start
    pay_id = request.args.get('pay_id')
    round_nm = request.args.get('round_nm')
    round_price = request.args.get('round_price')
    pay_round_mst = request.args.get('pay_round_mst')
    pay_round_members = request.args.get('pay_round_members')
    reg_dm = str(now)[:19]

    round = Round(round_nm, round_price, pay_id, int(pay_round_mst), pay_round_members, reg_dm)
    db.session.add(round)
    db.session.commit()
    #신규 회차 내용 add end

    pay_round_list = db.session.query(Round).filter(Round.pay_id == pay_id).order_by(Round.round_id).all()

    pay_review_list = get_review_list(pay_round_list)

    return jsonify(pay_review_list=pay_review_list)


@app.route('/delete_pay_round')
def delete_pay_round():
    pay_id = request.args.get('pay_id')
    round_id = request.args.get('round_id')

    #1. round 테이블에서 삭제
    db.session.query(Round).filter(Round.round_id == round_id).delete()
    db.session.commit()

    pay_round_list = db.session.query(Round).filter(Round.pay_id == pay_id).order_by(Round.round_id).all()

    pay_review_list = get_review_list(pay_round_list)

    return jsonify(pay_review_list=pay_review_list)


@app.route('/update_pay_round')
def update_pay_round():
    pay_id = request.args.get('pay_id')
    round_id = request.args.get('round_id')
    round_nm = request.args.get('round_nm')
    round_price = request.args.get('round_price')
    pay_round_mst = request.args.get('pay_round_mst')
    pay_round_member = request.args.get('pay_round_member')
    reg_dm = str(now)[:19]

    db.session.query(Round).filter(Round.round_id == round_id).update({"round_nm": round_nm, "round_price": round_price, "pay_round_mst": pay_round_mst, "pay_round_member": pay_round_member}, synchronize_session='evaluate')

    db.session.commit()

    pay_round_list = db.session.query(Round).filter(Round.pay_id == pay_id).order_by(Round.round_id).all()

    pay_review_list = get_review_list(pay_round_list)

    return jsonify(pay_review_list=pay_review_list)

################ round.html END ########## 
   
################ result.html #############

@app.route('/result_enter', methods=['POST'])
def result_enter():
    pay_id = request.form['pay_id']

    params = {'pay_id' : pay_id}

    return jsonify(params)


@app.route('/result/<pay_id>')
def result(pay_id):
    pay_id = pay_id
    pay_name = db.session.query(Payment).filter(Payment.pay_id == pay_id).first().pay_name
    
    pay_round_list = db.session.query(Round).filter(Round.pay_id == pay_id).order_by(Round.round_id).all()
    
    final_list_idx = calculate.calculate(pay_id, pay_round_list)
    
    final_list = []
    for i in range(0, len(final_list_idx)):
        final_list.append([final_list_idx[i][0], db.session.query(Member).filter(Member.pay_member_id == final_list_idx[i][1]).scalar().pay_member_nm, db.session.query(Member).filter(Member.pay_member_id == final_list_idx[i][2]).scalar().pay_member_nm, final_list_idx[i][3]])
    
    return render_template("result.html", pay_id=pay_id, final_list=final_list)

################ result.html END #########


if __name__ == "__main__":
    app.run(debug=True)
    app.config['TEMPLATES_AUTO_RELOAD'] = True      
    app.jinja_env.auto_reload = True