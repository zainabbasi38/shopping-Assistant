import json

PRODUCTS_FILE = "products.json"

def load_products():
    try:
        with open(PRODUCTS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def get_product_details(name):
    products = load_products()
    product = products.get(name.lower())
    if product:
        return f"Name: {name}\nPrice: {product['price']}\nDescription: {product['description']}"
    else:
        return "Sorry, this product is not available."

def add_product(name, price, description):
    products = load_products()
    products[name.lower()] = {"price": price, "description": description}
    
    with open(PRODUCTS_FILE, "w") as file:
        json.dump(products, file, indent=4)

    return f"Product '{name}' added successfully!"


def save_products(products):
    with open(PRODUCTS_FILE, "w") as file:
        json.dump(products, file, indent=4)


def remove_product(name: str) -> str:
    products = load_products()
    if name not in products:
        return f"Product '{name}' not found!"
    
    del products[name]
    save_products(products)
    return f"Product '{name}' removed successfully!"

def update_product(name: str, new_name: str = None, new_price: float = None, new_description: str = None) -> str:
    products = load_products()
    if name not in products:
        return f"Product '{name}' not found!"
    
    if new_name:
        products[new_name] = products.pop(name)
        name = new_name
    if new_price:
        products[name]["price"] = new_price
    if new_description:
        products[name]["description"] = new_description

    save_products(products)
    return f"Product '{name}' updated successfully!"

def list_all_products() -> str:
        """Retrieve the names of all available products in the inventory."""
        products = load_products()
        if not products:
            return "No products available in the inventory."
        return "Available products: " + ", ".join(products.keys())