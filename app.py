import os
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, text
from collections import defaultdict

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///orders.db")
# Render supplies postgres:// but SQLAlchemy requires postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)


def init_db():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                item TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                note TEXT
            )
        """))
        conn.commit()


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

    with engine.connect() as conn:
        for item, qty, note in zip(items, quantities, notes):
            item = item.strip()
            if not item:
                continue
            try:
                qty = max(1, int(qty))
            except (ValueError, TypeError):
                qty = 1
            conn.execute(
                text("INSERT INTO orders (name, item, quantity, note) VALUES (:name, :item, :qty, :note)"),
                {"name": name, "item": item, "qty": qty, "note": note.strip()},
            )
        conn.commit()

    return render_template("thanks.html", name=name)


@app.route("/orders")
def orders():
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT * FROM orders ORDER BY item, name")
        ).mappings().all()

    aggregated = defaultdict(lambda: {"total": 0, "people": []})
    for row in rows:
        key = row["item"]
        aggregated[key]["total"] += row["quantity"]
        entry = f"{row['name']} ×{row['quantity']}"
        if row["note"]:
            entry += f" ({row['note']})"
        aggregated[key]["people"].append(entry)

    by_person = defaultdict(list)
    for row in rows:
        by_person[row["name"]].append(row)

    return render_template("orders.html", aggregated=aggregated, by_person=by_person)


@app.route("/clear", methods=["POST"])
def clear():
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM orders"))
        conn.commit()
    return redirect(url_for("orders"))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
