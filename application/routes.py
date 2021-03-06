from application import app, db
from flask import render_template, request, redirect, url_for, flash, abort, session, jsonify, Blueprint
import json
import os.path
from werkzeug.utils import secure_filename
from application.models import Url

bp = Blueprint('urlshort', __name__)

@bp.route('/')
def home():
    shorturl = Url.objects.order_by("-code")
    return render_template('home.html', codes=shorturl, home=True)
    # return render_template('home.html', codes=session.keys())

@bp.route('/your-url', methods=['GET', 'POST'])
def your_url():
    if request.method == 'POST':
        urls = {}
        code = request.form['code']
        
        if os.path.exists('urls.json'):
            with open('urls.json') as urls_file:
                urls = json.load(urls_file)

        if code in urls.keys():
            flash('That short name has already been taken. Please select another name.')
            return redirect(url_for('urlshort.home'))

        # urls 
        if 'url' in request.form.keys():
            url = request.form['url']
            urls[code] = {'url': url}
            shorturl = Url(code=code, url=url)
            shorturl.save()
        # files
        else:
            f = request.files['file']
            full_name = code + secure_filename(f.filename)
            f.save('D:/Projects/Flask/short-url-creator/application/static/user_files/' + full_name)
            urls[code] = {'file': full_name}

        with open('urls.json', 'w') as url_file:
            json.dump(urls, url_file)
            session[code] = True

        return render_template('your_url.html', code=code)
    else:
        return redirect(url_for('urlshort.home'))

@bp.route('/<string:code>')
def redirect_to_url(code):
    if os.path.exists('urls.json'):
        with open('urls.json') as urls_file:
            urls = json.load(urls_file)
            if code in urls.keys():
                if 'url' in urls[code].keys():
                    return redirect(urls[code]['url'])
                else:
                    return redirect(url_for('static', filename='user_files/' + urls[code]['file']))

    return abort(404)

@bp.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

@bp.route('/api')
def session_api():
    return jsonify(list(session.keys()))
