import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://postgres:Aspen100@localhost:5432/trivia_test"

        setup_db(self.app, self.database_path)

        # Category related variables
        self.search_category = 'new_category'

        self.new_category = {
            'type': 'new_category'
            }

        # Question related variables
        self.search_question = 'a'
        self.delete_question = 'Delete me!'

        self.new_question = {
            'question': 'to be or not to be',
            'answer': 'Unanswerable',
            'category': 2,
            'difficulty': 1
            }

        self.new_question_for_search = {
            'question': 'Will I be deleted?',
            'answer': 'Unanswerable',
            'category': 2,
            'difficulty': 1
            }

        self.new_question_for_delete = {
            'question':self.delete_question,
            'answer': 'deletable',
            'category': 2,
            'difficulty': 1
            }
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """ Begin Test Suit """

    # Categories
    # Success
    def test_get_categories(self):
        """Test Get Categories """
        # print('...Get categories...')
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total'])
        self.assertTrue(data['categories'])


    #************************************************************************************#
    # Questions
    #************************************************************************************#
    #------------------------------------------------------------------------------------#
    # Get: Success
    #------------------------------------------------------------------------------------#
    def test_get_questions(self):
        """Test Get Questions"""
        # print('...Get questions...')
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


    # #------------------------------------------------------------------------------------#
    # # Add: Success
    # #------------------------------------------------------------------------------------#
    def test_add_question(self):
        """Test Add Question """
        # print('...Add question...')
        res = self.client().post('/questions', json=self.new_question, follow_redirects=True)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['totalQuestions'], True)


    # #------------------------------------------------------------------------------------#
    # # Search by question: Success
    # #------------------------------------------------------------------------------------#
    def test_search_by_question(self):
        """Test Search question by question """
        # print('...Search question for search term...')
        res = self.client().post('/questions', json=self.new_question_for_search)
        res = self.client().post('/questions/search', json={'searchTerm': self.search_question})
        items = json.loads(res.data).get('questions', None)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(items[0]['id'], True)

    # #------------------------------------------------------------------------------------#
    # # Search by category: Success
    # #------------------------------------------------------------------------------------#
    def test_search_by_category(self):
        """Test Search question by category """
        # print('...Search up question for selected category...')
        # print('...Creating a new category...')
        res = self.client().post('/categories', json=self.new_category)
        items = json.loads(res.data).get('id', None)
        # print('...Creating a new question for the newly created category...')
        new_question_for_search = {
            'question': 'Question for new category',
            'answer': 'Unanswerable',
            'category': items,
            'difficulty': 1
            }
        res = self.client().post('/questions', json=new_question_for_search)

        # print('...Searching for all questions linked to the new category...')
        res = self.client().post('/categories/' + str(items) + '/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['totalQuestions'], 1)

    # #------------------------------------------------------------------------------------#
    # # Search by category: Failure
    # #------------------------------------------------------------------------------------#
    def test_search_by_category_404(self):
        """Test Search question by category """
        # print('...Search up question for selected category...')
        res = self.client().post('/categories/' + str('1000') + '/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # #------------------------------------------------------------------------------------#
    # # Delete: Success
    # #------------------------------------------------------------------------------------#
    def test_del_question(self):
        """Test Delete Question """
        # print('...Delete question...')
        res = self.client().post('/questions', json=self.new_question_for_delete)
        res = self.client().post('/questions/search', json={'searchTerm': self.delete_question})
        items = json.loads(res.data).get('questions', None)
        res = self.client().delete('/questions/' + str(items[0]['id']) + '/delete', follow_redirects=True)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    # #------------------------------------------------------------------------------------#
    # # Delete: Failure
    # #------------------------------------------------------------------------------------#
    def test_del_question_404(self):
        """Test Delete Question """
        res = self.client().delete('/questions/' + str(1000) + '/delete', follow_redirects=True)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # #------------------------------------------------------------------------------------#
    # # Quizzes: Success
    # #------------------------------------------------------------------------------------#
    def test_play(self):
        """Test Play Quiz """
        print('...Play Quiz...')
        res = self.client().post('/quizzes',  json={"previous_questions":[10, 11],
                                                    "quiz_category":{"type":"Sports","id":"6"}})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


#
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
