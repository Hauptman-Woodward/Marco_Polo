#!/usr/bin/env python3
import os
import sys
import operator




# want to edit this function so marco does one image at a time
# and then moves so it is easier to update the loading bar

def get_images(images_path):
    '''
    returns a list of all file paths contained in the given directory.
    '''
    allowed_file_types = ['.png', '.jpeg', '.jpg', '.bmp', '.gif']
    files = [os.path.join(images_path,f) for f in os.listdir(images_path)]
    for file in files:
        if os.path.splitext(file)[-1] not in allowed_file_types:
            files.remove(file)
    return files


def load_image(file_path):
    f = open(file_path, 'rb')
    return {'image_bytes':[f.read()]}


def load_images(file_list):
    '''
    Loads images from a list of paths (should be from get_images) in format
    that can be read by the tensorflow package
    '''
    for i in file_list:
        files = open(i,'rb')
        yield {"image_bytes":[files.read()]},i


def classify_image(tf_predictor, image_path):
    '''
    Given a tensorflow predictor (the MARCO model) and the path to an image, 
    runs the model on that image. Returns a tuple where the first item is the
    classification with greatest confidence and the second is a dictionary where
    keys are image classification types and values are model confidence for that
    classification.

    param: tf_predictor: Tensorflow predictor object. Should be MARCO model \
        in ready to roll form.
    param: image_path: String. Path to an image that will be classified.
    '''
    sys.stdout = open(os.devnull, "w")
    results = tf_predictor(load_image(image_path))
    sys.stdout = sys.__stdout__

    vals = results['scores'][0]
    classes = results['classes'][0]
    dictionary = dict(zip(classes, vals))
    prediction = max(dictionary.items(), key=operator.itemgetter(1))[0]  # gets max confidence prediction
    new_dict = {}
    for key in dictionary:
        if type(key) == bytes:
            new_dict[key.decode('utf-8')] = dictionary[key]
        else:
            new_dict[key] = dictionary
        

    return prediction.decode('utf-8'), new_dict
