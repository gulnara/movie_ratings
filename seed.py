import model
import csv
import sqlalchemy.exc
import datetime

def load_users(session):
    #open csv file as f
    with open('seed_data/u.user') as f:
        #reads f file and breaks rows on | and stores strings of data in userreader file
        userreader = csv.reader(f, delimiter='|')
        #loops through list of strings and assigns variables to corresponding items in the list
        for row in userreader:
            id = int(row[0])
            age = int(row[1])
            gender = row[2]
            occupation = row[3]
            zipcode = row[4]
            #invokes our model which will talk to sqlalchemy and populate our database
            user = model.User(id=id, email=None, password=None, age=age, gender=gender, occupation=occupation, zipcode=zipcode)
            # stages data for commit
            session.add(user)
            #commits data to the database
            session.commit()
    #pass

def load_movies(session):
#use u.item
    with open('seed_data/u.item') as f:
        moviereader = csv.reader(f, delimiter='|')
        #for list of strings in moviereader assign titles to corresponding columns
        for row in moviereader:
            id = int(row[0])
            name = row[1].decode("latin_1")
            released_at = row[2] 
            if not released_at:
                continue
            #the date is represented as a string and we need to make it date format, hence 
            #parcing it in the date format accaptabe to python via strptime 
            released_at = datetime.datetime.strptime(released_at, "%d-%b-%Y")
            imdb_url = row[4]
            movie = model.Movie(id=id, name=name, released_at=released_at, imdb_url=imdb_url)
            session.add(movie)
            session.commit()
    #pass


def load_ratings(session):
    # use u.data
    with open('seed_data/u.data') as f:
        ratingreader = csv.reader(f, delimiter='\t')
        for row in ratingreader:
            user_id = int(row[0])
            movie_id = int(row[1])
            rating = int(row[2])
            r = model.Rating(user_id=user_id, movie_id=movie_id, rating=rating)
            session.add(r)
            session.commit()
    #pass

def main(session):
    # You'll call each of the load_* functions with the session as an argument
    load_users(session)
    load_movies(session)
    load_ratings(session)

if __name__ == "__main__":
    s= model.connect()
    main(s)
