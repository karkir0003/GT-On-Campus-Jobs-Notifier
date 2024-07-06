from flask import Flask, render_template, request, jsonify
import configparser
import util
import scheduler
import os

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('config.ini')
scraper_config = config['SCRAPER']


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/subscribe", methods=["GET", "POST"])
def add_subscriber():
    if request.method == "GET":
        return render_template("subscribed.html")
    elif request.method == "POST":
        email_subscriber = request.form.get('email', '')
        recaptcha_response = request.form.get('g-recaptcha-response', '')

        # Make sure the email provided is valid
        if not util.is_valid_email(email_subscriber):
            return {"error": "Please enter a valid email address or try refreshing the page."}, 400

        # Verify the recaptcha token. Helps to prevent spam and automated bots submissions
        if not util.is_valid_recaptcha(recaptcha_response):
            return {"error": "Failed to validate the reCAPTCHA. Please refresh the page and try again."}, 400

        try:
            util.add_email_subscriber(email_subscriber)
            return {'success': True}, 200
        except:
            return {"error": "You have already subscribed with this email account. Refresh the page and try again with a different email."}, 500


# Google Cloud Scheduler hits this endpoint for scraping and sending email
@app.route("/scraper/start", methods=["POST"])
def start_scraping():
    try:
        req_body = request.get_json(force=True)
        if req_body is None:
            return {"error": "No token provided"}, 400

        user_token = req_body.get('token', '')
        if user_token == scraper_config['SCRAPER_AUTH_TOKEN']:
            target_db = "prod" if os.getenv(
                "FLASK_ENV") == "production" else "test"
            scheduler.run_schedule(database=target_db)
            return {'success': True}, 200
        else:
            return {'error': 'Please provide a valid token'}, 400
    except Exception as e:
        print(e)
        return {'error': "Interal server error"}, 500


if __name__ == '__main__':
    app.run(debug=True)
