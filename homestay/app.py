import os
import secrets
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, default=2)
    amenities = db.Column(db.Text)
    image = db.Column(db.String(255))
    available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Gallery(db.Model):
    __tablename__ = 'gallery'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    image = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(60), default='general')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    guest_name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, default=5)
    comment = db.Column(db.Text, nullable=False)
    photo = db.Column(db.String(255))
    approved = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BookingRequest(db.Model):
    __tablename__ = 'booking_requests'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=True)
    check_in = db.Column(db.Date)
    check_out = db.Column(db.Date)
    guests = db.Column(db.Integer, default=1)
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    room = db.relationship('Room', backref='bookings')


class Experience(db.Model):
    __tablename__ = 'experiences'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    distance = db.Column(db.String(60))
    image = db.Column(db.String(255))
    category = db.Column(db.String(60), default='adventure')


class AdminSetting(db.Model):
    __tablename__ = 'admin_settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


def save_uploaded_file(file, subfolder=''):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_name = f"{secrets.token_hex(8)}_{filename}"
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], subfolder)
        os.makedirs(upload_path, exist_ok=True)
        file.save(os.path.join(upload_path, unique_name))
        if subfolder:
            return f"uploads/{subfolder}/{unique_name}"
        return f"uploads/{unique_name}"
    return None


def init_db():
    with app.app_context():
        db.create_all()
        admin = Admin.query.filter_by(username='shailendr07').first()
        if not admin:
            admin = Admin(username='shailendr07')
            admin.set_password('Cloudvista@shailendra')
            db.session.add(admin)

        if not Experience.query.first():
            experiences = [
                Experience(title='Kunjapuri Temple', description='A famous Shakti Peetha temple offering panoramic views of the Himalayas and the Ganges. Best visited at sunrise for a spiritual experience.', distance='14 km', category='spiritual'),
                Experience(title='Neer Waterfall', description='A beautiful natural waterfall located in the forest area near Rishikesh. A perfect trekking destination for nature lovers.', distance='7 km', category='nature'),
                Experience(title='Shivpuri Rafting', description='Experience the thrill of white water rafting on the holy Ganges river at Shivpuri — one of the best rafting spots near Rishikesh.', distance='16 km', category='adventure'),
                Experience(title='Sunrise Viewpoints', description='Watch the golden sunrise from the hilltops near Narendra Nagar. The view of the valley covered in mist is absolutely breathtaking.', distance='3 km', category='nature'),
                Experience(title='Laxman Jhula', description='The iconic suspension bridge over the Ganges river, surrounded by ashrams and temples, offering a vibrant spiritual atmosphere.', distance='10 km', category='culture'),
                Experience(title='Beatles Ashram', description='Visit the famous Maharishi Mahesh Yogi Ashram where The Beatles stayed in 1968. Now an art gallery with beautiful murals.', distance='12 km', category='culture'),
            ]
            for exp in experiences:
                db.session.add(exp)

        if not Room.query.first():
            rooms = [
                Room(name='Mountain View Suite', description='Enjoy breathtaking Himalayan views from this luxurious suite. Features a private balcony, king-size bed, and premium amenities.', price=3500, capacity=2, amenities='King Bed, Private Balcony, Mountain View, AC, Hot Water, WiFi, Room Service', available=True),
                Room(name='Valley Deluxe Room', description='A spacious deluxe room overlooking the serene valley. Perfect for couples and solo travelers seeking a peaceful retreat.', price=2500, capacity=2, amenities='Queen Bed, Valley View, AC, Hot Water, WiFi, Attached Bathroom', available=True),
                Room(name='Garden Family Room', description='Ideal for families, this spacious room opens to a beautiful garden. Features two beds and a cozy sitting area.', price=4000, capacity=4, amenities='2 Beds, Garden View, Fan, Hot Water, WiFi, Attached Bathroom, Sitting Area', available=True),
                Room(name='Heritage Double Room', description='Experience traditional Garhwali hospitality in this elegantly designed room with local art and wooden furnishings.', price=2000, capacity=2, amenities='Double Bed, Traditional Decor, Fan, Hot Water, WiFi, Shared Bathroom', available=True),
            ]
            for room in rooms:
                db.session.add(room)

        if not Review.query.first():
            reviews = [
                Review(guest_name='Priya Sharma', rating=5, comment='Absolutely magical stay! The mountain views from our room were stunning. Shailendra ji is the most welcoming host. Will definitely return!', approved=True),
                Review(guest_name='Rahul Mehta', rating=5, comment='Best homestay experience in Rishikesh. The food was delicious, the rooms were clean, and the location is perfect. Highly recommended!', approved=True),
                Review(guest_name='Anita Verma', rating=5, comment='A peaceful retreat in the lap of nature. The sunrise view from the terrace is worth every penny. Thank you for the wonderful hospitality!', approved=True),
            ]
            for review in reviews:
                db.session.add(review)

        db.session.commit()


@app.route('/')
def index():
    featured_rooms = Room.query.filter_by(available=True).limit(3).all()
    reviews = Review.query.filter_by(approved=True).limit(3).all()
    return render_template('index.html', featured_rooms=featured_rooms, reviews=reviews)


@app.route('/rooms')
def rooms():
    all_rooms = Room.query.filter_by(available=True).all()
    return render_template('rooms.html', rooms=all_rooms)


@app.route('/gallery')
def gallery():
    images = Gallery.query.order_by(Gallery.created_at.desc()).all()
    return render_template('gallery.html', images=images)


@app.route('/experiences')
def experiences():
    all_experiences = Experience.query.all()
    return render_template('experiences.html', experiences=all_experiences)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    rooms_list = Room.query.filter_by(available=True).all()
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        room_id = request.form.get('room_id') or None
        check_in = request.form.get('check_in') or None
        check_out = request.form.get('check_out') or None
        guests = request.form.get('guests', 1)
        message = request.form.get('message')

        if check_in:
            check_in = datetime.strptime(check_in, '%Y-%m-%d').date()
        if check_out:
            check_out = datetime.strptime(check_out, '%Y-%m-%d').date()

        booking = BookingRequest(
            name=name, email=email, phone=phone,
            room_id=room_id, check_in=check_in, check_out=check_out,
            guests=int(guests), message=message
        )
        db.session.add(booking)
        db.session.commit()
        flash('Your booking request has been sent! We will contact you shortly.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', rooms=rooms_list)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials. Please try again.', 'danger')
    return render_template('admin/login.html')


@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))


@app.route('/admin-panel/dashboard')
@login_required
def admin_dashboard():
    rooms_count = Room.query.count()
    gallery_count = Gallery.query.count()
    reviews_count = Review.query.count()
    bookings_count = BookingRequest.query.count()
    recent_bookings = BookingRequest.query.order_by(BookingRequest.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html',
                           rooms_count=rooms_count,
                           gallery_count=gallery_count,
                           reviews_count=reviews_count,
                           bookings_count=bookings_count,
                           recent_bookings=recent_bookings)


@app.route('/admin-panel/rooms', methods=['GET', 'POST'])
@login_required
def admin_rooms():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price', 0))
        capacity = int(request.form.get('capacity', 2))
        amenities = request.form.get('amenities')
        available = request.form.get('available') == 'on'
        image_path = None
        if 'image' in request.files:
            image_path = save_uploaded_file(request.files['image'], 'rooms')
        room = Room(name=name, description=description, price=price,
                    capacity=capacity, amenities=amenities, available=available,
                    image=image_path)
        db.session.add(room)
        db.session.commit()
        flash('Room added successfully!', 'success')
        return redirect(url_for('admin_rooms'))
    all_rooms = Room.query.all()
    return render_template('admin/rooms_manage.html', rooms=all_rooms)


@app.route('/admin-panel/rooms/edit/<int:room_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_room(room_id):
    room = Room.query.get_or_404(room_id)
    if request.method == 'POST':
        room.name = request.form.get('name')
        room.description = request.form.get('description')
        room.price = float(request.form.get('price', 0))
        room.capacity = int(request.form.get('capacity', 2))
        room.amenities = request.form.get('amenities')
        room.available = request.form.get('available') == 'on'
        if 'image' in request.files and request.files['image'].filename:
            image_path = save_uploaded_file(request.files['image'], 'rooms')
            if image_path:
                room.image = image_path
        db.session.commit()
        flash('Room updated successfully!', 'success')
        return redirect(url_for('admin_rooms'))
    return render_template('admin/rooms_manage.html', rooms=Room.query.all(), edit_room=room)


@app.route('/admin-panel/rooms/delete/<int:room_id>', methods=['POST'])
@login_required
def admin_delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    db.session.delete(room)
    db.session.commit()
    flash('Room deleted successfully!', 'success')
    return redirect(url_for('admin_rooms'))


@app.route('/admin-panel/gallery', methods=['GET', 'POST'])
@login_required
def admin_gallery():
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category', 'general')
        image_path = None
        if 'image' in request.files:
            image_path = save_uploaded_file(request.files['image'], 'gallery')
        if image_path:
            gallery_item = Gallery(title=title, image=image_path, category=category)
            db.session.add(gallery_item)
            db.session.commit()
            flash('Image added to gallery!', 'success')
        else:
            flash('Please select a valid image file.', 'danger')
        return redirect(url_for('admin_gallery'))
    images = Gallery.query.order_by(Gallery.created_at.desc()).all()
    return render_template('admin/gallery_manage.html', images=images)


@app.route('/admin-panel/gallery/delete/<int:image_id>', methods=['POST'])
@login_required
def admin_delete_gallery(image_id):
    image = Gallery.query.get_or_404(image_id)
    db.session.delete(image)
    db.session.commit()
    flash('Image deleted successfully!', 'success')
    return redirect(url_for('admin_gallery'))


@app.route('/admin-panel/reviews', methods=['GET', 'POST'])
@login_required
def admin_reviews():
    if request.method == 'POST':
        guest_name = request.form.get('guest_name')
        rating = int(request.form.get('rating', 5))
        comment = request.form.get('comment')
        approved = request.form.get('approved') == 'on'
        photo_path = None
        if 'photo' in request.files and request.files['photo'].filename:
            photo_path = save_uploaded_file(request.files['photo'], 'reviews')
        review = Review(guest_name=guest_name, rating=rating, comment=comment,
                        photo=photo_path, approved=approved)
        db.session.add(review)
        db.session.commit()
        flash('Review added successfully!', 'success')
        return redirect(url_for('admin_reviews'))
    all_reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('admin/reviews_manage.html', reviews=all_reviews)


@app.route('/admin-panel/reviews/delete/<int:review_id>', methods=['POST'])
@login_required
def admin_delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted!', 'success')
    return redirect(url_for('admin_reviews'))


@app.route('/admin-panel/reviews/toggle/<int:review_id>', methods=['POST'])
@login_required
def admin_toggle_review(review_id):
    review = Review.query.get_or_404(review_id)
    review.approved = not review.approved
    db.session.commit()
    flash('Review status updated!', 'success')
    return redirect(url_for('admin_reviews'))


@app.route('/admin-panel/bookings')
@login_required
def admin_bookings():
    bookings = BookingRequest.query.order_by(BookingRequest.created_at.desc()).all()
    return render_template('admin/dashboard.html', bookings=bookings, show_bookings=True,
                           rooms_count=Room.query.count(),
                           gallery_count=Gallery.query.count(),
                           reviews_count=Review.query.count(),
                           bookings_count=BookingRequest.query.count(),
                           recent_bookings=bookings)


@app.route('/admin-panel/bookings/status/<int:booking_id>', methods=['POST'])
@login_required
def admin_update_booking(booking_id):
    booking = BookingRequest.query.get_or_404(booking_id)
    booking.status = request.form.get('status', 'pending')
    db.session.commit()
    flash('Booking status updated!', 'success')
    return redirect(url_for('admin_bookings'))


if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
