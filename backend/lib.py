import os
from flask import Flask, request, abort, jsonify, flash, current_app#, response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category

# Number of questions each page could show
QUESTIONS_PER_PAGE = 10

# Function to return one page worth questions from the list.
# Request provides the current page numnber.
def paginate_questions(request, all_questions):
    page = request.args.get('page', 1, type=int)
    start = (page -1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    formatted_questions = [question.format() for question in all_questions]
    sel_questions = formatted_questions[start:end]
    return sel_questions

# Function to return categories for questions that
# will show on the current page ONLY.
def compile_categories(formatted_questions):
    categories={}
    for question in formatted_questions:
        category_id = question['category']
        if category_id not in categories.keys():
            category = Category.query.filter(Category.id == category_id).all()[0]
            categories[category.id]=category.type
    return categories

# Function to return questions that match selected category_id
def get_questions_by_category(category_id):
    questions = Question.query.filter(Question.category == category_id).all()
    return questions

# Function to return differencial between two lists.
def subtract(L1,L2):
   L3=L1
   for id in L2:
       for question in L1:
           if id == question.id:
               L3.remove(question)
   return L3
