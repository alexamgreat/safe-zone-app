from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, session
from flask_migrate import Migrate
from config import Config
from app.auth import get_current_user, signup, login, logout
from app.moderation import is_supportive
from app.crisis import check_for_crisis
from app.journal import CATEGORIES
from app.mood import MOODS, HEAVY_MOODS, calculate_streak
from app.quotes import quote_of_the_day
from app.presets import ENCOURAGEMENT_PRESETS
from app.avatars import AVATARS
from app.moderation import is_supportive, is_valid_nickname
from app.models import db, Post, Encouragement, EncouragementReaction, JournalEntry, MoodCheckIn, User, CompanionMessage
from app.companion import generate_reply, greeting

REACTION_LABELS = {
    "helped": "❤️ Helped me",
    "needed": "🤗 I needed this",
    "saved": "⭐ Saved",
}

migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    PUBLIC_ENDPOINTS = {"welcome", "do_signup", "do_login", "static"}

    @app.before_request
    def require_login():
        if request.endpoint in PUBLIC_ENDPOINTS or request.endpoint is None:
            return
        if not get_current_user():
            return redirect("/welcome")

    @app.route("/")
    def dashboard():
        user = get_current_user()
        streak = calculate_streak(user.id)
        quote = quote_of_the_day()
        recent_posts = Post.query.order_by(Post.created_at.desc()).all()
        wall_preview = (
            Encouragement.query.filter_by(post_id=None)
            .order_by(Encouragement.created_at.desc())
            .first()
        )
        stats = {
            "stories": Post.query.count(),
            "encouragements": Encouragement.query.count(),
            "people_helped": EncouragementReaction.query.count(),
        }
        today = datetime.utcnow().strftime("%A, %B %d, %Y")

        return render_template(
            "home.html",
            username=user.username,
            moods=MOODS,
            streak=streak,
            quote=quote,
            recent_posts=recent_posts,
            wall_preview=wall_preview,
            stats=stats,
            today=today,
        )

    @app.route("/feed")
    def feed():
        user = get_current_user()
        posts = Post.query.order_by(Post.created_at.desc()).all()
        return render_template("feed.html", username=user.username, posts=posts, current_user_id=user.id)

    @app.route("/post", methods=["POST"])
    def create_post():
        user = get_current_user()
        topic = request.form.get("topic")
        body = request.form.get("body", "").strip()

        if body:
            new_post = Post(user_id=user.id, topic=topic, body=body)
            db.session.add(new_post)
            db.session.commit()

            if check_for_crisis(body):
                return render_template("crisis_resources.html")

        return redirect("/feed")

    @app.route("/post/<int:post_id>/encourage", methods=["POST"])
    def add_encouragement(post_id):
        user = get_current_user()
        body = request.form.get("body", "").strip()
        post = Post.query.get_or_404(post_id)

        if not body:
            return redirect("/feed")

        ok, reason = is_supportive(body)
        if not ok:
            flash(reason)
            return redirect("/feed")

        encouragement = Encouragement(post_id=post.id, user_id=user.id, body=body)
        db.session.add(encouragement)
        db.session.commit()
        return redirect("/feed")

    @app.route("/journal")
    def journal():
        user = get_current_user()
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
        user = get_current_user()
        category = request.form.get("category")
        body = request.form.get("body", "").strip()

        if body and category in CATEGORIES:
            entry = JournalEntry(user_id=user.id, category=category, body=body)
            db.session.add(entry)
            db.session.commit()

            if check_for_crisis(body):
                return render_template("crisis_resources.html")

        return redirect("/journal")

    @app.route("/wall")
    def wall():
        user = get_current_user()
        encouragements = (
            Encouragement.query.filter_by(post_id=None)
            .order_by(Encouragement.created_at.desc())
            .all()
        )
        counts = {}
        for e in encouragements:
            counts[e.id] = {
                key: EncouragementReaction.query.filter_by(
                    encouragement_id=e.id, reaction_type=key
                ).count()
                for key in REACTION_LABELS
            }
        return render_template(
            "wall.html",
            username=user.username,
            encouragements=encouragements,
            counts=counts,
            reaction_labels=REACTION_LABELS,
        )

    @app.route("/wall/add", methods=["POST"])
    def add_wall_encouragement():
        user = get_current_user()
        body = request.form.get("body", "").strip()

        if body:
            ok, reason = is_supportive(body)
            if not ok:
                flash(reason)
                return redirect("/wall")

            encouragement = Encouragement(post_id=None, user_id=user.id, body=body)
            db.session.add(encouragement)
            db.session.commit()

        return redirect("/wall")

    @app.route("/wall/<int:encouragement_id>/react", methods=["POST"])
    def react_to_encouragement(encouragement_id):
        user = get_current_user()
        reaction_type = request.form.get("reaction_type")

        if reaction_type in REACTION_LABELS:
            already = EncouragementReaction.query.filter_by(
                encouragement_id=encouragement_id,
                user_id=user.id,
                reaction_type=reaction_type,
            ).first()

            if not already:
                reaction = EncouragementReaction(
                    encouragement_id=encouragement_id,
                    user_id=user.id,
                    reaction_type=reaction_type,
                )
                db.session.add(reaction)
                db.session.commit()

        return redirect("/wall")

    @app.route("/mood")
    def mood():
        user = get_current_user()
        history = (
            MoodCheckIn.query.filter_by(user_id=user.id)
            .order_by(MoodCheckIn.created_at.desc())
            .limit(14)
            .all()
        )
        return render_template(
            "mood.html", username=user.username, moods=MOODS, history=history
        )

    @app.route("/mood/add", methods=["POST"])
    def add_mood():
        user = get_current_user()
        mood_key = request.form.get("mood")
        note = request.form.get("note", "").strip()
        next_url = request.form.get("next", "/mood")

        if mood_key not in MOODS:
            return redirect(next_url)

        entry = MoodCheckIn(user_id=user.id, mood=mood_key, note=note or None)
        db.session.add(entry)
        db.session.commit()

        if note and check_for_crisis(note):
            return render_template("crisis_resources.html")

        if mood_key in HEAVY_MOODS and not note:
            flash("want to talk about what happened today? you can add a note anytime, or share on the feed.")

        return redirect(next_url)

    @app.route("/support")
    def support():
        user = get_current_user()
        return render_template("crisis_resources.html", username=user.username)

    @app.route("/encourage/random")
    def encourage_random():
        user = get_current_user()
        post = Post.query.order_by(db.func.random()).first()
        return render_template(
            "encourage.html",
            username=user.username,
            post=post,
            presets=ENCOURAGEMENT_PRESETS,
        )

    @app.route("/account")
    def account():
        user = get_current_user()
        return render_template("account.html", user=user, avatars=AVATARS)

    @app.route("/account/avatar", methods=["POST"])
    def set_avatar():
        user = get_current_user()
        avatar = request.form.get("avatar")
        if avatar in AVATARS:
            user.avatar = avatar
            db.session.commit()
        return redirect("/account")

    @app.route("/welcome")
    def welcome():
        if get_current_user():
            return redirect("/")
        return render_template("welcome.html")

    @app.route("/welcome/signup", methods=["POST"])
    def do_signup():
        email = request.form.get("email", "")
        password = request.form.get("password", "")

        if not email or not password:
            flash("please fill in both fields.")
            return redirect("/welcome")

        user, error = signup(email, password)
        if error:
            flash(error)
            return redirect("/welcome")

        return redirect("/")

    @app.route("/welcome/login", methods=["POST"])
    def do_login():
        email = request.form.get("email", "")
        password = request.form.get("password", "")

        user, error = login(email, password)
        if error:
            flash(error)
            return redirect("/welcome")

        return redirect("/")

    @app.route("/account/logout", methods=["POST"])
    def account_logout():
        logout()
        return redirect("/welcome")
    
    
    @app.route("/account/nickname", methods=["POST"])
    def set_nickname():
        user = get_current_user()
        nickname = request.form.get("nickname", "").strip()

        ok, reason = is_valid_nickname(nickname)
        if not ok:
            flash(reason)
            return redirect("/account")

        if User.query.filter(User.username == nickname, User.id != user.id).first():
            flash("that nickname is already taken.")
            return redirect("/account")

        user.username = nickname
        db.session.commit()
        flash("nickname updated!")
        return redirect("/account")
    @app.route("/companion")
    def companion():
        user = get_current_user()
        history = (
            CompanionMessage.query.filter_by(user_id=user.id)
            .order_by(CompanionMessage.created_at.asc())
            .all()
        )
        return render_template(
            "companion.html", username=user.username, history=history, greeting=greeting()
        )

    @app.route("/companion/send", methods=["POST"])
    def companion_send():
        user = get_current_user()
        body = request.form.get("body", "").strip()

        if body:
            user_msg = CompanionMessage(user_id=user.id, sender="user", body=body)
            db.session.add(user_msg)
            db.session.commit()

            if check_for_crisis(body):
                return render_template("crisis_resources.html")

            reply = generate_reply(body)
            companion_msg = CompanionMessage(user_id=user.id, sender="companion", body=reply)
            db.session.add(companion_msg)
            db.session.commit()

        return redirect("/companion")
    
    @app.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
    def edit_post(post_id):
        user = get_current_user()
        post = Post.query.get_or_404(post_id)

        if post.user_id != user.id:
            flash("you can only edit your own posts.")
            return redirect("/feed")

        if request.method == "POST":
            body = request.form.get("body", "").strip()
            topic = request.form.get("topic")

            if body:
                post.body = body
                post.topic = topic
                db.session.commit()

                if check_for_crisis(body):
                    return render_template("crisis_resources.html")

            return redirect("/feed")

        return render_template("edit_post.html", username=user.username, post=post)

    @app.route("/post/<int:post_id>/delete", methods=["POST"])
    def delete_post(post_id):
        user = get_current_user()
        post = Post.query.get_or_404(post_id)

        if post.user_id != user.id:
            flash("you can only delete your own posts.")
            return redirect("/feed")

        Encouragement.query.filter_by(post_id=post.id).delete()
        db.session.delete(post)
        db.session.commit()

        return redirect("/feed")
    

    return app

    