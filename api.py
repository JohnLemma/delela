from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_cors import CORS
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marketplace.db'
db = SQLAlchemy(app)
api = Api(app)

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

# Schemas for serialization
class PropertySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Property
        include_relationships = True
        load_instance = True

property_schema = PropertySchema()
properties_schema = PropertySchema(many=True)

# API Resources
class PropertyListAPI(Resource):
    def get(self):
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
        return properties_schema.dump(properties)

    def post(self):
        try:
            data = request.get_json()
            new_property = Property(**data)
            db.session.add(new_property)
            db.session.commit()
            return property_schema.dump(new_property), 201
        except Exception as e:
            return {'message': str(e)}, 400

class PropertyAPI(Resource):
    def get(self, property_id):
        property = Property.query.get_or_404(property_id)
        return property_schema.dump(property)

    def put(self, property_id):
        property = Property.query.get_or_404(property_id)
        data = request.get_json()
        
        for key, value in data.items():
            setattr(property, key, value)
            
        db.session.commit()
        return property_schema.dump(property)

    def delete(self, property_id):
        property = Property.query.get_or_404(property_id)
        db.session.delete(property)
        db.session.commit()
        return '', 204

# Register API resources
api.add_resource(PropertyListAPI, '/api/properties')
api.add_resource(PropertyAPI, '/api/properties/<int:property_id>')

# Additional endpoints for specific queries
@app.route('/api/properties/types')
def get_property_types():
    return jsonify({
        'types': ['house', 'car']
    })

@app.route('/api/properties/stats')
def get_property_stats():
    total_properties = Property.query.count()
    total_houses = Property.query.filter_by(type='house').count()
    total_cars = Property.query.filter_by(type='car').count()
    avg_house_price = db.session.query(db.func.avg(Property.price)).filter_by(type='house').scalar() or 0
    avg_car_price = db.session.query(db.func.avg(Property.price)).filter_by(type='car').scalar() or 0
    
    return jsonify({
        'total_properties': total_properties,
        'total_houses': total_houses,
        'total_cars': total_cars,
        'average_house_price': round(avg_house_price, 2),
        'average_car_price': round(avg_car_price, 2)
    })

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
                # ... (previous sample data)
            ]

            # Add all properties to the database
            for house in houses:
                new_house = Property(**house)
                db.session.add(new_house)

            db.session.commit()
            print("Added sample data to the database!")

    app.run(debug=True, host='0.0.0.0', port=5000)
