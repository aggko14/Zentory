from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zentory-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///zentory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, default=0.0)
    # Relationship allows us to see all sales for a product
    sales = db.relationship('Sale', backref='product', lazy=True)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    sales = db.relationship('Sale', backref='customer', lazy=True)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False) # 'income' or 'expense'
    date = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

def login_required(f):
    """Custom decorator to protect routes from unauthorized access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Einai Demo
        if request.form.get('username') == 'admin' and request.form.get('password') == '1234':
            session['user'] = 'admin'
            flash('Welcome back, Admin!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    products = Product.query.all()
    recent_sales = Sale.query.order_by(Sale.date.desc()).limit(5).all()
    transactions = Transaction.query.all()
    
    product_names = [p.name for p in products]
    stock_values = [round(p.stock * p.price, 2) for p in products]
    
    sale_dates = [s.date.strftime('%b %d') for s in reversed(recent_sales)]
    sale_totals = [round(s.total, 2) for s in reversed(recent_sales)]
    
    income = sum(t.amount for t in transactions if t.type == 'income')
    expense = sum(t.amount for t in transactions if t.type == 'expense')
    
    return render_template('dashboard.html',
                           stock_value=round(sum(stock_values), 2),
                           total_sales=Sale.query.count(),
                           customers=Customer.query.count(),
                           balance=round(income - expense, 2),
                           product_names=product_names,
                           stock_values=stock_values,
                           sale_dates=sale_dates,
                           sale_totals=sale_totals,
                           income=income,
                           expense=expense)

@app.route('/inventory', methods=['GET', 'POST'])
@login_required
def inventory():
    if request.method == 'POST':
        if 'delete_id' in request.form:
            product = Product.query.get(request.form['delete_id'])
            if product:
                db.session.delete(product)
                db.session.commit()
                flash(f'Product "{product.name}" removed.', 'success')
        else:
            new_product = Product(
                name=request.form['name'],
                stock=int(request.form['stock']),
                price=float(request.form['price'])
            )
            db.session.add(new_product)
            db.session.commit()
            flash('Product added to inventory.', 'success')
        return redirect(url_for('inventory'))
    
    return render_template('inventory.html', products=Product.query.all())

@app.route('/sales', methods=['GET', 'POST'])
@login_required
def sales():
    if request.method == 'POST':
        if 'delete_id' in request.form:
            sale = Sale.query.get(request.form['delete_id'])
            if sale:
                if sale.product:
                    sale.product.stock += sale.quantity
                db.session.delete(sale)
                db.session.commit()
                flash('Sale voided and inventory updated.', 'success')
        else:
            prod_id = int(request.form['product_id'])
            qty = int(request.form['quantity'])
            product = Product.query.get(prod_id)
            
            if product and product.stock >= qty:
                total_price = qty * product.price
                new_sale = Sale(customer_id=int(request.form['customer_id']), 
                                product_id=prod_id, quantity=qty, total=total_price)
                
                product.stock -= qty
                db.session.add(new_sale)
                db.session.commit()
                flash(f'Sale recorded: ${total_price}', 'success')
            else:
                flash('Transaction failed: Insufficient stock.', 'danger')
        return redirect(url_for('sales'))
    
    return render_template('sales.html', 
                           sales=Sale.query.order_by(Sale.date.desc()).all(), 
                           customers=Customer.query.all(), 
                           products=Product.query.all())

@app.route('/crm', methods=['GET', 'POST'])
@login_required
def crm():
    if request.method == 'POST':
        if 'delete_id' in request.form:
            customer = Customer.query.get(request.form['delete_id'])
            if customer:
                db.session.delete(customer)
                db.session.commit()
                flash('Customer record deleted.', 'success')
        else:
            new_cust = Customer(name=request.form['name'], 
                                email=request.form['email'], 
                                phone=request.form['phone'])
            db.session.add(new_cust)
            db.session.commit()
            flash('New customer profile created.', 'success')
        return redirect(url_for('crm'))
    return render_template('crm.html', customers=Customer.query.all())

@app.route('/accounting', methods=['GET', 'POST'])
@login_required
def accounting():
    if request.method == 'POST':
        if 'delete_id' in request.form:
            trans = Transaction.query.get(request.form['delete_id'])
            if trans:
                db.session.delete(trans)
                db.session.commit()
                flash('Transaction removed.', 'success')
        else:
            new_trans = Transaction(description=request.form['description'],
                                    amount=float(request.form['amount']),
                                    type=request.form['type'])
            db.session.add(new_trans)
            db.session.commit()
            flash('Transaction logged.', 'success')
        return redirect(url_for('accounting'))
    
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    balance = sum(t.amount if t.type == 'income' else -t.amount for t in transactions)
    return render_template('accounting.html', transactions=transactions, balance=round(balance, 2))

if __name__ == '__main__':
    app.run(debug=True)