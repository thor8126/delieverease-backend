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
        image_url="",
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
        image_url="",
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
        image_url="",
    )
    db.session.add(store3)
    db.session.flush()

    # Menu items for Pizza Palace
    pizza_items = [
        MenuItem(store_id=store.id, name="Margherita Pizza", price=199.0, is_available=True),
        MenuItem(store_id=store.id, name="Pepperoni Pizza", price=249.0, is_available=True),
        MenuItem(store_id=store.id, name="Garlic Bread", price=89.0, is_available=True),
        MenuItem(store_id=store.id, name="Cola", price=49.0, is_available=True),
        MenuItem(store_id=store.id, name="Chocolate Lava Cake", price=129.0, is_available=True),
    ]
    db.session.add_all(pizza_items)

    # Menu items for FreshMart
    grocery_items = [
        MenuItem(store_id=store2.id, name="Organic Bananas (1 kg)", price=59.0, is_available=True),
        MenuItem(store_id=store2.id, name="Whole Wheat Bread", price=45.0, is_available=True),
        MenuItem(store_id=store2.id, name="Full Cream Milk (1L)", price=65.0, is_available=True),
        MenuItem(store_id=store2.id, name="Free Range Eggs (12)", price=120.0, is_available=True),
        MenuItem(store_id=store2.id, name="Basmati Rice (5 kg)", price=399.0, is_available=True),
    ]
    db.session.add_all(grocery_items)

    # Menu items for Sweet Crust Bakery
    bakery_items = [
        MenuItem(store_id=store3.id, name="Butter Croissant", price=79.0, is_available=True),
        MenuItem(store_id=store3.id, name="Chocolate Muffin", price=69.0, is_available=True),
        MenuItem(store_id=store3.id, name="Blueberry Cheesecake (Slice)", price=149.0, is_available=True),
        MenuItem(store_id=store3.id, name="Sourdough Loaf", price=199.0, is_available=True),
        MenuItem(store_id=store3.id, name="Cinnamon Roll", price=89.0, is_available=True),
    ]
    db.session.add_all(bakery_items)

    db.session.commit()
    print("Database seeded successfully!")
    print("  Demo accounts (password: password123):")
    print("    Customer: customer@demo.com")
    print("    Rider:    rider@demo.com")
    print("    Merchant: merchant@demo.com  (Pizza Palace)")
    print("    Merchant: merchant2@demo.com (FreshMart)")
    print("    Merchant: merchant3@demo.com (Sweet Crust Bakery)")
