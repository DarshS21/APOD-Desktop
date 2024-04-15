from datetime import date
import os
import image_lib
import inspect
import sqlite3
import argparse
import datetime
import sys
import requests
import urllib
import re
import hashlib


# Global variables
image_cache_dir = None  # path of image cache directory
image_cache_db = None   # path of image cache database
api_key = 'byAB4j1YbHoJiYXa2mPtDjXYitr27pR2eDdIPf9r'  # Api key of APOd

def main():
    # Get the APOD date from the command line
    apod_date = get_apod_date()    

    # Get the path of the directory in which this script resides
    script_dir = get_script_dir()

    # Initialize the image cache path
    init_apod_cache(script_dir)

    # Add the APOD for the specified date to the cache
    apod_id = add_apod_to_cache(apod_date)

    # Information about the APOD from the DB
    apod_info = get_apod_info(apod_id)

    # APOD as the desktop background image
    if apod_id != 0:
        result = image_lib.set_desktop_background_image(apod_info['file_path'])
        if result:
            print("Setting desktop to"+apod_info['file_path']+"...success")
def get_apod_date():

    # Define the command-line arguments
    parser = argparse.ArgumentParser(description='APOD Desktop')
    parser.add_argument('date', nargs='?', default=datetime.date.today().strftime('%Y-%m-%d'),
                    help='APOD date (format: YYYY-MM-DD)')
    args = parser.parse_args()

    # Validate the specified date format YYYY-MM-DD
    try:
        apod_date = datetime.datetime.strptime(args.date, '%Y-%m-%d').date()
        assert apod_date >= datetime.date(1995, 6, 16)
        assert apod_date <= datetime.date.today()
    except (ValueError, AssertionError):
        print('Error: Invalid APOD date specified.')
        print("Script execution aborted ")
        sys.exit(1)
    return apod_date

def get_script_dir():

    # get the script path
    script_path = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
    return os.path.dirname(script_path)

def init_apod_cache(parent_dir):

    global image_cache_dir
    global image_cache_db

    # Determine the path of the image cache directory
    image_cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')

    print("image cache directory : ",image_cache_dir)    
    # Create the image cache directory if it does not already exist
    if not os.path.exists(image_cache_dir):
        os.makedirs(image_cache_dir)
        print("Image Cache Directory Created")
    else:
        print("Image Cache Directory already exists.")

    # Determine the path of image cache database
    image_cache_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
    image_cache_db = os.path.join(image_cache_db, 'apod.db')
    print("image cache database : ",image_cache_db)

    # Create the database if it does not already exist
    if not os.path.exists(image_cache_db):
        print("Image Cache DB Created")
    else:
        print("image Cache DB already exists.")    
    
    # Connect to the SQLite db and create the table if it doesn't already exist
    conn = sqlite3.connect(image_cache_db)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS apod_images
             (id INTEGER PRIMARY KEY, title TEXT, explanation TEXT, file_path TEXT, hash TEXT)''')



# Check if an image with the same SHA-256 hash value already exists in the cache
def hash_file(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
        return hashlib.sha256(data).hexdigest()


def add_apod_to_cache(apod_date):

    print("APOD date : ", apod_date.isoformat())

    apod_url = f'https://api.nasa.gov/planetary/apod'
    apod_params = {
        'api_key': api_key,
        'date': apod_date,
        'thumbs': True
    }

    response = requests.get(apod_url,params=apod_params)
   
    apod_data = response.json()
    if apod_data['media_type'] == 'image':
        image_download_url = apod_data['hdurl']
    elif apod_data['media_type'] == 'video':
        image_download_url = apod_data['thumbnail_url']
    print("Getting "+ apod_date.isoformat() +" APOD information from NASA...success")
    print("APOD title:",apod_data['title'])
    print("APOD URL:",image_download_url)
    print("Downloading image from ",image_download_url,"..success")

    img_content = image_lib.download_image(image_download_url)
    
    # make a image file path
    image_ext = os.path.splitext(urllib.parse.urlparse(image_download_url).path)[1]
    image_title = re.sub(r'[^a-zA-Z0-9\s_]+', '', apod_data['title']).strip().replace(' ', '_')
    image_file_name = f'{image_title}{image_ext}'
    image_file_path = os.path.join(image_cache_dir, image_file_name)
    image_hash = hash_file(image_file_path) if os.path.exists(image_file_path) else None
    if not image_hash:
        
        image_file_path = image_lib.save_image_file(img_content,image_file_path)

        image_hash = hash_file(image_file_path)
    # Check if the image already exists in the database
    conn = sqlite3.connect(image_cache_db)
    c = conn.cursor()
    print("APOD SHA-256:",image_hash)
    c.execute('SELECT id FROM apod_images WHERE hash=?', (image_hash,))
    existing_image_id = c.fetchone()
    conn.commit()
    if existing_image_id:
        print('Image already exists in cache.')
        return existing_image_id[0]
    else:
        # get a new list id
        new_Last_Id = add_apod_to_db(apod_data['title'], apod_data['explanation'], image_file_path, image_hash)
        print("APOD image is not already in cache.")
        print("APOD file path:",image_file_path)
        print("Saving image file as ",image_file_path, "...success")
        print("Adding APOD to image cache DB...success")
        return new_Last_Id



    return 0

def add_apod_to_db(title, explanation, file_path, sha256):
    conn = sqlite3.connect(image_cache_db) # connection establish
    c = conn.cursor()
    c.execute('INSERT INTO apod_images (title, explanation, file_path, hash) VALUES (?, ?, ?, ?)',
                (title, explanation, file_path, sha256)) # add the data into database
    new_Last_Id = c.lastrowid
    conn.commit()
    return new_Last_Id

def get_apod_id_from_db(image_sha256):

    return 0

def determine_apod_file_path(image_title, image_url):

    return

def get_apod_info(image_id):

    conn = sqlite3.connect(image_cache_db)
    cursor = conn.cursor()
    cursor.execute('SELECT title, explanation, file_path FROM apod_images WHERE id = ?', (image_id,))
    result = cursor.fetchone()


    apod_info = {
        'title': result[0], 
        'explanation': result[1],
        'file_path': result[2],
    }
    return apod_info

def get_all_apod_titles():

    return

if __name__ == '__main__':
    main()