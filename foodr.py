import urllib.request
import os
from PIL import Image
import requests

def food_detection(url_photo):
  try:
      path_original_image = '/home/gena/tele_bot/img/t.jpg'

      # open photo from url and save
      urllib.request.urlretrieve(url_photo, path_original_image)
      im = Image.open(path_original_image)  # open
      rgb_im = im.convert('RGB')  # convert to RGB
      image_name = os.path.basename(path_original_image)  # get the name of the image
      image_name_noext = os.path.splitext(image_name)[0] # get the name without the extension

      # create the path where the new images will be saved as '.JPG'
      path = "/home/gena/tele_bot/img/new/" + image_name_noext + '.jpg'
      rgb_im.save(path)

      # get the width and the height
      width, height = rgb_im.size
      size_mb = os.path.getsize(path) >> 20
      while (size_mb >= 1):
          # resize th image 75%
          size = int(width * 0.75), int(height * 0.75)
          rez_image = rgb_im.resize(size, Image.ANTIALIAS)
          # save the resized image
          rez_image.save(path)
          # get the size in MB
          size_mb = os.path.getsize(path) >> 20
      # LogMeal API
      api_user_token = '4fe6f02673a4abb10d396669713d476122f6c60b'
      headers = {'Authorization': 'Bearer ' + api_user_token}
      url = 'https://api.logmeal.es/v2/recognition/dish'
      resp = requests.post(url, files={'image': open(path, 'rb')}, headers=headers)
      list_of_food = ['_empty_', 'meat', 'seafood', 'fish', 'fried food']

      # if photo is food
      if resp.json()['foodType'][0]['name'] == ('food' or '_empty_'):

          # if photo in meat product group
          if resp.json()['foodFamily'][0]['name'] in list_of_food\
                  and resp.json()['recognition_results'][0]['prob'] > 0.2:
              # delete photo
              os.remove(path)
              # add group info if it's exist
              food_group = '(' + resp.json()['foodFamily'][0]['name'] + ')'\
              if resp.json()['foodFamily'][0]['name'] != '_empty_' else ''

              return ("\nBot Warning! Photo may contain not vegan food: " +
                      food_group,
                      resp.json()['recognition_results'][0]['name'])
      os.remove(path)
      return ' '
  except Exception as e:
    logging.exception('T with{e}')
