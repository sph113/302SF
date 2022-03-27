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
    orders = db.execute("SELECT Order_id, District, status FROM orders WHERE Order_id>0 ")
    return render_template("Status.html",orders=orders)

@app.route('/order/<order_id>',methods=['GET','POST'])
def checkorder(order_id):
    order_general=db.execute("Select * from orders where Order_id = :Order_id",Order_id=int(order_id))
    order_client=db.execute("SELECT * from orders_client where Order_id = :Order_id",Order_id=int(order_id))
    order_products=db.execute("SELECT * from orders_product where Order_id = :Order_id",Order_id=int(order_id))
    print(order_general)
    print(order_client)
    print(order_products)
    return render_template("order.html",order_general=order_general[0],order_client=order_client[0],order_products=order_products)

@app.route('/deliverystatus/<staff>',methods=['GET','POST'])
def deliverystatus(staff):
    staffname=db.execute("SELECT staff_name from staff")
    for i in staffname:
        if i['staff_name'] == staff:
            print('success')
            orders=db.execute("SELECT * from orders where staff=:staff",staff=staff)
            return render_template("updatestatus.html", staff=staff, orders=orders)
    return redirect('/')

@app.route('/update/')
def updatestatus():
    status = request.args.get('status')
    if session:
        orderid = int(request.args.get('orderid'))
        db.execute("UPDATE orders SET status = :status WHERE Order_id = :Order_id", status=status ,Order_id=orderid)
    return render_template("Status.html")

if __name__ == '__main__':
    app.run(debug=True)
