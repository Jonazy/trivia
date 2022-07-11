from importlib import resources
import os
from unicodedata import category
import unittest
import json
from urllib import response
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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    """
    Test category endpoint
    """
    def test_get_category(self):
        category = {
            "type": "English"
        }
        self.client().post('/categories', json = category)
        response = self.client.get('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'], True)
    

    """
    Test delete question endpoint
    """
    def test_delete_question(self):
        question_data = {
            "question": "What's English",
            "answer": "English is a language",
            "category": "Language",
            "difficulty": 1
        }
        create_question = self.client().post('/questions', json = question_data)
        data = json.loads(create_question.data)
        question_id = create_question.id
        response = self.client.delete('/question/{{question_id}}')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'], True)

    def test_404_delete_question(self):
        res = self.client().delete('/question/'+str(200))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['success'], False)

    """
    Test POST a new question 
    """
    def test_create_question(self):
        question_data = {
            "question": "What's English",
            "answer": "English is a language",
            "category": "Language",
            "difficulty": 3
        }

        response = self.client().post('/question', json = question_data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertTrue(data['success'])
        self.assertTrue(data['count'] > 0)

    """
    Test POST a new question with missing category
    """
    def test_error_create_question(self):

        question_data = {
            "question": "What's English",
            "answer": "English is a language",
            "difficulty": 1,
        } 
        response = self.client().post('/questions', json = question_data)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)

    """
    Test search question by category endpoint.
    """
    def test_get_questions_by_category(self):
        response = self.client().get('/questions/english')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['count'] > 0)

    """
    Test 400 if no questions with queried category is available.
    """
    def test_400_get_questions_by_category(self):
        response = self.client().get('/questions/english')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)

    """
    Test POST to search a question endpoint
    """
    def test_search_question(self):
        question_data = {
            "question": "What's English",
            "answer": "English is a language",
            "category": 2,
            "difficulty": 1,
        } 
        question = self.client().post('/question', json = question_data)

        search_question = {
            'searchTerm' : 'English',
        } 

        response = self.client().post('/questions', json = search_question)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['count'] > 0)

    """
    Test quizzes endpoint
    """
    def test_quiz(self):
        quize_data = {
            'previous_questions' : 1,
            'category' : 1
        } 
        response = self.client().post('/quizzes', json = quize_data)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()