from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marketplace.db'
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
    # Additional fields for houses
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Float)
    square_feet = db.Column(db.Integer)
    year_built = db.Column(db.Integer)
    # Additional fields for cars
    make = db.Column(db.String(50))
    model = db.Column(db.String(50))
    year = db.Column(db.Integer)
    mileage = db.Column(db.Integer)
    condition = db.Column(db.String(20))

# Routes
@app.route('/')
def home():
    # Get filter parameters
    property_type = request.args.get('type', 'all')
    sort_by = request.args.get('sort', 'created_at')
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
    return render_template('index.html', 
                         properties=properties,
                         property_type=property_type,
                         sort_by=sort_by,
                         search_query=search_query,
                         min_price=min_price,
                         max_price=max_price)

@app.route('/add', methods=['GET', 'POST'])
def add_property():
    if request.method == 'POST':
        property_type = request.form['type']
        new_property = Property(
            type=property_type,
            title=request.form['title'],
            description=request.form['description'],
            price=float(request.form['price']),
            location=request.form['location'],
            image_url=request.form['image_url']
        )
        
        # Add type-specific fields
        if property_type == 'house':
            new_property.bedrooms = request.form.get('bedrooms', type=int)
            new_property.bathrooms = request.form.get('bathrooms', type=float)
            new_property.square_feet = request.form.get('square_feet', type=int)
            new_property.year_built = request.form.get('year_built', type=int)
        else:  # car
            new_property.make = request.form.get('make')
            new_property.model = request.form.get('model')
            new_property.year = request.form.get('year', type=int)
            new_property.mileage = request.form.get('mileage', type=int)
            new_property.condition = request.form.get('condition')
        
        db.session.add(new_property)
        db.session.commit()
        flash('Property added successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('add_property.html')

@app.route('/property/<int:id>')
def property_detail(id):
    property = Property.query.get_or_404(id)
    return render_template('property_detail.html', property=property)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Add test data if the database is empty
        if Property.query.count() == 0:
            # Sample house data
            houses = [
                {
                    "type": "house",
                    "title": "Modern Villa with Pool",
                    "description": "Luxurious 4-bedroom villa with a private pool and garden",
                    "price": 850000,
                    "location": "Beverly Hills, CA",
                    "image_url": "https://images.unsplash.com/photo-1564013799919-ab600027ffc6",
                    "bedrooms": 4,
                    "bathrooms": 3.5,
                    "square_feet": 3200,
                    "year_built": 2020
                },
                {
                    "type": "house",
                    "title": "Cozy Downtown Apartment",
                    "description": "Modern 2-bedroom apartment in the heart of the city",
                    "price": 425000,
                    "location": "Manhattan, NY",
                    "image_url": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",
                    "bedrooms": 2,
                    "bathrooms": 2,
                    "square_feet": 1200,
                    "year_built": 2018
                },
                {
                    "type": "house",
                    "title": "Seaside Beach House",
                    "description": "Beautiful 3-bedroom house with ocean views",
                    "price": 975000,
                    "location": "Malibu, CA",
                    "image_url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750",
                    "bedrooms": 3,
                    "bathrooms": 2.5,
                    "square_feet": 2800,
                    "year_built": 2019
                },
                {
                    "type": "house",
                    "title": "Mountain View Cabin",
                    "description": "Rustic 2-bedroom cabin with stunning mountain views",
                    "price": 350000,
                    "location": "Aspen, CO",
                    "image_url": "https://images.unsplash.com/photo-1518780664697-55e3ad937233",
                    "bedrooms": 2,
                    "bathrooms": 1,
                    "square_feet": 1500,
                    "year_built": 2015
                },
                {
                    "type": "house",
                    "title": "Suburban Family Home",
                    "description": "Spacious 5-bedroom home perfect for families",
                    "price": 650000,
                    "location": "Austin, TX",
                    "image_url": "https://images.unsplash.com/photo-1568605114967-8130f3a36994",
                    "bedrooms": 5,
                    "bathrooms": 3,
                    "square_feet": 3800,
                    "year_built": 2017
                },
                {
                    "type": "house",
                    "title": "Urban Loft",
                    "description": "Contemporary 1-bedroom loft in historic building",
                    "price": 375000,
                    "location": "Chicago, IL",
                    "image_url": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688",
                    "bedrooms": 1,
                    "bathrooms": 1,
                    "square_feet": 950,
                    "year_built": 2016
                },
                {
                    "type": "house",
                    "title": "Luxury Penthouse",
                    "description": "Exclusive 3-bedroom penthouse with city views",
                    "price": 1250000,
                    "location": "Miami, FL",
                    "image_url": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00",
                    "bedrooms": 3,
                    "bathrooms": 3.5,
                    "square_feet": 2500,
                    "year_built": 2021
                }
            ]

            # Sample car data
            cars = [
                {
                    "type": "car",
                    "title": "2022 Tesla Model S",
                    "description": "Fully electric luxury sedan with autopilot",
                    "price": 89990,
                    "location": "San Francisco, CA",
                    "image_url": "https://images.unsplash.com/photo-1617788138017-80ad40651399",
                    "make": "Tesla",
                    "model": "Model S",
                    "year": 2022,
                    "mileage": 15000,
                    "condition": "Excellent"
                },
                {
                    "type": "car",
                    "title": "2021 BMW M3",
                    "description": "High-performance luxury sports car",
                    "price": 68000,
                    "location": "Los Angeles, CA",
                    "image_url": "https://images.unsplash.com/photo-1607853202273-797f1c22a38e",
                    "make": "BMW",
                    "model": "M3",
                    "year": 2021,
                    "mileage": 25000,
                    "condition": "Good"
                },
                {
                    "type": "car",
                    "title": "2023 Ford Mustang GT",
                    "description": "Classic American muscle car",
                    "price": 55000,
                    "location": "Detroit, MI",
                    "image_url": "https://images.unsplash.com/photo-1584345604476-8ec5e12e42dd",
                    "make": "Ford",
                    "model": "Mustang GT",
                    "year": 2023,
                    "mileage": 5000,
                    "condition": "New"
                },
                {
                    "type": "car",
                    "title": "2020 Toyota Camry",
                    "description": "Reliable mid-size sedan",
                    "price": 25000,
                    "location": "Phoenix, AZ",
                    "image_url": "https://images.unsplash.com/photo-1621007947382-bb3c3994e3fb",
                    "make": "Toyota",
                    "model": "Camry",
                    "year": 2020,
                    "mileage": 45000,
                    "condition": "Good"
                },
                {
                    "type": "car",
                    "title": "2022 Porsche 911",
                    "description": "High-end sports car with premium features",
                    "price": 135000,
                    "location": "Miami, FL",
                    "image_url": "https://images.unsplash.com/photo-1614162692292-7ac56d7f7f1e",
                    "make": "Porsche",
                    "model": "911",
                    "year": 2022,
                    "mileage": 8000,
                    "condition": "Excellent"
                },
                {
                    "type": "car",
                    "title": "2021 Honda CR-V",
                    "description": "Popular compact SUV",
                    "price": 28500,
                    "location": "Seattle, WA",
                    "image_url": "https://images.unsplash.com/photo-1568844293986-ca411c1a9ac9",
                    "make": "Honda",
                    "model": "CR-V",
                    "year": 2021,
                    "mileage": 35000,
                    "condition": "Good"
                },
                {
                    "type": "car",
                    "title": "2023 Audi e-tron GT",
                    "description": "Premium electric sports sedan",
                    "price": 102000,
                    "location": "Dallas, TX",
                    "image_url": "https://images.unsplash.com/photo-1617814065893-00757125efab",
                    "make": "Audi",
                    "model": "e-tron GT",
                    "year": 2023,
                    "mileage": 3000,
                    "condition": "Like New"
                },
                {
                    "type": "car",
                    "title": "2022 Mercedes-Benz S-Class",
                    "description": "Ultimate luxury sedan",
                    "price": 115000,
                    "location": "New York, NY",
                    "image_url": "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8",
                    "make": "Mercedes-Benz",
                    "model": "S-Class",
                    "year": 2022,
                    "mileage": 12000,
                    "condition": "Excellent"
                }
            ]

            # Add all properties to the database
            for house in houses:
                new_house = Property(**house)
                db.session.add(new_house)

            for car in cars:
                new_car = Property(**car)
                db.session.add(new_car)

            db.session.commit()
            print("Added sample data to the database!")

    app.run(debug=True)
