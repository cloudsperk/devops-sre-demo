import json
import os
import random
from datetime import datetime

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from prometheus_client import Counter, CONTENT_TYPE_LATEST, generate_latest

BASE_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(BASE_DIR, 'parking_data.json')

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'change-this-secret')

REQUEST_COUNT = Counter(
    'app_requests_total',
    'Total App Requests'
)


def load_data():
    if not os.path.exists(DATA_FILE):
        return {'users': {}, 'records': []}

    with open(DATA_FILE, 'r', encoding='utf-8') as handle:
        return json.load(handle)


def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as handle:
        json.dump(data, handle, indent=2, default=str)


def get_mobile():
    return session.get('mobile')


def get_active_record(records, mobile):
    return next(
        (item for item in records if item['mobile'] == mobile and item['checkout_time'] is None),
        None,
    )


def format_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def generate_otp():
    return f"{random.randint(100000, 999999)}"


@app.before_request
def count_requests():
    REQUEST_COUNT.inc()


@app.route('/', methods=['GET'])
def index():
    if get_mobile():
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    mobile = request.form.get('mobile', '').strip()
    if not mobile.isdigit() or len(mobile) < 8:
        flash('Please enter a valid mobile number.', 'error')
        return redirect(url_for('index'))

    session['mobile'] = mobile
    data = load_data()
    if mobile not in data['users']:
        data['users'][mobile] = {
            'mobile': mobile,
            'registered_at': format_timestamp(),
        }
        save_data(data)

    flash('Welcome! You are now logged in.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    mobile = get_mobile()
    if not mobile:
        return redirect(url_for('index'))

    data = load_data()
    record = get_active_record(data['records'], mobile)
    history = [item for item in data['records'] if item['mobile'] == mobile]
    return render_template('dashboard.html', mobile=mobile, record=record, history=history)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    mobile = get_mobile()
    if not mobile:
        return redirect(url_for('index'))

    data = load_data()
    active = get_active_record(data['records'], mobile)
    if active:
        flash('You already have an active parking session. Please checkout first.', 'warning')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        vehicle_type = request.form.get('vehicle_type', '').strip()
        vehicle_number = request.form.get('vehicle_number', '').strip().upper()
        vehicle_model = request.form.get('vehicle_model', '').strip()
        notes = request.form.get('notes', '').strip()

        if not vehicle_type or not vehicle_number or not vehicle_model:
            flash('Please fill in all required vehicle details.', 'error')
            return redirect(url_for('checkin'))

        record = {
            'id': f"{mobile}-{len(data['records']) + 1}",
            'mobile': mobile,
            'vehicle_type': vehicle_type,
            'vehicle_number': vehicle_number,
            'vehicle_model': vehicle_model,
            'notes': notes,
            'checkin_time': format_timestamp(),
            'checkout_time': None,
            'otp': None,
            'otp_requested_at': None,
        }
        data['records'].append(record)
        save_data(data)

        flash('Check-in complete. Your vehicle is now registered as parked.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('checkin.html')


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    mobile = get_mobile()
    if not mobile:
        return redirect(url_for('index'))

    data = load_data()
    record = get_active_record(data['records'], mobile)
    if not record:
        flash('No active parking session found. Please check in first.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        otp = request.form.get('otp', '').strip()
        if otp == record.get('otp'):
            record['checkout_time'] = format_timestamp()
            record['otp'] = None
            record['otp_requested_at'] = None
            save_data(data)
            flash('OTP verified. Your parking session is now closed.', 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid OTP. Please try again.', 'error')
        return render_template('checkout.html', record=record)

    if not record.get('otp'):
        record['otp'] = generate_otp()
        record['otp_requested_at'] = format_timestamp()
        save_data(data)

    return render_template('checkout.html', record=record)


@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
