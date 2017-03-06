from flask import render_template
from flask import flash

from flask_login import login_user, logout_user, current_user
from flask_login import login_required

from werkzeug.security import check_password_hash
from .database import User

from . import app
from .database import session, Entry

PAGINATE_BY = 10

@app.route("/")
@app.route("/page/<int:page>")
def entries(page=1):
    # Zero-indexed page
    default_entries = 10
    max_entries = 50

    try:
        entries_limit = int(request.args.get('limit', default_entries)) # ensures integer by eliminating floats
        print(entries_limit)
        assert entries_limit > 0 # guarantee positive number
        assert entries_limit <= max_entries # eliminate numbers of entries
    except (ValueError, AssertionError):
        entries_limit = default_entries

    page_index = page - 1

    count = session.query(Entry).count()

    start = page_index * entries_limit
    end = start + entries_limit

    total_pages = (count - 1) // entries_limit + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    entries = entries[start:end]

    return render_template("entries.html",
        entries=entries,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages
    )

@app.route("/entry/add", methods=["GET"])
@login_required
def add_entry_get():
    return render_template("add_entry.html")

from flask import request, redirect, url_for

@app.route("/entry/add", methods=["POST"])
@login_required
def add_entry_post():
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
        author=current_user
    )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))


@app.route("/entry/<id>")
def single_entry(id):
    entry = session.query(Entry)
    entry = entry.filter(Entry.id==id)
    entry = entry.one()
    return render_template("single_entry.html", entry=entry)


@app.route("/entry/<id>/edit", methods=["GET"])
@login_required
def edit_entry_get(id):
    entry = session.query(Entry)
    entry = entry.filter(Entry.id==id)
    entry = entry.one()
    return render_template("edit_entry.html", entry=entry)


@app.route("/entry/<id>/edit", methods=["POST"])
@login_required
def edit_entry_post(id):
    entry = session.query(Entry)
    entry = entry.filter(Entry.id==id)
    entry = entry.one()
    session.delete(entry)
    entry = Entry(title=request.form["title"], content=request.form["content"], author=current_user)
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))


@app.route("/entry/<id>/delete")
@login_required
def delete_entry(id):
    entry = session.query(Entry)
    entry = entry.filter(Entry.id==id)
    entry = entry.one()
    session.delete(entry)
    session.commit()
    return redirect(url_for("entries"))


@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))

    login_user(user)
    return redirect(request.args.get('next') or url_for("entries"))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("entries"))
