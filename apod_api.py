
import requests

NASA_API_KEY = 'byAB4j1YbHoJiYXa2mPtDjXYitr27pR2eDdIPf9r' # follow instructions to get this
APOD_URL = "https://api.nasa.gov/planetary/apod"

def main():
    apod_date = date.fromisoformat(argv[1])
    apod_info_dict = get_apod_info(apod_date)
    if apod_info_dict:
        apod_url = get_apod_image_url(apod_info_dict)
        apod_image_data = image_lib.download_image(apod_url)
        image_lib.save_image_file(apod_image_data,  r'C:\temp\image.jpg')
    return

def get_apod_info(apod_date):

    # Setup request parameters 
    apod_params = {
        'api_key' : NASA_API_KEY,
        'date' : apod_date,
        'thumbs' : True
    }

    # Send GET request to NASA API
    print(f'Getting {apod_date} APOD information from NASA...', end='')
    resp_msg = requests.get(APOD_URL, params=apod_params)

    # Check if the info was retrieved successfully
    if resp_msg.status_code == requests.codes.ok:
        print('success')
        print("resp_msg::::::::",resp_msg)
        # Convert the received info into a dictionary 
        apod_info_dict = resp_msg.json()
        return apod_info_dict
    else:
        print('failure')
        print(f'Response code: {resp_msg.status_code} ({resp_msg.reason})')    

def get_apod_image_url(apod_info_dict):

    if apod_info_dict['media_type'] == 'image':
        print("images:::::",apod_info_dict['hdurl'])
        return apod_info_dict['hdurl']
    elif apod_info_dict['media_type'] == 'video':
        print("Videos",apod_info_dict['thumbnail_url'])
        # Some video APODs do not have thumbnails, so this will sometimes fail
        return apod_info_dict['thumbnail_url']

if __name__ == '__main__':
    from datetime import date
    from sys import argv
    import image_lib
    main()