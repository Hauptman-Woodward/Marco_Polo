from datetime import datetime
from pathlib import Path
import os

from polo import *
from polo.crystallography.image import Image
# from polo.utils.io_utils import list_dir_abs, parse_HWI_filename_meta
from polo.utils.io_utils import if_dir_not_exists_make, list_dir_abs, parse_HWI_filename_meta
logger = make_default_logger(__name__)


class Run():

    AllOWED_PLOTS = ['Classification Counts',
                     'MARCO Accuracy', 'Classification Progress']

    def __init__(self, image_dir, run_name, image_spectrum=None, 
                 images=[], **kwargs):

        self.image_dir = str(image_dir)
        self.run_name = run_name
        self.image_spectrum = image_spectrum
        self.images = images
        self.__dict__.update(kwargs)

    def __getitem__(self, n):
        try:
            return self.images[n]
        except IndexError as e:
            return e

    def __len__(self):
        '''Returns the number of non null Images'''
        return sum([1 for i in self.images if i != None])

    def get_tooltip(self):
        return 'Run Name: {}\nSpectrum: {}\nDate: {}\nNum Images: {}'.format(
            self.run_name, self.image_spectrum, str(self.date), len(self)
        )

    def encode_images_to_base64(self):
        '''Helper method that encodes all images in the Run to
        base64.
        '''
        for image in self.images:
            if image: image.encode_base64()

    def add_images_from_dir(self):
        '''Adds the contents of a directory to `images` attribute.
        '''
        logger.info('Adding images to {} from {}'.format(self, self.image_dir))
        self.images = []
        for image_path in list_dir_abs(self.image_dir, allowed=True):
            self.images.append(
                Image(path=str(image_path), spectrum=self.image_spectrum,
                      date=self.date)
            )

    def unload_all_pixmaps(self, s=None, e=None, r=False):  # reduce memory usage

        if isinstance(s, int) and isinstance(e, int):
            images = self.images[s:e]
        else:
            images = self.images
        for image in images:
            if r:
                image.recursive_delete_pixmap_data()
            else:
                image.delete_pixmap_data()

    def get_images_by_classification(self, human=True):
        '''
        Create a dictionary of image classifcations. Keys are
        each type of classification and values are list of
        images with classification of the key. The human
        boolean determines what classifier should be used to
        determine the image type. Human = True sets the human
        as the classifier and False sets MARCO as the classifier.
        '''
        image_class_dict = {}
        for image in self.images:
            if image:
                c = None
                if human:
                    if image.human_class:
                        c = image.human_class
                else:
                    if image.machine_class:
                        c = image.machine_class
                if c in image_class_dict:
                    image_class_dict[c].append(image)
                else:
                    image_class_dict[c] = [image]
        return image_class_dict

    def get_image_table_data(self, image, attributes):
        im_dict, row_dict = image.__dict__, {}
        for arg in attributes:
            if arg in im_dict:
                row_dict[arg] = im_dict[arg]
            else:
                row_dict[arg] = None
        return row_dict

    def image_filter_query(self, image_types, human, marco, favorite):
        images = [i for i in self.images if i and i.standard_filter(
            image_types, human, marco, favorite
        )]
        if not images:
            images.append(Image.no_image())
        return images

    def get_human_statistics(self):
        '''
        Returns stats that would be shown in the stats tab of the viewer.
        '''
        return NotImplementedError

    def get_cocktails(self):
        '''
        Returns list of list of cocktails assigned to this run
        '''
        return NotImplementedError

    def export_to_csv(self, output_dir):
        '''
        Exports run classifcation data to a csv table.
        '''
        return NotImplementedError

    def get_heap_map_data(self):
        '''
        Returns data that will be needed to render the heatmap
        view of results
        '''
        return NotImplementedError

    def get_current_hits(self):
        # hits are classified as images with human crystal designation
        return [image for image in self.images
                if image and image.human_class == 'Crystals']


class HWIRun(Run):

    AllOWED_PLOTS = ['Classification Counts',
                     'MARCO Accuracy', 'Classification Progress',
                     'Plate Heatmaps']
    # HWI still store images in list but in order of well number
    # index = well -1
    def __init__(self, cocktail_menu, plate_id=None, num_wells=1536,
                alt_spectrum=None, next_run=None, previous_run=None, **kwargs):
        self.cocktail_menu = cocktail_menu
        self.plate_id = plate_id
        self.num_wells = num_wells
        self.next_run = next_run
        self.previous_run = previous_run
        self.alt_spectrum = alt_spectrum
        super(HWIRun, self).__init__(**kwargs)

    def get_tooltip(self):
        if 'plateName' in self.__dict__:
            platename = self.__dict__['plateName']
        else:
            platename = self.plate_id

        return super().get_tooltip() + '\nCocktail Version: {}\nPlate ID: {}'.format(
            os.path.basename(str(self.cocktail_menu.path)), str(platename)
        )

    def link_to_decendent(self, other_run):
        if type(other_run) == HWIRun:
            logger.info('Linking {} to {}'.format(self, other_run))
            for current_image, dec_image in zip(self.images, other_run.images):
                if current_image:
                    current_image.next_image = dec_image
                    # if not current_image.previous_image:
                    #     current_image.previous_image = current_image
                if dec_image:
                    dec_image.previous_image = current_image
                    # if not dec_image.next_image:
                    #     dec_image.next_image = dec_image
            self.next_run = other_run
            other_run.previous_run = self

    def link_to_alt_spectrum(self, other_run):
        # only a one way link from this run to the other run
        # outside funcion is required to cirle the list
        if isinstance(other_run, (HWIRun, Run)):
            for current_image, alt_image in zip(self.images, other_run.images):
                current_image.alt_image = alt_image
            self.alt_spectrum = other_run

        # only do a one way link here currently

    def sort_current_images_by_cocktail(self):
        '''
        Sorts the current slideshow images by cocktail number. Allows the user
        to navigate by cocktail number and therefore similar chemical conditions
        opposed to as by well number which is proxy for physical location in
        the well. Oftentimes due to plate shape similar well numbers will be
        in different family of chemcial conditions.
        '''
        self.current_slide_show_images.sort(
            key=lambda x: self.images[x].get_cocktail_number())
        self.current_image = 0
    
    def get_linked_alt_runs(self):
        if isinstance(self.alt_spectrum, (Run, HWIRun)):    
            linked_runs = [self.alt_spectrum]
            start_run = self.alt_spectrum.alt_spectrum
            while isinstance(start_run, (Run, HWIRun)) and start_run.run_name != self.alt_spectrum.run_name:
                if start_run.image_spectrum != IMAGE_SPECS[0]:  # not visible
                    linked_runs.append(start_run)
                else:
                    linked_runs.append(False)  # marker for found visble run in chaing that need to be replaced
                start_run = start_run.alt_spectrum
            return linked_runs
        else:
            return []
    
    def insert_into_alt_spec_chain(self):
        linked_runs = self.get_linked_alt_runs()
        if linked_runs:
            if len(linked_runs) == 1:
                linked_runs[0].link_to_alt_spectrum(self)
            else:
                try:
                    break_link_index = linked_runs.index(False)
                    p, n = break_link_index - 1, break_link_index + 1
                    if n >= len(linked_runs): n = 0
                    linked_runs[p].link_to_alt_spectrum(self)
                    self.link_to_alt_spectrum(n)
                except ValueError:
                    linked_runs[-1].link_to_alt_spectrum(self)

    def add_images_from_dir(self):
        '''
        Populates the images attribute with a list of images read from the
        image_dir location. Currently is dependent on having a cocktail
        dictionary available. This is passed into the function and would
        normally come from the most recently used HWI file that is
        stored as a dictionary in the mainWindow object.
        '''
        self.images = [BLANK_IMAGE for i in range(0, self.num_wells)]
        assert os.path.exists(self.image_dir)

        for image_path in list_dir_abs(self.image_dir, allowed=True):
            # cast to string as read in as Path object
            image_path = str(image_path)
            plate_id, well_num, date, other = parse_HWI_filename_meta(
                image_path)
            self.images[well_num-1] = Image(path=image_path,
                                            well_number=well_num,
                                            date=date, plate_id=plate_id,
                                            cocktail=self.cocktail_menu.cocktails[well_num],
                                            spectrum=self.image_spectrum)
        logger.info('Added {} images from {} to {}'.format(
            len(self.images), self.image_dir, self
        ))
