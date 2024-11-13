import os
import sys
import operator
from polo import make_default_logger, tf
import time

logger = make_default_logger(__name__)





def load_image(image_path):
    with open(str(image_path), 'rb') as f:
        image_bytes = f.read()
    return image_bytes


def process_model_output(model_output):
    # Extract classes and scores from the model output
    classes = model_output['classes'][0]
    scores = model_output['scores'][0]

    # Create a dictionary mapping classes to probabilities
    class_probabilities = {class_name.decode('utf-8'): float(score) 
                           for class_name, score in zip(classes, scores)}

    # Find the class with the highest probability
    highest_probability_class = max(class_probabilities, key=class_probabilities.get)

    return highest_probability_class, class_probabilities



def run_model(loaded_model, session, image_path):
    image_bytes = load_image(image_path)

    meta_graph = loaded_model        
    # Get the 'serving_default' signature
    signature = meta_graph.signature_def['serving_default']
    
    # Get input and output tensors
    input_tensor = session.graph.get_tensor_by_name(signature.inputs['image_bytes'].name)
    output_tensors = {name: session.graph.get_tensor_by_name(tensor_info.name) 
                      for name, tensor_info in signature.outputs.items()}
    
    # Run inference
    feed_dict = {input_tensor: [image_bytes]}
    results = session.run(output_tensors, feed_dict=feed_dict)
    
    processed_results = process_model_output(results)
    
    return processed_results


# https://github.com/tensorflow/models/blob/master/research/marco/Automated_Marco.py
# def run_model(tf_predictor, image_path):
#     '''Given a tensorflow predictor (the MARCO model) and the path to an image, 
#     runs the model on that image. Returns a tuple where the first item is the
#     classification with greatest confidence and the second is a dictionary where
#     keys are image classification types and values are model confidence for that
#     classification. The image classifications of this dictionary are used
#     universally throughout the program and are accessible through the
#     :const:`IMAGE_CLASSIFICATIONS` constant.

#     :param tf_predictor: Loaded MARCO model
#     :type tf_predictor: tensorflow model
#     :param image_path: Path to the image to be classified by the model
#     :type image_path: str
#     :return: tuple
#     :rtype: tuple
#     '''
#     try:
#         def load_image():
#             with open(image_path, 'rb') as f:
#                 return {'image_bytes': [f.read()]}

#         sys.stdout = open(os.devnull, "w")
#         data = load_image()
#         results = tf_predictor(data)
#         #sys.stdout = sys.__stdout__
#         # suppress output

#         vals = results['scores'][0]
#         classes = results['classes'][0]
#         dictionary = dict(zip(classes, vals))
#         prediction = max(dictionary.items(), key=operator.itemgetter(1))[
#             0]  # gets max confidence prediction
#         new_dict = {}
#         for key in dictionary:
#             if type(key) == bytes:
#                 new_dict[key.decode('utf-8')] = dictionary[key]
#             else:
#                 new_dict[key] = dictionary
        

#         # round values in the new dict
#         new_dict = {key: round(val, 3) for key, val in new_dict.items()}

#         return prediction.decode('utf-8'), new_dict
#     except Exception as e:
#         raise e
#         logger.error('Caught exception {}'.format(e))
#         return None, {}


