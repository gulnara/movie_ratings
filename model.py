from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, types
from sqlalchemy import Column, Integer, String, DateTime, Date
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
import datetime
import correlation 

engine = create_engine("sqlite:///ratings.db", echo=False)
session = scoped_session(sessionmaker(bind=engine, autocommit = False, autoflush = False))


Base = declarative_base()
Base.query = session.query_property()

### Class declarations go here
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True)
    email = Column(String(64), nullable=True)
    password = Column(String(64), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(1), nullable=True)
    occupation = Column(String(64), nullable=True)
    zipcode = Column(String(15), nullable=True)

    def similarity(self, other):
    	u_ratings = {}
    	paired_ratings = []
    	for r in self.ratings:
    		u_ratings[r.movie_id] = r

    	for r in other.ratings:
    		u_r = u_ratings.get(r.movie_id)
    		if u_r:
    			paired_ratings.append((u_r.rating, r.rating))

    	if paired_ratings:
    		return correlation.pearson(paired_ratings)
    	else:
    		return 0.0

    def predict_rating(self, movie):
    	if not self.ratings: return None
        ratings = self.ratings
        other_ratings = movie.ratings
        similarities = [ (self.similarity(r.user), r) for r in other_ratings ]
        similarities.sort(reverse = True)
        top = similarities[0]

        similarities = [ sim for sim in similarities if sim[0] > 0 ]
        if not similarities:
            return None
        numerator = sum([ r.rating * similarity for similarity, r in similarities ])
        denominator = sum([ similarity[0] for similarity in similarities ])
        prediction = (numerator/denominator)
        return prediction


class Movie(Base):
	__tablename__ = "movies"

	id = Column(Integer, primary_key = True)
	name = Column(String(128))
	released_at = Column(Date)
	imdb_url = Column(String(256))


class Rating(Base):
	__tablename__ = "ratings"

	id = Column(Integer, primary_key = True)
	user_id = Column(Integer, ForeignKey('users.id'))
	movie_id = Column(Integer, ForeignKey('movies.id'))
	rating = Column(Integer)

	user = relationship("User", backref=backref("ratings", order_by=id))
	movie = relationship("Movie", backref=backref("ratings", order_by=id))

### End class declarations

# def new_user():
# 	new_user = model.session.query(model.User).filter_by

def main():
    """In case we need this for something"""
    pass

if __name__ == "__main__":
    main()
