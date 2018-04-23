import io
import os
import time
import re
from PIL import Image, ImageFilter

import requests
import spacy
from json import dumps
from tesserocr import PyTessBaseAPI
import numpy as np
import pandas as pd
from keras.preprocessing import image
from keras.applications.inception_v3 \
    import decode_predictions, preprocess_input

from d3m import container, utils
from d3m.primitive_interfaces.base import PrimitiveBase, CallResult
from d3m.metadata import hyperparams, base \
    as metadata_base, params

__author__ = 'Distil'
__version__ = '1.0.0'

Inputs = container.List[str]
Outputs = container.List[dict]


class Params(params.Params):
    pass


class Hyperparams(hyperparams.Hyperparams):
    pass


class Croc(PrimitiveBase[Inputs, Outputs, Params, Hyperparams]):
    metadata = {}

    def __init__(self, *, hyperparams: Hyperparams)-> None:
        super().__init__(hyperparams=Hyperparams)

        self.target_size = (299, 299)
        self.model = InceptionV3(weights='imagenet')
        self.nlp = spacy.load('en')
        self.n_top_preds = 10

    def predict(self, *, inputs: Inputs, model=self.model,
                nlp=self.nlp,
                target_size=self.target_size,
                n_top_preds=self.n_top_preds) -> CallResult[Outputs]:
        """
            Produce image object classification predictions and OCR for an
            image provided as an URI or filepath

        Parameters
        ----------
        inputs : Image URI or filepath

        Returns
        -------
        output : A dict with objects, text and tokens, corresponding to the
            detected objects, raw text and tokens predicted to bne in the 
            supplied image.
        """

        image_path = inputs

        try:
            if validate_url(image_path):
                filename = 'target_img.jpg'
                load_image_from_web(image_path)
            else:
                filename = image_path
        except:
            return "Image loading failed."

        try:
            print('preprocessing image')
            X = np.array(
                [load_image(
                    filename, target_size, prep_func=preprocess_input)])

            print('making object predictions')
            object_predictions = classify_objects(X, model, decode_predictions,
                                                  n_top_preds)

            object_predictions = pd.DataFrame.from_records(
                object_predictions[0], columns=['id', 'label', 'confidence'])

            print('performing character recognition')
            char_predictions = char_detect(filename, nlp)

            if filename == 'target_img.jpg':
                os.remove('target_img.jpg')

            return dumps(dict(
                objects=result['objects'].to_dict(),
                text=[str(i) for i in result['chars']['text']],
                tokens=result['chars']['tokens']))
        except:
            return "Something went wrong when generating CROC predictions."

    def fit(self) -> None:
        pass

    def get_params(self) -> Params:
        return self._params

    def set_params(self, *, params: Params) -> None:
        self.params = params

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        pass

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

    def cleanup_text(raw_chars, nlp, logging=False):
        ''' use spacy to clean text and find tokens
        '''
        doc = nlp(raw_chars, disable=['parser', 'ner'])
        text = [t.text for t in doc]
        tokens = [tok.lemma_.lower().strip() for tok in doc
                  if tok.lemma_ != '-PRON-']
        tokens = [tok for tok in tokens
                  if tok not in nlp.Defaults.stop_words and
                  tok not in string.punctuation]

        return dict(tokens=list(set(tokens)), text=text)

    def classify_objects(image_array, model, decode_func, n_top_preds):
        ''' Returns binary array with ones where the model predicts that
            the image contains an instance of one of the target classes
            (specified by wordnet id)
        '''
        predictions = model.predict(images_array)
        # decode the results into list of tuples (class, description, probability)
        predictions = decode_func(predictions, top=n_top_preds)
        return predictions

    def char_detect(img_path, nlp):
        ''' Run tesseract ocr on an image supplied
            as an image path.
        '''
        with PyTessBaseAPI() as ocr_api:
            with Image.open(img_path) as image:
                # will need a better preprocessing approach here
                # if we stay with tesseract:
                sharp_image = image.filter(ImageFilter.SHARPEN)

                ocr_api.SetImage(sharp_image)
                raw_chars = ocr_api.GetUTF8Text()
                # char_confs = ocr_api.AllWordConfidences()

                text = cleanup_text(raw_chars, nlp)

                # utf encode the clean raw output
                clean_chars = [i.encode('utf-8') for i in text['text']]

                return dict(tokens=text['tokens'], text=clean_chars)
