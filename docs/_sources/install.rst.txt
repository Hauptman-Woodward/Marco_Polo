Installation Guide
=========================

Please visit `the GitHub Release page <https://github.com/Hauptman-Woodward/Marco_Polo/releases>`_
and follow the install instructions for the latest release for your operating
system, but before you do please review the OS specific notes below.

OS Specific Installation Notes
++++++++++++++++++++++++++++++++

Windows
---------------------------

A full installer is available for Windows 10. It is highly recommended to only
install polo for the local user (this is the default) as otherwise Polo will
require administrator privileges to run properly. 

Additionally, it is likely that when you try to run the installer you will
be greeted with this prompt from Windows warning you that Polo is from
an unverified publisher. 

If you wish to continue the install select "More Info".

.. image:: images/more_info.png
    :align: center

This will show the "Run Anyway" button. Select it to proceed with the installation.

.. image:: images/run_anyway.png
    :align: center

If you are concerned about the content of Polo please feel free to visit the
GitHub page where all code is available for review.

Mac and Ubuntu
---------------------------

While there is no installer available for Mac and Ubuntu Linux, executable
files are. Your machine is likely to have similar security concerns to
Windows about running an exe you downloaded from the internet so you may need
to take special action the first time you run Polo.

On Mac you can follow the steps below to give Polo permission to run.

1. In the Finder, locate the app you want to open. Don’t use Launchpad to do this. Launchpad doesn’t allow you to access the shortcut menu.

2. Control-click the app icon, then choose Open from the shortcut menu.

3. Click Open.

This will add Polo to your list of approved programs.

On Ubuntu (or Mac) you can give Polo permission to run as an executable
with the command :code:`sudo chmod +x Polo` in the directory your Polo
exe is located in.

For any operating system, if something isn't working correctly, doesn't seem
intuitive or you think could work better please let me know! Please
see the :ref:`I Found a Bug` section for more information on how to report
issues and make suggestions.


Issues Others have Encountered
++++++++++++++++++++++++++++++++

Below is a compilation of issues others have encountered and potential 
OS specific solutions solutions. If you have an issue and are able to solve the
problem on your own, please let me know about via either the GihHub Issues page
of the Google form. Both of which can be found in the :ref:`I Found a Bug`
section. 

Windows
------------------------

Installing for All Users
****************************************************************************************

The windows version of Polo is the only distribution that includes an installer.
Some testers encountered issues running Polo when installing Polo for all users instead of
just the local user (default install)

The Cause
..................................

As part of normal operation Polo writes a log and other files in the directory the exe
is contained in. If Polo is installed for all users, the exe will be located in
a location that requires administrator privileges to write to and Polo will be
unable write and open normally.

The Solution
..................................

If you do not want to re-install Polo for the local user. Left click the
the desktop shortcut or exe file and select "Run as administrator". Or just
reinstall Polo for the local user.

Mac
------------

Polo is recognized as a txt file, not exe
****************************************************************************************

Some users have found that the Mac Polo exe after it is downloaded is recognized
as a txt file and not as an exe file (which can be run on your computer). If
this is the case for you it is fixable but will require some command line usage.

The cause
..................................

Currently, not sure about this one.

The Solution
..................................

1. Determine the filepath to your Polo (txt) exe file. The filepath can be
copied to your clipboard by left clicking and selecting *Copy*

2. Open the terminal. This can be done by going to Spotlight search and searching
for "terminal"

3. Enter the command below into the terminal and press enter. Replace the
text in [ ] with the filepath you just copied. Do **not** include the braces. 
If you are prompted to give your password, do so.

:code:`sudo chmod +x [Your/Polo/Filepath]`

You should be able to run Polo as a program now.

"Polo" can't be opened because Sandbox is not allowed to open documents in Terminal
****************************************************************************************

Some users using Mojave OS are greeted with the error message (shown below)
when attempting to launch Polo for the first time. 

.. image:: images/sandbox_error.png
    :align: center

The Cause
..................................

This issue is believed to be related to Mac security settings which are rightfully
hesitant to run programs from outside developers.

The Solution
..................................

If this occurs execute the steps desribed in the solution section of
:ref:`Polo is recognized as a txt file, not exe`. You can also attempt control
clicking the Polo executable and selecting **Open**. 


Running From Source
++++++++++++++++++++++++++++++++

If you do not want to use the binary files, you can run Polo like any
other Python program. Steps to do so are below.

1. Create a python 3.5 virtual environment. I used conda for this, but there are many other options. This is high recommended as Polo is dependent on some legacy versions of common packages like TensorFlow.

2. Activate your newly created virtual environment

3. Make sure you are using the latest version of pip. You can update using the command :code:`pip install --upgrade pip`.

4. Install all the dependencies in the includes :code:`requirements.txt` file. This can be done most easily with the command :code:`pip install -r requirements.txt`.

5. You now should be able to run Polo with the command :code:`python Polo.py`

