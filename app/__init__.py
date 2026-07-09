from flask import Flask, render_template, request, redirect, flash
from config import Config
from app.models import db, Post, Encouragement, JournalEntry
from app.auth import get_or_create_user
from app.moderation import is_supportive
from app.crisis import check_for_crisis
from app.journal import CATEGORIES


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route("/")
    def home():
        user = get_or_create_user()
        posts = Post.query.order_by(Post.created_at.desc()).all()
        return render_template("feed.html", username=user.username, posts=posts)

    @app.route("/post", methods=["POST"])
    def create_post():
        user = get_or_create_user()
        topic = request.form.get("topic")
        body = request.form.get("body", "").strip()

        if body:
            new_post = Post(user_id=user.id, topic=topic, body=body)
            db.session.add(new_post)
            db.session.commit()

            if check_for_crisis(body):
                return render_template("crisis_resources.html")

        return redirect("/")

    @app.route("/post/<int:post_id>/encourage", methods=["POST"])
    def add_encouragement(post_id):
        user = get_or_create_user()
        body = request.form.get("body", "").strip()
        post = Post.query.get_or_404(post_id)

        if not body:
            return redirect("/")

        ok, reason = is_supportive(body)
        if not ok:
            flash(reason)
            return redirect("/")

        encouragement = Encouragement(post_id=post.id, user_id=user.id, body=body)
        db.session.add(encouragement)
        db.session.commit()
        return redirect("/")

    @app.route("/journal")
    def journal():
        user = get_or_create_user()
        entries = (
            JournalEntry.query.filter_by(user_id=user.id)
            .order_by(JournalEntry.created_at.desc())
            .all()
        )
        return render_template(
            "journal.html", username=user.username, entries=entries, categories=CATEGORIES
        )

    @app.route("/journal/add", methods=["POST"])
    def add_journal_entry():
        user = get_or_create_user()
        category = request.form.get("category")
        body = request.form.get("body", "").strip()

        if body and category in CATEGORIES:
            entry = JournalEntry(user_id=user.id, category=category, body=body)
            db.session.add(entry)
            db.session.commit()

            if check_for_crisis(body):
                return render_template("crisis_resources.html")

        return redirect("/journal")

    return app