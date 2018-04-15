import io
import os
import time
import re
from PIL import Image, ImageFilter

import requests
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


def classify_objects(image_array, model, decode_func, n_top_preds):
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
            raw_chars = ocr_api.GetUTF8Text()
            # char_confs = ocr_api.AllWordConfidences()

            # nasty regex to fix up the tesseract output
            # # whitespace between punctuation/symbols
            raw_chars = re.sub(
                r"([\w/'+$\s-]+|[^\w/'+$\s-]+)\s*", r"\1 ", raw_chars)
            # # split on whitespace
            raw_chars = re.split('(\W+)\*', raw_chars)[0].split(' ')
            # # replace persistent newlines
            raw_chars = [i.replace('\n', ' ') for i in raw_chars]
            chars = []

            for i in raw_chars:
                if i not in ['']:
                    chars.extend(i.split(' '))

            # tokenize text output
            clean_tokens = list(set([i.lower() for i in chars
                                    if len(i) > 0 and
                                    i.lower() in dictionary.vocab]))
            # utf encode the clean raw output
            clean_chars = [i.encode('utf-8') for i in chars]

            return dict(tokens=clean_tokens, text=clean_chars)


def croc(image_path, dictionary=spacy.load('en'), target_size=(299, 299),
         n_top_preds=10):

    print('loading model')
    from keras.applications.inception_v3 \
        import (InceptionV3, decode_predictions, preprocess_input)
    model = InceptionV3(weights='imagenet')

    if validate_url(image_path):
        filename = 'target_img.jpg'
        load_image_from_web(image_path)
    else:
        filename = image_path

    print('preprocessing image')
    X = np.array(
        [load_image(
            filename, target_size, prep_func=preprocess_input)])

    print('making object predictions')
    object_predictions = classify_objects(X, model, decode_predictions,
                                          n_top_preds)

    print('performing character recognition')
    char_predictions = char_detect(filename, dictionary)

    if filename == 'target_img.jpg':
        os.remove('target_img.jpg')

    return dict(objects=object_predictions, chars=char_predictions)
