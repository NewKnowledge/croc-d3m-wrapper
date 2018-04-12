# Character Recognition and Object Classification (CROC) D3M Wrapper

CROC takes a local image or URL and performs object classification and optical character recognition. It produces a set of *N* object classification predictions with a pre-trained Keras model (default: imagenet) and performs character recognition with the `tesseract` library. All code is written in Python 3.5 and must be run in 3.5 or greater.

## Install

pip3 install git+https://github.com/NewKnowledge/croc-d3m-wrapper

## Input

`croc()` takes an image path---either a local path or a URL.

## Output

`croc()` returns a dict with the keys `objects` and `chars`. 
- `objects` is a pandas dataframe with columns `id`, `label` and `confidence`
- `chars` is a dict with the keys `tokens` and `text`
	-`tokens` is a list of all unique, English words detected 
	-`text` is a list of the raw character output with some cleaning