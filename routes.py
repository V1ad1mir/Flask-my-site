from flask import Blueprint, render_template, request, flash, redirect
import os
from random import shuffle
from werkzeug.utils import secure_filename

import server_operations


main_bp = Blueprint('main', __name__)


@main_bp.route('/test') 
def index():
    return "test"


@main_bp.route('/photos')
def photos():
    """
    Renders a page displaying all the photos in the 'static/uploads' folder, randomly sorted.
    """
    photo_folder = 'static/uploads'
    photo_files = os.listdir(photo_folder)
    shuffle(photo_files)
    return render_template('photos.html', photos=photo_files)

@main_bp.route('/question', methods=['GET', 'POST'])    
def question():
    try:
        all_questions_list = server_operations.get_all_community_questions()
        
        # Check if the "Show questions with answers only" checkbox is checked
        checkbox_answers = request.args.get('answered', False, type=bool)
        
        # Filter the questions based on the checkbox value
        filtered_questions_list = all_questions_list if not checkbox_answers else [q for q in all_questions_list if q['answer'] is not None]
        
        return render_template('ask_others.html', all_questions=filtered_questions_list, show_answered_questions=checkbox_answers)    
    except Exception as e:
        flash('An error occurred: {}'.format(str(e)), 'error')
        return render_template('ask_others.html')
    


