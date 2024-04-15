
import ctypes
import requests
import os
def main():
    # TODO: Add code to test the functions in this module
    return

def download_image(image_url):
    # Download an image from a URL.
    response = requests.get(image_url)
    return response.content

def save_image_file(image_data, image_path):
    #Saves image data as a file on disk on given path.
    with open(image_path, 'wb') as f:
        f.write(image_data)
    return image_path

def set_desktop_background_image(image_path):
    #Sets the desktop background image to a specific image.

    SPI_SETDESKWALLPAPER = 20
    result = ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, os.path.abspath(image_path), 0)
    if result==1:
        return True
    else:
        return False

def scale_image(image_size, max_size=(800, 600)):
    resize_ratio = min(max_size[0] / image_size[0], max_size[1] / image_size[1])
    new_size = (int(image_size[0] * resize_ratio), int(image_size[1] * resize_ratio))
    return new_size

if __name__ == '__main__':
    main()