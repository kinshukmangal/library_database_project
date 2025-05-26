from flask import Flask, session, redirect, url_for
from routes.auth import auth_bp
from routes.member import member_bp
from routes.librarian import librarian_bp
from routes.admin import admin_bp
from routes.book import book_bp  # For QR & /book/<book_id>

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Replace with env variable for production

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(member_bp, url_prefix="/member")
app.register_blueprint(librarian_bp, url_prefix="/librarian")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(book_bp)

# Redirect home route based on login
@app.route('/')
def home():
    user = session.get('user')
    if user:
        return redirect(url_for(f"{user['role']}.dashboard")+"/")
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True)
