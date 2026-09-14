from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

tasks = []

@app.route("/")
def index():
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add():
    task = request.form.get("task")
    if task:
        tasks.append({"id": len(tasks) + 1, "title": task, "done": False})
    return redirect(url_for("index"))

@app.route("/done/<int:task_id>")
def done(task_id):
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = not t["done"]
    return redirect(url_for("index"))

@app.route("/delete/<int:task_id>")
def delete(task_id):
    global tasks
    tasks = [t for t in tasks if t["id"] != task_id]
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
