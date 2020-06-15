import numpy as np


def float_integerizer(nums, n=2, rounder=True):
    # rounds floats to 1 decimal place and multplies by
    # ten to convert to ints
    nums = [int(round(n, 1))*10 for n in nums]
    if rounder:
        for i, _ in enumerate(nums):
            if nums[i] % n != 0:
                nums[i] = nums[i]-1
    return nums


def get_pH_steps(rounded_nums, step=2):
    return np.arange(min(rounded_nums), max(rounded_nums)+step, step)
    # return pH increments for graph these are the ticks


def format_pH_steps_as_labels(steps, scaler=10):
    labels = []
    for i, s in enumerate(steps):
        if i % 4 == 0:
            labels.append(str(s/scaler))
        else:
            labels.append('')
    return labels


# cats are always image types currently
def get_classication_boxplot_data(run, human=True):
    # human == true means use human classication for image
    data_dict = run.get_images_by_classification(human=human)
    return {c: len(data_dict[c]) for c in data_dict}


def get_violin_data(run, y_axis, human=True):
    data_dict = {}
    for image in run.images:
        if image:
            pass


def make_labeled_heatmap(steps, rounded_nums, cats):
    '''
    Creates a list of list representing the pixels of a heatmap from categorical x numerical
    data.

    :param steps: List. "Ticks" for the numerical data axis. See get_pH_steps or get_concentration_steps.
    :param rounded_nums: List. Processed numerical axis data. Each datapoint should be an integer \
        scaled from a float. Each point corresponds to a value for the cats list for each index.
    :param cats: List. Categorical data axis. The value for each datapoint is determined by the \
        rounded_nums list. The string at index 10 of cats correpsonds to the int stored at index \
        10 of rounded_nums
    '''
    unique_cats = set(cats)

    image_dict = {c: np.zeros(shape=len(steps)) for c in cats}
    index_dict = {s: i for i, s in enumerate(steps)}

    # cats are categorical data nums are values coresponding to each instance of data point
    for c, r in zip(cats, rounded_nums):
        image_dict[c][index_dict[r]] += 1

    # need to know order so can assign correct lable to correct tick
    y_labs = list(unique_cats)

    return [list(image_dict[cat]) for cat in y_labs], y_labs
