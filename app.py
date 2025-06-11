from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)

# ✅ Get MongoDB URI from Railway environment variable
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise Exception("MONGO_URI not found in environment variables.")

# ✅ Create Mongo client
client = MongoClient(MONGO_URI)
db = client["flask_database"]  # Name of your database
todos = db["todos"]            # Name of your collection

# ✅ Home route — add & display todos
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        content = request.form.get("content")
        degree = request.form.get("degree")
        if content and degree:
            todos.insert_one({"content": content, "degree": degree})
        return redirect(url_for("index"))
    all_todos = list(todos.find())
    return render_template("index.html", todos=all_todos)

# ✅ Delete route
@app.post("/<id>/delete/")
def delete(id):
    todos.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("index"))

# ✅ Run app (host/port for Railway)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
