import os
from flask import Flask, request, abort, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from backend.models import setup_db, Question, Category, db


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    '''
     Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    # cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
     Use the after_request decorator to set Access-Control-Allow
    '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    '''
    Create an endpoint to handle GET requests 
    for all available categories.
    '''
    # @app.route('/index' , methods=['GET', 'POST'])
    # def index():
    #   if request.method == 'GET':
    #     place = request.args.get('place', None)
    #     if place:
    #       return place
    #     return "No place information is given"

    # global_query
    categories = Category.query.all()
    questions = Question.query.all()

    def row2dict(row):
        d = {}
        for column in row.__table__.columns:
            d[column.id] = str(getattr(row, column.type))
        return d

    QUESTION_PER_SHELF = 10

    def paginate_qustion(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTION_PER_SHELF
        end = start + QUESTION_PER_SHELF
        question = [q.format() for q in selection]
        current_question = question[start:end]

        return current_question

    @app.route('/categories')
    def get_all_catogaries():
        try:
            id_list = []
            type_list = []
            for u in categories:
                id_list.append(u.id)
                type_list.append(u.type)
            cat_dict = dict(zip(id_list, type_list))

        except:
            # abort 404 if no categories found
            if (len(cat_dict) == 0):
                abort(404)

        # return data to view
        return jsonify({
            'success': True,
            'categories': cat_dict
        })

    ''' 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories.
    '''

    @app.route('/questions')
    def get_questions():
        current_questions = Question.query.first()
        current_categories = Category.query.filter(
            Category.type == current_questions.category).one_or_none().format()
        try:
            error = False
            question_list = []
            for q in Question.query.filter_by(category = current_categories.get('type')):
                question_list.append(q)

        except:
            error = True
            abort(422)
        finally:
            p_q = paginate_qustion(request, current_questions.format())
            return jsonify({
                'Catogaries': [c.format() for c in categories],
                'Current category': current_categories,
                'totalQustion': len(question_list),
                'questions': current_questions.format()
            })



    '''
    Create an endpoint to DELETE question using a question ID. 
  
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''

    @app.route('/questions/<int:id>/delete', methods=['DELETE'])
    @cross_origin()
    def delete_question(id):
        # delete via id
        question = Question.query.filter(Question.id == id).one_or_none()
        if question is None:
            abort(404)
        question.delete()
        return jsonify({"total books": len(Question.query.all()),
                        'qustions state': 'deleted successfully',
                        'delete Queston ID':id})
        # return render_template(url_for(get_questions))

    '''
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.  
    '''

    @app.route('/create/question', methods=['POST'])
    def create_question():
        try:
            body = request.get_json()
            new_qus = body.get('question', None)
            new_answer = body.get('answer', None)
            catog = body.get('rate', None)
            diff = body.get('difficulty', None)
            question = Question(question=new_qus, answer=new_answer, category=catog, difficulty=diff)
            question.insert()
        except:
            abort(202)
        finally:
            return jsonify({
                "successful": True,
                "total books": len(Question.query.all()),
                "messege": 'Created',
                'created_question_id': question.id
            })

    ''' 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 
    '''

    @app.route('/search/question', methods=['GET', 'POST'])
    def search_question():
        body = request.get_json()
        search_term = body.get('title', None)
        qSearch = Question.query.filter(
            Question.question.ilike("%{}%".format(search_term))).all()
        # method search_qustion declared in the Question class
        r = Question.search_qustion(search_term, qSearch)
        count = len(qSearch)
        if count is None:
            abort(202)
        return jsonify({
            "count": count,
            "question searched": [r for r in qSearch]
        })

    '''
    Create a GET endpoint to get questions based on category.  
    '''

    @app.route('/questions/categories')
    def category_question():
        error = False
        try:
            id_list_q = []
            question_list = []
            answer_list = []
            category_list = []
            difficulty_list = []
            #questions and categories in global variable for Questions  and Categories query defined top of the code
            for u in questions:
                id_list_q.append(u.id)
                question_list.append(u.question)
                answer_list.append(u.answer)
                category_list.append(u.category)
                difficulty_list.append(u.difficulty)
                # categories_dict = dict(zip(question_list, category_list))
            question_list_per_cat = []
            cat_for_qus = []
            for c in categories:
                for q in questions:
                    if q.category == c.type:
                        question_list_per_cat.append(q.question)
                        cat_for_qus.append(c.type)
                # qus_cat_dict = dict(zip(cat_for_qus, question_list_per_cat))
            allQues = []
            for q in zip(cat_for_qus, question_list_per_cat):
                allQues.append("{}: {}".format(*q))
        except:
            error = True
            abort(404)

        finally:
            return jsonify({'statues: ': 'Successfully done',
                            'error': error,
                            'Questions per catogery': [q for q in allQues]
                            })

    ''' 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 
   
    '''

    @app.route('/questions/quiz', methods=['POST', 'GET'])
    def quiz_question():
        question_list_per_cat = []
        cat_for_qus = []
        # body = request.get_json()
        # answer = body.get('answer', None)
        try:
            #questions and categories in global variable for Questions  and Categories query defined top of the code
            for c in categories:
                for q in questions:
                    if c.type == q.category:
                        question_list_per_cat.append(q.question)
                        cat_for_qus.append(q.category)
            answer = 'football'

        except:
            abort(404)
        finally:
            random_qus = random.choice(question_list_per_cat)
            random_qus_query = Question.query.filter(Question.question == random_qus).one_or_none()
            if random_qus_query.answer == answer:
                true_or_false = True
            else:
                true_or_false = False
            return jsonify({'random question ': random_qus,
                            'Answer': true_or_false,
                            'categories': cat_for_qus
                            })

    '''
    Error handlers for all expected errors 
    including 404, 422 and 500. 
    '''

    # error handlers

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "sorry not found try another things"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable "
        }), 422

    @app.errorhandler(500)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error "
        }), 500

    return app

# coded by Alfatih
