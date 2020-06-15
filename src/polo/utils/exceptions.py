class EmptyDirectoryError(Exception):
    '''Raised when attempting to load images from an empty directory'''
    pass

class NotHWIDirectoryError(Exception):
    '''
    Raised when user attempts to read in a directory as HWI but it does
    not look like one.
    
    TODO: Add utils function to determine when to raise this exception.
    '''
    pass

class IncompletePlateError(Exception):
    '''
    Raised when reading in an HWI directory but it does not contain number
    of images corresponding to number of wells.
    '''
    pass

class EmptyRunNameError(Exception):
    '''
    Raised when reading in an HWI directory but it does not contain number
    of images corresponding to number of wells.
    '''
    pass

class InvalidCocktailFile(Exception):
    '''
    Raised when user attempts to load in a file containing well cocktail
    information that does not confrom to existing formating standards.
    '''
    pass

class ForbiddenImageTypeError(Exception):
    '''
    Raised when user attempts to load in an image that is not in the allowed
    image types.
    '''
    pass

class NotASolutionError(Exception):
    '''
    Raised when user attempts to load in an image that is not in the allowed
    image types.
    '''
    pass



