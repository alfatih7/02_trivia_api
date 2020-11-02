import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask import request
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trvdb"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', '1993239', 'localhost:5432',
                                                             self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    Write at least one test for each test for successful operation and for expected errors.
    """

    '''
       TEST: At this point, when you start the application
       you should see questions and categories generated,
       ten questions per page and pagination at the bottom of the screen for three pages.
       Clicking on the page numbers should update the questions. 
       '''

    def test_get_quetions_paginated(self):
        """Test _____________ """
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['totalQustion'])
        self.assertTrue(len(data['questions']))

    '''
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
     '''

    def test_404_request_error_paginated(self):
        response = self.client().get('/questions?page=100')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_404_if_question_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_create_qustion(self):
        res = self.client().post('/create/question', json={'created_question_id': 100})
        data = json.loads(res.data)
        self.assertEqual(data['created_question_id'])

        pass

    def test_422_error_create(self):
        response = self.client().get('/create/question')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['successful'], False)
        self.assertEqual(data['message'], 'not created')

    '''
    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''

    def test_search_question(self):
        res = self.client().post('/search/questions', json={'question searched': 'wrong qustion'})
        data = json.loads(res.data)
        self.assertEqual(data['question searched'])
        pass

    def test_404_error_search_question(self):
        response = self.client().get('/search/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)

    '''
    In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown.
    '''

    def test_qustion_by_categories(self):
        res = self.client().post('/questions/categories',
                                 json={'Questions per catogery': 'no Catogory', 'statues': 'False'})
        data = json.loads(res.data)
        self.assertEqual(data['Questions per catogery'])
        self.assertEqual(data['statues'], True)
        pass

    def test_404_test_qustion_by_categoriesn(self):
        response = self.client().get('/questions/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['statues'], False)

    '''
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''

    def test_quiz_qustion_by_categories(self):
        res = self.client().post('/questions/quiz',
                                 json={'random question ': 'what is your favorit game?', 'categories': 'toy questions',
                                       'Answer': 'football'})
        data = json.loads(res.data)
        self.assertEqual(data['random question'])
        self.assertEqual(data['answer'], True)
        self.assertEqual(data['categories'])

    def test_error_quiz_qustion_by_categories(self):
        res = self.client().post('/questions/quiz',
                                 json={'random question ': 'random_qus', 'categories': 'no category'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)

        pass


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
