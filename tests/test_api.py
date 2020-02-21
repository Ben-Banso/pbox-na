import unittest
import importlib

app = __import__("/home/ben/projects/personal-box/na/pbox-na.py")

class MyTestCase(unittest.TestCase):
        
    def setUp(self):
        app.app.testing = True
        self.app = app.app.test_client()

    def test_home(self):
        result = self.app.get('/')
        print(result)
