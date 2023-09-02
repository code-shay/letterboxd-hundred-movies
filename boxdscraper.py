# -*- coding: utf-8 -*-
# Make sure to update the profile slug in order to have the code work for your profile.

from bs4 import BeautifulSoup
import requests
from PIL import Image
import json
from io import BytesIO
import os

_domain = "https://letterboxd.com/"
_filepath = os.getcwd()

# UPDATE THIS
profile_slug = "movieshay/films/by/date/"

profileURL = _domain + profile_slug

# Retreiving 100 movies from the letterboxd list view. 
# This can be scaled up to get all movies
def get_100_movies(profileURL):
    film_url_list = []

    while len(film_url_list) < 100:
        profileSoup = BeautifulSoup(requests.get(profileURL).content, "html.parser")
        table = profileSoup.find('ul', class_ ='poster-list')

        if table is None:
            return None

        films = table.find_all('li')

        for film in films:
            film_card = film.find('div').get('data-target-link')
            film_url_list.append(_domain + film_card)
            if(len(film_url_list) == 100):
                return film_url_list

        next_button = profileSoup.find('a', class_='next')

        if next_button is None:
            break
        else:
            profileURL = _domain + next_button['href']

    return film_url_list

# Getting the URL for the image of the poster used by letterboxd. 
# A better way to do this would by by using TMDb, but our scope 
# is limited to just using letterboxd.
def getMoviePosterURL(movieSoup):
    script_w_data = movieSoup.select_one('script[type="application/ld+json"]')
    json_obj = json.loads(script_w_data.text.split(' */')[1].split('/* ]]>')[0])
    posterURL = json_obj['image']

    return(posterURL)

# Getting the movie title - this is not used
def getMovieTitle(movieSoup):
    movieTitle = movieSoup.select_one('meta[property="og:title"]')["content"]
    return(movieTitle)

# Getting the image from the URL as a PIL Image object
def getPosterImage(posterURL):
    response = requests.get(posterURL)
    img = Image.open(BytesIO(response.content))
    return img

posterList = []
movie_url_list = get_100_movies(profileURL)

for movieURL in movie_url_list:
    movieHTML = requests.get(movieURL).content
    movieSoup = BeautifulSoup(movieHTML, "html.parser")
    posterURL = getMoviePosterURL(movieSoup)
    posterList.append(getPosterImage(posterURL))

collageSize = tuple([10*x for x in posterList[0].size])
collage = Image.new(mode="RGB" ,size=collageSize)
row = 0
column = 0
no_of_cols = 10

# Pasting poster in a grid. Rown number is not limited, so editing 
# no_of_cols is sufficient to change the shape of the grid as desired
for poster in posterList:
    if (column == no_of_cols):
        row +=1
        column = 0

    collage.paste(poster, box=[poster.width*column, poster.height*row])
    column += 1


collagePath = os.path.join(_filepath, "FinalCollage.png")
collage.save(collagePath)

# The following code is used to generate palettes based on the poster. 
# It is unrefined at the moment, and requires further work. 
# The base is strong though!

def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def get_dominant_color(pil_img, palette_size=16, rank=1):
    # Resize image to speed up processing
    img = pil_img.copy()
    img.thumbnail((100, 100))

    # Reduce colors (uses k-means internally)
    paletted = img.convert('P', palette=Image.ADAPTIVE, colors=palette_size)

    # Find the color that occurs most often
    palette = paletted.getpalette()
    color_counts = sorted(paletted.getcolors(), reverse=True)
    #print(color_counts)
    palette_index = color_counts[rank - 1][1]
    dominant_color = palette[palette_index*3:palette_index*3+3]

    hex_dominant_color = rgb_to_hex(dominant_color[0], dominant_color[1], dominant_color[2])

    return hex_dominant_color

domColorPalette = Image.new(mode = "RGB", size = [1400, 500])

image_no = 0
image_size = [12, 500]

for poster in posterList:
    domColor1 = Image.new(mode = "RGB", size = image_size, color= get_dominant_color(poster))
    domColor2 = Image.new(mode = "RGB", size = image_size, color= get_dominant_color(poster, rank = 2))
    #domColor3 = Image.new(mode = "RGB", size = image_size, color= get_dominant_color(poster, rank = 3))
    #domColor4 = Image.new(mode = "RGB", size = image_size, color= get_dominant_color(poster, rank = 4))
    #domColor5 = Image.new(mode = "RGB", size = image_size, color= get_dominant_color(poster, rank = 5))

    domColorPalette.paste(domColor1, box = [12 * image_no, 0])
    domColorPalette.paste(domColor2, box = [12 * image_no, 250])
    #domColorPalette.paste(domColor3, box = [12 * image_no, int(500/2 + 500/4)])
    #domColorPalette.paste(domColor4, box = [12 * image_no, int(500/2 + 500/4 + 500/8)])
    #domColorPalette.paste(domColor5, box = [12 * image_no, int(500/2 + 500/4 + 500/8 + 500/16)])

    image_no += 1



PalettePath = os.path.join(_filepath, "FinalPalette.png")
domColorPalette.save(PalettePath)



