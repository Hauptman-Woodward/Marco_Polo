import os
import sys
import operator
from polo import make_default_logger

logger = make_default_logger(__name__)

def run_model(tf_predictor, image_path):
    '''Given a tensorflow predictor (the MARCO model) and the path to an image, 
    runs the model on that image. Returns a tuple where the first item is the
    classification with greatest confidence and the second is a dictionary where
    keys are image classification types and values are model confidence for that
    classification. The image classifications of this dictionary are used
    universally throughout the program and are accessible through the
    :const:`IMAGE_CLASSIFICATIONS` constant.

    :param tf_predictor: Loaded MARCO model
    :type tf_predictor: tensorflow model
    :param image_path: Path to the image to be classified by the model
    :type image_path: str
    :return: tuple
    :rtype: tuple
    '''
    try:
        def load_image():
            with open(image_path, 'rb') as f:
                return {'image_bytes': [f.read()]}

        sys.stdout = open(os.devnull, "w")
        data = load_image()
        results = tf_predictor(data)
        sys.stdout = sys.__stdout__
        # suppress output

        vals = results['scores'][0]
        classes = results['classes'][0]
        dictionary = dict(zip(classes, vals))
        prediction = max(dictionary.items(), key=operator.itemgetter(1))[
            0]  # gets max confidence prediction
        new_dict = {}
        for key in dictionary:
            if type(key) == bytes:
                new_dict[key.decode('utf-8')] = dictionary[key]
            else:
                new_dict[key] = dictionary
        

        # round values in the new dict
        new_dict = {key: round(val, 3) for key, val in new_dict.items()}

        return prediction.decode('utf-8'), new_dict
    except Exception as e:
        logger.error('Caught exception {}'.format(e))
        return None, {}


