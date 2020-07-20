
import random

from PyQt5 import QtWidgets

import matplotlib
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from polo.plots.plot_utils import *
from polo.utils.dialog_utils import make_message_box

matplotlib.use('QT5Agg')


# Ensure using PyQt5 backend


# Matplotlib canvas class to create figure


class MplCanvas(Canvas):
    def __init__(self, parent=None, run=None, width=8, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.run = run
        Canvas.__init__(self, self.fig)
        self.setParent(parent)

        Canvas.setSizePolicy(
            self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        Canvas.updateGeometry(self)


# Matplotlib widget  methods do into this class

class StaticCanvas(MplCanvas):

    def compute_initial_figure(self):  # figure for debug and test
        self.meta_stats()

    def clear_axis(self):
        self.fig.clf()
    
    def peg_plot(self, run):
        # create image heat map of the plot or something like that
        # first need to collect all the PEGS and get their weight
        pass

    def plot_current_map_view(self, plate_rows, plate_cols, current_wells):
        self.clear_axis()
        self.fig.add_subplot(111)
        plate = np.zeros(plate_rows*plate_cols) # reshape(plate_rows, plate_cols)
        for i in range(len(plate)):
            if i in current_wells:
                plate[i] = 1
        plate = plate.reshape(plate_rows, plate_cols)
        axis = self.fig.get_axes()[0]
        axis.get_xaxis().set_visible(False)
        axis.get_yaxis().set_visible(False)
        im = axis.imshow(plate)

    def marco_accuracy(self, current_run):
        correctness = [0, 0]
        for image in current_run.images:
            if image:
                if image.human_class:  # only compare images actually classified
                    if image.human_class == image.machine_class:
                        correctness[0] += 1
                    else:
                        correctness[1] += 1
        return correctness

    def classification_progress(self, current_run):
        # need to know total classified and
        # human, machine machine is the total
        class_dict = {'Crystals': [0, 0], 'Precipitate': [0, 0],
                      'Clear': [0, 0], 'Other': [0, 0], None: [0, 0]}
        # two lists tuple for each bar
        for image in current_run.images:
            if image.machine_class in class_dict:  # could be None
                class_dict[image.machine_class][1] += 1
            if image.human_class in class_dict:
                class_dict[image.machine_class][0] += 1

        bar_values = [class_dict[x][0] for x in class_dict.keys(
        )], [class_dict[x][1] for x in class_dict.keys()], list(class_dict.keys())
        return bar_values

    def plot_classification_progress(self, current_run):
        try:
            self.clear_axis()

            ax = self.fig.add_subplot(111)
            classified_values, unclass_values, labels = self.classification_progress(
                current_run)
            ax.bar(labels, unclass_values, color='grey')
            ax.bar(labels, classified_values, color='lightblue')
            ax.set_title('Classification Progress By MARCO Designation')
            self.draw()
        except Exception as e:
            m = make_message_box(
                parent=self,
                message='Could not complete plot drawing. Failed with error {}'.format(e)
            )
            m.exec_()

        def plot_meta_stats(self, current_run):
            self.clear_axis()
            # add all subplots here
            self.fig.add_subplot(111)
            # make classification progress plot
            # make accuracy plot
            labels = ['Correct', 'Incorrect']
            marco_accuracy = self.marco_accuracy(current_run)
            self.fig.get_axes()[0].bar(
                labels, marco_accuracy, color='lightblue')
            self.fig.get_axes()[0].set_title(
                'MARCO Classification Accuracy')
            self.draw()
        


    def plot_plate_heatmaps(self, current_run):

        self.clear_axis()

        self.fig.add_subplot(221)  # 4 by 1 plot organization
        self.fig.add_subplot(222)
        self.fig.add_subplot(223)
        self.fig.add_subplot(224)

        # DANGER plot is dependent on haveing a full 1536 well plate
        # should adjust for the given number of plates 

        # preplot checks to make sure it is good to graph
        # should include that all images have marco classifications
        # and that there are 1536 images 


        try:
            for k, image_type in enumerate(['Crystals', 'Precipitate', 'Clear', 'Other']):
                data = []
                for i, image in enumerate(current_run.images):
                    if image and image.prediction_dict:
                        confidence = image.prediction_dict[image_type]
                        if image.well_number:
                            data.append(confidence)
                    else:
                        data.append(0)
                data = np.reshape(data, (48, 32))  # DANGER Assumes 1536 images
                data = data.astype(np.float)
                im = self.fig.get_axes()[k].imshow(data, cmap='hot')
                self.fig.get_axes()[k].set_title(
                    '{} Confidence Map'.format(image_type))

            cb_ax = self.fig.add_axes([0.83, 0.1, 0.02, 0.8])
            cbar = self.fig.colorbar(im, cax=cb_ax)

            # store figure so can easily
            # check if want to redraw it

            self.draw()
        except Exception:  # lazy error handling for now see code above try block
            m = make_message_box(
                parent=self,
                message='Could not complete plot drawing. Failed with error {}'.format(e)
            )
            m.exec_()

    def plot_existing_plot(self, saved_figure):
        self.clear_axis()
        self.fig = saved_figure
        self.draw()

    def plot_violins(self, current_run, x_var, y_var, title, x_lab, y_lab):
        self.clear_axis()
        self.fig.add_axes(111)

        pass

    def plot_bars(self, current_run):
        self.clear_axis()
        ax = self.fig.add_subplot(121)
        ax.set_title('Human Classifications')
        ax_2 = self.fig.add_subplot(122)
        ax_2.set_title('MARCO Classifications')

        human_dict = {str(key): len(current_run.get_images_by_classification(human=True)[
            key]) for key in current_run.get_images_by_classification(human=True)}
        if 'None' in human_dict:
            human_dict.pop('None')
        machine_dict = {str(key): len(current_run.get_images_by_classification(human=False)[
            key]) for key in current_run.get_images_by_classification(human=False)}

        for axis, data_dict in zip([ax, ax_2], [human_dict, machine_dict]):
            labels = sorted(list(data_dict.keys()))
            heights = [data_dict[label] for label in labels]
            axis.bar(labels, heights)

        self.draw()

    def plot_cocktail_map(self, current_run):
        # currently only supports pH as quantative axis
        # TODO other types including cat to cat plot
        pass

    def plot_cocktail_additives_map(self, current_run):
        self.clear_axis()

        additives, pH = [], []
        for image in current_run.images:
            if image:
                if image.human_class == 'Crystals':
                    if image.cocktail:
                        try:
                            ph = float(image.cocktail.pH)
                            for additive in image.cocktail.solutions:
                                pH.append(ph)
                                additives.append(additive.chemical_additive)
                        except ValueError:
                            continue

        # print(pH)
        pH = float_integerizer(pH)

        # get the pH and additive data

        steps = get_pH_steps(pH)

        pixel_data, y_labs = make_labeled_heatmap(steps, pH, additives)
        x_labs = format_pH_steps_as_labels(steps)


        ax = self.fig.add_subplot(111)
        ax.set_xticks(list(range(len(steps))))
        ax.set_xticklabels(x_labs)
        ax.set_yticks(list(range(len(y_labs))))
        ax.set_yticklabels(y_labs)

        ax.imshow(pixel_data, interpolation='nearest')

        self.draw()

    def plot_additive_map(self, current_run):

        # TODO Make this not ugly af and trim to lower triangle
        # add spot for if cocktail only has one additive
        crystal_images, unique_additives = [], set([])
        for image in current_run.images:
            if image and image.human_class == 'Crystals':
                crystal_images.append(image)
        
        for xtal in crystal_images:
            for additive in xtal.cocktail.solutions:
                unique_additives.add(additive.chemical_additive)
        
        num_additives = len(unique_additives)

        unique_additives = list(unique_additives)  # this is final ordering

        additives_index_dict = {additive: n for n, additive in enumerate(unique_additives)}

        additive_dict = {additive: np.zeros(num_additives) for additive in unique_additives}
                # seems like there is issue with being cast to strings here
        for xtal in crystal_images:
            for additive in xtal.cocktail.solutions:
                #additive_dict[additive][additives_index_dict[]]
                for additive_pair in xtal.cocktail.solutions:  # double dipping here
                    additive_dict[additive.chemical_additive][additives_index_dict[additive_pair.chemical_additive]] += 1
        
        image_array = [additive_dict[a] for a in unique_additives]


        self.clear_axis()
        ax = self.fig.add_subplot(111)
        ax.imshow(image_array)
        self.draw


        # now need to wrap everything up together and order by the sorted
        # unique additive list

class MplWidget(QtWidgets.QWidget):
    '''
    QWidget for displaying matplotlib plots. The mainWindow widget "matplot"
    should be reasigned to an object of this type when intializing and then
    whenever the current plot needs to be cleared and a new one drawn. Holds
    all methods for drawing supported plots in the app. 
    '''

    def __init__(self, parent=None, width=8, height=5, dpi=100, toolbar=True):
        QtWidgets.QWidget.__init__(self, parent)   # Inherit from QWidget
        # Create canvas object
        self.canvas = MplCanvas(width=width, height=height, dpi=dpi)
        self.vbl = QtWidgets.QVBoxLayout()         # Set box for plotting
        if toolbar:
            self.toolbar = NavigationToolbar(self.canvas, parent)
            self.vbl.addWidget(self.toolbar)
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)

    # might want to move these data getting functions to run objects

    def plot_plate_heatmaps(self, current_run, width, height, dpi=100):

        self.resize_canvas(width, height, dpi)

        self.fig.add_subplot(141)  # 4 by 1 plot organization
        self.fig.add_subplot(142)
        self.fig.add_subplot(143)
        self.fig.add_subplot(144)

        for k, image_type in enumerate(['Crystals', 'Precipitate', 'Clear', 'Other']):
            data = []
            for i, image in enumerate(current_run.images):
                if image:
                    confidence = image.prediction_dict[image_type]
                    if image.well_number:
                        data.append(confidence)
                else:
                    data.append(0)
            data = np.reshape(data, (48, 32))
            self.fig.get_axes()[k].imshow(data)

    def test_plot(self):
        ydata = [random.randint(0, 10)]
        self.fig.add_subplot(111)
        self.fig.get_axes()[0].plot(ydata, ydata)
        self.canvas.draw()

    def marco_accuracy(self, current_run):
        correctness = [0, 0]
        for image in current_run.images:
            if image:
                if image.human_class:  # only compare images actually classified
                    if image.human_class == image.machine_class:
                        correctness[0] += 1
                    else:
                        correctness[1] += 1
        return correctness

    def classification_types(self, current_run):
        # side by side bar plot showing number of human classified images
        # and machine classified images
        for image in current_run.images:
            pass

    def marco_preformance(self, current_run):
        # classified correctly, incorrectly, total images
        correctness = [0, 0, 0]
        for image in current_run.images:
            if image.human_class == image.machine_class:
                correctness[0] += 1
            else:
                correctness[1] += 1
        correctness[-1] = len(current_run)

        return correctness

    def meta_stats(self, current_run):

        # add all subplots here
        self.fig.add_subplot(221)
        self.fig.add_subplot(222)
        self.fig.add_subplot(223)
        self.fig.add_subplot(224)

        # make classification progress plot
        classified_values, unclass_values, labels = self.classification_progress(
            current_run)
        self.fig.get_axes()[0].bar(labels, unclass_values, color='grey')
        self.fig.get_axes()[0].bar(
            labels, classified_values, color='lightblue')
        self.fig.get_axes()[0].set_title(
            'Classification Progress By MARCO Designation')

        # make accuracy plot
        labels = ['Correct', 'Incorrect']
        marco_accuracy = self.marco_accuracy(current_run)
        self.fig.get_axes()[1].bar(
            labels, marco_accuracy, color='lightblue')
        self.fig.get_axes()[1].set_title(
            'MARCO Classification Accuracy')

    def single_image_confidence(self, image):
        '''
        Makes a plot of MARCO confidence values for one image.
        '''
        if image and image.prediction_dict:  # protect from empty dict and images
            self.fig.add_subplot(1, 1, 1)
            image_class, confidence = [], []
            for each_image_class in image.prediction_dict:
                image_class.append(each_image_class)
                confidence.append(image.prediction_dict[each_image_class])

            self.fig.get_axes()[0].bar(image_class, confidence)

    # get two lists that connected by index of additive name and pH value for cocktail it is in

    def get_solution_ph_data(self, run):
        solutions, pH_values = [], []
        for image in run.images:
            for solution in image.cocktail.solutions:
                solutions.append(solution.chemcial_additive)
                pH_values.append(image.cocktail.pH)
        return solutions, pH_values

    def two_d_hist(self, current_hits, y_var='pH'):

        # need to think about what is actually being plotted
        # get a collection of cocktails that are in the hits
        # from that collection have many solutions but each cocktail
        # has only one pH so if want to compare pH need to tie that pH to
        # the solution in some way

        # want to compare a additive to a numerical propery in this plot
        # which could be concentration or pH start with pH becuase
        # dont need to worry about units stuff then
        # assume x will be

        self.fig.add_subplot(111)

        self.fig.get_axes()[0].tick_params(
            axis='x', which='major', labelsize=8)

        cocktails = [image.cocktail for image in current_hits]
        extended_solutions = []
        for each_cocktail in cocktails:
            for each_solution in each_cocktail.solutions:
                extended_solutions.append((each_solution,
                                           each_cocktail.pH,
                                           len(each_cocktail.solutions)))
        extended_solutions_set = list(
            set(ext_sol[0].chemical_additive for ext_sol in extended_solutions))

        # how to map a solution to a number

        additives_dict = {additive: i+1 for i,
                          additive in enumerate(extended_solutions_set)}
        rev_additives_dict = {v: k for k, v in additives_dict.items()}

        x_axis, y_axis = [], []
        for each_solution in extended_solutions:
            x_axis.append(additives_dict[each_solution[0].chemical_additive])
            if y_var == 'pH':
                # store pH at second index
                y_axis.append(float(each_solution[1]))
            elif y_var == 'concentration':
                pass  # come back since need to deal with units
            elif y_var == 'num_solutions':
                y_axis.append(each_solution[2])

        x_ticks = list(range(1, len(additives_dict)+1))
        x_labs = [rev_additives_dict[x] for x in x_ticks]

        self.fig.get_axes()[0].set_xticks(x_ticks)
        self.fig.get_axes()[0].set_xticklabels(x_labs,
                                               rotation='vertical')

        # ploy data and add color bar
        hist = self.fig.get_axes()[0].hist2d(x_axis, y_axis)
        self.fig.colorbar(hist[3])

        # set main and axis titles
        title = 'Chemcial Additive vs. {} for\nCrystal Producing Cocktails'.format(
            y_var)
        y_axis_title, x_axis_title = str(y_var), 'Cheicmal Additive'

        self.fig.get_axes()[0].set_title(title)
        self.fig.get_axes()[0].set_ylabel(y_axis_title)

    def check_categorical_axis(self, axis_data):
        if all(isinstance(i, str) for i in axis_data):
            return True
        else:
            return False

    def convert_cat_to_num(self, axis_data):
        unique_cats = list(set(axis_data))
        cat_dict = {i+1: cat for i, cat in enumerate(unique_cats)}
        return cat_dict, [cat_dict[cat] for cat in axis_data]
        # return the dictionary that tells you what number is what cat
        # and the axis_data converted to numberical using the dict

        title = '{} vs. {} in Crystal Producing Cocktails'.format(x_var, y_var)
        self.fig.get_axes()[0].hist2d(x_axis, y_axis)
        self.fig.get_axes()[0].set_title(title)
