from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
import sqlite3
from datetime import datetime, timedelta
from urllib.parse import quote

app = FastAPI(title="Raithu Sethu")

DB = "raithu_sethu.db"


# ============================================================
# DATABASE
# ============================================================

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    con = db()
    cur = con.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS crops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        crop TEXT NOT NULL,
        quantity REAL NOT NULL,
        price REAL NOT NULL,
        location TEXT NOT NULL,
        description TEXT DEFAULT '',
        farmer_name TEXT DEFAULT 'Demo Farmer',
        phone TEXT DEFAULT '9999999999',
        flash_sale INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS requirements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        crop TEXT NOT NULL,
        quantity REAL NOT NULL,
        location TEXT NOT NULL,
        payment TEXT NOT NULL,
        buyer_name TEXT DEFAULT 'Demo Buyer',
        phone TEXT DEFAULT '8888888888',
        status TEXT DEFAULT 'Open',
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crop_id INTEGER,
        crop TEXT,
        farmer_name TEXT,
        buyer_name TEXT,
        quantity REAL,
        price REAL,
        total REAL,
        location TEXT,
        payment TEXT,
        status TEXT DEFAULT 'Pending',
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        message TEXT,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        audience TEXT DEFAULT 'all',
        title TEXT,
        message TEXT,
        notification_type TEXT DEFAULT 'general',
        is_read INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT,
        title TEXT,
        note TEXT,
        reminder_time TEXT,
        done INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    );
    """)

    con.commit()
    con.close()


init_db()


# ============================================================
# DATA
# ============================================================

CATEGORIES = {
    "Vegetables": {
        "icon": "🥕",
        "crops": [
            "Tomato", "Onion", "Potato", "Brinjal", "Okra",
            "Green Chilli", "Cabbage", "Cauliflower",
            "Carrot", "Spinach"
        ]
    },
    "Fruits": {
        "icon": "🍎",
        "crops": [
            "Mango", "Banana", "Papaya", "Guava",
            "Pomegranate", "Orange", "Watermelon", "Grapes"
        ]
    },
    "Flowers": {
        "icon": "🌸",
        "crops": [
            "Rose", "Jasmine", "Marigold",
            "Chrysanthemum", "Tuberose", "Lotus"
        ]
    },
    "Seeds": {
        "icon": "🌱",
        "crops": [
            "Paddy Seed", "Wheat Seed", "Maize Seed",
            "Groundnut Seed", "Sunflower Seed", "Vegetable Seeds"
        ]
    },
    "Pulses": {
        "icon": "🫘",
        "crops": [
            "Red Gram", "Green Gram", "Black Gram",
            "Bengal Gram", "Cowpea"
        ]
    },
    "Grains": {
        "icon": "🌾",
        "crops": [
            "Rice", "Wheat", "Maize", "Sorghum",
            "Pearl Millet", "Ragi"
        ]
    },
    "Spices": {
        "icon": "🌶️",
        "crops": [
            "Turmeric", "Ginger", "Chilli",
            "Coriander", "Cumin", "Black Pepper"
        ]
    }
}


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def esc(value):
    if value is None:
        return ""
    return str(value)


# ============================================================
# HTML / CSS
# ============================================================

CSS = """
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
    background: #f1f8f3;
    color: #17351f;
}

a {
    text-decoration: none;
    color: inherit;
}

.header {
    background: linear-gradient(135deg, #087f3d, #19a653);
    color: white;
    min-height: 82px;
    padding: 14px 5%;
    display: flex;
    align-items: center;
    gap: 15px;
    box-shadow: 0 3px 12px #0002;
}

.logo {
    font-size: 42px;
}

.header-text {
    flex: 1;
}

.header-text h1 {
    margin: 0;
    font-size: 27px;
}

.header-text p {
    margin: 4px 0 0;
    opacity: .9;
}

.header a {
    background: white;
    color: #087f3d;
    padding: 11px 18px;
    border-radius: 10px;
    font-weight: bold;
}

.container {
    width: 92%;
    max-width: 1250px;
    margin: 30px auto;
}

.hero {
    text-align: center;
    padding: 45px 20px 30px;
}

.hero h1 {
    font-size: 42px;
    color: #087f3d;
    margin-bottom: 10px;
}

.hero p {
    font-size: 18px;
    color: #587060;
}

.cards {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 25px;
    max-width: 1000px;
    margin: 30px auto;
}

.card {
    background: white;
    border-radius: 20px;
    padding: 35px;
    text-align: center;
    box-shadow: 0 8px 25px #185b2a18;
    border: 1px solid #dceee0;
    transition: .2s;
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 30px #185b2a25;
}

.card-icon {
    font-size: 65px;
}

.card h2 {
    color: #087f3d;
}

.button,
button {
    border: 0;
    cursor: pointer;
    display: inline-block;
    padding: 12px 20px;
    border-radius: 10px;
    background: #0a8f43;
    color: white;
    font-weight: bold;
    font-size: 15px;
}

.button:hover,
button:hover {
    background: #066c32;
}

.button.secondary {
    background: #e7f5eb;
    color: #087f3d;
}

.button.danger {
    background: #c0392b;
}

.dashboard-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
}

.dashboard-title h1 {
    color: #087f3d;
    margin-bottom: 5px;
}

.menu-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 35px;
}

.menu-card {
    background: white;
    padding: 23px;
    border-radius: 15px;
    border: 1px solid #dceee0;
    box-shadow: 0 4px 15px #185b2a12;
    transition: .2s;
}

.menu-card:hover {
    transform: translateY(-3px);
    border-color: #0a8f43;
}

.menu-icon {
    font-size: 35px;
}

.menu-card h3 {
    margin: 10px 0 5px;
    color: #087f3d;
}

.menu-card p {
    margin: 0;
    color: #617064;
}

.section {
    background: white;
    border-radius: 18px;
    padding: 25px;
    margin-bottom: 25px;
    box-shadow: 0 5px 20px #185b2a12;
}

.section h2 {
    color: #087f3d;
}

.category-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
}

.category {
    background: #eaf7ed;
    border: 2px solid #d1ebd7;
    border-radius: 14px;
    padding: 22px 10px;
    text-align: center;
    font-weight: bold;
    color: #087f3d;
}

.category:hover {
    background: #d9f1df;
    border-color: #0a8f43;
}

.category-icon {
    display: block;
    font-size: 42px;
    margin-bottom: 8px;
}

.crop-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
}

.crop-card {
    background: white;
    border-radius: 14px;
    padding: 20px;
    border: 1px solid #dceee0;
    box-shadow: 0 4px 15px #185b2a12;
}

.crop-card h3 {
    color: #087f3d;
    margin-top: 0;
}

.crop-card .price {
    font-size: 21px;
    font-weight: bold;
    color: #e67e22;
}

.form-card {
    max-width: 650px;
    margin: auto;
    background: white;
    border-radius: 18px;
    padding: 30px;
    box-shadow: 0 6px 25px #185b2a18;
}

.form-card label {
    display: block;
    margin-top: 15px;
    margin-bottom: 6px;
    font-weight: bold;
}

.form-card input,
.form-card select,
.form-card textarea {
    width: 100%;
    padding: 13px;
    border: 1px solid #cbdccc;
    border-radius: 9px;
    font-size: 15px;
}

.form-card textarea {
    min-height: 100px;
    resize: vertical;
}

.form-card button {
    width: 100%;
    margin-top: 20px;
}

.list {
    display: grid;
    gap: 15px;
}

.item {
    background: white;
    border-radius: 15px;
    padding: 20px;
    border-left: 5px solid #0a8f43;
    box-shadow: 0 4px 15px #185b2a12;
}

.item h3 {
    margin-top: 0;
    color: #087f3d;
}

.item-row {
    display: flex;
    justify-content: space-between;
    gap: 15px;
    flex-wrap: wrap;
}

.badge {
    display: inline-block;
    background: #e5f6e9;
    color: #087f3d;
    padding: 6px 10px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: bold;
}

.badge.orange {
    background: #fff1dc;
    color: #c76b00;
}

.badge.red {
    background: #ffe4e1;
    color: #b52b20;
}

.empty {
    background: white;
    border-radius: 18px;
    padding: 45px;
    text-align: center;
    color: #68786d;
}

.empty-icon {
    font-size: 55px;
}

.back {
    margin-bottom: 20px;
    display: inline-block;
    color: #087f3d;
    font-weight: bold;
}

footer {
    margin-top: 50px;
    background: #063d1e;
    color: white;
    text-align: center;
    padding: 25px;
}

.flash {
    border-left-color: #f39c12;
    background: #fffaf0;
}

.flash-price {
    color: #d35400;
    font-size: 22px;
    font-weight: bold;
}

.chat-box {
    background: white;
    border-radius: 18px;
    padding: 20px;
    max-width: 800px;
    margin: auto;
}

.chat-messages {
    min-height: 300px;
    max-height: 450px;
    overflow-y: auto;
    background: #f1f8f3;
    border-radius: 12px;
    padding: 15px;
}

.message {
    background: white;
    padding: 10px 14px;
    margin: 8px 0;
    border-radius: 12px;
    box-shadow: 0 2px 8px #0001;
}

.message strong {
    color: #087f3d;
}

.inline-form {
    display: inline;
}

.two-column {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

.stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
    margin-bottom: 25px;
}

.stat {
    background: white;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 4px 15px #185b2a12;
}

.stat-number {
    font-size: 30px;
    font-weight: bold;
    color: #087f3d;
}

@media(max-width: 800px) {
    .cards,
    .menu-grid,
    .category-grid,
    .crop-grid,
    .stats,
    .two-column {
        grid-template-columns: 1fr 1fr;
    }
}

@media(max-width: 550px) {
    .cards,
    .menu-grid,
    .category-grid,
    .crop-grid,
    .stats,
    .two-column {
        grid-template-columns: 1fr;
    }

    .header {
        flex-wrap: wrap;
    }

    .hero h1 {
        font-size: 30px;
    }
}
"""


# ============================================================
# PAGE WRAPPER
# ============================================================

def page(title, content):
    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - Raithu Sethu</title>
<style>{CSS}</style>
</head>

<body>

<header class="header">
    <div class="logo">🌾</div>
    <div class="header-text">
        <h1>Raithu Sethu</h1>
        <p>Direct Farmer → Buyer Agricultural Marketplace</p>
    </div>
    <a href="/">Home</a>
</header>

{content}

<footer>
    🌾 Raithu Sethu • Direct Farmer → Buyer Marketplace
</footer>

</body>
</html>
"""


# ============================================================
# HOME
# ============================================================

@app.get("/", response_class=HTMLResponse)
def home():

    html = """
<div class="container">

<div class="hero">
    <h1>🌾 Welcome to Raithu Sethu</h1>
    <p>
        A direct marketplace connecting farmers and buyers
        without unnecessary middlemen.
    </p>
</div>

<div class="cards">

    <a href="/farmer">
        <div class="card">
            <div class="card-icon">👨‍🌾</div>
            <h2>Farmer</h2>
            <p>
                List crops, view buyer requirements,
                receive notifications and manage orders.
            </p>
            <span class="button">Enter Farmer Dashboard</span>
        </div>
    </a>

    <a href="/buyer">
        <div class="card">
            <div class="card-icon">🛒</div>
            <h2>Buyer</h2>
            <p>
                Browse crops, find farmers,
                place orders and post requirements.
            </p>
            <span class="button">Enter Buyer Dashboard</span>
        </div>
    </a>

</div>

</div>
"""

    return page("Home", html)


# ============================================================
# FARMER DASHBOARD
# ============================================================

@app.get("/farmer", response_class=HTMLResponse)
def farmer():

    con = db()

    crops = con.execute(
        "SELECT COUNT(*) c FROM crops"
    ).fetchone()["c"]

    requirements = con.execute(
        "SELECT COUNT(*) c FROM requirements WHERE status='Open'"
    ).fetchone()["c"]

    orders = con.execute(
        "SELECT COUNT(*) c FROM orders WHERE status='Pending'"
    ).fetchone()["c"]

    notifications = con.execute(
        "SELECT COUNT(*) c FROM notifications WHERE is_read=0"
    ).fetchone()["c"]

    con.close()

    menu = """
<div class="menu-grid">

<a href="/farmer/my-crops" class="menu-card">
<div class="menu-icon">🌱</div>
<h3>My Crops</h3>
<p>View your listed crops</p>
</a>

<a href="/category/farmer/Vegetables" class="menu-card">
<div class="menu-icon">➕</div>
<h3>Add Crop</h3>
<p>List agricultural produce</p>
</a>

<a href="/farmer/requirements" class="menu-card">
<div class="menu-icon">📋</div>
<h3>Buyer Requirements</h3>
<p>See what buyers need</p>
</a>

<a href="/farmer/matches" class="menu-card">
<div class="menu-icon">🤝</div>
<h3>Matched Buyers</h3>
<p>Find matching requirements</p>
</a>

<a href="/farmer/flash-sale" class="menu-card">
<div class="menu-icon">⚡</div>
<h3>Flash Sale</h3>
<p>View fast-selling produce</p>
</a>

<a href="/farmer/messages" class="menu-card">
<div class="menu-icon">💬</div>
<h3>Messages</h3>
<p>Chat with buyers</p>
</a>

<a href="/farmer/notifications" class="menu-card">
<div class="menu-icon">🔔</div>
<h3>Notifications</h3>
<p>Marketplace alerts</p>
</a>

<a href="/farmer/reminders" class="menu-card">
<div class="menu-icon">⏰</div>
<h3>Reminders</h3>
<p>Manage your reminders</p>
</a>

<a href="/farmer/orders" class="menu-card">
<div class="menu-icon">📦</div>
<h3>Orders</h3>
<p>Manage buyer orders</p>
</a>

</div>
"""

    categories = "".join(
        f"""
        <a class="category" href="/category/farmer/{name}">
            <span class="category-icon">{data['icon']}</span>
            {name}
        </a>
        """
        for name, data in CATEGORIES.items()
    )

    html = f"""
<div class="container">

<div class="dashboard-title">
    <div>
        <h1>👨‍🌾 Farmer Dashboard</h1>
        <p>Manage your farm marketplace.</p>
    </div>
</div>

<div class="stats">
    <div class="stat">
        <div class="stat-number">{crops}</div>
        <div>My Crops</div>
    </div>

    <div class="stat">
        <div class="stat-number">{requirements}</div>
        <div>Buyer Requests</div>
    </div>

    <div class="stat">
        <div class="stat-number">{orders}</div>
        <div>Pending Orders</div>
    </div>

    <div class="stat">
        <div class="stat-number">{notifications}</div>
        <div>Notifications</div>
    </div>
</div>

{menu}

<div class="section">
    <h2>🌾 Crop Categories</h2>
    <div class="category-grid">
        {categories}
    </div>
</div>

</div>
"""

    return page("Farmer Dashboard", html)


# ============================================================
# BUYER DASHBOARD
# ============================================================

@app.get("/buyer", response_class=HTMLResponse)
def buyer():

    con = db()

    crops = con.execute(
        "SELECT COUNT(*) c FROM crops"
    ).fetchone()["c"]

    requirements = con.execute(
        "SELECT COUNT(*) c FROM requirements"
    ).fetchone()["c"]

    orders = con.execute(
        "SELECT COUNT(*) c FROM orders"
    ).fetchone()["c"]

    messages = con.execute(
        "SELECT COUNT(*) c FROM messages"
    ).fetchone()["c"]

    con.close()

    categories = "".join(
        f"""
        <a class="category" href="/category/buyer/{name}">
            <span class="category-icon">{data['icon']}</span>
            {name}
        </a>
        """
        for name, data in CATEGORIES.items()
    )

    html = f"""
<div class="container">

<div class="dashboard-title">
    <div>
        <h1>🛒 Buyer Dashboard</h1>
        <p>Find agricultural products directly from farmers.</p>
    </div>
</div>

<div class="stats">
    <div class="stat">
        <div class="stat-number">{crops}</div>
        <div>Available Crops</div>
    </div>

    <div class="stat">
        <div class="stat-number">{requirements}</div>
        <div>Requirements</div>
    </div>

    <div class="stat">
        <div class="stat-number">{orders}</div>
        <div>My Orders</div>
    </div>

    <div class="stat">
        <div class="stat-number">{messages}</div>
        <div>Messages</div>
    </div>
</div>

<div class="menu-grid">

<a href="/buyer/browse" class="menu-card">
<div class="menu-icon">🔎</div>
<h3>Browse Crops</h3>
<p>Find available produce</p>
</a>

<a href="/buyer/requirements/new" class="menu-card">
<div class="menu-icon">📋</div>
<h3>Post Requirement</h3>
<p>Tell farmers what you need</p>
</a>

<a href="/buyer/matches" class="menu-card">
<div class="menu-icon">🤝</div>
<h3>Matched Farmers</h3>
<p>See suitable farmers</p>
</a>

<a href="/buyer/orders" class="menu-card">
<div class="menu-icon">📦</div>
<h3>My Orders</h3>
<p>Track purchases</p>
</a>

<a href="/buyer/messages" class="menu-card">
<div class="menu-icon">💬</div>
<h3>Messages</h3>
<p>Contact farmers</p>
</a>

<a href="/buyer/notifications" class="menu-card">
<div class="menu-icon">🔔</div>
<h3>Notifications</h3>
<p>Marketplace alerts</p>
</a>

<a href="/buyer/reminders" class="menu-card">
<div class="menu-icon">⏰</div>
<h3>Reminders</h3>
<p>Manage reminders</p>
</a>

<a href="/buyer/flash-sale" class="menu-card">
<div class="menu-icon">⚡</div>
<h3>Flash Sale</h3>
<p>View special offers</p>
</a>

</div>

<div class="section">
<h2>🌾 Browse Categories</h2>

<div class="category-grid">
{categories}
</div>

</div>

</div>
"""

    return page("Buyer Dashboard", html)


# ============================================================
# CATEGORY PAGE
# ============================================================

@app.get("/category/{role}/{category}", response_class=HTMLResponse)
def category(role: str, category: str):

    if category not in CATEGORIES:
        return HTMLResponse("Category not found", status_code=404)

    data = CATEGORIES[category]

    crops = ""

    for crop in data["crops"]:

        crops += f"""
        <a class="crop-card" href="/crop/{role}/{quote(category)}/{quote(crop)}">
            <div class="category-icon">{data['icon']}</div>
            <h3>{crop}</h3>
            <span class="button">
                {'View Farmers' if role == 'buyer' else 'List Crop'}
            </span>
        </a>
        """

    back = "/buyer" if role == "buyer" else "/farmer"

    html = f"""
<div class="container">

<a class="back" href="{back}">← Back to Dashboard</a>

<div class="hero">
    <h1>{data['icon']} {category}</h1>
    <p>Select a crop to continue.</p>
</div>

<div class="crop-grid">
{crops}
</div>

</div>
"""

    return page(category, html)


# ============================================================
# CROP PAGE
# ============================================================

@app.get("/crop/{role}/{category}/{crop}", response_class=HTMLResponse)
def crop_page(role: str, category: str, crop: str):

    if role == "farmer":

        html = f"""
<div class="container">

<a class="back" href="/category/farmer/{quote(category)}">
← Back to {category}
</a>

<div class="form-card">

<h1>🌱 List {crop}</h1>

<p>
Add your {crop} to the Raithu Sethu marketplace.
</p>

<form method="post" action="/farmer/add-crop">

<input type="hidden" name="category" value="{esc(category)}">
<input type="hidden" name="crop" value="{esc(crop)}">

<label>Quantity (kg)</label>
<input type="number" name="quantity" min="1" step="0.1" required>

<label>Price per kg (₹)</label>
<input type="number" name="price" min="1" step="0.01" required>

<label>Farm Location</label>
<input type="text" name="location" placeholder="Village / City" required>

<label>Farmer Name</label>
<input type="text" name="farmer_name" value="Demo Farmer">

<label>Phone</label>
<input type="tel" name="phone" value="9999999999">

<label>Description</label>
<textarea name="description"
placeholder="Quality, variety, harvest information..."></textarea>

<label>
<input type="checkbox" name="flash_sale" value="1">
 Put this crop in Flash Sale
</label>

<button type="submit">
🌱 List Crop
</button>

</form>

</div>

</div>
"""

    else:

        html = f"""
<div class="container">

<a class="back" href="/category/buyer/{quote(category)}">
← Back to {category}
</a>

<div class="form-card">

<h1>🛒 Buy / Request {crop}</h1>

<p>
Choose whether you want to request this crop from farmers.
</p>

<form method="post" action="/buyer/requirement">

<input type="hidden" name="category" value="{esc(category)}">
<input type="hidden" name="crop" value="{esc(crop)}">

<label>Quantity Required (kg)</label>
<input type="number" name="quantity" min="1" step="0.1" required>

<label>Your Location</label>
<input type="text" name="location"
placeholder="City / Delivery location" required>

<label>Buyer Name</label>
<input type="text" name="buyer_name" value="Demo Buyer">

<label>Phone</label>
<input type="tel" name="phone" value="8888888888">

<label>Payment Method</label>

<select name="payment" required>
<option value="">Select Payment Method</option>
<option value="Cash on Delivery">Cash on Delivery</option>
<option value="UPI">UPI</option>
<option value="Bank Transfer">Bank Transfer</option>
<option value="Cash at Pickup">Cash at Pickup</option>
</select>

<button type="submit">
📋 Send Requirement
</button>

</form>

</div>

</div>
"""

    return page(crop, html)


# ============================================================
# FARMER ADD CROP
# ============================================================

@app.post("/farmer/add-crop")
def add_crop(
    category: str = Form(...),
    crop: str = Form(...),
    quantity: float = Form(...),
    price: float = Form(...),
    location: str = Form(...),
    farmer_name: str = Form("Demo Farmer"),
    phone: str = Form("9999999999"),
    description: str = Form(""),
    flash_sale: str = Form("0")
):

    con = db()

    cur = con.execute("""
        INSERT INTO crops
        (category,crop,quantity,price,location,
         description,farmer_name,phone,flash_sale,created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (
        category,
        crop,
        quantity,
        price,
        location,
        description,
        farmer_name,
        phone,
        1 if flash_sale == "1" else 0,
        now()
    ))

    crop_id = cur.lastrowid

    con.execute("""
        INSERT INTO notifications
        (audience,title,message,notification_type,created_at)
        VALUES (?,?,?,?,?)
    """, (
        "buyer",
        "New Crop Available",
        f"{crop} is now available from {farmer_name}.",
        "crop",
        now()
    ))

    con.commit()
    con.close()

    return RedirectResponse(
        f"/farmer/success?crop={quote(crop)}",
        status_code=303
    )


# ============================================================
# BUYER REQUIREMENT
# ============================================================

@app.post("/buyer/requirement")
def requirement(
    category: str = Form(...),
    crop: str = Form(...),
    quantity: float = Form(...),
    location: str = Form(...),
    payment: str = Form(...),
    buyer_name: str = Form("Demo Buyer"),
    phone: str = Form("8888888888")
):

    con = db()

    cur = con.execute("""
        INSERT INTO requirements
        (category,crop,quantity,location,payment,
         buyer_name,phone,status,created_at)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (
        category,
        crop,
        quantity,
        location,
        payment,
        buyer_name,
        phone,
        "Open",
        now()
    ))

    req_id = cur.lastrowid

    con.execute("""
        INSERT INTO notifications
        (audience,title,message,notification_type,created_at)
        VALUES (?,?,?,?,?)
    """, (
        "farmer",
        "🔔 New Buyer Requirement",
        f"{buyer_name} needs {quantity} kg of {crop} in {location}.",
        "requirement",
        now()
    ))

    con.commit()
    con.close()

    return RedirectResponse(
        "/buyer/success",
        status_code=303
    )


# ============================================================
# SUCCESS
# ============================================================

@app.get("/farmer/success", response_class=HTMLResponse)
def farmer_success(crop: str = "crop"):

    return page("Success", f"""
<div class="container">
<div class="empty">

<div class="empty-icon">✅</div>

<h1>Crop Listed Successfully!</h1>

<p>
Your {esc(crop)} is now available in the marketplace.
</p>

<a class="button" href="/farmer/my-crops">
View My Crops
</a>

<a class="button secondary" href="/farmer">
Dashboard
</a>

</div>
</div>
""")


@app.get("/buyer/success", response_class=HTMLResponse)
def buyer_success():

    return page("Success", """
<div class="container">
<div class="empty">

<div class="empty-icon">✅</div>

<h1>Requirement Posted!</h1>

<p>
Your requirement has been sent to farmers.
Matching farmers will appear in Matched Farmers.
</p>

<a class="button" href="/buyer/matches">
Find Matched Farmers
</a>

<a class="button secondary" href="/buyer">
Dashboard
</a>

</div>
</div>
""")


# ============================================================
# MY CROPS
# ============================================================

@app.get("/farmer/my-crops", response_class=HTMLResponse)
def my_crops():

    con = db()

    rows = con.execute("""
        SELECT * FROM crops
        ORDER BY id DESC
    """).fetchall()

    con.close()

    content = ""

    for c in rows:

        flash = ""

        if c["flash_sale"]:
            flash = '<span class="badge orange">⚡ FLASH SALE</span>'

        content += f"""
<div class="item">

<div class="item-row">

<div>
<h3>🌾 {esc(c['crop'])}</h3>

{flash}

<p>📦 Quantity: <b>{c['quantity']} kg</b></p>
<p>💰 Price: <b>₹{c['price']}/kg</b></p>
<p>📍 {esc(c['location'])}</p>
<p>{esc(c['description'])}</p>

</div>

<div>

<a class="button" href="/farmer/toggle-flash/{c['id']}">
{'Remove Flash Sale' if c['flash_sale'] else '⚡ Flash Sale'}
</a>

</div>

</div>

</div>
"""

    if not content:
        content = """
<div class="empty">
<div class="empty-icon">🌱</div>
<h2>No crops listed yet</h2>
<a class="button" href="/category/farmer/Vegetables">
Add Your First Crop
</a>
</div>
"""

    return page("My Crops", f"""
<div class="container">

<a class="back" href="/farmer">← Farmer Dashboard</a>

<h1>🌱 My Crops</h1>

<div class="list">
{content}
</div>

</div>
""")


# ============================================================
# TOGGLE FLASH SALE
# ============================================================

@app.get("/farmer/toggle-flash/{crop_id}")
def toggle_flash(crop_id: int):

    con = db()

    row = con.execute(
        "SELECT flash_sale,crop FROM crops WHERE id=?",
        (crop_id,)
    ).fetchone()

    if row:
        new_value = 0 if row["flash_sale"] else 1

        con.execute(
            "UPDATE crops SET flash_sale=? WHERE id=?",
            (new_value, crop_id)
        )

        con.execute("""
            INSERT INTO notifications
            (audience,title,message,notification_type,created_at)
            VALUES (?,?,?,?,?)
        """, (
            "buyer",
            "Flash Sale Updated",
            f"{row['crop']} flash sale is now {'active' if new_value else 'inactive'}.",
            "flash_sale",
            now()
        ))

    con.commit()
    con.close()

    return RedirectResponse(
        "/farmer/my-crops",
        status_code=303
    )


# ============================================================
# BUYER BROWSE
# ============================================================

@app.get("/buyer/browse", response_class=HTMLResponse)
def browse():

    con = db()

    crops = con.execute("""
        SELECT * FROM crops
        WHERE quantity > 0
        ORDER BY id DESC
    """).fetchall()

    con.close()

    cards = ""

    for c in crops:

        flash = ""

        if c["flash_sale"]:
            flash = '<span class="badge orange">⚡ FLASH SALE</span>'

        cards += f"""
<div class="crop-card">

{flash}

<h3>🌾 {esc(c['crop'])}</h3>

<p>👨‍🌾 {esc(c['farmer_name'])}</p>
<p>📍 {esc(c['location'])}</p>
<p>📦 {c['quantity']} kg available</p>

<div class="price">
₹{c['price']}/kg
</div>

<p>{esc(c['description'])}</p>

<a class="button" href="/buyer/buy/{c['id']}">
Buy / Order
</a>

<a class="button secondary"
href="/buyer/contact/{c['id']}">
Contact
</a>

</div>
"""

    if not cards:
        cards = """
<div class="empty">
<div class="empty-icon">🌱</div>
<h2>No crops available</h2>
<p>Farmers have not listed crops yet.</p>
</div>
"""

    return page("Browse Crops", f"""
<div class="container">

<a class="back" href="/buyer">← Buyer Dashboard</a>

<h1>🔎 Browse Crops</h1>

<div class="crop-grid">
{cards}
</div>

</div>
""")


# ============================================================
# BUY CROP
# ============================================================

@app.get("/buyer/buy/{crop_id}", response_class=HTMLResponse)
def buy_page(crop_id: int):

    con = db()

    crop = con.execute(
        "SELECT * FROM crops WHERE id=?",
        (crop_id,)
    ).fetchone()

    con.close()

    if not crop:
        return HTMLResponse("Crop not found", status_code=404)

    return page("Place Order", f"""
<div class="container">

<a class="back" href="/buyer/browse">← Browse Crops</a>

<div class="form-card">

<h1>🛒 Order {esc(crop['crop'])}</h1>

<p>
Farmer: <b>{esc(crop['farmer_name'])}</b>
</p>

<p>
Available: <b>{crop['quantity']} kg</b>
</p>

<p>
Price: <b>₹{crop['price']}/kg</b>
</p>

<form method="post" action="/buyer/order">

<input type="hidden" name="crop_id" value="{crop['id']}">

<label>Your Name</label>
<input name="buyer_name" value="Demo Buyer" required>

<label>Quantity (kg)</label>
<input type="number"
       name="quantity"
       min="1"
       max="{crop['quantity']}"
       step="0.1"
       required>

<label>Delivery Location</label>
<input name="location" required>

<label>Payment Method</label>

<select name="payment" required>
<option value="">Select Payment</option>
<option>UPI</option>
<option>Cash on Delivery</option>
<option>Bank Transfer</option>
<option>Cash at Pickup</option>
</select>

<button type="submit">
📦 Place Order
</button>

</form>

</div>

</div>
""")


@app.post("/buyer/order")
def create_order(
    crop_id: int = Form(...),
    buyer_name: str = Form(...),
    quantity: float = Form(...),
    location: str = Form(...),
    payment: str = Form(...)
):

    con = db()

    crop = con.execute(
        "SELECT * FROM crops WHERE id=?",
        (crop_id,)
    ).fetchone()

    if not crop:
        con.close()
        return HTMLResponse("Crop not found", status_code=404)

    if quantity > crop["quantity"]:
        con.close()
        return HTMLResponse(
            "Requested quantity is greater than available quantity.",
            status_code=400
        )

    total = quantity * crop["price"]

    con.execute("""
        INSERT INTO orders
        (crop_id,crop,farmer_name,buyer_name,
         quantity,price,total,location,payment,
         status,created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (
        crop_id,
        crop["crop"],
        crop["farmer_name"],
        buyer_name,
        quantity,
        crop["price"],
        total,
        location,
        payment,
        "Pending",
        now()
    ))

    con.execute("""
        UPDATE crops
        SET quantity = quantity - ?
        WHERE id=?
    """, (
        quantity,
        crop_id
    ))

    con.execute("""
        INSERT INTO notifications
        (audience,title,message,notification_type,created_at)
        VALUES (?,?,?,?,?)
    """, (
        "farmer",
        "🛒 New Order",
        f"{buyer_name} ordered {quantity} kg of {crop['crop']}.",
        "order",
        now()
    ))

    con.commit()
    con.close()

    return RedirectResponse(
        "/buyer/orders",
        status_code=303
    )


# ============================================================
# BUYER ORDERS
# ============================================================

@app.get("/buyer/orders", response_class=HTMLResponse)
def buyer_orders():

    con = db()

    orders = con.execute("""
        SELECT * FROM orders
        ORDER BY id DESC
    """).fetchall()

    con.close()

    items = ""

    for o in orders:

        items += f"""
<div class="item">

<h3>📦 {esc(o['crop'])}</h3>

<p>Farmer: <b>{esc(o['farmer_name'])}</b></p>
<p>Quantity: <b>{o['quantity']} kg</b></p>
<p>Total: <b>₹{o['total']:.2f}</b></p>
<p>Payment: {esc(o['payment'])}</p>
<p>Location: {esc(o['location'])}</p>

<span class="badge">{esc(o['status'])}</span>

</div>
"""

    if not items:
        items = """
<div class="empty">
<div class="empty-icon">📦</div>
<h2>No orders yet</h2>
<a class="button" href="/buyer/browse">Browse Crops</a>
</div>
"""

    return page("My Orders", f"""
<div class="container">

<a class="back" href="/buyer">← Buyer Dashboard</a>

<h1>📦 My Orders</h1>

<div class="list">
{items}
</div>

</div>
""")


# ============================================================
# FARMER ORDERS
# ============================================================

@app.get("/farmer/orders", response_class=HTMLResponse)
def farmer_orders():

    con = db()

    orders = con.execute("""
        SELECT * FROM orders
        ORDER BY id DESC
    """).fetchall()

    con.close()

    items = ""

    for o in orders:

        actions = ""

        if o["status"] == "Pending":
            actions = f"""
<a class="button"
href="/farmer/order/{o['id']}/accept">
Accept
</a>

<a class="button danger"
href="/farmer/order/{o['id']}/reject">
Reject
</a>
"""

        items += f"""
<div class="item">

<h3>📦 {esc(o['crop'])}</h3>

<p>Buyer: <b>{esc(o['buyer_name'])}</b></p>
<p>Quantity: <b>{o['quantity']} kg</b></p>
<p>Total: <b>₹{o['total']:.2f}</b></p>
<p>Payment: {esc(o['payment'])}</p>
<p>Delivery: {esc(o['location'])}</p>

<span class="badge">{esc(o['status'])}</span>

<div style="margin-top:15px">
{actions}
</div>

</div>
"""

    if not items:
        items = """
<div class="empty">
<div class="empty-icon">📦</div>
<h2>No orders received</h2>
</div>
"""

    return page("Farmer Orders", f"""
<div class="container">

<a class="back" href="/farmer">← Farmer Dashboard</a>

<h1>📦 Buyer Orders</h1>

<div class="list">
{items}
</div>

</div>
""")


@app.get("/farmer/order/{order_id}/{action}")
def order_action(order_id: int, action: str):

    status = {
        "accept": "Accepted",
        "reject": "Rejected"
    }.get(action)

    if not status:
        return HTMLResponse("Invalid action", status_code=400)

    con = db()

    order = con.execute(
        "SELECT * FROM orders WHERE id=?",
        (order_id,)
    ).fetchone()

    if order:

        con.execute(
            "UPDATE orders SET status=? WHERE id=?",
            (status, order_id)
        )

        con.execute("""
            INSERT INTO notifications
            (audience,title,message,notification_type,created_at)
            VALUES (?,?,?,?,?)
        """, (
            "buyer",
            f"Order {status}",
            f"Your order for {order['crop']} was {status.lower()} by the farmer.",
            "order",
            now()
        ))

        con.commit()

    con.close()

    return RedirectResponse(
        "/farmer/orders",
        status_code=303
    )


# ============================================================
# BUYER REQUIREMENTS PAGE
# ============================================================

@app.get("/buyer/requirements/new", response_class=HTMLResponse)
def new_requirement():

    options = ""

    for category, data in CATEGORIES.items():

        for crop in data["crops"]:
            options += f"""
            <option value="{crop}" data-category="{category}">
            {crop}
            </option>
            """

    return page("Post Requirement", f"""
<div class="container">

<a class="back" href="/buyer">← Buyer Dashboard</a>

<div class="form-card">

<h1>📋 Post Buyer Requirement</h1>

<form method="post" action="/buyer/requirement">

<label>Crop</label>

<select name="crop" required>
<option value="">Select Crop</option>
{options}
</select>

<label>Category</label>

<select name="category" required>
<option>Vegetables</option>
<option>Fruits</option>
<option>Flowers</option>
<option>Seeds</option>
<option>Pulses</option>
<option>Grains</option>
<option>Spices</option>
</select>

<label>Quantity Required (kg)</label>
<input type="number" name="quantity" min="1" step="0.1" required>

<label>Location</label>
<input name="location" placeholder="Delivery location" required>

<label>Buyer Name</label>
<input name="buyer_name" value="Demo Buyer">

<label>Phone</label>
<input name="phone" value="8888888888">

<label>Payment</label>

<select name="payment" required>
<option>UPI</option>
<option>Cash on Delivery</option>
<option>Bank Transfer</option>
<option>Cash at Pickup</option>
</select>

<button type="submit">
📋 Post Requirement
</button>

</form>

</div>

</div>
""")


# ============================================================
# FARMER REQUIREMENTS
# ============================================================

@app.get("/farmer/requirements", response_class=HTMLResponse)
def farmer_requirements():

    con = db()

    rows = con.execute("""
        SELECT * FROM requirements
        WHERE status='Open'
        ORDER BY id DESC
    """).fetchall()

    con.close()

    content = ""

    for r in rows:

        content += f"""
<div class="item">

<h3>📋 {esc(r['crop'])}</h3>

<p>
Buyer: <b>{esc(r['buyer_name'])}</b>
</p>

<p>
Required:
<b>{r['quantity']} kg</b>
</p>

<p>
Location:
<b>{esc(r['location'])}</b>
</p>

<p>
Payment:
{esc(r['payment'])}
</p>

<p>
Phone:
<a href="tel:{esc(r['phone'])}">
{esc(r['phone'])}
</a>
</p>

<span class="badge">{esc(r['status'])}</span>

<br><br>

<a class="button"
href="/farmer/message/{r['id']}">
💬 Contact Buyer
</a>

</div>
"""

    if not content:
        content = """
<div class="empty">
<div class="empty-icon">📋</div>
<h2>No open requirements</h2>
<p>New buyer requests will appear here.</p>
</div>
"""

    return page("Buyer Requirements", f"""
<div class="container">

<a class="back" href="/farmer">← Farmer Dashboard</a>

<h1>📋 Buyer Requirements</h1>

<div class="list">
{content}
</div>

</div>
""")


# ============================================================
# MATCHING
# ============================================================

@app.get("/buyer/matches", response_class=HTMLResponse)
def buyer_matches():

    con = db()

    requirements = con.execute("""
        SELECT * FROM requirements
        ORDER BY id DESC
        LIMIT 10
    """).fetchall()

    crops = con.execute("""
        SELECT * FROM crops
        WHERE quantity > 0
        ORDER BY id DESC
    """).fetchall()

    con.close()

    content = ""

    for r in requirements:

        matched = [
            c for c in crops
            if c["crop"].lower() == r["crop"].lower()
        ]

        content += f"""
<div class="item">

<h3>🤝 Matches for {esc(r['crop'])}</h3>

<p>
Requirement:
<b>{r['quantity']} kg</b>
</p>

"""

        if matched:

            for c in matched:

                content += f"""
<div class="section">

<h3>🌾 {esc(c['crop'])}</h3>

<p>
Farmer: <b>{esc(c['farmer_name'])}</b>
</p>

<p>
Location: {esc(c['location'])}
</p>

<p>
Available: {c['quantity']} kg
</p>

<p class="price">
₹{c['price']}/kg
</p>

<a class="button" href="/buyer/buy/{c['id']}">
Buy
</a>

<a class="button secondary"
href="/buyer/contact/{c['id']}">
Contact Farmer
</a>

</div>
"""

        else:

            content += """
<p>
No exact crop match yet. More farmers may list this crop later.
</p>
"""

        content += "</div>"

    if not content:
        content = """
<div class="empty">
<div class="empty-icon">🤝</div>
<h2>No matches yet</h2>
<p>Post a requirement first.</p>
<a class="button" href="/buyer/requirements/new">
Post Requirement
</a>
</div>
"""

    return page("Matched Farmers", f"""
<div class="container">

<a class="back" href="/buyer">← Buyer Dashboard</a>

<h1>🤝 Matched Farmers</h1>

<div class="list">
{content}
</div>

</div>
""")


@app.get("/farmer/matches", response_class=HTMLResponse)
def farmer_matches():

    con = db()

    requirements = con.execute("""
        SELECT * FROM requirements
        WHERE status='Open'
        ORDER BY id DESC
    """).fetchall()

    crops = con.execute("""
        SELECT * FROM crops
    """).fetchall()

    con.close()

    content = ""

    for r in requirements:

        matched = [
            c for c in crops
            if c["crop"].lower() == r["crop"].lower()
        ]

        if matched:

            content += f"""
<div class="item">

<h3>🤝 Buyer wants {esc(r['crop'])}</h3>

<p>
Quantity:
<b>{r['quantity']} kg</b>
</p>

<p>
Location:
{esc(r['location'])}
</p>

<a class="button"
href="/farmer/message/{r['id']}">
Contact Buyer
</a>

</div>
"""

    if not content:
        content = """
<div class="empty">
<div class="empty-icon">🤝</div>
<h2>No matches yet</h2>
<p>List crops that buyers are requesting.</p>
</div>
"""

    return page("Matched Buyers", f"""
<div class="container">

<a class="back" href="/farmer">← Farmer Dashboard</a>

<h1>🤝 Matched Buyers</h1>

<div class="list">
{content}
</div>

</div>
""")


# ============================================================
# FLASH SALES
# ============================================================

@app.get("/farmer/flash-sale", response_class=HTMLResponse)
def farmer_flash():

    con = db()

    crops = con.execute("""
        SELECT * FROM crops
        WHERE flash_sale=1
        ORDER BY id DESC
    """).fetchall()

    con.close()

    content = ""

    for c in crops:

        content += f"""
<div class="item flash">

<h3>⚡ {esc(c['crop'])}</h3>

<p>Farmer: {esc(c['farmer_name'])}</p>

<p class="flash-price">
₹{c['price']}/kg
</p>

<p>
{c['quantity']} kg available
</p>

</div>
"""

    if not content:
        content = """
<div class="empty">
<div class="empty-icon">⚡</div>
<h2>No Flash Sale Crops</h2>
<p>Add a crop and activate Flash Sale.</p>
</div>
"""

    return page("Flash Sale", f"""
<div class="container">

<a class="back" href="/farmer">← Farmer Dashboard</a>

<h1>⚡ Flash Sale</h1>

<div class="list">
{content}
</div>

</div>
""")


@app.get("/buyer/flash-sale", response_class=HTMLResponse)
def buyer_flash():

    con = db()

    crops = con.execute("""
        SELECT * FROM crops
        WHERE flash_sale=1 AND quantity > 0
    """).fetchall()

    con.close()

    content = ""

    for c in crops:

        content += f"""
<div class="crop-card">

<div class="badge orange">
⚡ FLASH SALE
</div>

<h3>{esc(c['crop'])}</h3>

<p>{esc(c['farmer_name'])}</p>

<p class="price">
₹{c['price']}/kg
</p>

<p>{c['quantity']} kg available</p>

<a class="button" href="/buyer/buy/{c['id']}">
Buy Now
</a>

</div>
"""

    if not content:
        content = """
<div class="empty">
<div class="empty-icon">⚡</div>
<h2>No Flash Sale Available</h2>
</div>
"""

    return page("Flash Sale", f"""
<div class="container">

<a class="back" href="/buyer">← Buyer Dashboard</a>

<h1>⚡ Flash Sale</h1>

<div class="crop-grid">
{content}
</div>

</div>
""")


# ============================================================
# CONTACT FARMER
# ============================================================

@app.get("/buyer/contact/{crop_id}", response_class=HTMLResponse)
def contact_farmer(crop_id: int):

    con = db()

    crop = con.execute(
        "SELECT * FROM crops WHERE id=?",
        (crop_id,)
    ).fetchone()

    con.close()

    if not crop:
        return HTMLResponse("Crop not found", status_code=404)

    phone = crop["phone"]

    return page("Contact Farmer", f"""
<div class="container">

<a class="back" href="/buyer/browse">← Browse Crops</a>

<div class="form-card">

<h1>📞 Contact Farmer</h1>

<h2>{esc(crop['crop'])}</h2>

<p>
Farmer:
<b>{esc(crop['farmer_name'])}</b>
</p>

<p>
Location:
{esc(crop['location'])}
</p>

<p>
Phone:
<b>{esc(phone)}</b>
</p>

<a class="button"
href="tel:{esc(phone)}">
📞 Call Farmer
</a>

<a class="button secondary"
href="/buyer/message/{crop_id}">
💬 Send Message
</a>

</div>

</div>
""")


# ============================================================
# MESSAGES
# ============================================================

@app.get("/buyer/messages", response_class=HTMLResponse)
def buyer_messages():

    return message_page("Buyer", "/buyer")


@app.get("/farmer/messages", response_class=HTMLResponse)
def farmer_messages():

    return message_page("Farmer", "/farmer")


def message_page(role, back):

    con = db()

    messages = con.execute("""
        SELECT * FROM messages
        ORDER BY id DESC
        LIMIT 100
    """).fetchall()

    con.close()

    content = ""

    for m in reversed(messages):

        content += f"""
<div class="message">
<strong>{esc(m['sender'])}</strong>
→ {esc(m['receiver'])}

<br>

{esc(m['message'])}

<br>

<small>{esc(m['created_at'])}</small>
</div>
"""

    return page("Messages", f"""
<div class="container">

<a class="back" href="{back}">
← Dashboard
</a>

<h1>💬 Messages</h1>

<div class="chat-box">

<div class="chat-messages">
{content or '<p>No messages yet.</p>'}
</div>

<form method="post" action="/message/send">

<input type="hidden" name="sender" value="{role}">
<input type="hidden"
       name="receiver"
       value="Farmer" if="{role}" == "Buyer" else "Buyer">

<label>Message</label>

<input
    name="message"
    placeholder="Write a message..."
    required
>

<button type="submit">
Send Message
</button>

</form>

</div>

</div>
""")


@app.post("/message/send")
def send_message(
    sender: str = Form(...),
    receiver: str = Form(...),
    message: str = Form(...)
):

    con = db()

    con.execute("""
        INSERT INTO messages
        (sender,receiver,message,created_at)
        VALUES (?,?,?,?)
    """, (
        sender,
        receiver,
        message,
        now()
    ))

    con.execute("""
        INSERT INTO notifications
        (audience,title,message,notification_type,created_at)
        VALUES (?,?,?,?,?)
    """, (
        receiver.lower(),
        "💬 New Message",
        f"{sender} sent you a new message.",
        "message",
        now()
    ))

    con.commit()
    con.close()

    return RedirectResponse(
        f"/{'buyer' if sender == 'Buyer' else 'farmer'}/messages",
        status_code=303
    )


# ============================================================
# MESSAGE FROM REQUIREMENT
# ============================================================

@app.get("/farmer/message/{requirement_id}")
def farmer_message_requirement(requirement_id: int):

    con = db()

    r = con.execute(
        "SELECT * FROM requirements WHERE id=?",
        (requirement_id,)
    ).fetchone()

    con.close()

    if not r:
        return HTMLResponse("Requirement not found", status_code=404)

    return page("Contact Buyer", f"""
<div class="container">

<a class="back" href="/farmer/requirements">
← Requirements
</a>

<div class="form-card">

<h1>💬 Contact Buyer</h1>

<p>
Buyer: <b>{esc(r['buyer_name'])}</b>
</p>

<p>
Looking for:
<b>{esc(r['quantity'])} kg {esc(r['crop'])}</b>
</p>

<form method="post" action="/message/send">

<input type="hidden" name="sender" value="Farmer">
<input type="hidden" name="receiver" value="Buyer">

<label>Message</label>

<textarea
name="message"
required
>Hi, I can provide {esc(r['quantity'])} kg of {esc(r['crop'])}.</textarea>

<button type="submit">
💬 Send Message
</button>

</form>

</div>

</div>
""")


@app.get("/buyer/message/{crop_id}")
def buyer_message_crop(crop_id: int):

    con = db()

    c = con.execute(
        "SELECT * FROM crops WHERE id=?",
        (crop_id,)
    ).fetchone()

    con.close()

    if not c:
        return HTMLResponse("Crop not found", status_code=404)

    return page("Contact Farmer", f"""
<div class="container">

<div class="form-card">

<h1>💬 Contact Farmer</h1>

<p>
Farmer:
<b>{esc(c['farmer_name'])}</b>
</p>

<p>
Crop:
<b>{esc(c['crop'])}</b>
</p>

<form method="post" action="/message/send">

<input type="hidden" name="sender" value="Buyer">
<input type="hidden" name="receiver" value="Farmer">

<label>Message</label>

<textarea
name="message"
required
>Hi, I am interested in your {esc(c['crop'])}.</textarea>

<button type="submit">
Send Message
</button>

</form>

</div>

</div>
""")


# ============================================================
# NOTIFICATIONS
# ============================================================

@app.get("/farmer/notifications", response_class=HTMLResponse)
def farmer_notifications():

    return notifications_page("farmer", "/farmer")


@app.get("/buyer/notifications", response_class=HTMLResponse)
def buyer_notifications():

    return notifications_page("buyer", "/buyer")


def notifications_page(audience, back):

    con = db()

    rows = con.execute("""
        SELECT * FROM notifications
        WHERE audience IN ('all', ?)
        ORDER BY id DESC
    """, (audience,)).fetchall()

    con.execute("""
        UPDATE notifications
        SET is_read=1
        WHERE audience IN ('all', ?)
    """, (audience,))

    con.commit()
    con.close()

    content = ""

    for n in rows:

        content += f"""
<div class="item">

<h3>{esc(n['title'])}</h3>

<p>{esc(n['message'])}</p>

<small>{esc(n['created_at'])}</small>

</div>
"""

    if not content:
        content = """
<div class="empty">
<div class="empty-icon">🔔</div>
<h2>No notifications</h2>
</div>
"""

    return page("Notifications", f"""
<div class="container">

<a class="back" href="{back}">
← Dashboard
</a>

<h1>🔔 Notifications</h1>

<div class="list">
{content}
</div>

</div>
""")


# ============================================================
# REMINDERS
# ============================================================

@app.get("/farmer/reminders", response_class=HTMLResponse)
def farmer_reminders():

    return reminders_page("farmer", "/farmer")


@app.get("/buyer/reminders", response_class=HTMLResponse)
def buyer_reminders():

    return reminders_page("buyer", "/buyer")


def reminders_page(role, back):

    con = db()

    reminders = con.execute("""
        SELECT * FROM reminders
        WHERE role=?
        ORDER BY id DESC
    """, (role,)).fetchall()

    con.close()

    content = ""

    for r in reminders:

        status = "Completed" if r["done"] else "Pending"

        content += f"""
<div class="item">

<h3>⏰ {esc(r['title'])}</h3>

<p>{esc(r['note'])}</p>

<p>
Reminder:
<b>{esc(r['reminder_time'])}</b>
</p>

<span class="badge">{status}</span>

"""

        if not r["done"]:

            content += f"""
<br><br>

<a class="button"
href="/reminder/done/{r['id']}">
Mark Done
</a>
"""

        content += "</div>"

    if not content:
        content = """
<div class="empty">
<div class="empty-icon">⏰</div>
<h2>No reminders</h2>
</div>
"""

    return page("Reminders", f"""
<div class="container">

<a class="back" href="{back}">
← Dashboard
</a>

<div class="form-card">

<h1>⏰ Add Reminder</h1>

<form method="post" action="/reminder/add">

<input type="hidden" name="role" value="{role}">

<label>Reminder Title</label>
<input name="title" placeholder="Example: Contact tomato buyer" required>

<label>Note</label>
<textarea name="note"></textarea>

<label>Date and Time</label>
<input type="datetime-local" name="reminder_time" required>

<button type="submit">
⏰ Add Reminder
</button>

</form>

</div>

<br>

<h2>My Reminders</h2>

<div class="list">
{content}
</div>

</div>
""")


@app.post("/reminder/add")
def add_reminder(
    role: str = Form(...),
    title: str = Form(...),
    note: str = Form(""),
    reminder_time: str = Form(...)
):

    con = db()

    con.execute("""
        INSERT INTO reminders
        (role,title,note,reminder_time,created_at)
        VALUES (?,?,?,?,?)
    """, (
        role,
        title,
        note,
        reminder_time,
        now()
    ))

    con.commit()
    con.close()

    return RedirectResponse(
        f"/{role}/reminders",
        status_code=303
    )


@app.get("/reminder/done/{reminder_id}")
def reminder_done(reminder_id: int):

    con = db()

    reminder = con.execute(
        "SELECT role FROM reminders WHERE id=?",
        (reminder_id,)
    ).fetchone()

    if reminder:

        con.execute(
            "UPDATE reminders SET done=1 WHERE id=?",
            (reminder_id,)
        )

        con.commit()

        role = reminder["role"]

    else:
        role = "farmer"

    con.close()

    return RedirectResponse(
        f"/{role}/reminders",
        status_code=303
    )


# ============================================================
# API - LIVE DATA
# ============================================================

@app.get("/api/stats")
def stats():

    con = db()

    result = {
        "crops": con.execute(
            "SELECT COUNT(*) c FROM crops"
        ).fetchone()["c"],

        "requirements": con.execute(
            "SELECT COUNT(*) c FROM requirements"
        ).fetchone()["c"],

        "orders": con.execute(
            "SELECT COUNT(*) c FROM orders"
        ).fetchone()["c"],

        "messages": con.execute(
            "SELECT COUNT(*) c FROM messages"
        ).fetchone()["c"]
    }

    con.close()

    return JSONResponse(result)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )