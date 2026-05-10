from flask import Flask, render_template
from prometheus_client import Counter, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST

app = Flask(__name__)

REQUEST_COUNT = Counter(
    'app_requests_total',
    'Total App Requests'
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/count')
def home():
    REQUEST_COUNT.inc()
    return "Hello"

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {
        'Content-Type': CONTENT_TYPE_LATEST
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
