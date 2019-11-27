import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

def boxoffice_scraper(imdbid):
    bo_url = 'https://www.boxofficemojo.com/title/' + imdbid
    r = requests.get(bo_url)
    bo_soup = BeautifulSoup(r.text,'lxml')
    try:
        opening = bo_soup.body.div.main.div.contents[2].contents[3].contents[1].contents[1].span.contents[0]
    except:
        opening = np.nan
    try:
        budget = bo_soup.body.div.main.div.contents[2].contents[3].contents[2].contents[1].span.contents[0]
    except: 
        budget = np.nan
    try:
        domestic = bo_soup.body.div.main.div.contents[5].div.div.table.contents[1].contents[3].span.contents[0]
    except:
        domestic = np.nan
    return [budget,opening,domestic]

def get_omdb_data(imdbid):
    API_KEY = 'myAPI_KEY'
    url = 'http://www.omdbapi.com/?'
    url = url + API_KEY + imdbid
    r = requests.get(url)
    try:
        omdb_data = r.json()
    except:
        return
    if omdb_data['Response'] == 'False':
        return omdb_data
    try:
        rt_score = omdb_data['Ratings'][1]['Value'].strip('%')
    
    except:
        rt_score = np.nan
    omdb_data['Rotten Tomatoes Score'] = rt_score 
    boxoffice_data = boxoffice_scraper(imdbid)
    omdb_data['Budget'] = boxoffice_data[0]
    omdb_data['Opening Weekend'] = boxoffice_data[1]
    omdb_data['Domestic Gross'] = boxoffice_data[2]
    return(omdb_data)
    
def create_omdb_dataset(idList):
    omdb_list = []
    for id in idList:
        omdb_list.append(get_omdb_data(id))
    return pd.DataFrame(omdb_list)
    
movies = pd.read_csv('the-movies-dataset/movies_metadata.csv')
imdbid_list = list(movies['imdb_id'].astype('str'))
omdb_df = create_omdb_dataset(imdbid_list)
omdb_df['Released'] = pd.to_datetime(omdb_df['Released'])
d1 = omdb_df[['imdbID','Title','Year','Rated','Budget','Domestic Gross',
             'Opening Weekend','imdbRating','imdbVotes',
             'Rotten Tomatoes Score','Metascore','Runtime','Director',
             'Actors','Released','Awards']] 
d2 = movies[['vote_average','vote_count','belongs_to_collection','genres',
                'production_companies','spoken_languages']]
movies_df = pd.concat([d1,d2],axis=1)
movies_df.to_csv('movies_dataset.csv')

