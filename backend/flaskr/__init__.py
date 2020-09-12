import os
from flask import Flask, request, abort, jsonify, flash, current_app, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from flask_cors import cross_origin

#Import exceptions
from sqlalchemy import exc

#Import supporting functions
from lib import *


# QUESTIONS_PER_PAGE = 10
SECRET_KEY = os.urandom(32)

def create_app(test_config=None):
  ''' create and configure the app '''
  app = Flask(__name__, instance_relative_config=True)
  ''' Security '''
  app.secret_key = SECRET_KEY
  ''' Database '''
  db = setup_db(app)
  ''' CORS '''
  cors = CORS(app, supports_credentials=True)
  app.config['CORS_HEADERS'] = 'Content-Type'

  ''' after_request decorator: setting Access-Control-Allow '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
      response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
      return response

  '''
  -----------------------------------------------------------
  Default endpoint. Not exposed to end user.
  -----------------------------------------------------------
  ***********************************************************
  Expected Inputs: None
  Expected Output: jsonified message.
  ***********************************************************
  -----------------------------------------------------------
  Linked tests:None
  -----------------------------------------------------------
  '''
  @app.route('/')
  def hello():
      return jsonify({'message': 'Welcome to the trivia app!'})

  '''
  -----------------------------------------------------------
  This endpoint to handles GET requests for all
  available categories.
  -----------------------------------------------------------
  ***********************************************************
  Expected Inputs: None
  Expected Output: Dictionary of categories.
  ***********************************************************
  -----------------------------------------------------------
  Linked tests:test_get_categories
  -----------------------------------------------------------
  '''
  @app.route('/categories', methods=['GET'])
  def categories():
    try:
        categories = Category.query.order_by('id').all()
        formatted_categories = {category.id: category.type for category in categories}
    except Exception as e:
        print(e)
        return jsonify({'message': e})
    return jsonify({'success': True,
                    'total' : len(categories),
                    'categories' : formatted_categories})

  '''
  -----------------------------------------------------------
  This endpoint to handles GET requests for questions,
  including pagination (every 10 questions).
  -----------------------------------------------------------
  ***********************************************************
  Expected Inputs: None
  Expected Output:
    list of all questions from database
    number of total questions
    current category
    categories
  ***********************************************************
  -----------------------------------------------------------
  Linked tests:test_get_questions
  -----------------------------------------------------------
  '''
  @app.route('/questions', methods=['GET'])
  def questions():
    try:
      questions = Question.query.order_by('id').all()
      formatted_questions = paginate_questions(request, questions)
      categories = compile_categories(formatted_questions)
    except Exception as e:
        flash(e)
        return jsonify({'message': e})
    return jsonify({'success': True,
                    'currentCategory': None,
                    'categories' : categories,
                    'totalQuestions' : len(questions),
                    'questions' : formatted_questions})

  '''
  -----------------------------------------------------------
  This endpoint to handles DELETE requests for questions.
  It returns list of all remaining questions from database.
  -----------------------------------------------------------
  ***********************************************************
  Expected Inputs: id of the question
  Expected Output:
    list of all questions from database
    number of total questions
    current category
    categories
  ***********************************************************
  -----------------------------------------------------------
  Linked tests:test_del_question
  -----------------------------------------------------------
  '''
  @app.route('/questions/<int:question_id>/delete', methods=['DELETE'])
  def delete_question(question_id):
      question = Question.query.filter(Question.id == question_id).one_or_none()
      if question is None:
          abort(404)
      try:
          question.delete()
          questions = Question.query.order_by('id').all()
          formatted_questions = paginate_questions(request, questions)
          categories = compile_categories(formatted_questions)
      except Exception as e:
          print(e)
          return jsonify({'success': False,
                          'message' : 'error'})
      return jsonify({'success': True,
                      'currentCategory': None,
                      'categories' : categories,
                      'totalQuestions' : len(questions),
                      'questions' : formatted_questions})

  '''
  -----------------------------------------------------------
  This endpoint handles creation of new questions via POST
  It returns list of all questions from database.
  -----------------------------------------------------------
  ***********************************************************
  Expected Inputs:
    question: string. The text of the question
    answer: string. The text of the answer
    difficulty: int.
    category: id of the category the question belongs to.
        Mapped to id column of the categories table.
  Expected Output:
    list of all questions from database
    number of total questions
    current category
    categories
  ***********************************************************
  -----------------------------------------------------------
  Linked tests:test_add_question, test_del_question
  -----------------------------------------------------------
  '''
  @app.route('/questions', methods=['POST'])
  def add_question():
    try:
      que = request.get_json()['question']
      answer = request.get_json()['answer']
      difficulty = request.get_json()['difficulty']
      category = request.get_json()['category']
      question = Question(question=que, answer=answer, category=category, difficulty=difficulty)
      question.insert()
    except Exception as e:
        print(e)
        return jsonify({'message': e})
    return redirect(url_for('questions'))

  '''
  -----------------------------------------------------------
  This endpoint to handles search of question based on
  partial search term. It returns any questions for whom
  the search term is a substring of the question.
  -----------------------------------------------------------
  ***********************************************************
  Expected Inputs:
    search term: string.
  Expected Output:
    list of all questions from database
    number of total questions
    current category
    categories
  ***********************************************************
  -----------------------------------------------------------
  Linked tests:test_search_by_question, test_del_question
  -----------------------------------------------------------
  '''

  @app.route('/questions/search', methods=['POST'])
  def search_questions():
      data =[]
      try:
          question = '%' + request.get_json()['searchTerm'] + '%'
          questions = Question.query.filter(Question.question.ilike(question)).all()
          formatted_questions = paginate_questions(request, questions)
          categories = compile_categories(formatted_questions)
      except Exception as e:
          print(e)
          return jsonify({'message': e})
      return jsonify({'success': True,
                      'currentCategory': None,
                      'categories' : categories,
                      'totalQuestions' : len(formatted_questions),
                      'questions' : formatted_questions})

  '''
  -----------------------------------------------------------
  This endpoint to handles search of question based on
  category id. It returns questions with the specified
  category id.
  -----------------------------------------------------------
  ***********************************************************
  Expected Inputs:
    category_id: int. Id of the category to be searched.
  Expected Output:
    list of all questions from database
    number of total questions
    current category
    categories
  ***********************************************************
  -----------------------------------------------------------
  Linked tests:test_search_by_category
  -----------------------------------------------------------
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['POST'])
  def search_questions_by_categories(category_id):
      questions = get_questions_by_category(category_id)
      if len(questions)==0:
          abort(404)
      try:
          formatted_questions = paginate_questions(request, questions)
          categories = compile_categories(formatted_questions)
      except Exception as e:
          print(e)
          return jsonify({'success': False,
                          'message' : 'error'})
      return jsonify({'success': True,
                      'currentCategory': None,
                      'categories' : categories,
                      'totalQuestions' : len(formatted_questions),
                      'questions' : formatted_questions})
  '''
  -----------------------------------------------------------
  This endpoint generates questions to play the quiz.
  It takes category and previous question parameters and
  returns a random questions within the given category,
  if provided, and that is not one of the previous questions.
  -----------------------------------------------------------
  ***********************************************************
  Expected Inputs:
    quiz_category: Object.
        The category user clicked to play the quiz
    previous_questions: Object.
        List of id(s) of previously answered questions
  Expected Output:
    one question
    List of ids of previously answered questions
  ***********************************************************
  -----------------------------------------------------------
  Linked tests:test_play
  -----------------------------------------------------------
  '''
  @app.route('/quizzes', methods=['POST'])
  def quizzes():
      data =[]
      try:
          formatted_question = None
          previous_questions = request.get_json()['previous_questions']
          quiz_category = request.get_json()['quiz_category']
          category_id = quiz_category['id']
          questions = get_questions_by_category(category_id)
          new_questions= subtract(questions, previous_questions)
          if len(new_questions) > 0:
              formatted_question = random.choice(new_questions).format()
      except Exception as e:
          print(e)
          return jsonify({'message': e})
      return jsonify({'success': True,
                      'previous_questions' : previous_questions,
                      'question' : formatted_question})

  '''
  ***********************************************************
  Error Handler
  ***********************************************************
  '''
  @app.errorhandler(500)
  def internal_server(error):
      return jsonify({
             "success": False,
             "error": 500,
             "message": "internal server error"
         }), 500

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
               "success": False,
               "error": 422,
               "message": "unprocessable"
           }), 422

  @app.errorhandler(404)
  def not_found(error):
        return jsonify({
              "success": False,
              "error": 404,
              "message": "resource not found"
          }), 404

  @app.errorhandler(400)
  def bad_request(error):
        return jsonify({
              "success": False,
              "error": 400,
              "message": "bad request"
          }), 400


  '''
  ***********************************************************
  -----------------------------------------------------------
  Supporting routes.Not connected to UI. Used for testing.
  -----------------------------------------------------------
  '''

  '''
  -----------------------------------------------------------
  This endpoint handles creation of new category via POST
  It returns the id of newly created category
  -----------------------------------------------------------
  ***********************************************************
  Expected Inputs:
    type: String. Name of the new category.
  Expected Output:
    id of the newly created category.
  ***********************************************************
  -----------------------------------------------------------
  Linked tests:test_search_by_category
  -----------------------------------------------------------
  '''
  @app.route('/categories', methods=['POST'])
  def add_category():
      try:
          category_type = request.get_json()['type']
          category = Category(type=category_type)
          category.insert()
      except Exception as e:
          print(e)
          return jsonify({'success': False,
                          'message' : e.message})
      return jsonify({'success': True,
                      'id' : category.id})

  '''***********************************************************
  '''

  return app
