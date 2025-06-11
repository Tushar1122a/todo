from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)

# ✅ Use Mongo URI from environment variable (works on Railway)
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)

# Connect to database and collection
db = client.flask_database
todos = db.todos

# Home Route - Get and Post
@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        content = request.form["content"]
        degree = request.form["degree"]
        todos.insert_one({"content": content, "degree": degree})
        return redirect(url_for("index"))
    all_todos = todos.find()
    return render_template("index.html", todos=all_todos)

# Delete Route
@app.post("/<id>/delete/")
def delete(id):
    todos.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("index"))

# Run app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # allow Railway to assign a port
    app.run(host="0.0.0.0", port=port, debug=True)
