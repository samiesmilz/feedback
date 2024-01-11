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
    if 'username' in session:
        flash("Please logout of this account first...", 'info')
        return redirect(f"/users/{session['username']}")

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

        session['username'] = username
        flash(f"Hi {new_user.username}, Welcome to Easy Feedback.", "info")
        return redirect(f"/users/{username}")
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
            session['username'] = username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ["Invalid username or password."]
    return render_template("login.html", form=form)


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """ Get and display all feedback with option to add new feedback """

    if "username" not in session:
        flash("Please login first!", "warning")
        return redirect("/login")
    # Retrieve all feedback
    feedback = Feedback.query.all()
    form = FeedbackForm()
    username = session['username']
    user = User.query.get_or_404(username)

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
        return redirect("/feedback")

    return render_template('feedback.html', user=user, form=form, feedback=feedback)


@app.route("/users/<username>")
def secret(username):
    """ Show the secret page """
    if "username" not in session:
        flash("Please login first!", "warning")
        return redirect("/login")
    user = User.query.get_or_404(username)
    form = FeedbackForm()
    # Retrieve all feedback
    feedback = Feedback.query.all()
    return render_template("profile.html", user=user, form=form, feedback=feedback)


@app.route("/logout")
def logount_user():
    session.pop("username")
    flash("You are successfully logged out.", "success")
    return redirect("/")


@app.route("/feedback/<int:id>/delete", methods=['POST'])
def delete_feedback(id):
    """ Delete the feedback based on it's id """
    if 'username' not in session:
        flash("Please login first.", 'warning')
        return redirect("/login")

    feedcom = Feedback.query.get_or_404(id)
    username = session['username']
    if feedcom.username == session['username']:
        db.session.delete(feedcom)
        db.session.commit()
        flash("Your feedcom has been deleted successfuly.", "info")
        return redirect(f"/users/{username}")
    flash("You don't have permission to delete this feedcom.", "danger")
    user = User.query.get_or_404(username)
    form = FeedbackForm()
    # Retrieve all feedback
    feedback = Feedback.query.filter_by(username=username).all()
    return redirect(f"/users/{username}", form=form, user=user, feedback=feedback)
