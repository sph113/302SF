from flask import Flask, render_template,redirect, request, session
import json, requests
from cs50 import SQL
from flask_session import Session

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL ( "sqlite:///data.db" )

def updateorders():
    orders = []
    link = "http://xnobe.synology.me:8080/ordersjson/"
    url = requests.get(link)
    text = url.text
    data = json.loads(text)
    iterdata = iter(data)
    next(iterdata)
    for i in iterdata:
        number = i
        link2 = "http://xnobe.synology.me:8080/ordersjson/" + number.replace('order', '')
        url2 = requests.get(link2)
        text2 = url2.text
        data2 = json.loads(text2)
        orders.append(data2)
    return orders

@app.route('/', methods=['GET','POST'])
def index():
    orders=updateorders()
    staffs= db.execute("select * from staff order by staff_id")
    if request.method == 'POST':
        print(request.form.getlist("selected_orders"))
        print(request.form.getlist("staffs"))
        orderstoarrange=request.form.getlist("selected_orders")
        staff=request.form.getlist("staffs")
        session['orderstoarrange']=orderstoarrange
        session['staff']=staff
        if 'orderstoarrange' in session:
            return redirect("/manage")
    print(staffs)
    return render_template("index.html",orders=orders,staffs=staffs)

@app.route('/manage')
def manage():
    return render_template("manage.html",session=session)

@app.route('/updatedeliver', methods=['GET'])
def update():
     return render_template("updatedeliver.html")

@app.route('/Status')
def status():
    return render_template("Status.html")

if __name__ == '__main__':
    app.run(debug=True)
