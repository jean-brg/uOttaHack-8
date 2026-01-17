# IMPORTS
from flask import Flask, render_template, jsonify
from flask_cors import CORS

# APP INIT
app = Flask(__name__)
CORS(app)

# HOME ROUTE
@app.route("/")
def home():
    return render_template("index.html")

@app.route('/api/data', methods=['GET'])
def get_data():
    result = {"message": "Connected to Python!"}
    return jsonify(result)

# RUNNER
if __name__ == "__main__":
    app.run(debug=True)
