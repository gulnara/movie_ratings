from flask import Flask, render_template, redirect, request, url_for, session, flash, g
import model
from model import session as db_session, User, Rating, Movie

app = Flask(__name__)



@app.teardown_request
def shutdown_session(exception = None):
    db_session.remove()

@app.before_request
def load_user_id():
    g.user_id = session.get('user_id')

@app.route("/index")
@app.route("/")
def index():
	if g.user_id:
		return redirect(url_for("display_search"))
	return render_template("home.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/authenticate", methods=["POST"])
def authenticate():
	email = request.form['email']
	password = request.form['password']
	user = db_session.query(User).filter_by(email=email, password=password).one()
	session['user_id'] = user.id
	return redirect(url_for("display_search"))

@app.route("/register")
def register():
	return render_template("register.html")

@app.route("/signup", methods=["POST"])
def signup():
	email = request.form['email']
	password = request.form['password']
	age = request.form['age']
	gender = request.form['gender']
	occupation = request.form['occupation']
	zipcode = request.form["zipcode"]
	existing = db_session.query(User).filter_by(email=email).first()
	if existing:
		flash("Email already in use", "error")
		return redirect(url_for("index"))

	user = User(email=email, password=password, age=age, gender=gender, occupation=occupation, zipcode=zipcode)
	db_session.add(user)
	db_session.commit()
	db_session.refresh(user)
	session['user_id'] = user.id
	return redirect(url_for("display_search"))

@app.route("/all_users")
def all_users():
    user_list = model.session.query(model.User).limit(5).all()
    return render_template("user_list.html", users=user_list)
    # user_list = model.session.query(model.Movie).limit(5).all()
    # return render_template("user_list.html", movies=user_list)
    # return render_template("index.html")

@app.route("/search", methods=["GET"])
def display_search():
	return render_template("search.html")

@app.route("/search", methods=["POST"])
def search():
	query = request.form['query']
	movies = db_session.query(Movie).\
			filter(Movie.name.ilike("%" + query + "%")).\
			limit(20).all()
	return render_template("result.html", movies=movies)

@app.route("/movie/<int:id>", methods=["GET"])
def view_movie(id):
	movie = db_session.query(Movie).get(id)
	ratings = movie.ratings
	rating_nums = []
	user_rating = None
	for rating in ratings:
		if rating.user_id == session['user_id']:
			user_rating = rating
		rating_nums.append(rating.rating)
	avg_rating = float(sum(rating_nums))/len(rating_nums)
	
	# Prediction code: only predict if the user hasn't rated it yet
	prediction = None
	if not user_rating:
		user = db_session.query(User).get(g.user_id)
		prediction = user.predict_rating(movie)
		print prediction
	# End prediction

	return render_template("movie.html", movie=movie, average=avg_rating, 
							user_rating=user_rating, prediction=prediction)

@app.route("/rate/<int:id>", methods=["POST"])
def rate_movie(id):
	rating_number = int(request.form['rating'])
	user_id = session['user_id']
	rating = db_session.query(Rating).filter_by(user_id=user_id, movie_id=id).first()

	if not rating:
		flash("Rating added")
		rating = Rating(user_id=user_id, movie_id=id)
		db_session.add(rating)
	else:
		flash("Rating updated")

	rating.rating = rating_number
	db_session.commit()

	return redirect(url_for("view_movie", id=id))

@app.route("/my_ratings")
def my_ratings():
	if not g.user_id:
		return redirect(url_for("index"))
	ratings = db_session.query(Rating).filter_by(user_id=g.user_id).all()
	return render_template("my_ratings.html", ratings=ratings)

@app.route("/logout")
def logout():
    del session['user_id']
    return redirect(url_for("index"))

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


if __name__ == "__main__":
	app.run(debug = True)