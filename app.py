
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ecommerce.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    image_url = db.Column(db.String(200))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)

@app.route("/products", methods=["GET"])
def get_products():
    products = Product.query.all()
    return jsonify([{"id": p.id, "name": p.name, "price": p.price, "image": p.image_url} for p in products])

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    hashed_password = generate_password_hash(data["password"])
    user = User(username=data["username"], email=data["email"], password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "تم التسجيل بنجاح!"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()
    if user and check_password_hash(user.password, data["password"]):
        return jsonify({"message": "تم تسجيل الدخول بنجاح!"})
    return jsonify({"message": "بيانات غير صحيحة"}), 401

@app.route("/checkout", methods=["POST"])
def checkout():
    data = request.json
    order = Order(user_id=data["user_id"])
    db.session.add(order)
    db.session.flush()
    for item in data["items"]:
        order_item = OrderItem(order_id=order.id, product_id=item["product_id"], quantity=item["quantity"])
        db.session.add(order_item)
    db.session.commit()
    return jsonify({"message": "تمت العملية بنجاح", "order_id": order.id})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
