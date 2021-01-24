
class Menu():

    def __init__(self, filepath, cocktail_type):
        self.filepath
        self.cocktail_type
    
# need a menu and something else to go with things well
# lets say I want to make my images work with this program
# what would I need to do
# these have some associatedted cocktail data that I want to use

class Menu():
    pass

class Cocktail():
    pass

class Image():
    pass

# What are the variable types of input?
# Images (way they are stored and all that)
# Cocktail data associated to images
# Would be great if you could subclass these and have a way to get your data
# into the program
# Other classes to import the data read it it is too messy
# Lets assume there are images in one directory how to read that into a
# specific run 
# Each run should be created from a specific directry and each run object should
# be able to do that. Problems come when you add the graphical interface
# and need to deal with threading and that kind of thing.


class Run():

    def __init__(self, dir_path, images=[]):
        self.dir_path = dir_path
        self.images = images
    
    def read_images_from_directory(self):
        pass

class Image():

    def __init__(self, filepath):
        self.filepath = filepath
    

# how to organize linked images as well is a question
# database like approach would work but be very different

# Runs are basically the same but the way we get infomtaion into them is
# different but aldo that information may have different levels of detail
# and be in differenet formats 
    


    
    