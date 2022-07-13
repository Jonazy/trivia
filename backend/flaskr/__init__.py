from crypt import methods
from importlib import resources
import os
from tkinter import N
from unicodedata import category

from sqlalchemy import false
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from http_status_code import (
  HTTP_200_OK, HTTP_201_CREATED, 
  HTTP_404_NOT_FOUND, 
  HTTP_400_BAD_REQUEST, 
  HTTP_401_UNAUTHORIZED, 
  HTTP_500_INTERNAL_SERVER_ERROR,
  HTTP_422_UNPROCESSABLE,
  HTTP_405_METHOD_NOT_ALLOWED
)

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  @app.after_request
  def after_request(response):
    response.header.add("Access-Control-Allow-Headers", "Content-Type, Authorization, true")
    response.header.add("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
    return response

  @app.route('/categories', methods=['GET'])
  def categories():
    categories = Category.query.all()

    return jsonify({
      'success': 'true',
      'result': categories,
    }), HTTP_200_OK

  @app.route('/questions', methods=['GET'])
  def questions():
    # pagination
    page = request.args.get('page', 1, type=int)

    questions = Question.query.peginate(page=page, per_page=QUESTIONS_PER_PAGE)
    count = len(Question.query.all())

    current_categories = []
    for c_categories in questions.caetgory:
      current_categories.append(c_categories)

    categories = []
    for category in Category.query.all():
      categories.append(category.format())

    return jsonify({
      "success": True,
      "count": count,
      "questions": questions,
      "current_category": current_categories,
      "categories": categories
    }), HTTP_200_OK

  @app.route('/question/<int:id>', methods=['DELETE'])
  def question(id):
    try:
      question = Question.query.filter_by(id=id).first()
      if question is None:
        return jsonify({
          "success": False,
          "message": "Record not found"
        }), HTTP_404_NOT_FOUND
      else:
        return jsonify({
          "success": True
        }), HTTP_200_OK
    except:
      return jsonify({
        "success": False,
        "messsage": "something went wrong"
      }), HTTP_500_INTERNAL_SERVER_ERROR

  @app.route('/question', methods=['POST'])
  def question():
    question = request.get_json().get('question', None)
    answer = request.get_json().get('answer', None)
    difficulty = request.get_json().get('difficulty', None)

    if question is "":
      return jsonify({
        "success": False,
        "message": "Question is required!"
      }), HTTP_400_BAD_REQUEST

    if answer is "":
      return jsonify({
        "success": False,
        "message": "Answer is required!"
      }), HTTP_400_BAD_REQUEST

    if category is "":
      return jsonify({
        "success": False,
        "message": "Category is required!"
      }), HTTP_400_BAD_REQUEST

    if difficulty is "":
      return jsonify({
        "success": False,
        "message": "Difficulty is required!"
      }), HTTP_400_BAD_REQUEST

    try:
      question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
      question.insert()
      count = len(Question.query.all())
      page = request.args.get('page', 1, type=int)
      questions = Question.query.paginate(page=page, per_page=QUESTIONS_PER_PAGE)

      return jsonify({
        "success": True,
        "questions": questions,
        "count": count
      }), HTTP_201_CREATED

    except:
      return jsonify({
        "success": False,
        "message": "something went wrong"
      }), HTTP_500_INTERNAL_SERVER_ERROR

  @app.route('/questions', methods=['POST'])
  def question_search():
    search_string = request.get_json().get('search_key', None)
    if search_string is "":
      return jsonify({
        "success": False,
        "message": "Enter search word!"
      }), HTTP_400_BAD_REQUEST

    try:
      search = Question.query.filter(Question.query.question.contains(search_string)).order_by(Question.id).all()
      if search is not None:
        return jsonify({
            "success": True,
            "questions": search
          }), HTTP_200_OK
      else:
        return jsonify({
            "success": False,
            "questions": search
          }), HTTP_404_NOT_FOUND

    except:
      return jsonify({
        "success": False,
        "message": "something went wrong"
      }), HTTP_500_INTERNAL_SERVER_ERROR

  @app.route('/questions/<str:category>', methods=['GET'])
  def questions_by_category(category):
    questions = Question.query.filter_by(category=category).ordery_by(Question.id).all()

    if questions is None:
      return jsonify({
            "success": False,
            "message": "Record not found"
          }), HTTP_404_NOT_FOUND

    else:
      return jsonify({
            "success": True,
            "questions": questions
          }), HTTP_200_OK

  @app.route('/quizzes', methods=['POST'])
  def quizzes():
    category = request.get_json.get('quiz_category', None)
    previous_questions = request.get_json.get('previous_questions', None)

    if category is "":
      return jsonify({
        "success": False,
        "message": "Category is required!"
      }), HTTP_400_BAD_REQUEST
    if previous_questions is None:
      if category:
        questions = Question.query.filter(Question.category==category).all()
      else:
        questions = Question.query.filter.all()
    else:
      if category:
        questions = Question.query.filter(Question.id != previous_questions, Question.category==category).all()
      else:
        questions = Question.query.filter(Question.id != previous_questions).all()

    random_question = random.randint(0, len(questions))

    return jsonify({
      "success": True,
      "quizzes": random_question
    }), HTTP_200_OK

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "error": 422,
      "success": False,
      "message": "unprocessable"
    }), HTTP_422_UNPROCESSABLE

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "error": 400,
      "success": False,
      "message": "bad request"
    }), HTTP_400_BAD_REQUEST

  @app.errorhandler(401)
  def unauthorized(error):
    return jsonify({
      "error": 402,
      "success": False,
      "message": "unauthorized"
    }), HTTP_401_UNAUTHORIZED
  
  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "error": 405,
      "success": False,
      "message": "method not allowed"
    }), HTTP_405_METHOD_NOT_ALLOWED

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      "error": 500,
      "success": False,
      "message": "internal server error"
    }), HTTP_500_INTERNAL_SERVER_ERROR
  
  return app

    