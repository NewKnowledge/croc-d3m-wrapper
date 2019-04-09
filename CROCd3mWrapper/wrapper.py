import os
import sys
import typing
from json import loads
import numpy as np
import pandas as pd
from keras import backend as K

from d3m_croc import *

from d3m.primitive_interfaces.transformer import TransformerPrimitiveBase
from d3m.primitive_interfaces.base import CallResult

from d3m import container, utils
from d3m.metadata import hyperparams, base as metadata_base
from d3m.container import DataFrame as d3m_DataFrame
from common_primitives import utils as utils_cp, dataset_to_dataframe as DatasetToDataFrame

__author__ = 'Distil'
__version__ = '1.2.4'
__contact__ = 'mailto:numa@newknowledge.io'

Inputs = container.pandas.DataFrame
Outputs = container.pandas.DataFrame

class Hyperparams(hyperparams.Hyperparams):
    target_columns = hyperparams.Set(
        elements=hyperparams.Hyperparameter[str](''),
        default=(),
        max_size=sys.maxsize,
        min_size=0,
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description='names of columns with image paths'
    )

    output_labels = hyperparams.Set(
        elements=hyperparams.Hyperparameter[str](''),
        default=(),
        max_size=sys.maxsize,
        min_size=0,
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description='desired names for croc output columns'
    )


class croc(TransformerPrimitiveBase[Inputs, Outputs, Hyperparams]):
    """
            Produce image object classification predictions and OCR for an
            image provided as an URI or filepath
        Parameters
        ----------
        inputs : pandas dataframe where a column is a pd.Series of image paths/URLs
        Returns
        -------
        output : A dataframe with objects, text and tokens, corresponding to the
            detected objects, raw text and tokens predicted to be in the
            supplied images.
        """
    metadata = metadata_base.PrimitiveMetadata({
        # Simply an UUID generated once and fixed forever. Generated using "uuid.uuid4()".
        "id": "404fae2a-2f0a-4c9b-9ad2-fb1528990561",
        "version": __version__,
        "name": "croc",
        # Keywords do not have a controlled vocabulary. Authors can put here whatever they find suitable.
        "keywords": ["OCR," "object detection", "image analysis"],
        "source": {
            "name": __author__,
            'contact': __contact__,
            "uris": [
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
                  "package_uri": "git+https://github.com/NewKnowledge/croc-d3m-wrapper.git@{git_commit}#egg=CROCd3mWrapper".format(
                        git_commit=utils.current_git_commit(os.path.dirname(__file__))
                        ),
              },
                        {
            "type": "TGZ",
            "key": "croc_weights",
            "file_uri": "http://public.datadrivendiscovery.org/croc.tar.gz",
            "file_digest":"0be3e8ab1568ec8225b173112f4270d665fb9ea253093cd9ea98c412c9053c92"
        },
        ],
        # The same path the primitive is registered with entry points in setup.py.
        "python_path": "d3m.primitives.digital_image_processing.croc.Croc",
        # Choose these from a controlled vocabulary in the schema. If anything is missing which would
        # best describe the primitive, make a merge request.
        "algorithm_types": [
            metadata_base.PrimitiveAlgorithmType.MULTILABEL_CLASSIFICATION
            ],
        "primitive_family": metadata_base.PrimitiveFamily.DIGITAL_IMAGE_PROCESSING
    })

    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, volumes: typing.Dict[str,str]=None)-> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, volumes=volumes)

        self.volumes = volumes

    def _get_column_base_path(self, inputs: Inputs, column_name: str) -> str:
        # fetches the base path associated with a column given a name if it exists
        column_metadata = inputs.metadata.query((metadata_base.ALL_ELEMENTS,))
        if not column_metadata or len(column_metadata) == 0:
            return None

        num_cols = column_metadata['dimension']['length']
        for i in range(0, num_cols):
            col_data = inputs.metadata.query((metadata_base.ALL_ELEMENTS, i))
            if col_data['name'] == column_name and 'location_base_uris' in col_data:
                return col_data['location_base_uris'][0]

        return None

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> CallResult[Outputs]:
        """
            Produce image object classification predictions and OCR for an
            image provided as an URI or filepath

        Parameters
        ----------
        inputs : pandas dataframe where a column is a pd.Series of image paths/URLs

        Returns
        -------
        output : A dataframe with objects, text and tokens, corresponding to the
            detected objects, raw text and tokens predicted to be in the
            supplied images.
        """

        target_columns = self.hyperparams['target_columns']
        output_labels = self.hyperparams['output_labels']

        imagepath_df = inputs
        image_analyzer = Croc(weights_path=self.volumes["croc_weights"]+"/inception_v3_weights_tf_dim_ordering_tf_kernels.h5",
                             isa_path=self.volumes["croc_weights"]+"/is_a.py",
                             id_mapping_path=self.volumes["croc_weights"]+"/id_mapping.py",
                             spacy_path=self.volumes["croc_weights"]+"/en_core_web_md-1.2.1.tar.gz")

        for i, ith_column in enumerate(target_columns):
            # initialize an empty dataframe
            result_df = pd.DataFrame()
            output_label = output_labels[i]

            # get the base uri from the column metadata and remove the the
            # scheme portion
            base_path = self._get_column_base_path(inputs, ith_column)
            if base_path:
                base_path = base_path.split('://')[1]

            for image_path in imagepath_df.loc[:, ith_column]:

                # append the image path to the base path if it exists, otherwise just
                # use the image path as found in the column
                if base_path:
                    input_path = os.path.join(base_path, image_path)
                else:
                    input_path = image_path

                jth_result = loads(
                    image_analyzer.predict(input_path=input_path))

                result_df = result_df.append(
                    {output_label + '_object_id': jth_result['objects']['id'],
                     output_label + '_object_label': jth_result['objects']['label'],
                     output_label + '_object_conf': jth_result['objects']['confidence'],
                     output_label + '_object_trees': jth_result['object_trees'],
                     output_label + '_tokens': jth_result['tokens'],
                     output_label + '_text': jth_result['text']},
                    ignore_index=True)

            imagepath_df = pd.concat(
                [imagepath_df.reset_index(drop=True), result_df], axis=1)

            imagepath_df.index.name = 'd3mIndex'

        # clear the session to avoid tensorflow state errors when invoking downstream primitives
        K.clear_session()
        
        # create metadata for the croc output dataframe
        croc_df = d3m_DataFrame(imagepath_df)
        # first column (_object_conf)
        col_dict = dict(croc_df.metadata.query((metadata_base.ALL_ELEMENTS, 0)))
        col_dict['structural_type'] = type("it is a string")
        col_dict['name'] = output_label + "_object_conf"
        col_dict['semantic_types'] = ('http://schema.org/Text', 'https://metadata.datadrivendiscovery.org/types/Attribute')
        croc_df.metadata = croc_df.metadata.update((metadata_base.ALL_ELEMENTS, 0), col_dict)
        # second column (_object_id)
        col_dict = dict(croc_df.metadata.query((metadata_base.ALL_ELEMENTS, 1)))
        col_dict['structural_type'] = type("it is a string")
        col_dict['name'] = output_label + "_object_id"
        col_dict['semantic_types'] = ('http://schema.org/Text', 'https://metadata.datadrivendiscovery.org/types/Attribute')
        croc_df.metadata = croc_df.metadata.update((metadata_base.ALL_ELEMENTS, 1), col_dict)
        # third column (_object_label)
        col_dict = dict(croc_df.metadata.query((metadata_base.ALL_ELEMENTS, 2)))
        col_dict['structural_type'] = type("it is a string")
        col_dict['name'] = output_label + "_object_label"
        col_dict['semantic_types'] = ('http://schema.org/Text', 'https://metadata.datadrivendiscovery.org/types/Attribute')
        croc_df.metadata = croc_df.metadata.update((metadata_base.ALL_ELEMENTS, 2), col_dict)
        # fourth column (_object_trees)
        col_dict = dict(croc_df.metadata.query((metadata_base.ALL_ELEMENTS, 3)))
        col_dict['structural_type'] = type("it is a string")
        col_dict['name'] = output_label + "_object_trees"
        col_dict['semantic_types'] = ('http://schema.org/Text', 'https://metadata.datadrivendiscovery.org/types/Attribute')
        croc_df.metadata = croc_df.metadata.update((metadata_base.ALL_ELEMENTS, 3), col_dict)
        # five column (_text)
        col_dict = dict(croc_df.metadata.query((metadata_base.ALL_ELEMENTS, 4)))
        col_dict['structural_type'] = type("it is a string")
        col_dict['name'] = output_label + "_text"
        col_dict['semantic_types'] = ('http://schema.org/Text', 'https://metadata.datadrivendiscovery.org/types/Attribute')
        croc_df.metadata = croc_df.metadata.update((metadata_base.ALL_ELEMENTS, 4), col_dict)
        # sixth column (_tokens)
        col_dict = dict(croc_df.metadata.query((metadata_base.ALL_ELEMENTS, 5)))
        col_dict['structural_type'] = type("it is a string")
        col_dict['name'] = output_label + "_tokens"
        col_dict['semantic_types'] = ('http://schema.org/Text', 'https://metadata.datadrivendiscovery.org/types/Attribute')
        croc_df.metadata = croc_df.metadata.update((metadata_base.ALL_ELEMENTS, 5), col_dict)

        return CallResult(croc_df)


if __name__ == '__main__':
    volumes = {} # d3m large primitive architecture dictionary of large files
    volumes["croc_weights"]='/home/croc_weights' # location of extracted required files archive
    client = croc(hyperparams={'target_columns': ['filename'],
                               'output_labels': ['filename']}, volumes=volumes)
    input_dataset = container.Dataset.load("file:///home/datasets/seed_datasets_current/LL1_penn_fudan_pedestrian/TRAIN/dataset_TRAIN/datasetDoc.json")
    ds2df_client = DatasetToDataFrame.DatasetToDataFramePrimitive(hyperparams = {"dataframe_resource":"0"})
    df = d3m_DataFrame(ds2df_client.produce(inputs = input_dataset).value) 
    result = client.produce(inputs=df)
    print(result.value)
