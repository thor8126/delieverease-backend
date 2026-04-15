from werkzeug.security import generate_password_hash
from models import db, User, Store, MenuItem


def seed_database():
    """Seed the database with demo data if empty."""
    if User.query.first() is not None:
        print("Database already seeded. Skipping.")
        return

    print("Seeding database...")

    # Default password for all demo accounts
    default_pw = generate_password_hash("password123")

    # Platform Owner account
    owner = User(
        name="Platform Owner",
        email="owner@deliverease.com",
        password_hash=default_pw,
        role="owner",
        address="DeliverEase HQ",
    )
    db.session.add(owner)

    # Merchant account
    merchant = User(
        name="Pizza Palace",
        email="merchant@demo.com",
        password_hash=default_pw,
        role="merchant",
        address="123 Market Street, Downtown",
    )
    db.session.add(merchant)
    db.session.flush()  # get merchant.id

    # Rider account
    rider = User(
        name="Ravi Kumar",
        email="rider@demo.com",
        password_hash=default_pw,
        role="rider",
        address="45 Rider Lane, Central Area",
    )
    db.session.add(rider)

    # A demo customer
    customer = User(
        name="Demo Customer",
        email="customer@demo.com",
        password_hash=default_pw,
        role="customer",
        address="78 Customer Road, Suburbs",
    )
    db.session.add(customer)

    # Store linked to merchant
    store = Store(
        merchant_id=merchant.id,
        name="Pizza Palace",
        category="Food",
        is_open=True,
        image_url="https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=800&q=80",
    )
    db.session.add(store)
    db.session.flush()  # get store.id

    # Second store - Grocery
    merchant2 = User(
        name="FreshMart",
        email="merchant2@demo.com",
        password_hash=default_pw,
        role="merchant",
        address="200 Grocery Blvd",
    )
    db.session.add(merchant2)
    db.session.flush()

    store2 = Store(
        merchant_id=merchant2.id,
        name="FreshMart Grocery",
        category="Grocery",
        is_open=True,
        image_url="https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=800&q=80",
    )
    db.session.add(store2)
    db.session.flush()

    # Third store - Bakery
    merchant3 = User(
        name="Sweet Crust Bakery",
        email="merchant3@demo.com",
        password_hash=default_pw,
        role="merchant",
        address="55 Baker Street",
    )
    db.session.add(merchant3)
    db.session.flush()

    store3 = Store(
        merchant_id=merchant3.id,
        name="Sweet Crust Bakery",
        category="Bakery",
        is_open=True,
        image_url="https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=800&q=80",
    )
    db.session.add(store3)
    db.session.flush()

    # Menu items for Pizza Palace (AUD)
    pizza_items = [
        MenuItem(store_id=store.id, name="Margherita Pizza", price=18.99, image_url="https://images.unsplash.com/photo-1574071318508-1cdbab80d002?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store.id, name="Pepperoni Pizza", price=24.50, image_url="https://images.unsplash.com/photo-1628840042765-356cda07504e?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store.id, name="Garlic Bread", price=8.50, image_url="https://images.unsplash.com/photo-1573140247632-f8fd74997d5c?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store.id, name="Hawaiian Pizza", price=21.00, image_url="https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store.id, name="BBQ Chicken Pizza", price=23.50, image_url="https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store.id, name="Meat Lovers Pizza", price=26.50, image_url="https://images.unsplash.com/photo-1604382354936-07c5d9983bd3?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store.id, name="Vegan Delight Pizza", price=22.00, image_url="https://images.unsplash.com/photo-1574071318508-1cdbab80d002?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store.id, name="Cola (Can)", price=3.50, image_url="https://images.unsplash.com/photo-1622483767028-3f66f32aef97?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store.id, name="Chocolate Lava Cake", price=12.00, image_url="https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store.id, name="Tiramisu", price=14.50, image_url="https://images.unsplash.com/photo-1571115177098-24ec42ed204d?auto=format&fit=crop&w=800&q=80", is_available=True),
    ]
    db.session.add_all(pizza_items)

    # Menu items for FreshMart (AUD)
    grocery_items = [
        MenuItem(store_id=store2.id, name="Organic Bananas (1 kg)", price=4.50, image_url="https://images.unsplash.com/photo-1571501679680-de32f1e7aad4?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store2.id, name="Whole Wheat Bread", price=3.80, image_url="https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store2.id, name="Full Cream Milk (1L)", price=2.50, image_url="https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store2.id, name="Free Range Eggs (1Dozen)", price=7.50, image_url="https://images.unsplash.com/photo-1506976773554-15c2d30d1aa5?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store2.id, name="Basmati Rice (5 kg)", price=22.00, image_url="https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store2.id, name="Fuji Apples (1 kg)", price=6.00, image_url="https://images.unsplash.com/photo-1560806887-1e4cd0b6faa6?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store2.id, name="Avocados (2 pack)", price=5.50, image_url="https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store2.id, name="Greek Yogurt (500g)", price=4.20, image_url="https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store2.id, name="Fresh Orange Juice (1L)", price=5.00, image_url="https://images.unsplash.com/photo-1622483767028-3f66f32aef97?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store2.id, name="Cheddar Cheese (250g)", price=8.50, image_url="https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?auto=format&fit=crop&w=800&q=80", is_available=True),
    ]
    db.session.add_all(grocery_items)

    # Menu items for Sweet Crust Bakery (AUD)
    bakery_items = [
        MenuItem(store_id=store3.id, name="Butter Croissant", price=5.50, image_url="https://images.unsplash.com/photo-1555507036-ab1f40ce88cb?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store3.id, name="Chocolate Muffin", price=4.50, image_url="https://images.unsplash.com/photo-1606890737305-7baa6f452097?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store3.id, name="Blueberry Cheesecake", price=8.50, image_url="https://images.unsplash.com/photo-1533134242443-d4fd215305ad?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store3.id, name="Sourdough Loaf", price=7.00, image_url="https://images.unsplash.com/photo-1586444248902-2f64ed30a7d9?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store3.id, name="Cinnamon Roll", price=6.00, image_url="https://images.unsplash.com/photo-1509365465994-3e813a35b1c5?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store3.id, name="Apple Pie Slice", price=7.50, image_url="https://images.unsplash.com/photo-1621236378699-8597faa6a71e?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store3.id, name="Almond Croissant", price=6.50, image_url="https://images.unsplash.com/photo-1623366302587-bca8eb2df1b9?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store3.id, name="Macarons (6 pack)", price=15.00, image_url="https://images.unsplash.com/photo-1569864358642-9d1684040f43?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store3.id, name="Chocolate Eclair", price=6.00, image_url="https://images.unsplash.com/photo-1612201142855-7873bc1661b4?auto=format&fit=crop&w=800&q=80", is_available=True),
        MenuItem(store_id=store3.id, name="Fruit Tart", price=6.50, image_url="https://images.unsplash.com/photo-1519915028121-7d3463d20a1b?auto=format&fit=crop&w=800&q=80", is_available=True),
    ]
    db.session.add_all(bakery_items)

    db.session.commit()
    print("Database seeded successfully!")
    print("  Demo accounts (password: password123):")
    print("    Owner:    owner@deliverease.com")
    print("    Customer: customer@demo.com")
    print("    Rider:    rider@demo.com")
    print("    Merchant: merchant@demo.com  (Pizza Palace)")
    print("    Merchant: merchant2@demo.com (FreshMart)")
    print("    Merchant: merchant3@demo.com (Sweet Crust Bakery)")

