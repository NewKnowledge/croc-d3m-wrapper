import os
import time
import pickle
import re
import enchant
from glob import glob
from PIL import Image, ImageFilter

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


def classify_objects(images_array, model, decode_func, n_top=10):
    ''' Returns binary array with ones where the model predicts that
        the image contains an instance of one of the target classes
        (specified by wordnet id)
    '''
    predictions = model.predict(images_array)
    # decode the results into list of tuples (class, description, probability)
    predictions = decode_func(predictions, top=n_top)
    return predictions


def char_detect(img_path, dictionary):
    """ Run tesseract ocr on an image supplied
        as an image path.
    """
    with PyTessBaseAPI() as ocr_api:
        with Image.open(img_path) as image:
            # will need a better preprocessing approach here
            # if we stay with tesseract:
            sharp_image = image.filter(ImageFilter.SHARPEN)

            ocr_api.SetImage(sharp_image)
            chars = ocr_api.GetUTF8Text()
            # char_confs = ocr_api.AllWordConfidences()

            chars = re.split('(\W+)\*', chars)[0].split(' ')
            chars = [i.strip('\n') for i in chars]

            clean_tokens = [i.lower() for i in chars
                            if len(i) > 0 and
                            dictionary.check(i)]
            clean_chars = [i.encode('utf-8') for i in chars]

            return {
                'tokens': clean_tokens,
                'text': clean_chars
                }


def croc(data_path, dictionary=enchant.Dict("en_US"), target_size=(299, 299)):

    print('loading model')
    from keras.applications.inception_v3 \
        import (InceptionV3, decode_predictions, preprocess_input)
    model = InceptionV3(weights='imagenet')

    print('preprocessing images')
    img_paths = glob(data_path + '/*')
    X = np.array([load_image(img_, target_size, prep_func=preprocess_input)
                  for img_ in img_paths
                  if os.path.isfile(img_)])

    print('making object predictions')
    object_predictions = classify_objects(X, model, decode_predictions)

    print('performing character recognition')
    char_predictions = [char_detect(img_, dictionary)
                        for img_ in img_paths
                        if os.path.isfile(img_)]

    object_predictions = pd.DataFrame.from_records(
        object_predictions[0], columns=['id', 'label', 'confidence'])
    words = pd.Series(char_predictions[0]['tokens'])
    text = pd.Series(char_predictions[0]['text'])

    return {
        'objects': object_predictions,
        'words': words,
        'chars': text
        }
