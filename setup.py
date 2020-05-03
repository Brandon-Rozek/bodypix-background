from setuptools import setup, find_packages

setup(name="bodypix-background",
      version="0.1",
      author="Brandon Rozek",
      packages=find_packages(),
      install_requires=[
          "opencv-python~=4.2.0.34",
          "numpy~=1.18.3",
          "pyzmq~=19.0.0",
          "pyfakewebcam==0.1.0"
      ]
)
