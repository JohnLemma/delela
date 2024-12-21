from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marketplace.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10))  # 'house' or 'car'
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    image_url = db.Column(db.String(200))
    
    # House-specific fields
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Float)
    square_feet = db.Column(db.Integer)
    year_built = db.Column(db.Integer)
    
    # Car-specific fields
    make = db.Column(db.String(50))
    model = db.Column(db.String(50))
    year = db.Column(db.Integer)
    mileage = db.Column(db.Integer)
    condition = db.Column(db.String(20))

def add_sample_data():
    # Only add sample data if the database is empty
    if Property.query.count() == 0:
        # Sample house data
        houses = [
            {
                "type": "house",
                "title": "Modern Villa with Pool",
                "description": "Luxurious 4-bedroom villa with a private pool and garden",
                "price": 8500000,  # 8.5 million ETB
                "location": "Bole, Addis Ababa",
                "image_url": "https://images.unsplash.com/photo-1564013799919-ab600027ffc6",
                "bedrooms": 4,
                "bathrooms": 3.5,
                "square_feet": 3200,
                "year_built": 2020
            },
            {
                "type": "house",
                "title": "Cozy Family Home",
                "description": "Beautiful 3-bedroom house in a quiet neighborhood",
                "price": 4500000,  # 4.5 million ETB
                "location": "CMC, Addis Ababa",
                "image_url": "https://images.unsplash.com/photo-1576941089067-2de3c901e126",
                "bedrooms": 3,
                "bathrooms": 2,
                "square_feet": 2400,
                "year_built": 2019
            }
        ]

        # Sample car data
        cars = [
            {
                "type": "car",
                "title": "2022 Toyota Land Cruiser",
                "description": "Well-maintained SUV with low mileage",
                "price": 12000000,  # 12 million ETB
                "location": "Addis Ababa",
                "image_url": "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf",
                "make": "Toyota",
                "model": "Land Cruiser",
                "year": 2022,
                "mileage": 15000,
                "condition": "Excellent"
            },
            {
                "type": "car",
                "title": "2021 Toyota Corolla",
                "description": "Fuel-efficient sedan in great condition",
                "price": 3500000,  # 3.5 million ETB
                "location": "Addis Ababa",
                "image_url": "https://images.unsplash.com/photo-1590362891991-f776e747a588",
                "make": "Toyota",
                "model": "Corolla",
                "year": 2021,
                "mileage": 25000,
                "condition": "Good"
            }
        ]

        try:
            # Add all properties to the database
            for house in houses:
                new_house = Property(**house)
                db.session.add(new_house)

            for car in cars:
                new_car = Property(**car)
                db.session.add(new_car)

            db.session.commit()
            print("Added sample data successfully!")
        except Exception as e:
            print(f"Error adding sample data: {e}")
            db.session.rollback()

# Initialize database and add sample data
with app.app_context():
    try:
        db.create_all()
        add_sample_data()
    except Exception as e:
        print(f"Error initializing database: {e}")

# Routes
@app.route('/')
def home():
    try:
        # Get filter parameters
        property_type = request.args.get('type', 'all')
        sort_by = request.args.get('sort', 'newest')
        search_query = request.args.get('search', '')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        
        # Base query
        query = Property.query
        
        # Apply filters
        if property_type != 'all':
            query = query.filter_by(type=property_type)
        
        if search_query:
            search = f"%{search_query}%"
            query = query.filter(
                db.or_(
                    Property.title.ilike(search),
                    Property.description.ilike(search),
                    Property.location.ilike(search)
                )
            )
        
        if min_price is not None:
            query = query.filter(Property.price >= min_price)
        if max_price is not None:
            query = query.filter(Property.price <= max_price)
        
        # Apply sorting
        if sort_by == 'price_low':
            query = query.order_by(Property.price.asc())
        elif sort_by == 'price_high':
            query = query.order_by(Property.price.desc())
        elif sort_by == 'newest':
            query = query.order_by(Property.created_at.desc())
        else:  # oldest
            query = query.order_by(Property.created_at.asc())
        
        properties = query.all()
        return render_template('index.html', properties=properties)
    except Exception as e:
        print(f"Error in home route: {e}")
        flash('An error occurred while loading properties.', 'danger')
        return render_template('index.html', properties=[])

@app.route('/property/<int:property_id>')
def property_detail(property_id):
    try:
        property = Property.query.get_or_404(property_id)
        return render_template('property_detail.html', property=property)
    except Exception as e:
        print(f"Error in property_detail route: {e}")
        flash('Property not found.', 'danger')
        return redirect(url_for('home'))

@app.route('/add', methods=['GET', 'POST'])
def add_property():
    if request.method == 'POST':
        try:
            data = {
                'type': request.form['type'],
                'title': request.form['title'],
                'description': request.form['description'],
                'price': float(request.form['price']),
                'location': request.form['location'],
                'image_url': request.form['image_url']
            }
            
            if data['type'] == 'house':
                data.update({
                    'bedrooms': int(request.form['bedrooms']),
                    'bathrooms': float(request.form['bathrooms']),
                    'square_feet': int(request.form['square_feet']),
                    'year_built': int(request.form['year_built'])
                })
            else:  # car
                data.update({
                    'make': request.form['make'],
                    'model': request.form['model'],
                    'year': int(request.form['year']),
                    'mileage': int(request.form['mileage']),
                    'condition': request.form['condition']
                })
            
            new_property = Property(**data)
            db.session.add(new_property)
            db.session.commit()
            
            flash('Property added successfully!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            print(f"Error adding property: {e}")
            flash('Error adding property. Please try again.', 'danger')
            return redirect(url_for('add_property'))
    
    return render_template('add_property.html')

if __name__ == '__main__':
    app.run(debug=True)
