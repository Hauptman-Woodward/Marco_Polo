Future Maintainers
==================================

Hello, if you are reading this it should be because you are interested in
or have been assigned to modify / maintain / improve Polo. Here, I will do my
best to fill you in on Polo's background and go through the problems, quirks
and bugs that you may encounter while modifying Polo.

Background
#######################################

Polo was created over the course of 10 weeks for the 2020 BioXFEL summer
internship. Development focused on creating a working final product that could
be improved on and extended in the future, which is probably why you are here.
Polo was my first real adventure into GUI programming and the PyQt library
so if you have significant experience with either there are definitely quirks to
be found and many places for improvement. Enjoy.

Getting Started
#######################################

Polo is written in Python (specifically Python 3.5) and uses the PyQt library
as the GUI "engine". To get going modifying Polo I would recommend taking a
look at the :ref:`Running From Source` section as it goes over how to setup
a virtual environment for Polo development. Make sure you follow these
instructions or do something equivalent as Polo is dependent on some
legacy versions of common python packages and mixing those in with a global
environment could get messy.

I also **highly**, **highly** recommend installing PyQt Designer for your
development machine. PyQt Designer will allow you to open the :code:`.ui`
files located in the :code:`pyqt_designer` directory. The :code:`.ui` files
are then translated by the :code:`pyuic5` command line program into Python
scripts which define the layout of the graphical interface.

I used  `This tutorial <https://pythonbasics.org/qt-designer-python/>`_ 
to install PyQt Designer and other devtools like pyuic5 on Ubuntu. 

This will allow you to graphically modify interfaces and easily find the names of widgets so
you can make sure buttons and other interfaces get connected to the correct
functions. Additionally, you can modify the :code:`UI_helper.py` script in
the :code:`src` directory with the path to your :code:`pyqt_designer` directory
to automatically generate the Python files which define each interface.

Directory Layout
#######################################

Polo directory structure just for fun.

.. code-block:: text

    .
    ├── docs
    │   ├── _images
    │   ├── _modules
    │   │   ├── polo
    │   │   │   ├── crystallography
    │   │   │   ├── marco
    │   │   │   ├── threads
    │   │   │   ├── utils
    │   │   │   ├── widgets
    │   │   │   └── windows
    │   │   └── tests
    │   ├── _sources
    │   └── _static
    │       ├── css
    │       ├── fonts
    │       │   ├── Lato
    │       │   └── RobotoSlab
    │       └── js
    ├── misc
    │   └── inno_scripts
    │       └── windows
    ├── pyqt_designer
    ├── sphinx
    │   ├── _build
    │   └── images
    └── src
        ├── astor
        ├── data
        │   ├── cocktail_data
        │   ├── images
        │   │   ├── default_images
        │   │   ├── icons
        │   │   └── logos
        │   ├── savedmodel
        │   │   └── variables
        │   └── text
        ├── polo
        │   ├── cockatoo
        │   │   ├── cockatoo
        │   │   ├── data
        │   │   ├── docs
        │   │   │   ├── api
        │   │   │   ├── examples
        │   │   │   └── images
        │   │   ├── examples
        │   │   ├── screens
        │   │   │   ├── csv
        │   │   │   │   ├── hwi
        │   │   │   │   └── test-screens
        │   │   │   └── json
        │   │   │       ├── hwi
        │   │   │       └── test-screens
        │   │   └── tests
        │   ├── crystallography
        │   │   
        │   ├── designer
        │   │   
        │   ├── marco
        │   │   
        │   ├── plots
        │   │   
        │   ├── threads
        │   │   
        │   ├── utils
        │   │   
        │   ├── widgets
        │   │   
        │   └── windows
        │       
        ├
        ├── templates
        │   └── static
        ├── tests
        └── unrar
            ├── Darwin
            └── Windows
                ├── Win32
                └── Win64


src Directory
-------------------------

The src directory includes all Python scripts Polo needs to run plus any
data required, such as the MARCO tensflow model. Below are short desciptions
of what you'll find in this directory.

- :code:`Polo.py` : Main script. Use to launch the application.
- :code:`UI_helper.py` : Helper script to convert :code:`.ui` files to :code:`.py` files. See :ref:`Getting Started`.
- :code:`polo` : The Polo package. Contains all scripts that define Polo behavior and interfaces.
- :code:`data` : Contains all data required for Polo to run. Such as cocktail csv files, the MARCO model and icon images 
- :code:`unrar` : Contains unrar executables for Windows and Mac
- :code:`templates` : Jinja2 html templates for creating html file exports
- :code:`astor` : I kept getting an error from Tensorflow that this directory could not be found so I included it and the problem was solved

misc Directory
------------------------

Contains odds and ends notes or other files that didn't really have a place
anywhere else. One of the most useful may be the :code:`polo.iss` script. This
is an inno setup script I used for created the Polo windows installer. Feel
free to use it, but make sure to modify the filepaths in it before running.

pyqt_designer Directory
---------------------------

Holds all :code:`.ui` files, which are really :code:`.xml` files that
PyQt Designer uses to serialize the interfaces you design in it. They are
translated to Python files which then define the graphical interface for
Polo. See the :ref:`Getting Started` section for a bit more detail on this.

sphinx Directory
----------------------

Contains rst files and images which define Polo's documentation. With
sphinx installed via pip you can recreate Polo's documentation with the
command :code:`make html`. For these files to be rendered on the GitHub
pages site they need to be places into the :code:`docs` directory. You will
also need to install the read the docs theme for sphinx. 

docs Directory
------------------------

Holds documentation html files. Rendered as the Polo website using GitHub
sites.


Polo Package Notes
#######################################

All the scripts that make up the actual Polo program are located in
:code:`src/Polo`. In this section I will go over a few important aspects of the
program that may be helpful and are not covered explicitly in the API documentation.

Notable Scripts
----------------------------

The :code:`__init__` Script
+++++++++++++++++++++++++++++

Most variables that are used across Polo scripts are defined in here and is
worth taking a look at as the stuff in here comes up all over other scripts.
The items below are some of the major functions of the :code:`__init__` :
file.

1. Defines filepaths to the stuff in the :code:`data`:
2. Defines the version of the program via the :code:`polo_version`: variable
3. Defines the image classification and image spectrum keywords
4. Defines how MSO classification codes are translated into MARCO classifications
5. Determines which unrar executable to use based on the OS
6. Defines regular expressions used for parsing cocktail data
7. Defines urls to Polo documentation site pages

The :code:`windows/main_window` Script
+++++++++++++++++++++++++++++++++++++++++

The :code:`windows/main_window.py` script defines the :class:`MainWindow` class
from which all other widgets are staged within. If you are looking for how one
widget communicates to another, how menu selections are handled or how runs
are opened this would be the file to look in. Since the :class:`MainWindow`
class contains most other widgets in some way it is a good place to look when
relationships between widgets are in question.

Subpackages
#######################################

Crystallography Subpackage
----------------------------

Contains scripts relating to crystallography and high-throughput imaging.
Most of the main data containing classes are defined here.

Designer Subpackage
----------------------------

Contains all the pyqt Designer generated UI scripts. These are used to define
the graphical interfaces (buttons, knobs, etc.) that make up the widgets and
dialogs defined in Polo. These scripts do not provide any functionality to
the graphical components, they just define their layout and names. 

Marco Subpackage
----------------------------

Holds scripts relating to running the MARCO model for image classification.
There is really only one important function in here which classifies an image
passed to it.

Plots Subpackage
----------------------------

Functions related to generating plots shown in the plots tab of the main window.
This one is kind of a todo I didn't get around to and there is a lot of clean up
that could be done here. Especially since plots does not have its own widget
like the slideshow inspector or plate inspectors.

Threads Subpackage
----------------------------

A lot of the operations Polo undertakes, like running the MARCO model, are
CPU intense and cannot be run on the same thread that the GUI is run on. The
threads package holds the :code:`thread.py` script which defines QThread objects
for running various tasks outside of the GUI thread. This prevents the freezing
the GUI when preforming a large operation. Windows is particularly fast to recognize
a frozen program so it is often necessary to put tasks that take more than a few
seconds onto a thread.

Utils Subpackage
----------------------------

TODO

Widgets Subpackage
----------------------

TODO

Windows Subpackage
-----------------------

TODO


Creating Exes for Distribution
#######################################

Once you have made some modifications to your program you are going to want
to create exe for potential users. I used Pyinstaller to create the exe files
and then on Windows Inno setup to create an installer and will cover those
topic in this section.

Pyinstaller Overview and Usage Guide
----------------------------------------

Pyinstaller is not included as a dependency in the :code:`requirements.txt`
file so will need to install it using Pip.

Polo includes a :code:`.spec` file in the outermost directory. This is the file
I used on Ubuntu, Mac and Windows to generate exe files. It should be noted that
the exe will be specific to the operating system you create it on. A Polo
exe created on Windows will only work on Windows machines. Despite it's file
extention, the  :code:`.spec` file is really a python script that passes
information along to pyinstaller.

Running pyinstaller using the :code:`.spec` file is actually 
very easy and can be done with the command
:code:`pyinstaller Polo.spec`. Additionally, I have made some changes to the
:code:`.spec` which allow you to generate one file exes by appending
:code:`F` onto the end of the pyinstaller command. However, you will likely
need to make some modifications to the :code:`.spec` before you run it.

Spec File Details and Modifications
--------------------------------------

Before running the :code:`.spec` file you will need to modify a couple
file paths based on the locations on your development machine(s).

First, you'll notice the dictionary :code:`Tensorflow_location`. Much of the
:code:`.spec` is devoted to dealing with packing Tensorflow 1.14 as pyinstaller
misses the binary files in the Tensorflow library that are required for the
package to work correctly. Therefore these files need to be collected as
passed to pyinstaller explictly to create a working exe. Stragenly, I only
encoutered this problem on Linux and Mac.
The :code:`tensorflow_location` dictionary specifies the location of the
Tensorflow package on your machine. You will need to modify these paths to
the Tensorflow package being used by your virtual environment.

Next, you'll need to modify the :code:`polo_locations` dictionary values.
This dictionary maps operating system types to the location of the Polo
repository on that machine. When run, the :code:`.spec` file recognizes
the OS it is being run on and picks the file path corresponding to that OS.

After making these modifications you should be able to run the :code:`.spec`
file successfully. If something is not working correctly I recommend
running the pyinstaller command without :code:`F` argument to create
a directory instead of a single file. This will let you more easily see
exactly what pyinstaller has included in your distribution. If it isn't in
the directory distribution it won't be found in the single file distribution.

Editing and Extending this Documentation
###########################################

Documentation Background
------------------------------

All Polo documentation is written using the RST (restructured text) markdown
language. I find myself going back to this `cheat sheet <https://thomas-cokelaer.info/tutorials/sphinx/rest_syntax.html>`_ 
when I have syntax questions but overall it is very similar to GitHub markdown. 
The code (API) documentation and html is generated using Sphinx Python package which you
can read more about at the `Sphinx website <https://www.sphinx-doc.org/en/master/index.html>`_.

.. note::

    Everything below has been done on Ubuntu (Linux) OS. Results may vary on Windows or Mac.


Editing the Docs
-----------------------------

You can edit the documentation in two main ways. First, directly editing the rst files located in the
:code:`sphinx` directory of the Polo repository. This is the best way to edit pages like the :ref:`User Guide`
or :ref:`Installation Guide` that are not generated automatically. The second way is through the docstrings
of Polo functions. Sphinx collects these docstrings and creates the code documentation from them.
Either way, you will need to render your rst / Python files to HTML which actually forms the documentation
website. To learn how, read on.

Creating HTML Files
-------------------------------

1. If you have not done so already, install the Sphinx package and the Read the Docs theme. Follow the instructions
in the `Sphinx Installation Guide <https://www.sphinx-doc.org/en/master/usage/installation.html>`_ to install
Sphinx and use the command :code:`pip install sphinx_rtd_theme` to install the RTD theme. You should use whatever
virtual environment you are using while working on Polo as all the dependencies required to run Polo will be
required to run Sphinx.

2. Navigate to the :code:`sphinx` directory of the Polo repository. Run the command :code:`make html`. This should
collect docstrings and render your RST files to html. They will be places in the :code:`sphinx/_build/html`
directory of the Polo repository.

3. Checkout the changes you made by opening the HTML files. If everything looks good move all files to the
:code:`docs` folder of the repository and commit your changes. If GitHub pages is still being used to host
the documentation website, the changes should come online in a few minutes. If some other hosting solution is
in use, I can guide you no further.

Debugging
---------------------------

A good place to start if things go weird in creating the documentation is the :code:`conf.py` file
located in the :code:`sphinx` directory of the Polo repository. It defines filepaths and assets that
are used when rendering so it is a good place to start looking for issues.



