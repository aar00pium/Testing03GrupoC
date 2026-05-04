from flask import Flask, send_from_directory
import controller
import model

app = Flask(__name__, static_folder=".", static_url_path="")

model.init_db()

app.register_blueprint(controller.bp)

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    print("http://127.0.0.1:5000")
    app.run(debug=True)