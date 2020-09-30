# Background

One of the largest challenges in obtaining X-ray diffraction
data from biological samples is growing large, high quality crystals.
Currently, there is not way to reliably predict successful crystallization
conditions based on protein sequence alone and so high-throughput approaches
are very appealing. High-throughput crystallization screens test a large
chemical space using hundreds of different crystallization cocktails at the
nano-drop scale. Successful conditions can then be scaled up and optimized to
grow larger crystals.

The High-Throughput Crystallization Screening Center at the Hauptman-Woodward 
Medical Research Institute provides this high-throughput screening service to
users, offering 1536 condition screens for both soluble and membrane protein
samples. Each plate is imaged over a period of two months using
brightfield microscopy, as well as SHG and UV-TPEF microscopy, using Formulatrix Rock Imagers.

This high-throughput produces a large volume of images that must be
sorted through in order to pick out the best condition; a task that can be
very tedious and repetitious.

In 2019 Bruno *et al* published [Classification of crystallization outcomes using deep convolution neural networks](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0198883)
which included a CNN model that could accurately classify crystallization screening
images, opening the door to automating this process. The MARCO model is open-source and available for users to implement, and has been incorporated into See3 software for Collaborative Crystallization Centre (Australia) users, but has not been available in an average-user oriented graphical user interface (GUI) program.

Polo is therefore designed to incorporate the benefits of the MARCO model
and integrate the functionality of established crystallization image
labeling software such as [MacroscopeJ](https://hwi.buffalo.edu/wp-content/uploads/2016/11/MsjManual-0_1_1_3.pdf)
to create a GUI targeted for HWI Crystallization Center users and others with crystallization screening
experiments.  Polo incorporates all the tools needed to go from raw crystallization images
to designing optimization screens without the need to install any dependencies.

For more information, please visit the documentation page linked below.

# Helpful Links

- [Documentation](https://hauptman-woodward.github.io/Marco_Polo/)
- [2020 SSRL / LCLS Users' Meeting Poster and Live Session](https://events.bizzabo.com/SLAC-UsersMeeting-2020/agenda/session/363994)
