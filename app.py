from flask import Flask, request, render_template
import pickle
import requests
import pandas as pd
from patsy import dmatrices

app = Flask(__name__)

movies = pickle.load(open('models/movies_list.pkl','rb'))
similarity = pickle.load(open('models/similarity.pkl','rb'))
movies['title'] = movies['title'].str.lower()

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=3afc3d9c9bc6a9321feca626d548c13a&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path
  
def recommend(movie):
    # print(movies)
    index = movies[movies['title']==movie].index[0]
    # print(index)
    distances = sorted(list(enumerate(similarity[index])),reverse=True,key=lambda x:x[1])
    recommended_movies_name = []
    recommended_movies_poster = []
    overview = []
    # recommended_movies_name.append([movie])
    for i in distances[0:9]:
        movie_id = movies.iloc[i[0]].id
        recommended_movies_name.append(movies.iloc[i[0]].title)
        recommended_movies_poster.append(fetch_poster(movie_id))
        overview.append(movies.iloc[i[0]].overview)

    # print(recommended_movies_name)
    recommended_movies_name = [movie_name.capitalize() for movie_name in recommended_movies_name]
    
    return recommended_movies_name,recommended_movies_poster, overview

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/recommendation',methods=['GET','POST'])
def recommendation():
    movies_list = movies['title'].values
    print(movies_list)
    if request.method=='POST':
        try:
        #     print(request.form['movie'])
        # except:
        #     print('error')
            if request.form:
                movies_name = request.form['movie']
                # print(type(movies_name))
                movies_name = movies_name.lower()
                recommended_movies_name,recommended_movies_poster,overview = recommend(movies_name)
                print()
                print(recommended_movies_name)
                print(recommended_movies_poster)
                print(overview)
                # overview = []
                # for i in range(len(recommended_movies_name)):
                #     # index = movies[movies['title']==recommended_movies_name[i]].index[0]
                #     overview.append(movies.iloc[[i][0]].overview)
                
                n = len(recommended_movies_poster)

                # print(overview)
                return render_template('recommendation.html',movie=movies_name ,movies_name=recommended_movies_name, poster = recommended_movies_poster,overview = overview, movies_list = movies_list, n=n)
            
        except Exception as e:
            error = {'error':e}
            # movies_name = request.form['movie']
            return render_template('error.html')
    
    return render_template('recommendation.html', movies_list = movies_list)


if __name__ == '__main__':
    # Start the Flask application
    app.run(debug=True)