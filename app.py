from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import FloatField, IntegerField, SelectField, StringField,SubmitField,BooleanField
import os
from datetime import datetime
from wtforms.validators import DataRequired, NumberRange, Regexp, Length

app=Flask(__name__)
app.secret_key='mykey'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'parking.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

instance_path = os.path.join(basedir, 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    bookings = db.relationship('Booking', backref='user', lazy=True)

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    total_spots = db.Column(db.Integer, nullable=False)
    available_spots = db.Column(db.Integer, nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False, default=50.0)
    spots = db.relationship('ParkingSpot', backref='parking_lot', lazy=True, cascade='all, delete-orphan')

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_number = db.Column(db.String(10), nullable=False)
    is_occupied = db.Column(db.Boolean, default=False)
    parking_lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    bookings = db.relationship('Booking', backref='parking_spot', lazy=True, cascade='all, delete-orphan')

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(20), nullable=False)
    booking_time = db.Column(db.DateTime, default=datetime.utcnow)
    release_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')
    total_cost = db.Column(db.Float, default=50.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parking_spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    parking_lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)

class LoginForm(FlaskForm):
    email= StringField('Email', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])

class SignUpForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    fullname = StringField('Full Name', validators=[DataRequired(), Regexp(r'^[A-Za-z\s]+$', message='Full name must contain only alphabets and spaces')])
    pincode = StringField('Pincode', validators=[DataRequired(), Length(min=6, max=6, message='Pincode must be exactly 6 digits'), Regexp(r'^\d{6}$', message='Pincode must contain only numbers')])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=10, message='Phone number must be exactly 10 digits'), Regexp(r'^\d{10}$', message='Phone number must contain only numbers')])
    submit = SubmitField('Sign Up')

class ReleaseParkingForm(FlaskForm):
    spot_display = StringField('Current Spot ID')
    vehicle_display = StringField('Vehicle Number')
    cost_display = StringField('Parking Cost')
    submit = SubmitField('Release Spot')

class ReleaseSpotForm(FlaskForm):
    spot_id = IntegerField('Spot ID', validators=[DataRequired()])
    submit = SubmitField('Release Spot')

class SearchForm(FlaskForm):
    location = StringField('Search Location', validators=[])

class LotSelectionForm(FlaskForm):
    lot_id = SelectField('Select Parking Lot', choices=[], validators=[DataRequired()])
    submit = SubmitField('Load Available Spots')

class BookingForm(FlaskForm):
    lot_id = IntegerField('Lot ID', validators=[DataRequired()])
    spot_id = SelectField('Available Spots', choices=[], validators=[DataRequired()])
    vehicle_number = StringField('Vehicle Number', validators=[DataRequired()])
    submit = SubmitField('Book Now')

class LotManagementForm(FlaskForm):
    lot_id = IntegerField('Lot ID', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ParkingLotForm(FlaskForm):
    name = StringField('Lot Name', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    total_spots = IntegerField('Total Spots', validators=[DataRequired()])
    price_per_hour = FloatField('Price per Hour (₹)', validators=[DataRequired()])
    submit = SubmitField('Add Parking Lot')

class AdminSearchForm(FlaskForm):
    search = StringField('Search Parking Lots', validators=[])

class EditParkingLotForm(FlaskForm):
    name = StringField('Lot Name', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    total_spots = IntegerField('Total Spots', validators=[DataRequired()])
    price_per_hour = FloatField('Price per Hour (₹)', validators=[DataRequired()])
    submit = SubmitField('Update Parking Lot')

class EditSpotNameForm(FlaskForm):
    spot_number = StringField('Spot Name/Number', validators=[DataRequired(), Length(min=1, max=10)])
    submit = SubmitField('Update Spot Name')

class ChangeSpotStatusForm(FlaskForm):
    is_occupied = BooleanField('Spot Occupied')
    submit = SubmitField('Update Status')

@app.route('/',methods=['GET','POST'])
def home():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            user = User.query.filter_by(email=email, password=password).first()
            if user:
                session['email'] = email
                session['user_id'] = user.id
                first_user = User.query.order_by(User.id).first()
                if user.id == first_user.id:
                    session['is_admin'] = True
                    return redirect(url_for('admin_dashboard'))
                else:
                    session['is_admin'] = False
                    return redirect(url_for('user_dashboard'))
            else:
                flash('Invalid credentials, please try again.', 'error')
                return redirect(url_for('home'))
    return render_template('Login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            address = form.address.data
            fullname = form.fullname.data
            pincode = form.pincode.data
            phone = form.phone.data
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email already registered. Please use a different email.', 'error')
                return render_template('SignUp.html', form=form)
            new_user = User(
                email=email,
                password=password,
                fullname=fullname,
                address=address,
                pincode=pincode,
                phone=phone
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Signup successful! You can now log in.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Please fill out all fields correctly.', 'error')
    return render_template('SignUp.html',form=form)

@app.route('/user-dashboard', methods=['GET', 'POST'])
def user_dashboard():
    if 'email' not in session:
        flash('You need to log in first.', 'error')
        return redirect(url_for('home'))
    email = session['email']
    user = User.query.filter_by(email=email).first()
    lot_selection_form = LotSelectionForm()
    booking_form = BookingForm()
    search_form = SearchForm()
    release_form = ReleaseParkingForm()
    parking_lots = ParkingLot.query.all()
    lot_selection_form.lot_id.choices = [('', 'Choose a parking lot')] + [
        (str(lot.id), f"{lot.name} - {lot.location} ({lot.available_spots} spots available)")
        for lot in parking_lots
    ]
    booking_form.spot_id.choices = [('', 'Select a lot first')]
    selected_lot = None
    available_spots = []
    search_location = request.args.get('location', '')
    if search_location:
        search_form.location.data = search_location
        parking_lots = ParkingLot.query.filter(
            ParkingLot.location.contains(search_location) | 
            ParkingLot.name.contains(search_location)
        ).all()
        lot_selection_form.lot_id.choices = [('', 'Choose a parking lot')] + [
            (str(lot.id), f"{lot.name} - {lot.location} ({lot.available_spots} spots available)")
            for lot in parking_lots
        ]
    if request.method == 'POST' and lot_selection_form.submit.data and lot_selection_form.validate():
        selected_lot_id = int(lot_selection_form.lot_id.data)
        selected_lot = ParkingLot.query.get(selected_lot_id)
        if selected_lot:
            available_spots = ParkingSpot.query.filter_by(
                parking_lot_id=selected_lot_id, 
                is_occupied=False
            ).all()
            booking_form.lot_id.data = selected_lot_id
            booking_form.spot_id.choices = [('', 'Select a spot')] + [
                (str(spot.id), f"Spot {spot.spot_number}")
                for spot in available_spots
            ]
            lot_selection_form.lot_id.data = str(selected_lot_id)
            if not available_spots:
                flash('No available spots in this parking lot.', 'warning')
    if request.method == 'POST' and booking_form.submit.data and booking_form.validate():
        existing_booking = Booking.query.filter_by(user_id=user.id, status='active').first()
        if existing_booking:
            flash('You already have an active booking. Please release it first.', 'error')
        else:
            spot_id = int(booking_form.spot_id.data)
            lot_id = booking_form.lot_id.data
            vehicle_number = booking_form.vehicle_number.data
            parking_spot = ParkingSpot.query.get(spot_id)
            parking_lot = ParkingLot.query.get(lot_id)
            if parking_spot and parking_lot and not parking_spot.is_occupied:
                try:
                    new_booking = Booking(
                        user_id=user.id,
                        parking_spot_id=parking_spot.id,
                        parking_lot_id=parking_lot.id,
                        vehicle_number=vehicle_number.upper(),
                        total_cost=parking_lot.price_per_hour
                    )
                    parking_spot.is_occupied = True
                    parking_lot.available_spots -= 1
                    db.session.add(new_booking)
                    db.session.commit()
                    flash(f'Parking booked successfully! Spot: {parking_spot.spot_number} at {parking_lot.name}', 'success')
                    return redirect(url_for('user_dashboard'))
                except Exception as e:
                    db.session.rollback()
                    flash('An error occurred while booking. Please try again.', 'error')
            else:
                flash('Selected parking spot is no longer available.', 'error')
    parking_lots_data = []
    for lot in parking_lots:
        parking_lots_data.append({
            'id': lot.id,
            'name': lot.name,
            'location': lot.location,
            'available': lot.available_spots,
            'price_per_hour': lot.price_per_hour
        })
    current_booking = None
    booking_history = []
    if user:
        active_booking = Booking.query.filter_by(user_id=user.id, status='active').first()
        if active_booking:
            current_booking = {
                'spot_id': active_booking.parking_spot.spot_number,
                'lot_id': active_booking.parking_spot.parking_lot.name,
                'vehicle_number': active_booking.vehicle_number,
                'booking_time': active_booking.booking_time.strftime('%Y-%m-%d %H:%M')
            }
            release_form.spot_display.data = active_booking.parking_spot.spot_number
            release_form.vehicle_display.data = active_booking.vehicle_number
            release_form.cost_display.data = f"₹{active_booking.total_cost}"
        past_bookings = Booking.query.filter_by(user_id=user.id).filter(
            Booking.status.in_(['completed', 'cancelled'])
        ).order_by(Booking.booking_time.desc()).limit(5).all()
        for booking in past_bookings:
            booking_history.append({
                'id': f"{booking.id:03d}",
                'location': booking.parking_spot.parking_lot.name,
                'date': booking.booking_time.strftime('%Y-%m-%d'),
                'status': booking.status
            })    
    user_stats = {
        'total_bookings': Booking.query.filter_by(user_id=user.id).count(),
        'completed_bookings': Booking.query.filter_by(user_id=user.id, status='completed').count(),
        'cancelled_bookings': Booking.query.filter_by(user_id=user.id, status='cancelled').count(),
        'total_spent': db.session.query(db.func.sum(Booking.total_cost)).filter_by(user_id=user.id, status='completed').scalar() or 0
    }
    return render_template('user_dashboard.html', 
                         email=email,
                         parking_lots=parking_lots_data, 
                         search_location=search_location,
                         current_booking=current_booking, 
                         booking_history=booking_history,
                         lot_selection_form=lot_selection_form,
                         booking_form=booking_form,
                         search_form=search_form, 
                         release_form=release_form,
                         selected_lot=selected_lot,
                         available_spots=available_spots,
                         user_stats=user_stats)

@app.route('/user-charts', methods=['GET'])
def user_charts():
    if 'email' not in session:
        flash('You need to log in first.', 'error')
        return redirect(url_for('home'))
    email = session['email']
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('home'))
    user_stats = {
        'total_bookings': Booking.query.filter_by(user_id=user.id).count(),
        'completed_bookings': Booking.query.filter_by(user_id=user.id, status='completed').count(),
        'cancelled_bookings': Booking.query.filter_by(user_id=user.id, status='cancelled').count(),
        'total_spent': db.session.query(db.func.sum(Booking.total_cost)).filter_by(user_id=user.id, status='completed').scalar() or 0
    }
    current_booking = Booking.query.filter_by(user_id=user.id, status='active').first()
    return render_template('user_charts.html',
                         email=email,
                         user_stats=user_stats,
                         current_booking=current_booking)

@app.route('/release-parking', methods=['POST'])
def release_parking():
    if 'email' not in session:
        flash('You need to log in first.', 'error')
        return redirect(url_for('home'))
    email = session['email']
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('user_dashboard'))    
    release_form = ReleaseParkingForm()
    if not release_form.validate_on_submit():
        flash('Invalid form submission.', 'error')
        return redirect(url_for('user_dashboard'))
    
    active_booking = Booking.query.filter_by(user_id=user.id, status='active').first()
    if not active_booking:
        flash('You do not have any active booking to release.', 'error')
        return redirect(url_for('user_dashboard'))
    
    try:
        parking_duration = datetime.utcnow() - active_booking.booking_time
        hours_parked = max(1, int(parking_duration.total_seconds() / 3600))        
        active_booking.status = 'completed'
        active_booking.release_time = datetime.utcnow()
        active_booking.total_cost = active_booking.total_cost * hours_parked
        parking_spot = active_booking.parking_spot
        parking_spot.is_occupied = False
        parking_lot = parking_spot.parking_lot
        parking_lot.available_spots += 1
        db.session.commit()
        flash(f'Parking spot {parking_spot.spot_number} released successfully! Duration: {hours_parked} hour(s), Cost: ₹{active_booking.total_cost}', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while releasing the parking spot. Please try again.', 'error')
        print(f"Release error: {e}")
    return redirect(url_for('user_dashboard'))

@app.route('/admin-dashboard', methods=['GET'])
def admin_dashboard():
    if 'email' not in session or not session.get('is_admin', False):
        flash('Admin access required.', 'error')
        return redirect(url_for('home'))
    email = session['email']
    form = ParkingLotForm()
    search_form = AdminSearchForm()
    search_query = request.args.get('search', '')
    if search_query:
        search_form.search.data = search_query
    if search_query:
        parking_lots = ParkingLot.query.filter(
            ParkingLot.name.contains(search_query) | 
            ParkingLot.location.contains(search_query)
        ).all()
    else:
        parking_lots = ParkingLot.query.all()
    parking_lots_data = []
    for lot in parking_lots:
        spots = ParkingSpot.query.filter_by(parking_lot_id=lot.id).all()
        occupied_spots = sum(1 for spot in spots if spot.is_occupied)
        parking_lots_data.append({
            'id': lot.id,
            'name': lot.name,
            'location': lot.location,
            'total_spots': lot.total_spots,
            'occupied_spots': occupied_spots,
            'available_spots': lot.total_spots - occupied_spots,
            'price_per_hour': lot.price_per_hour,
            'spots': spots
        })
    admin_data = {
        'parking_lots': parking_lots_data,
        'search_query': search_query
    }
    return render_template('admin_dashboard.html', email=email, admin_data=admin_data, form=form, search_form=search_form)

@app.route('/add-parking-lot', methods=['POST'])
def add_parking_lot():
    if 'email' not in session or not session.get('is_admin', False):
        flash('Admin access required.', 'error')
        return redirect(url_for('home'))
    form = ParkingLotForm()
    if form.validate_on_submit():
        name = form.name.data
        location = form.location.data
        total_spots = form.total_spots.data
        price_per_hour = form.price_per_hour.data
        new_lot = ParkingLot(
            name=name,
            location=location,
            total_spots=total_spots,
            available_spots=total_spots,
            price_per_hour=price_per_hour
        )
        db.session.add(new_lot)
        db.session.commit()
        for i in range(1, total_spots + 1):
            spot = ParkingSpot(
                spot_number=f"A{i:02d}",
                parking_lot_id=new_lot.id,
                is_occupied=False
            )
            db.session.add(spot)    
        db.session.commit()
        flash(f'Parking lot "{name}" added successfully with {total_spots} spots!', 'success')
    else:
        flash('Please fill all fields correctly.', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/delete-parking-lot/<int:lot_id>', methods=['POST'])
def delete_parking_lot(lot_id):
    if 'email' not in session or not session.get('is_admin', False):
        flash('Admin access required.', 'error')
        return redirect(url_for('home'))
    lot = ParkingLot.query.get_or_404(lot_id)
    occupied_spots = ParkingSpot.query.filter_by(parking_lot_id=lot_id, is_occupied=True).count()
    if occupied_spots > 0:
        flash(f'Cannot delete lot "{lot.name}". {occupied_spots} spots are currently occupied.', 'error')
        return redirect(url_for('admin_dashboard'))
    lot_name = lot.name
    db.session.execute(db.text('DELETE FROM booking WHERE parking_lot_id = :lot_id'), {'lot_id': lot_id})
    db.session.execute(db.text('DELETE FROM parking_spot WHERE parking_lot_id = :lot_id'), {'lot_id': lot_id})
    db.session.execute(db.text('DELETE FROM parking_lot WHERE id = :lot_id'), {'lot_id': lot_id})
    db.session.commit()
    flash(f'Parking lot "{lot_name}" deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/release-spot/<int:spot_id>', methods=['POST'])
def release_spot(spot_id):
    if 'email' not in session or not session.get('is_admin', False):
        flash('Admin access required.', 'error')
        return redirect(url_for('home'))
    spot = ParkingSpot.query.get_or_404(spot_id)
    if not spot.is_occupied:
        flash(f'Spot {spot.spot_number} is not currently occupied.', 'warning')
        return redirect(url_for('admin_dashboard'))
    active_booking = Booking.query.filter_by(parking_spot_id=spot_id, status='active').first()
    if active_booking:
        active_booking.status = 'cancelled'
        active_booking.release_time = datetime.utcnow()
    spot.is_occupied = False
    lot = spot.parking_lot
    lot.available_spots += 1
    db.session.commit()
    flash(f'Spot {spot.spot_number} has been released successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/edit-parking-lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_parking_lot(lot_id):
    if 'email' not in session or not session.get('is_admin', False):
        flash('Admin access required.', 'error')
        return redirect(url_for('home'))
    lot = ParkingLot.query.get_or_404(lot_id)
    form = EditParkingLotForm(obj=lot)
    if request.method == 'POST' and form.validate_on_submit():
        old_total_spots = lot.total_spots
        new_total_spots = form.total_spots.data
        lot.name = form.name.data
        lot.location = form.location.data
        lot.price_per_hour = form.price_per_hour.data
        if new_total_spots != old_total_spots:
            current_spots = ParkingSpot.query.filter_by(parking_lot_id=lot_id).all()
            current_spots_count = len(current_spots)
            if new_total_spots > current_spots_count:
                spots_to_add = new_total_spots - current_spots_count
                for i in range(current_spots_count + 1, current_spots_count + spots_to_add + 1):
                    new_spot = ParkingSpot(
                        spot_number=f"A{i:02d}",
                        parking_lot_id=lot_id,
                        is_occupied=False
                    )
                    db.session.add(new_spot)
                lot.available_spots += spots_to_add
                flash(f'Added {spots_to_add} new parking spots!', 'success')
            elif new_total_spots < current_spots_count:
                spots_to_remove = current_spots_count - new_total_spots
                unoccupied_spots = [spot for spot in current_spots if not spot.is_occupied]
                if len(unoccupied_spots) < spots_to_remove:
                    flash(f'Cannot reduce spots to {new_total_spots}. Only {len(unoccupied_spots)} spots are available for removal (others are occupied).', 'error')
                    return render_template('edit_parking_lot.html', lot=lot, form=form, email=session['email'])                
                for i in range(spots_to_remove):
                    spot_to_remove = unoccupied_spots[i]
                    db.session.execute(db.text('DELETE FROM booking WHERE parking_spot_id = :spot_id'), {'spot_id': spot_to_remove.id})
                    db.session.delete(spot_to_remove)                
                lot.available_spots -= spots_to_remove
                flash(f'Removed {spots_to_remove} parking spots!', 'warning')
        lot.total_spots = new_total_spots
        db.session.commit() 
        flash(f'Parking lot "{lot.name}" updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_parking_lot.html', lot=lot, form=form, email=session['email'])

@app.route('/view-parking-spot/<int:spot_id>')
def view_parking_spot(spot_id):
    if 'email' not in session or not session.get('is_admin', False):
        flash('Admin access required.', 'error')
        return redirect(url_for('home'))
    spot = ParkingSpot.query.get_or_404(spot_id)
    release_spot_form = ReleaseSpotForm()
    edit_spot_form = EditSpotNameForm()
    status_form = ChangeSpotStatusForm()
    edit_spot_form.spot_number.data = spot.spot_number
    status_form.is_occupied.data = spot.is_occupied
    booking_history = Booking.query.filter_by(parking_spot_id=spot_id).order_by(
        Booking.booking_time.desc()
    ).limit(10).all()
    current_booking = None
    if spot.is_occupied:
        current_booking = Booking.query.filter_by(
            parking_spot_id=spot_id, 
            status='active'
        ).first()
    spot_data = {
        'id': spot.id,
        'spot_number': spot.spot_number,
        'is_occupied': spot.is_occupied,
        'lot_name': spot.parking_lot.name,
        'lot_location': spot.parking_lot.location,
        'price_per_hour': spot.parking_lot.price_per_hour,
        'current_booking': current_booking,
        'booking_history': booking_history
    }
    return render_template('view_parking_spot.html', spot=spot_data, email=session['email'],
                         release_spot_form=release_spot_form,
                         edit_spot_form=edit_spot_form, status_form=status_form)

@app.route('/edit-spot-name/<int:spot_id>', methods=['POST'])
def edit_spot_name(spot_id):
    if 'email' not in session or not session.get('is_admin', False):
        flash('Admin access required.', 'error')
        return redirect(url_for('home'))
    spot = ParkingSpot.query.get_or_404(spot_id)
    form = EditSpotNameForm()
    if form.validate_on_submit():
        old_name = spot.spot_number
        new_name = form.spot_number.data.strip()
        existing_spot = ParkingSpot.query.filter_by(
            parking_lot_id=spot.parking_lot_id,
            spot_number=new_name
        ).filter(ParkingSpot.id != spot_id).first()
        if existing_spot:
            flash(f'Spot name "{new_name}" already exists in this parking lot. Please choose a different name.', 'error')
        else:
            spot.spot_number = new_name
            db.session.commit()
            flash(f'Spot name updated from "{old_name}" to "{new_name}" successfully!', 'success')
    else:
        flash('Please enter a valid spot name (1-10 characters).', 'error')
    return redirect(url_for('view_parking_spot', spot_id=spot_id))

@app.route('/change-spot-status/<int:spot_id>', methods=['POST'])
def change_spot_status(spot_id):
    if 'email' not in session or not session.get('is_admin', False):
        flash('Admin access required.', 'error')
        return redirect(url_for('home'))
    spot = ParkingSpot.query.get_or_404(spot_id)
    form = ChangeSpotStatusForm()
    if form.validate_on_submit():
        old_status = "Occupied" if spot.is_occupied else "Available"
        new_status_occupied = form.is_occupied.data
        new_status = "Occupied" if new_status_occupied else "Available"
        if spot.is_occupied and not new_status_occupied:
            active_booking = Booking.query.filter_by(parking_spot_id=spot_id, status='active').first()
            if active_booking:
                active_booking.status = 'cancelled'
                active_booking.release_time = datetime.now()
                flash(f'Active booking #{active_booking.id} has been cancelled due to status change.', 'warning')
        if not spot.is_occupied and new_status_occupied:
            pass
        spot.is_occupied = new_status_occupied
        lot = spot.parking_lot
        if spot.is_occupied != new_status_occupied:
            if new_status_occupied: 
                lot.available_spots -= 1
            else:  
                lot.available_spots += 1
        db.session.commit()
        if old_status != new_status:
            flash(f'Spot {spot.spot_number} status changed from "{old_status}" to "{new_status}" successfully!', 'success')
        else:
            flash(f'Spot {spot.spot_number} status remains "{new_status}".', 'info')
    else:
        flash('Invalid form submission.', 'error')
    return redirect(url_for('view_parking_spot', spot_id=spot_id))

@app.route('/admin/users')
def admin_users():
    if 'email' not in session or not session.get('is_admin', False):
        flash('Admin access required.', 'error')
        return redirect(url_for('home'))
    users = User.query.filter(User.id != 1).all()
    users_data = []
    for user in users:
        total_bookings = Booking.query.filter_by(user_id=user.id).count()
        active_bookings = Booking.query.filter_by(user_id=user.id, status='active').count()
        users_data.append({
            'id': user.id,
            'fullname': user.fullname,
            'email': user.email,
            'phone': user.phone,
            'address': user.address,
            'pincode': user.pincode,
            'total_bookings': total_bookings,
            'active_bookings': active_bookings
        })
    return render_template('admin_users.html', users=users_data, email=session['email'])

@app.route('/admin/reports')
def admin_reports():
    if 'email' not in session or not session.get('is_admin', False):
        flash('Admin access required.', 'error')
        return redirect(url_for('home'))
    all_bookings = db.session.query(Booking, User, ParkingSpot, ParkingLot).join(
        User, Booking.user_id == User.id
    ).join(
        ParkingSpot, Booking.parking_spot_id == ParkingSpot.id
    ).join(
        ParkingLot, Booking.parking_lot_id == ParkingLot.id
    ).order_by(Booking.booking_time.desc()).limit(50).all()
    bookings_data = []
    total_revenue = 0
    for booking, user, spot, lot in all_bookings:
        duration = "Ongoing"
        if booking.booking_time:
            end_time = booking.release_time if booking.release_time else datetime.now()
            duration_delta = end_time - booking.booking_time
            hours = int(duration_delta.total_seconds() / 3600)
            minutes = int((duration_delta.total_seconds() % 3600) / 60)
            duration = f"{hours}h {minutes}m"
        bookings_data.append({
            'id': booking.id,
            'user_name': user.fullname,
            'user_email': user.email,
            'vehicle_number': booking.vehicle_number,
            'lot_name': lot.name,
            'spot_number': spot.spot_number,
            'booking_time': booking.booking_time.strftime('%Y-%m-%d %H:%M'),
            'release_time': booking.release_time.strftime('%Y-%m-%d %H:%M') if booking.release_time else 'Ongoing',
            'duration': duration,
            'status': booking.status,
            'cost': booking.total_cost
        })
        if booking.status == 'completed':
            total_revenue += booking.total_cost
    stats = {
        'total_bookings': Booking.query.count(),
        'active_bookings': Booking.query.filter_by(status='active').count(),
        'completed_bookings': Booking.query.filter_by(status='completed').count(),
        'cancelled_bookings': Booking.query.filter_by(status='cancelled').count(),
        'total_revenue': total_revenue,
        'total_users': User.query.count() - 1,
        'total_lots': ParkingLot.query.count(),
        'total_spots': ParkingSpot.query.count()
    }
    return render_template('admin_reports.html', bookings=bookings_data, stats=stats, email=session['email'])

def init_db():
    db.create_all()
    if ParkingLot.query.first():
        return
    lots = [
        ParkingLot(name='City Mall Parking', location='Mall', total_spots=20, available_spots=15, price_per_hour=50.0),
        ParkingLot(name='Airport Parking', location='Airport', total_spots=15, available_spots=8, price_per_hour=75.0),
        ParkingLot(name='Downtown Plaza', location='Downtown', total_spots=10, available_spots=3, price_per_hour=60.0),
        ParkingLot(name='Shopping Center', location='Mall', total_spots=18, available_spots=12, price_per_hour=45.0),
        ParkingLot(name='Business District', location='Downtown', total_spots=12, available_spots=6, price_per_hour=80.0)
    ]
    for lot in lots:
        db.session.add(lot)
    db.session.commit()
    for lot in ParkingLot.query.all():
        for i in range(1, lot.total_spots + 1):
            spot = ParkingSpot(
                spot_number=f"A{i:02d}",
                parking_lot_id=lot.id,
                is_occupied=(i > lot.available_spots)
            )
            db.session.add(spot)
    db.session.commit()
    if User.query.count() == 0:
        admin_user = User(
            email='admin@parking.com',
            password='admin123',
            fullname='Admin User',
            address='Admin Office',
            phone='0000000000',
            pincode='00000'
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created: admin@parking.com / admin123")
    print("Database initialized with sample data!")

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)