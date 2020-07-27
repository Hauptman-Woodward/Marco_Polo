Installation Guide
=========================

Please visit `the GitHub Release page <https://github.com/EthanHolleman/Marco_Polo/releases>`_
and follow the install instructions for the latest release for your operating
system. 

More details coming soon.

Running From Source
=========================

If you do not want to use the binary files, you can run Polo like any
other Python program. Steps to do so are below.

1. Create a python 3.5 virtual environment. I used conda for this,
but there are many other options. This is high recommended as Polo is
dependent on some legacy versions of common packages like TensorFlow.
2. Activate your newly created virtual environment,
3. Make sure you are using the latest version of pip. You can update using
the command :code:`pip install --upgrade pip`.
4. Install all the dependencies in the includes :code:`requirements.txt`
file. This can be done most easily with the command 
:code:`pip install -r requirements.txt`.
5. You now should be able to run Polo with the command :code:`python Polo.py`

