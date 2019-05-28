from flask import Blueprint, render_template, request, redirect, url_for
from pinboard.db import get_db
from datetime import datetime
import json

bp = Blueprint("board", __name__)

@bp.route("/")
def list():
    user_session_cookie = ""
    if 'pinboard_session' in request.cookies:
        user_session_cookie = request.cookies["pinboard_session"]

    posts = get_posts(user_session_cookie, True)
    return render_template("board/list.html", posts=posts, session=user_session_cookie)

@bp.route("/add", methods=("GET", "POST"))
def add():
    if request.method == "GET":
        return render_template("board/add.html")
    else:
        title = request.form["title"]
        description = request.form["description"]
        color = request.form["color"]

        db = get_db()
        db.execute(
            "INSERT INTO post (title, description, color) VALUES (?, ?, ?)",
            (title, description, color)
        )

        db.commit()

        return redirect(url_for("board.list"))

@bp.route("/like_post", methods=("GET", "POST"))
def like_post():
    if request.method == "POST":
        user_session = request.form["user_session"]
        post_id = request.form["post_id"]

        db = get_db()
        db.execute(
            "INSERT INTO likes (user_session, post_id) VALUES (?, ?)",
            (user_session, post_id)
        )

        db.commit()
        posts = get_posts(user_session, True)
        return json.dumps(posts)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_posts(session, to_json = False):
    db = get_db()

    if to_json:
        db.row_factory = dict_factory

    cursor = db.cursor()

    query = """SELECT rowid, *, 
            (SELECT COUNT(*) from likes WHERE post_id=post.rowid) as like_count, 
            (SELECT COUNT(*) from likes WHERE post_id=post.rowid AND user_session='{0}') as liked_by_me 
        FROM post ORDER BY created DESC"""
    rows = cursor.execute(query.format(session)).fetchall()

    sorted_by_popularity = popularity_sorting(rows)
    return sorted_by_popularity

def popularity_sorting(posts):
    date_format = "%Y-%m-%d %H:%M:%S"
    max_date = posts[0]["created"]
    max_data_timestamp = datetime.strptime(max_date, date_format).timestamp()
    min_date = posts[-1]["created"]
    min_data_timestamp = datetime.strptime(min_date, date_format).timestamp()
    post_amount = len(posts)

    scale = 10
    created_diff = int(max_data_timestamp - min_data_timestamp)
    score_value = created_diff / post_amount / scale
    formatted_score_value = float('%.2f'%score_value)

    for post in posts:
        date_score = int(datetime.strptime(post["created"], date_format).timestamp())
        post_score = formatted_score_value * post["like_count"]

        post["created_like_score"] = date_score + post_score

    sorted_by_popularity_score = sorted(posts, key=lambda post: post["created_like_score"], reverse=True)

    return sorted_by_popularity_score