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

    def __init__(self, image_dir, run_name, image_spectrum=None, date=None, 
                 images=[], **kwargs):
        '''Run objects represent one particular imaging run of a sample. They
        store `Image` objects that hold the actual imaging data as well as
        metadata associated with the imaging run and the sample.

        :param image_dir: Directory that contains the screening images
        :type image_dir: str of Path
        :param run_name: Name of this run. Should be unique as it is used to
        uniquely identify each Run instance
        :type run_name: str
        :param image_spectrum: Imaging technology used to capture the images in this run, defaults to None
        :type image_spectrum: str, optional
        :param date: Date the images in this Run were taken, defaults to None
        :type date: datetime, optional
        :param images: List of all `Image` instances in this run, defaults to []
        :type images: list, optional
        '''
        self.image_dir = str(image_dir)
        self.run_name = run_name
        self.image_spectrum = image_spectrum
        self.images = images
        self.date = date
        self.__dict__.update(kwargs)

    def __getitem__(self, n):
        try:
            return self.images[n]
        except IndexError as e:
            return e

    def __len__(self):
        '''Returns the number of non null Images'''
        if isinstance(self.images, list):
            return len(self.images)
        else:
            return 0
    
    def __hash__(self):
        return hash(str(self.run_name) + str(self.image_dir))

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
        self.images = []
        for image_path in list_dir_abs(self.image_dir, allowed=True):
            new_image = Image(path=str(image_path), spectrum=self.image_spectrum,
                              date=self.date)
            if isinstance(new_image, Image):
                self.images.append(new_image)
            

    def unload_all_pixmaps(self, start=None, end=None, a=False):  # reduce memory usage
        '''Delete the pixmap data of all Image instances stored in the
        `images` attribute. Should be used to free up memory after the run
        is no longer being viewed by the user.

        :param start: Start index for range of images to unload, defaults to None
        :type start: int, optional
        :param end: End index for range of images to unload, defaults to None
        :type end: int, optional
        :param a: Flag to unload pixmap data for all images and images they are linked to, defaults to False
        :type all: bool, optional
        '''

        if isinstance(start, int) and isinstance(end, int):
            images = self.images[start:end]
        else:
            images = self.images
        for image in images:
            if a:
                image.delete_all_pixmap_data()
            else:
                image.delete_pixmap_data()

    def get_images_by_classification(self, human=True):
        '''Create a dictionary of image classificationss. Keys are
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

    def image_filter_query(self, image_types, human, marco, favorite):
        '''General use method for returning Images based on a set of
        filters. Used whereever a user is allowed to narrow the set
        of images available for view.

        :param image_types: Returned images must have a classification that is included in this variable
        :type image_types: list or set
        :param human: Qualify the classification type with a human classifier. 
        :type human: bool
        :param marco: Qualify the classification type with a MARCO classifier.
        :type marco: bool
        :param favorite: Returned images must be marked as `favorite` if set to True
        :type favorite: bool
        :return: Images that meet the specified requirements specified in the above arguments.
        :rtype: list
        '''
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
        Exports run classification data to a csv table.
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
        '''The same as :func:`~polo.crystallography.Run.get_tooltip`.
        '''
        if 'plateName' in self.__dict__:
            platename = self.__dict__['plateName']
        else:
            platename = self.plate_id

        return super().get_tooltip() + '\nCocktail Version: {}\nPlate ID: {}'.format(
            os.path.basename(str(self.cocktail_menu.path)), str(platename)
        )

    def link_to_next_date(self, other_run):
        '''Link this `Run` to another `Run` instance that is of the same
        sample but photographed at a later date. This creates a
        bi-directional linked list structure between the two runs.
        This `Run` instance will point to `other_run` through the `next_run`
        attribute and `other_run` will point back to this `Run` through
        the `previous_run` attribute. This method does not attempt to recognize
        which run was imaged first so this should be determined before calling,
        likely by sorting a list of Run instances by their `date` attribute.

        Example:

        .. code-block:: python

            # Starting with a collection of Run objects in a list
            runs = [run_b, run_a, run_d, run_c]
            # sort them by date
            runs = sorted(runs, lambda r: r.date)
            # link them together by date
            [r[i].link_to_next_date(r[i+1]) for i in range(len(runs)-2)]
        
        This would create a linked list with a structure link the representation
        below.

        .. code-block:: text

            run_a <-> run_b <-> run_c <-> run_d


        :param other_run: HWIRun instance representing the next imaging run
        :type other_run: HWIRun
        '''

        if type(other_run) == HWIRun:
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
        '''Similar to :func:`~polo.crystallography.HWIRun.link_to_next_date`
        except instead of creating a linked list through the `next_run` and
        `previous_run` attributes this method does so through the `alt_spectrum`
        attribute. The linked list created is mono-directional so if a
        series of runs are being linked the last run should be linked to the
        first run to circularize the linked list.

        :param other_run: Run to link to this Run by spectrum 
        :type other_run: HWIRun
        '''
        
        if isinstance(other_run, (HWIRun, Run)):
            for current_image, alt_image in zip(self.images, other_run.images):
                current_image.alt_image = alt_image
            self.alt_spectrum = other_run
    
    def get_linked_alt_runs(self):
        '''Return all runs that this run is linked to by spectrum. See
        :func:`~polo.crystallography.HWIRun.link_to_alt_spectrum`

        :return: List of runs linked to this run by spectrum
        :rtype: list
        '''
        if isinstance(self.alt_spectrum, (Run, HWIRun)):    
            linked_runs = [self.alt_spectrum]
            start_run = self.alt_spectrum.alt_spectrum
            while isinstance(start_run, (Run, HWIRun)) and start_run.run_name != self.alt_spectrum.run_name:
                if start_run.image_spectrum != IMAGE_SPECS[0]:  # not visible
                    linked_runs.append(start_run)
                else:
                    linked_runs.append(False)
                start_run = start_run.alt_spectrum
            return linked_runs
        else:
            return []
    
    def insert_into_alt_spec_chain(self):
        '''When runs are first loaded into Polo they are automatically linked together.
        Normally, runs that are linked by date should all be visible spectrum images and
        runs linked by spectrum should all be non-visible spectrum images. The visible
        spectrum run will then point to one non-visible spectrum run via their
        `alt_spectrum` attribute. This means that one could navigate from a visible
        spectrum run to all alt spectrum runs but not get back to the visible spectrum
        run. Therefore, before a run is set to be viewed by the user this method
        temporary inserts the run it is called on into the alt spectrum 
        circular linked list. 
        Also see :func:`~polo.crystallography.HWIRun.link_to_alt_spectrum`.
        '''
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
        '''Populates the `images` attribute with a list of `Images` instances
        read from the `image_dir` attribute filepath. Currently is 
        dependent on having a cocktail menu available.
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