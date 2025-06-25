from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient, errors
from bson.objectid import ObjectId
import os, json
from uuid import uuid4

app = Flask(__name__)
app.secret_key = "your-secret-key"


MONGO_URI = os.getenv("MONGO_URI")
use_mongo = False
todos_collection = None

try:
    if MONGO_URI:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.server_info()  # Trigger connection attempt
        db = client["flask_database"]
        todos_collection = db["todos"]
        use_mongo = True
except Exception as e:
    print("⚠️ MongoDB unavailable, falling back to JSON database.")
    use_mongo = False


DATA_FILE = "data.json"

def load_json():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_json(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        content = request.form.get("content", "").strip()
        degree = request.form.get("degree", "").strip()

        if not content:
            flash("❗ Please provide content.", "error")
        else:
            if use_mongo:
                todos_collection.insert_one({"content": content, "degree": degree})
            else:
                todos = load_json()
                todos.append({
                    "id": str(uuid4()),
                    "content": content,
                    "degree": degree
                })
                save_json(todos)
            flash("✅ Response saved!", "success")
        return redirect(url_for("index"))

    if use_mongo:
        todos = list(todos_collection.find())
        
        for todo in todos:
            todo["id"] = str(todo["_id"])
    else:
        todos = load_json()

    return render_template("index.html", todos=todos)


@app.post("/<id>/delete/")
def delete(id):
    if use_mongo:
        todos_collection.delete_one({"_id": ObjectId(id)})
    else:
        todos = load_json()
        todos = [t for t in todos if t["id"] != id]
        save_json(todos)
    flash("🗑️ Todo deleted.", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # required by Railway
    app.run(host="0.0.0.0", port=port, debug=True)


