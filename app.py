import os
from datetime import datetime
import uuid
import bcrypt
import pymysql
from flask import Flask, request, redirect, url_for, render_template, session, flash
from pony.orm import Database, db_session, select, commit, Required, Optional, Set, PrimaryKey
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'supersecurekey123')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/webp'}

db = Database()

class User(db.Entity):
    _table_ = 'users'
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    email = Required(str, unique=True)
    phone = Optional(str)
    address = Optional(str)
    password_hash = Required(str)
    role = Required(str, default='buyer')
    is_verified = Required(bool, default=False)
    verify_token = Optional(str)
    products = Set('Product')
    cart_items = Set('CartItem')
    wishlist_items = Set('WishlistItem')
    orders = Set('Order')
    order_items_bought = Set('OrderItem', reverse='buyer')

class Product(db.Entity):
    _table_ = 'products'
    id = PrimaryKey(int, auto=True)
    warung_name = Required(str)
    name = Required(str)
    description = Optional(str)
    price = Required(float)
    stock = Required(int)
    image_path = Optional(str)
    seller = Required(User)
    cart_items = Set('CartItem')
    wishlist_items = Set('WishlistItem')
    order_items = Set('OrderItem')

class CartItem(db.Entity):
    _table_ = 'cart_items'
    id = PrimaryKey(int, auto=True)
    user = Required(User)
    product = Required(Product)
    quantity = Required(int)

class WishlistItem(db.Entity):
    _table_ = 'wishlist_items'
    id = PrimaryKey(int, auto=True)
    user = Required(User)
    product = Required(Product)

class Order(db.Entity):
    _table_ = 'orders'
    id = PrimaryKey(int, auto=True)
    seller = Required(User)
    total_amount = Required(float)
    created_at = Required(str)
    items = Set('OrderItem')

class OrderItem(db.Entity):
    _table_ = 'order_items'
    id = PrimaryKey(int, auto=True)
    order = Required(Order)
    product = Required(Product)
    buyer = Required(User)
    product_name = Required(str)
    warung_name = Required(str)
    price = Required(float)
    quantity = Required(int)

db.bind(provider='mysql', host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME'))
db.generate_mapping(create_tables=True)

with db_session:
    if not User.get(email='anandatechnologysolution@gmail.com'):
        hashed = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        User(name='Admin', email='anandatechnologysolution@gmail.com', password_hash=hashed, role='admin', is_verified=True)

def require_role(role=None):
    def decorator(f):
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            with db_session:
                user = User[session['user_id']]
                if not user.is_verified:
                    flash('Verifikasi email Anda terlebih dahulu.')
                    return redirect(url_for('login'))
                if role and user.role != role:
                    return redirect(url_for('home'))
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@app.route('/')
def home():
    with db_session:
        products = list(select(p for p in Product if p.stock > 0))
        return render_template('index.html', title='UMKM Online', products=products)

@app.route('/about-us')
def about_us():
    return render_template('about-us.html', title='Tentang Kami')

@app.route('/contact-us')
def contact_us():
    return render_template('contact-us.html', title='Kontak Kami')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        role = request.form.get('role', 'buyer')
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        token = uuid.uuid4().hex
        with db_session:
            User(name=name, email=email, phone=phone, password_hash=hashed, role=role, verify_token=token, is_verified=False)
        flash('Akun berhasil dibuat. Silakan verifikasi email Anda.')
        return redirect(url_for('verify_email', token=token))
    return render_template('register.html', title='Daftar Akun')

@app.route('/verify/<token>')
def verify_email(token):
    with db_session:
        user = select(u for u in User if u.verify_token == token).get()
        if user:
            user.is_verified = True
            user.verify_token = ''
            flash('Email berhasil diverifikasi.')
            return redirect(url_for('login'))
    flash('Token verifikasi tidak valid.')
    return redirect(url_for('register'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        with db_session:
            user = User.get(email=email)
            if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                if not user.is_verified:
                    flash('Silakan verifikasi email Anda sebelum login.')
                    return redirect(url_for('verify_email', token=user.verify_token))
                session['user_id'] = user.id
                session['role'] = user.role
                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                elif user.role == 'seller':
                    return redirect(url_for('seller_dashboard'))
                return redirect(url_for('home'))
        flash('Email atau password salah.')
    return render_template('login.html', title='Login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard/seller', methods=['GET', 'POST'])
@require_role('seller')
def seller_dashboard():
    if request.method == 'POST':
        warung_name = request.form['warung_name']
        prod_name = request.form['prod_name']
        desc = request.form['desc']
        stock = int(request.form['stock'])
        price = float(request.form['price'])
        img = request.files['image']
        img_path = None
        if img and img.mimetype in ALLOWED_MIME_TYPES:
            filename = secure_filename(f"{uuid.uuid4().hex}_{img.filename}")
            img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img_path = filename
        with db_session:
            Product(warung_name=warung_name, name=prod_name, description=desc, price=price, stock=stock, image_path=img_path, seller=User[session['user_id']])
        return redirect(url_for('seller_dashboard'))
    with db_session:
        my_products = list(select(p for p in Product if p.seller.id == session['user_id']))
        return render_template('seller_dashboard.html', title='Dashboard Penjual', products=my_products)

@app.route('/product/<int:prod_id>')
def product_detail(prod_id):
    with db_session:
        product = Product.get(id=prod_id)
        if not product:
            flash('Produk tidak ditemukan.')
            return redirect(url_for('home'))
        in_wishlist = False
        if session.get('user_id'):
            in_wishlist = WishlistItem.get(user=User[session['user_id']], product=product) is not None
        return render_template('product_detail.html', title=product.name, product=product, in_wishlist=in_wishlist)

@app.route('/product/edit/<int:prod_id>', methods=['GET', 'POST'])
@require_role('seller')
def edit_product(prod_id):
    if request.method == 'POST':
        with db_session:
            product = Product[prod_id]
            if product.seller.id != session['user_id']:
                flash('Anda tidak memiliki akses ke produk ini.')
                return redirect(url_for('seller_dashboard'))
            product.warung_name = request.form['warung_name']
            product.name = request.form['prod_name']
            product.description = request.form['desc']
            product.stock = int(request.form['stock'])
            product.price = float(request.form['price'])
            img = request.files.get('image')
            if img and img.filename and img.mimetype in ALLOWED_MIME_TYPES:
                if product.image_path:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], product.image_path)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                filename = secure_filename(f"{uuid.uuid4().hex}_{img.filename}")
                img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                product.image_path = filename
        flash('Produk berhasil diperbarui.')
        return redirect(url_for('seller_dashboard'))
    with db_session:
        product = Product[prod_id]
        if product.seller.id != session['user_id']:
            flash('Anda tidak memiliki akses ke produk ini.')
            return redirect(url_for('seller_dashboard'))
        return render_template('edit_product.html', title='Edit Produk', product=product)

@app.route('/product/delete/<int:prod_id>', methods=['POST'])
@require_role('seller')
def delete_product(prod_id):
    with db_session:
        product = Product[prod_id]
        if product.seller.id != session['user_id']:
            flash('Anda tidak memiliki akses ke produk ini.')
            return redirect(url_for('seller_dashboard'))
        if product.image_path:
            old_path = os.path.join(app.config['UPLOAD_FOLDER'], product.image_path)
            if os.path.exists(old_path):
                os.remove(old_path)
        select(c for c in CartItem if c.product == product).delete(bulk=True)
        select(w for w in WishlistItem if w.product == product).delete(bulk=True)
        product.delete()
    flash('Produk berhasil dihapus.')
    return redirect(url_for('seller_dashboard'))

@app.route('/dashboard/buyer')
@require_role('buyer')
def buyer_dashboard():
    with db_session:
        products = list(select(p for p in Product if p.stock > 0))
        cart_items = list(select(c for c in CartItem if c.user.id == session['user_id']))
        total = sum(c.product.price * c.quantity for c in cart_items)
        return render_template('buyer_dashboard.html', title='Dashboard Pembeli', products=products, cart=cart_items, total=total)

@app.route('/cart/add/<int:prod_id>', methods=['POST'])
@require_role('buyer')
def add_to_cart(prod_id):
    qty = int(request.form['quantity'])
    with db_session:
        existing = CartItem.get(user=User[session['user_id']], product=Product[prod_id])
        if existing:
            existing.quantity += qty
        else:
            CartItem(user=User[session['user_id']], product=Product[prod_id], quantity=qty)
    flash('Produk ditambahkan ke keranjang.')
    return redirect(url_for('product_detail', prod_id=prod_id))

@app.route('/cart/remove/<int:item_id>', methods=['POST'])
@require_role('buyer')
def remove_from_cart(item_id):
    with db_session:
        item = CartItem.get(id=item_id)
        if item and item.user.id == session['user_id']:
            item.delete()
    flash('Item dihapus dari keranjang.')
    return redirect(url_for('cart_page'))

@app.route('/cart')
@require_role('buyer')
def cart_page():
    with db_session:
        cart_items = list(select(c for c in CartItem if c.user.id == session['user_id']))
        total = sum(c.product.price * c.quantity for c in cart_items)
        return render_template('cart.html', title='Keranjang Belanja', cart=cart_items, total=total)

@app.route('/wishlist/toggle/<int:prod_id>', methods=['POST'])
@require_role('buyer')
def toggle_wishlist(prod_id):
    with db_session:
        user = User[session['user_id']]
        product = Product[prod_id]
        existing = WishlistItem.get(user=user, product=product)
        if existing:
            existing.delete()
            flash('Produk dihapus dari wishlist.')
        else:
            WishlistItem(user=user, product=product)
            flash('Produk ditambahkan ke wishlist.')
    return redirect(url_for('product_detail', prod_id=prod_id))

@app.route('/wishlist')
@require_role('buyer')
def wishlist_page():
    with db_session:
        items = list(select(w for w in WishlistItem if w.user.id == session['user_id']))
        return render_template('wishlist.html', title='Wishlist Saya', items=items)

@app.route('/checkout', methods=['GET', 'POST'])
@require_role('buyer')
def checkout():
    if request.method == 'POST':
        address = request.form['address']
        payment = request.form['payment']
        courier = request.form['courier']
        with db_session:
            buyer = User[session['user_id']]
            cart_items = list(select(c for c in CartItem if c.user.id == session['user_id']))
            sellers_orders = {}
            for item in cart_items:
                seller_id = item.product.seller.id
                if seller_id not in sellers_orders:
                    sellers_orders[seller_id] = []
                sellers_orders[seller_id].append(item)
            for seller_id, items in sellers_orders.items():
                seller = User[seller_id]
                total = sum(i.product.price * i.quantity for i in items)
                order = Order(seller=seller, total_amount=total, created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                for item in items:
                    OrderItem(order=order, product=item.product, buyer=buyer, product_name=item.product.name, warung_name=item.product.warung_name, price=item.product.price, quantity=item.quantity)
                    item.product.stock -= item.quantity
            select(c for c in CartItem if c.user.id == session['user_id']).delete(bulk=True)
        flash('Pesanan berhasil dibuat.')
        return redirect(url_for('buyer_dashboard'))
    with db_session:
        cart = list(select(c for c in CartItem if c.user.id == session['user_id']))
        return render_template('checkout.html', title='Checkout', cart=cart)

@app.route('/upgrade-seller')
@require_role('buyer')
def upgrade_to_seller():
    with db_session:
        user = User[session['user_id']]
        user.role = 'seller'
    return redirect(url_for('seller_dashboard'))

@app.route('/admin')
@require_role('admin')
def admin_dashboard():
    with db_session:
        sellers = list(select(u for u in User if u.role == 'seller'))
        buyers = list(select(u for u in User if u.role == 'buyer'))

        seller_data = []
        for s in sellers:
            orders = list(select(o for o in Order if o.seller.id == s.id))
            total_revenue = sum(o.total_amount for o in orders)
            total_orders = len(orders)
            products = list(select(p for p in Product if p.seller.id == s.id))
            product_stats = []
            for p in products:
                buyer_count = len(set(select(oi.buyer.id for oi in OrderItem if oi.product.id == p.id)))
                total_sold = sum(select(oi.quantity for oi in OrderItem if oi.product.id == p.id))
                product_revenue = sum(select(oi.price * oi.quantity for oi in OrderItem if oi.product.id == p.id))
                product_stats.append({
                    'name': p.name,
                    'stock': p.stock,
                    'price': p.price,
                    'buyer_count': buyer_count,
                    'total_sold': total_sold,
                    'revenue': product_revenue
                })
            seller_data.append({
                'id': s.id,
                'name': s.name,
                'email': s.email,
                'phone': s.phone or '-',
                'is_verified': s.is_verified,
                'total_revenue': total_revenue,
                'total_orders': total_orders,
                'products': product_stats
            })

        total_platform_revenue = sum(sd['total_revenue'] for sd in seller_data)
        total_platform_orders = sum(sd['total_orders'] for sd in seller_data)
        total_sellers = len(sellers)
        total_buyers = len(buyers)

        buyer_data = []
        for b in buyers:
            purchase_count = len(select(oi for oi in OrderItem if oi.buyer.id == b.id))
            buyer_data.append({
                'name': b.name,
                'email': b.email,
                'phone': b.phone or '-',
                'purchase_count': purchase_count
            })

        return render_template('admin_dashboard.html', title='Admin Dashboard',
            seller_data=seller_data, buyer_data=buyer_data,
            total_revenue=total_platform_revenue, total_orders=total_platform_orders,
            total_sellers=total_sellers, total_buyers=total_buyers)

@app.route('/admin/approve/<int:user_id>')
@require_role('admin')
def approve_seller(user_id):
    with db_session:
        user = User[user_id]
        user.is_verified = True
    flash('Penjual berhasil di-approve.')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject/<int:user_id>')
@require_role('admin')
def reject_seller(user_id):
    with db_session:
        user = User[user_id]
        user.is_verified = False
    flash('Penjual berhasil di-reject.')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    port_server = int(os.getenv('PORT', 5000))
    app.run(host='127.0.0.1', port=port_server, debug=True)