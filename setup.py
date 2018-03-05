from distutils.core import setup

setup(name = "eudatL3", 
      version="2018030501", 
      author="Carl-Fredrik Enell",
      author_email="carl-fredrik.enell@eiscat.se",
      url="http://www.eiscat.se/raw/fredrik/",
      package_dir = {'': 'modules'},
      py_modules = ['madSearch'],
      scripts = ['scripts/L3toB2.py'],
)
