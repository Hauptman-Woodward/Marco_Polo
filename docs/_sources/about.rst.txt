About
==========================================

.. image:: ./images/lysozyme.png
   :alt: lysozyme
   :width: 400

`X-ray Crystal Structure of Lysozyme Protein`


Background
-------------------------

One of the largest hurtles to obtaining X-ray diffraction
data from biological samples is growing large, high quality crystals.

Currently, there is not way to reliably predict successful crystallization
conditions based on protein sequence alone and so high-throughput approaches
are very appealing. High-throughput crystallization screens test a large
chemical space using hundreds of different crystallization cocktails at the
nano-drop scale. Successful conditions can then be scaled up and optimized to
grow larger crystals.

The high-throughput crystallization screening center at the Hauptman-Woodward 
Medical Research Institute provides this high-throughput screening service to
users; offering 1536 condition screens for both soluble and membrane protein
samples. Each plate is imaged over a period of two months in using both
visible light microscopy and UV-TPEF photography.

This high-throughput produces a large volume of images that must be
sorted through in order to pick out the best condition; a task that can be
very tedious and repetitious.

In 2019 Bruno *et al* published `Classification of crystallization outcomes using deep convolutional neural networks <https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0198883>`_
which included a CNN model that could accurately classify crystallization screening
images, opening the door to automating this process. The MARCO model has been
used in large scale projects such as the `xtution database <http://xtuition.org/>`_
but has not been utilized in a average-user oriented graphical program.

Polo is therefore designed to incorporate the benefits of the MARCO model
and integrate the functionality of established crystallization image
labeling software such as `MacroscopeJ <https://hwi.buffalo.edu/wp-content/uploads/2016/11/MsjManual-0_1_1_3.pdf>`_
to create a GUI targeted for HWI and other high-throughput crystallization screening
users that incorporates all the tools needed to go from raw crystallization images
to designing optimization screens without the need to install any dependencies. 

Features
----------------

Automatic Image Classification
++++++++++++++++++++++++++
Using the MARCO model Polo can cut down the time you spend looking 
through your crystallization images by identifying wells likely to 
contain a protein crystal. This can reduce the total number of 
images that need to be considered from thousands to hundreds.

Multiple Image View Modes
+++++++++++++++++++++++
Polo allows you to view your crystallization images in a variety of 
ways that make it easier to identify true crystal hits. Images can be 
viewed individually or in grids of up to 96. 
If a sample has been imaged at multiple points in time it is easy 
to create timeline views that allow you to assess the effectiveness 
of a screening condition over time. Additionally, if your samples 
have been imaged with photographic technologies outside of visible 
light microscopy it is easy to compare these images to verify 
the presence of protein crystals.

Integrated FTP Browser
+++++++++++++++++++++++++++
Polo includes an simple FTP browser that allows you to download image 
files from a remote server directly into Polo without then need to 
install other software such as FileZilla. Polo is also packaged with 
unrar for Windows and Mac.

Data Management
++++++++++++++++++++++

Your image classifications are easily saved and managed via the xtal file format. Xtal files are similar to mso files created by MacroscopeJ and encode your image classifications, MARCO classifications, cocktail formulation and other metadata. In addition, xtal files increase portability 
by encoding your screening images directly into the file along side your 
metadata. This allows your classifications to be easily shared with 
one file to anyone else with Polo on their computer. 

Polo also has options to export your runs to csv files without 
encoding your screening images or to HTML reports for a more 
visual way to share your results with those who do not use Polo.

Open Source Code Base
++++++++++++++++++++++

Polo is written in Python and is licensed under the 
GNU 3.X license. This allows for modification and use of any of the 
Polo source code. If you wish to change modify or extend any of 
Polo’s functionality you are free to do so. Additionally, 
documentation is available at THIS LINK. 

