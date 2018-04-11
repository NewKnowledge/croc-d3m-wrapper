import io
import os
import time
import re
import requests
from PIL import Image, ImageFilter

import spacy
from tesserocr import PyTessBaseAPI
import numpy as np
import pandas as pd
from keras.preprocessing import image


def load_image(img_path, target_size, prep_func=lambda x: x):
    ''' load image given path and convert to an array
    '''
    img = image.load_img(img_path, target_size=target_size)
    x = image.img_to_array(img)
    return prep_func(x)


def load_image_from_web(image_url):
    ''' load an image from a provided hyperlink
    '''
    # get image
    response = requests.get(image_url)
    with Image.open(io.BytesIO(response.content)) as img:
        # convert to jpeg
        if img.format is not 'jpeg':
            img = img.convert('RGB')
        img.save('target_img.jpg')


def validate_url(url):
    url_validator = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return bool(url_validator.match(url))


def classify_objects(images_array, model, decode_func, n_top_preds=10):
    ''' Returns binary array with ones where the model predicts that
        the image contains an instance of one of the target classes
        (specified by wordnet id)
    '''
    predictions = model.predict(images_array)
    # decode the results into list of tuples (class, description, probability)
    predictions = decode_func(predictions, top=n_top_preds)
    return predictions


def char_detect(img_path, dictionary):
    """ Run tesseract ocr on an image supplied
        as an image path.
    """
    with PyTessBaseAPI() as ocr_api:
        with Image.open(img_path) as img:
            # will need a better preprocessing approach here
            # if we stay with tesseract:
            sharp_image = img.filter(ImageFilter.SHARPEN)

            ocr_api.SetImage(sharp_image)
            chars = ocr_api.GetUTF8Text()
            # char_confs = ocr_api.AllWordConfidences()

            chars = re.split('(\W+)\*', chars)[0].split(' ')
            chars = [i.replace('\n', ' ').strip(' ') for i in chars]

            clean_tokens = [i for i in chars
                            if len(i) > 0 and
                            i in dictionary.vocab]
            clean_chars = [i.encode('utf-8') for i in chars]

            return dict(tokens=clean_tokens, text=clean_chars)


def croc(image_path, dictionary=spacy.load('en'), target_size=(299, 299)):

    print('loading model')
    from keras.applications.inception_v3 \
        import (InceptionV3, decode_predictions, preprocess_input)
    model = InceptionV3(weights='imagenet')

    if validate_url(image_path):
        load_image_from_web(image_path)

    print('preprocessing images')
    X = np.array(
        [load_image(
            'target_img.jpg', target_size, prep_func=preprocess_input)])

    print('making object predictions')
    object_predictions = classify_objects(X, model, decode_predictions)

    print('performing character recognition')
    char_predictions = char_detect('target_img.jpg', dictionary)

    # save output
    object_predictions = pd.DataFrame.from_records(
        object_predictions[0], columns=['id', 'label', 'confidence'])
    words = pd.Series(char_predictions['tokens'])
    text = pd.Series(char_predictions['text'])

    os.remove('target_img.jpg')

    return dict(objects=object_predictions, chars=char_predictions)
