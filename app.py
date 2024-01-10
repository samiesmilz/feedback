from flask import Flask, flash, redirect, render_template, session, request
from models import connect_db, db, User, Feedback
from forms import UserForm, FeedbackForm, UserLoginForm
from sqlalchemy.exc import IntegrityError


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "ANOTHER24"


# connect to databe
connect_db(app)

# Use app context to create tables
with app.app_context():
    db.create_all()


@app.route("/")
def homepage():
    """ Show homepage """
    return render_template("index.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    """ Register new user """
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(
            username, password, email, first_name, last_name)
        db.session.add(new_user)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()  # Rollback if an IntegrityError occurs
            form.username.errors.append(
                "That's a good username - but it's taken. Pick another.")
            return render_template("register.html", form=form)

        session['user_id'] = new_user.id
        flash(f"Hi {new_user.username}, Welcome to Easy Feedback.", "info")
        return redirect("/feedback")
    # Only set the error message if the form has been submitted and validation failed
    elif request.method == 'POST':
        form.username.errors = ["Invalid username - not available."]

    return render_template("register.html", form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    """Login into the application"""
    form = UserLoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome back, {user.username}!", "info")
            session['user_id'] = user.id
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ["Invalid username/password."]
    return render_template("login.html", form=form)


@app.route('/feedback/<username>', methods=['GET', 'POST'])
def feedback(username):
    """ Get and display all feedback with option to add new feedback """

    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect("/login")
    # Retrieve all feedback
    feedback = Feedback.query.all()
    form = FeedbackForm()

    if form.validate_on_submit():
        # Form was submitted and passed validation
        # Process the data or redirect to another page
        title = form.title.data
        content = form.content.data
        new_comment = Feedback(title=title, content=content,
                               username=username)
        db.session.add(new_comment)
        db.session.commit()
        flash("Feedback has been created!", "success")
        return redirect("/profile")

    return render_template('feedback.html', userform=form, all_feedback=feedback)


@app.route("/users/<username>")
def secret(username):
    """ Show the secret page """
    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect("/login")
    user = User.query.get_or_404(username)
    form = FeedbackForm()
    # Retrieve all feedback
    feedback = Feedback.query.all()
    return render_template("profile.html", user=user, form=form, feedback=feedback)


@app.route("/logout")
def logount_user():
    session.pop("user_id")
    flash("You are successfully logged out.", "success")
    return redirect("/")
