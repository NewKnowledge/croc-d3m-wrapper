import os
import typing
import numpy as np
import pandas as pd

from nk_croc import *

from d3m.primitive_interfaces.base import PrimitiveBase, CallResult

from d3m import container, utils
from d3m.metadata import hyperparams, base as metadata_base, params

__author__ = 'Distil'
__version__ = '1.0.0'

Inputs = container.List[str]
Outputs = container.List[dict]


class Params(params.Params):
    pass


class Hyperparams(hyperparams.Hyperparams):
    pass


class croc(PrimitiveBase[Inputs, Outputs, Params, Hyperparams]):
    metadata = metadata_base.PrimitiveMetadata({
        # Simply an UUID generated once and fixed forever. Generated using "uuid.uuid4()".
        'id': "404fae2a-2f0a-4c9b-9ad2-fb1528990561",
        'version': __version__,
        'name': "croc",
        # Keywords do not have a controlled vocabulary. Authors can put here whatever they find suitable.
        'keywords': ['OCR', 'object detection', 'image analysis'],
        'source': {
            'name': __author__,
            'uris': [
                # Unstructured URIs.
                "https://github.com/NewKnowledge/croc-d3m-wrapper",
            ],
        },
        # A list of dependencies in order. These can be Python packages, system packages, or Docker images.
        # Of course Python packages can also have their own dependencies, but sometimes it is necessary to
        # install a Python package first to be even able to run setup.py of another package. Or you have
        # a dependency which is not on PyPi.
        "installation": [
              {
                  "type": "UBUNTU",
                  "package": "tesseract-ocr",
                  "version": "3.04.01-6"
              },
              {
                  "type": "UBUNTU",
                  "package": "libtesseract-dev",
                  "version": "3.04.01-6"
              },
              {
                  "type": "UBUNTU",
                  "package": "libleptonica-dev",
                  "version": "1.74.4-1"
              },
              {
                  "type": "PIP",
                  "package_uri": "git+https://github.com/NewKnowledge/nk_croc.git@72c40cde6a6495054e06b4b4b4f561e2b55c1dfd#egg=nk_croc"
              },
              {
                  "type": "PIP",
                  "package_uri": "git+https://github.com/NewKnowledge/croc-d3m-wrapper.git@{git_commit}#egg=CROCd3mWrapper".format(
                    git_commit="52cbbb80b360bc70b5f0e99ff70a2d7abf44fd8d")
              }
        ],
        # The same path the primitive is registered with entry points in setup.py.
        'python_path': 'd3m.primitives.distil.croc',
        # Choose these from a controlled vocabulary in the schema. If anything is missing which would
        # best describe the primitive, make a merge request.
        "algorithm_types": [
            metadata_base.PrimitiveAlgorithmType.MULTILABEL_CLASSIFICATION
            ],
        "primitive_family": metadata_base.PrimitiveFamily.DIGITAL_IMAGE_PROCESSING
    })

    def __init__(self, *, hyperparams: Hyperparams)-> None:
        super().__init__(hyperparams=hyperparams)

    def fit(self) -> None:
        pass

    def get_params(self) -> Params:
        return self._params

    def set_params(self, *, params: Params) -> None:
        self.params = params

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        pass

    def produce(self, *, inputs: Inputs) -> CallResult[Outputs]:
        """
            Produce image object classification predictions and OCR for an
            image provided as an URI or filepath

        Parameters
        ----------
        inputs : Image URI or local filepath

        Returns
        -------
        output : A dict with objects, text and tokens, corresponding to the
            detected objects, raw text and tokens predicted to bne in the 
            supplied image.
        """

        image_path = inputs

        image_analyzer = Croc()

        return image_analyzer.predict(inputs=image_path)


if __name__ == '__main__':
    client = croc(hyperparams={})
    image_path = 'http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg'
    result = client.produce(inputs=image_path)
    print(result)
