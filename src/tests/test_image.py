# import unittest, os, random
# from datetime import datetime
# sask
# from Crystallography.image import Image
# from Crystallography.run import Run, HWIRun

# MACHINE_CLASSES = [b'Clear', b'Precipitate', b'Other', b'Crystal']
# TEST_IMAGE = 'tests/test_data/X0000156850011201907031159.jpg'
# TEST_IMAGE_DIR = 'tests/test_data/X000015685201907031114-jpg'

# unclassified_image = Image(image_path=TEST_IMAGE)


# class TestImage(unittest.TestCase):
    
#     unclassified_image = Image(image_path=TEST_IMAGE)
    
#     def test_classify_image(self):
#         self.unclassified_image.classify_image()
#         self.assertIn(unclassified_image.machine_class, MACHINE_CLASSES)



# class TestRun(unittest.TestCase):
    
#     def setUp(self):
        
#         self.test_run = Run(image_dir=TEST_IMAGE_DIR,
#                     run_name=os.path.basename(TEST_IMAGE_DIR),
#                     )
#         self.test_run_image = Run(image_dir=TEST_IMAGE_DIR,
#                     run_name=os.path.basename(TEST_IMAGE_DIR),
#                     )
#         self.test_run_image.add_images_from_image_dir()
    
#     def tearDown(self):
#         self.test_run.dispose()
    
    
#     def test_add_images_from_image_dir(self):
#         pass
        
#         for image in self.test_run_image.images:
#             self.assertIsInstance(type(image), Image)  # check all images are of type Image
            
    
#     def test_get_current_slideshow_images(self):
#         self.test_run_image.get_current_slideshow_images([], human=False,
#                                                          marco=False)
#         self.assertEqual(self.test_run_image.current_image, 0)
#         self.assertEqual(self.test_run_image.current_slide_show_images,
#                          [])  # later should have path to default image possibly
        
    
    
#     def test_change_current_image_classification(self):
#         self.test
#         new_classification = 'Crystal'  # something with byte strings might happen
#         # need to have slide show images to work
#         self.test_run.change_image_classificaion()

#     def test_next_image(self):
#         current_image = self.test_run.current_image
#         self.test_run.next_image()
#         self.assertEqual(current_image+1, self.test_run.current_image)
    
#     def test_previous_image(self):
#         current_image = self.test_run.current_image
#         self.test_run.previous_image
        
    
# class TestHWIRun(unittest.TestCase):
    
#     def setUp(self):
        
#         self.test_run_image = HWIRun(image_dir=TEST_IMAGE_DIR,
#                                      run_name=os.path.basename(TEST_IMAGE_DIR))
#         self.default_cocktails = 'tests/test_data/X000015685201907031114-jpg/compositelist000043.txt'
    
#     def tearDown(self):
#         self.test_run_image.dispose()
    
#     def test_wells_constant(self):
#         self.assertEqual(1536, self.test_run_image.NUM_WELLS)
    
#     def test_get_images_from_dir(self):
#         well_numbers = set([i for i in range(1, 1537)])
        
#         self.test_run_image.get_images_from_dir()
#         for image in self.test_run_image.images:
#             self.assertIsInstance(type(image), Image)  # check all images are of type Image
#             self.assertIn(image.well_number, well_numbers)
#             self.assertIsInstance(type(image.date), datetime)
#             self.assertIsNone(image.path)
        
#         self.assertIsNone(self.test_run_image.cocktail_path)  # make sure cocktails added
#         self.assertEqual(self.test_run_image.cocktail_path, self.default_cocktails)
      


# if __name__ == '__main__':
#     unittest.main()