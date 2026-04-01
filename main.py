from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
from wtforms import StringField, SubmitField, FloatField, IntegerField
class Base(DeclarativeBase):
    pass

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

# CREATE DB
app.config['SQLALCHEMY_DATABASE_URI'] ="sqlite:///movies.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class MovieForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    year = IntegerField("Year",validators=[DataRequired()])
    description = StringField("Description",validators = [DataRequired()])
    rating = IntegerField("Rating", validators=[DataRequired()])
    review = StringField("Review", validators=[DataRequired()])
    img_url = StringField("Url",validators=[DataRequired()])
    movie_id = IntegerField("id",validators=[DataRequired()])
    submit =  SubmitField("Add Movie")





# CREATE TABLE
class Movie(db.Model):
    id: Mapped[int] =mapped_column(Integer , primary_key=True)
    title: Mapped[str] = mapped_column(String(250),unique=True , nullable=False)
    year : Mapped[int] = mapped_column(Integer , unique = False, nullable=False)
    description : Mapped[str] = mapped_column(String(400), unique = False , nullable = False)
    rating : Mapped[float] = mapped_column(Float ,unique = False , nullable = False  )
    review : Mapped[str] = mapped_column (String(400) ,unique = False , nullable = False )
    img_url : Mapped[str] = mapped_column(String(200), unique = False , nullable = False )
    ranking : Mapped[int] = mapped_column(Integer , unique = False , nullable = False)

with app.app_context():
    db.create_all()

new_movie = Movie(
    title="Phone Booth",
    year=2002,
    description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    rating=7.3,
    ranking=10,
    review="My favourite character was the caller.",
    img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
)
with app.app_context():
    if not db.session.query(Movie).filter_by(title="Phone Booth").first():
        db.session.add(new_movie)
        db.session.commit()
@app.route("/")
def home():
    result = db.session.execute(db.select(Movie).order_by(Movie.rating))
    all_movies = result.scalars().all()

    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()

    return render_template("index.html", movies=all_movies)



@app.route("/edit",methods=['GET', 'POST'])
def edit():
        form = MovieForm()
        if form.validate_on_submit():
            new_movie = Movie(
            id=form.movie_id.data,
            title =form.title.data,
            year = form.year.data,
            description = form.description.data,
            rating = form.rating.data,
            review = form.review.data ,
            img_url = form.img_url.data,
            )
            db.session.add(new_movie)
            db.session.commit()
            return redirect(url_for("home"))
        return render_template("add.html", form= form )


@app.route("/add", methods=["GET", "POST"])
def add():
    form = MovieForm()

    if form.validate_on_submit():
        new_movie = Movie(
            id=form.movie_id.data,
            title=form.title.data,
            year=form.year.data,
            description=form.description.data,
            rating=form.rating.data,
            review=form.review.data,
            img_url=form.img_url.data,
            ranking=0
        )

        db.session.add(new_movie)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("add.html", form=form)

@app.route("/delete/<int:movie_id>")
def delete(movie_id):
    movie_to_delete = db.get_or_404(Movie , movie_id)

    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))
@app.route("/add_comment", methods=["POST"])
def add_comment():
    data = request.get_json()

    new_comment = Comment(
        name=data["name"],
        text=data["comment"],
        rating=data["rating"]
    )

    db.session.add(new_comment)
    db.session.commit()

    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
