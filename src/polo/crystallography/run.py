from datetime import datetime
from pathlib import Path
import os

from polo import *
from polo.crystallography.image import Image
# from polo.utils.io_utils import list_dir_abs, parse_HWI_filename_meta
from polo.utils.io_utils import if_dir_not_exists_make, list_dir_abs, parse_HWI_filename_meta

logger = make_default_logger(__name__)

DEFAULT_IMAGE = Image(path=str(DEFAULT_IMAGE_PATH))
BLANK_IMAGE = Image(path=str(BLANK_IMAGE))


class Run():
    '''
    Holds data relating to an individual screening run, or one plate of
    images.
    '''
    AllOWED_PLOTS = ['Classification Counts',
                     'MARCO Accuracy', 'Classification Progress']

    def __init__(self, image_dir, run_name, images=None,
                 save_file_path=None, log=None, date=None,
                 image_spectrum=None, next_run=None, previous_run=None,
                 alt_spectrum=None, journal={},
                 current_image=None, current_image_index=0, *args, **kwargs):
        '''
        :param image_dir: String. Path to directory containing images to \
            be classified.
        :param run_name: String. Unique name of this run.
        :param images: List. List of Image objects is images already exist \
            and need to be passed into a run (Unlikely).
        :param current_image: Int. Index in self.current_slide_show_images \
            where the image that should be currently rendered into the app \
            can be found.
        :param current_slide_show_images: List. List of indexes in self.images. \
            The Images at these indicies are the set of images that based \
            on current filters applied by the user, are \
            available for viewing. Works in tandem with the value stored \
            in self.current_image to create a chain of reference
            that recovers the actual image object stored in self.images. No
            image objects are ever stored in self.current_image or\
            self.current_slide_show_images.
        '''
        self.image_dir = str(image_dir)
        self.run_name = run_name
        self.images = images
        self.current_table_data = []
        self.next_run = None
        self.image_spectrum = image_spectrum
        self.save_file_path = save_file_path
        self.date = date
        self.next_run = next_run
        self.previous_run = previous_run
        self.alt_spectrum = alt_spectrum

    def __getitem__(self, n):
        try:
            return self.images[n]
        except IndexError as e:
            return e

    def __len__(self):
        '''Returns the number of non null Images'''
        return sum([1 for i in self.images if i != None])

    def encode_images_to_base64(self):
        for image in self.images:
            if image:
                image.encode_base64()

    def add_images_from_dir(self):
        '''
        Adds the contents of a directory to self.images

        TODO: Add validation for file types and content. Handle if user
              gives a directory where there are no images or edge cases like
              that.
        '''
        logger.info('Adding images to {} from {}'.format(self, self.image_dir))
        self.images = []
    

        for image_path in list_dir_abs(self.image_dir, allowed=True):
            self.images.append(
                Image(path=str(image_path), spectrum=self.image_spectrum,
                      date=self.date)
            )

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

    def get_table_data(self, image_types, human, marco):
        logger.info('Getting table data for {} with image types {}'.format(
            self, image_types
        ))
        headers = ['path', 'well_number', 'date',
                   'machine_class', 'human_class', 'spectrum']

        header_dict = {header: i for i, header in enumerate(headers)}
        images = self.image_filter_query(image_types, human, marco)
        table_data = {}
        row = 1
        for image_index in images:
            image = self.images[image_index]
            image_dict = self.get_image_table_data(image, headers)
            for header in image_dict:
                col = header_dict[header]
                table_data[(row, col)] = image_dict[header]
            row += 1

        for header in header_dict:
            # add header values to first row
            table_data[(0, header_dict[header])] = header

        self.current_table_data = table_data
        logger.info('Returned table with {} rows and {} columns'.format(
            row, len(headers)
        ))
        return row, len(headers)

    def get_current_table_data(self, image_types, human=True, marco=False):
        images = self.image_filter_query(image_types, human, marco)
        return self.get_table_data(images)

    def image_filter_query(self, image_types, human=False, marco=False):
        images = []
        for i, image in enumerate(self.images):
            filter_result = self.image_filter_engine(
                image, image_types, human, marco)
            if filter_result:
                images.append(filter_result)
        if images:
            return images
        else:
            return [DEFAULT_IMAGE]

    def image_filter_engine(self, image, image_types, human=False, marco=False):
        if not image_types:
            image_types == IMAGE_CLASSIFICATIONS
        if not human and not marco:
            if image.spectrum == 'Visible':
                human, marco = True, True
            else:
                return image
        if isinstance(image, Image):  # is an image
            if human and image.human_class:  # human classification precidence over marco
                if image.human_class in image_types:
                    return image
            if marco and image.machine_class:
                if image.machine_class in image_types:
                    return image
            # non visible spectrum needs no classificaion
            # IDEA if has a connected spectrum than image
            # filtering is done based on the images
            # in the visible spectrum and the well
            # numbers of this spectrum are returned

    def add_journal_entry(self, contents, title):
        entry_datetime = datetime.now()
        self.journal[str(entry_datetime)] = (title, contents)
        logger.info('Add entry with title {} to journal'.format(title))
        # jounal is doulbe dict first key is title and second is datetime
        # of when the entry was added

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
        return [image for image in self.images if image and image.human_class == 'Crystals']


class HWIRun(Run):

    AllOWED_PLOTS = ['Classification Counts',
                     'MARCO Accuracy', 'Classification Progress',
                     'Plate Heatmaps']
    # HWI still store images in list but in order of well number
    # index = well -1
    '''
    Child class of Run. Is used to represent runs from the HWI screening center
    as images will have additional metadata like well and cocktail information.
    Main difference is that HWIRuns will always contain 1536 images as that is
    the number of wells in a HWI crystallization plate. Each well uses a
    different chemcial cocktail which is described in the cocktail tsv file
    included in the directory of images provided by HWI in each run. 
    '''

    def __init__(self, image_dir, run_name, cocktail_dict=None,
                 images=[], plate_id=None, annotations=None,
                 save_file_path=None, num_wells=1536, image_spectrum=None, date=None,
                 next_run=None, previous_run=None, alt_spectrum=None,
                 number_grid_pages=None, current_grid_page=1, journal=None, current_image_index=0,
                 current_image=None, *args, **kwargs):
        '''
        param: cocktail_path: String. Path to tsv or csv file that contains \
            information on chemical cocktail composition and well asignments.
        param: plate_id: String. Unique key given to plate that images are \
            taken from. Should be parsable from the directory name.

        TODO: Add methods that check if image and run directory names are valid
        based on curreent HWI formating practices. If not throw somekind of
        error to the user and import as a Run object. Could also include some
        methods that try to infer correct image names based on surroning file
        names.
        '''
        super().__init__(image_dir, run_name, images=images,
                         annotations=annotations,
                         save_file_path=save_file_path, date=date,
                         image_spectrum=image_spectrum, next_run=next_run,
                         previous_run=previous_run, alt_spectrum=alt_spectrum,
                         number_grid_pages=number_grid_pages, current_grid_page=current_grid_page,
                         journal=journal, current_image=current_image,
                         current_image_index=current_image_index)

        self.cocktail_dict = cocktail_dict
        self.plate_id = plate_id
        self.num_wells = num_wells

    def link_to_predecessor(self, other_run):
        if type(other_run) == HWIRun:
            logger.info('Linking {} to {}'.format(self, other_run))
            for current_image, pred_image in zip(self.images, other_run.images):
                if current_image:
                    current_image.previous_image = pred_image
                if pred_image:
                    pred_image.next_image = current_image

    def link_to_decendent(self, other_run):
        if type(other_run) == HWIRun:
            logger.info('Linking {} to {}'.format(self, other_run))
            for current_image, dec_image in zip(self.images, other_run.images):
                if current_image:
                    current_image.next_image = dec_image
                    if not current_image.previous_image:
                        current_image.previous_image = current_image
                if dec_image:
                    dec_image.previous_image = current_image
                    if not dec_image.next_image:
                        dec_image.next_image = dec_image

            self.next_run = other_run
            other_run.previous_run = self

    def link_to_alt_spectrum(self, other_run):
        if isinstance(other_run, (HWIRun, Run)):
            for current_image, alt_image in zip(self.images, other_run.images):
                current_image.alt_image = alt_image
                alt_image.alt_image = current_image
                if self.image_spectrum == 'Visible':
                    alt_image.machine_class = current_image.machine_class
                    alt_image.human_class = current_image.human_class
                else:
                    current_image.machine_class = alt_image.machine_class
                    current_image.human_class = alt_image.human_class

                self.alt_spectrum = other_run
                other_run.alt_spectrum = self

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

    def link_to_alt_images(self, other_run):

        # establish if a visible spectrum is present in the linking
        # if so it gets preference for marco classifications
        # images in this run need to give classifications to other ru

        for current_image, alt_image in zip(self.images, other_run.images):
            current_image.alternative_image = alt_image
            alt_image.alternative_image = current_image
            if self.image_spectrum == 'Visible':
                alt_image.machine_class = current_image.machine_class
                alt_image.human_class = current_image.human_class
            else:
                current_image.machine_class = alt_image.machine_class
                current_image.human_class = alt_image.human_class

            self.alt_spectrum = other_run
            other_run.alt_spectrum = self

    def add_images_from_dir(self):
        '''
        Populates the images attribute with a list of images read from the
        image_dir location. Currently is dependent on having a cocktail
        dictionary available. This is passed into the function and would
        normally come from the most recently used HWI file that is
        stored as a dictionary in the mainWindow object.
        '''
        self.images = [BLANK_IMAGE for i in range(0, self.num_wells)]
        print(self.image_dir)
        assert os.path.exists(self.image_dir)

        for image_path in list_dir_abs(self.image_dir, allowed=True):
            # cast to string as read in as Path object
            image_path = str(image_path)
            plate_id, well_num, date, other = parse_HWI_filename_meta(
                image_path)
            print(type(well_num), 'well_number type')
            self.images[well_num-1] = Image(path=image_path,
                                            well_number=well_num,
                                            date=date, plate_id=plate_id,
                                            cocktail=self.cocktail_dict[well_num],
                                            spectrum=self.image_spectrum)
        logger.info('Added {} images from {} to {}'.format(
            len(self.images), self.image_dir, self
        ))
