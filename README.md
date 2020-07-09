# Background
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

In 2019 Bruno *et al* published [Classification of crystallization outcomes using deep convolution neural networks](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0198883)
which included a CNN model that could accurately classify crystallization screening
images, opening the door to automating this process. The MARCO model has been
used in large scale projects such as the [xtution database](http://xtuition.org/)
but has not been utilized in a average-user oriented graphical program.

Polo is therefore designed to incorporate the benefits of the MARCO model
and integrate the functionality of established crystallization image
labeling software such as [MacroscopeJ](https://hwi.buffalo.edu/wp-content/uploads/2016/11/MsjManual-0_1_1_3.pdf)
to create a GUI targeted for HWI and other high-throughput crystallization screening
users that incorporates all the tools needed to go from raw crystallization images
to designing optimization screens without the need to install any dependencies.

For more information, please visit the documentation page linked below.
# [Link to Docs](https://ethanholleman.github.io/Marco_Polo/)
