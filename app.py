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
    getafter=db.execute('select Order_id from orders order by order_id')
    iterdata = iter(data)
    for i in iterdata:
        number = i
        realnumber = number.replace('order', '')
        valuetocheck = {'Order_id': int(realnumber) }
        if not valuetocheck in getafter:
            link2 = "http://xnobe.synology.me:8080/ordersjson/" + realnumber
            url2 = requests.get(link2)
            text2 = url2.text
            data2 = json.loads(text2)
            orders.append(data2)
    return orders


def updatedatabase(orders):
    for order in orders:
        Company = order['Company']
        Order_id = order['Order_id']
        District = order['District']
        Amounts=0
        Total_weight=0
        product_id=[]
        product_name=[]
        amount=[]
        weight=[]
        for i in order['Product']:
            Amounts = Amounts + i['amount']
            Total_weight = Total_weight + i['weight']
            product_id.append(i['id'])
            product_name.append(i['name'])
            amount.append(i['amount'])
            weight.append(i['weight'])
        Customer_name = order['Customer_Name']
        Customer_id = order['Customer_ID']
        Contact = order['Phone_number']
        Flat = order['Flat']
        Floor = order['Floor']
        Estate = order['Estate']
        Street = order['Street']
        print(Company, Order_id, District, Amounts, Total_weight)
        db.execute("INSERT INTO orders (Company, Order_id, District, Customer_id ,Amount, Total_weight) VALUES (:Company, :Order_id,:District, :Customer_id, :Amount, :Total_weight)",Company=Company, Order_id=Order_id, Customer_id=Customer_id,District=District, Amount=Amounts, Total_weight=Total_weight)
        db.execute("INSERT INTO orders_client (Company, Customer_id, Customer_name, Contact, Flat, Floor, Estate, Street, District, Order_id) VALUES (:Company, :Customer_id, :Customer_name, :Contact, :Flat, :Floor, :Estate, :Street, :District,:Order_id)",Company=Company,Customer_id=Customer_id,Customer_name=Customer_name,Contact=Contact,Flat=Flat,Floor=Floor,Estate=Estate,Street=Street,District=District,Order_id=Order_id)
        y=0
        for x in product_id:
            db.execute("INSERT INTO orders_product (order_id, Company, product_id, amount, weight, product) VALUES (:order_id, :Company, :product_id, :amount, :weight,:product)",order_id=Order_id, Company=Company, product_id=product_id[y], amount=amount[y], weight=weight[y],product=product_name[y])
            y=y+1

@app.route('/', methods=['GET','POST'])
def index():
    updatedatabase(updateorders())
    orders=db.execute("select * from orders WHERE Order_id>0")
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
    for i in session['orderstoarrange']:
        db.execute("UPDATE orders SET staff = :staff ,status=:status WHERE Order_id = :Order_id",staff=session['staff'][0],status="Arranged" ,Order_id = int(i))
    return redirect('/')

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
    app.run(debug=True, use_reloader=True)
