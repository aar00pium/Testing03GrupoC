from flask import Flask, send_from_directory
from controller import citas_bp

app = Flask(__name__, static_folder="static", template_folder="templates")
app.register_blueprint(citas_bp)

@app.route("/")
def index():
    return send_from_directory("templates", "index.html")

if __name__ == "__main__":
    print("=" * 50)
    print("Gestión de Citas — Grupo C")
    print("http://localhost:5000")
    print("=" * 50)
    app.run(debug=True)