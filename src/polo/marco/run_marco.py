import os
import sys
import operator

def classify_image(tf_predictor, image_path):
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



    sys.stdout = open(os.devnull, "w")
    results = tf_predictor(load_image(image_path))
    sys.stdout = sys.__stdout__
    # suppress output


    def load_image(file_path):
        f = open(file_path, 'rb')
        return {'image_bytes': [f.read()]}

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

    return prediction.decode('utf-8'), new_dict
