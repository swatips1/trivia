#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import unittest
import json
from flaskr import create_app
from flask_cors import cross_origin
from models import *

#Test case class. Most of the times, named <object>TestCase
class ResourceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        # self.database = "demo"
        # self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        # setup_db(self.app, self.database_path)

    def tearDown(self):
        pass

    def test_given_behavior(self):
        res = self.client().get('/')

        self.assertEqual(res.status_code, 200)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
