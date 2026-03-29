import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g
from collections import defaultdict

app = Flask(__name__)
DATABASE = "orders.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            item TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            note TEXT
        )
    """)
    db.commit()
    db.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name", "").strip()
    items = request.form.getlist("item[]")
    quantities = request.form.getlist("quantity[]")
    notes = request.form.getlist("note[]")

    if not name:
        return redirect(url_for("index"))

    db = get_db()
    for item, qty, note in zip(items, quantities, notes):
        item = item.strip()
        if not item:
            continue
        try:
            qty = max(1, int(qty))
        except (ValueError, TypeError):
            qty = 1
        db.execute(
            "INSERT INTO orders (name, item, quantity, note) VALUES (?, ?, ?, ?)",
            (name, item, qty, note.strip()),
        )
    db.commit()
    return render_template("thanks.html", name=name)


@app.route("/orders")
def orders():
    db = get_db()
    rows = db.execute("SELECT * FROM orders ORDER BY item, name").fetchall()

    # Aggregate by item
    aggregated = defaultdict(lambda: {"total": 0, "people": []})
    for row in rows:
        key = row["item"]
        aggregated[key]["total"] += row["quantity"]
        entry = f"{row['name']} ×{row['quantity']}"
        if row["note"]:
            entry += f" ({row['note']})"
        aggregated[key]["people"].append(entry)

    # Also collect per-person view
    by_person = defaultdict(list)
    for row in rows:
        by_person[row["name"]].append(row)

    return render_template("orders.html", aggregated=aggregated, by_person=by_person)


@app.route("/clear", methods=["POST"])
def clear():
    db = get_db()
    db.execute("DELETE FROM orders")
    db.commit()
    return redirect(url_for("orders"))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
