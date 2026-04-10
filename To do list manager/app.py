from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# DB create
conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    task TEXT,
    completed INTEGER DEFAULT 0
)
''')
conn.commit()
conn.close()


# 🏠 HOME PAGE
@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    status_dict = {}

    for day in range(1, 31):
        date = f"2026-04-{day:02d}"   # ✅ IMPORTANT FIX (01,02,03...)
        c.execute("SELECT completed FROM tasks WHERE date=?", (date,))
        tasks = c.fetchall()

        if len(tasks) == 0:
            status_dict[day] = "none"
        else:
            all_done = all(t[0] == 1 for t in tasks)
            status_dict[day] = "green" if all_done else "red"

    conn.close()
    return render_template('index.html', status_dict=status_dict)


# 📋 TASK PAGE
@app.route('/tasks/<date>', methods=['GET', 'POST'])
def tasks(date):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    if request.method == 'POST':
        task = request.form['task']
        c.execute("INSERT INTO tasks (date, task) VALUES (?, ?)", (date, task))
        conn.commit()

    c.execute("SELECT * FROM tasks WHERE date=?", (date,))
    tasks = c.fetchall()

    conn.close()
    return render_template('tasks.html', tasks=tasks, date=date)


# ❌ DELETE
@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(request.referrer)


# ✔️ TOGGLE
@app.route('/toggle/<int:id>/<date>')
def toggle(id, date):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT completed FROM tasks WHERE id=?", (id,))
    status = c.fetchone()[0]

    c.execute("UPDATE tasks SET completed=? WHERE id=?", (1-status, id))
    conn.commit()
    conn.close()

    return redirect(f'/tasks/{date}')   # ✅ BACK to same date page


if __name__ == '__main__':
    app.run(debug=True)