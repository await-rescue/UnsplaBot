# -*- coding: utf-8 -*-

import sys
import os
import requests
import shutil
import time
import random

from country_codes import country_codes
from cities_top_600 import cities


UNSPLASH_ACCESS_KEY = os.environ.get('UNSPLASH_ACCESS_KEY')
UNSPLASH_SECRET_KEY = os.environ.get('UNSPLASH_SECRET_KEY')

PER_PAGE = random.randint(2, 5)
BASE_URL = 'https://api.unsplash.com/search/photos?client_id={}&per_page={}'.format(UNSPLASH_ACCESS_KEY, PER_PAGE)

IMAGE_MODES = ['regular', 'full']
IMAGE_MODE = IMAGE_MODES[0]

MODE = os.environ.get('MODE')

ORIENTATIONS = ['landscape', 'portrait', 'squarish']
ORIENTATION = ORIENTATIONS[0]

SELECT_MODE = 'likes'


cur_path = os.path.dirname(__file__)
image_path = os.path.join(cur_path, 'images')

def wait():
    time.sleep(75)

def get_image_location(keyword):
    return os.path.join(cur_path, "images/{}/{}/{}/{}.{}".format(MODE, ORIENTATION, IMAGE_MODE, keyword, 'jpeg'))

def get_images_folder():
    return os.path.join(cur_path, 'images/{}/{}/{}'.format(MODE, ORIENTATION, IMAGE_MODE))

def get_image_url(keyword, mode='likes'):
    # Just a check to see if we already downloaded it
    image_location = get_image_location(keyword.replace(' city', ''))
    if os.path.exists(image_location):
        print("✋🏻 Image exists at {}".format(image_location))
        return

    # query = '{}%20{}'.format(keyword, 'scenic'
    query = "{}".format(keyword)

    url = "{}&query={}&orientation={}".format(BASE_URL, query, ORIENTATION)
    
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.HTTPError as e:
        print('😡 Request failed for {}: {}'.format(keyword, e))
        wait()
        return 
    
    response_json = response.json()

    rate_limit_remaining = response.headers.get('X-Ratelimit-Remaining')
    rate_limit = response.headers.get('X-Ratelimit-Limit')
    print('rate limit: {}, remaining: {}'.format(rate_limit, rate_limit_remaining))

    results = response_json.get('results')

    select_mode = SELECT_MODE

    if len(results) > 0:
        # Get result with most likes
        if select_mode == 'likes':
            likes = 0
            result_url = None
            for result in results:
                result_url = result.get('urls', {}).get(IMAGE_MODE) if result['likes'] > likes else result_url
        else:
            result_url = results[random.randint(0, len(results) -1)].get('urls', {}).get(IMAGE_MODE)

        print(result_url)
        return result_url
    else:
        print('👀 no image for {}'.format(keyword))
        wait()

def get_image(keyword):
    url = get_image_url(keyword)
    if not url:
        return

    dir_path = get_images_folder()
    if not os.path.exists(dir_path):    
        os.makedirs(dir_path)

    # hacky, remove city from keywords
    # image_location = get_image_location(keyword.replace(' city', ''))
    image_location = get_image_location(keyword)

    response = requests.get(url, stream=True)
    local_file = open(image_location, 'wb')

    response.raw.decode_content = True
    shutil.copyfileobj(response.raw, local_file)

    del response
    print("✅ Image saved to {}".format(image_location))
    wait()

def start():
    if MODE == 'countries':
        for country in country_codes:
            get_image(country['Name'])
    if MODE == 'cities':
        for city in cities:
            # TODO: might need AND if possible
            # get_image('{} {}'.format(city['name'], 'city'))

            get_image(city['name'])

    print('💥DONE')


if len(sys.argv) > 1:
    keyword = str(sys.argv[1])
    get_image(keyword)
else:
    print("🏁 Grabbing images")
    start()

