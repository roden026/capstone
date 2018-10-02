from flask import render_template, flash, redirect
from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user
from app.models import User
from app.models import Review
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from flask import url_for
from app import db
from app.forms import RegistrationForm, SurveyForm
from datetime import datetime
from app.forms import EditProfileForm
from app.forms import PostForm
from app.models import Post
import pandas as pd
from topics import predict_topic
import prediction
import os

# plotting modules
from bokeh.models import HoverTool, FactorRange, Plot, LinearAxis, Grid, Range1d
from bokeh.models.glyphs import VBar
from bokeh.plotting import figure
from bokeh.embed import file_html
from bokeh.resources import CDN
from bokeh.models.sources import ColumnDataSource
from bokeh import palettes
from plotting import create_bar_chart, create_hover_tool
import numpy as np

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("index.html", title='Explore', posts=posts.items,
                          next_url=next_url, prev_url=prev_url)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/survey', methods=['GET', 'POST'])
def survey():
    form = SurveyForm()
    if form.validate_on_submit():

        review = Review(
            content = form.content.data,
            overall_rating = form.overall_rating.data,
            type_traveller = form.type_traveller.data,
            cabin_flown = form.cabin_flown.data,
            seat_comfort_rating = form.seat_comfort_rating.data,
            cabin_staff_rating = form.cabin_staff_rating.data,
            food_beverages_rating = form.food_beverages_rating.data,
            inflight_entertainment_rating = form.inflight_entertainment_rating.data,
            ground_service_rating = form.ground_service_rating.data,
            wifi_connectivity_rating = form.wifi_connectivity_rating.data,
            value_money_rating = form.value_money_rating.data)
        db.session.add(review)
        db.session.commit()

        return redirect(url_for('results'))
    return render_template('survey.html', title='Survey', form=form)

@app.route('/results', methods=['GET', 'POST'])
def results():
    # get most recent review (the one that was just submitted)
    record = Review.query.order_by(Review.timestamp.desc()).first_or_404()

    # build a dictionary from the record to then construct a dataframe for the record
    dict = {
        'content': record.content,
        'overall_rating' : record.overall_rating,
        'type_traveller' : record.type_traveller,
        'cabin_flown' : record.cabin_flown,
        'seat_comfort_rating' : record.seat_comfort_rating,
        'cabin_staff_rating' : record.cabin_staff_rating,
        'food_beverages_rating' : record.food_beverages_rating,
        'inflight_entertainment_rating' : record.inflight_entertainment_rating,
        'ground_service_rating' : record.ground_service_rating,
        'wifi_connectivity_rating' : record.wifi_connectivity_rating,
        'value_money_rating' : record.value_money_rating}

    # make dataframe
    df = pd.DataFrame(dict, index=[0])

    # get predicted topics - returns list of topics and distributions
    topic, topic_probability_scores = predict_topic([df['content']])
    best_topic = np.argmax(topic_probability_scores[0])+1

    # Get text only predciction using mechanism that could be used on twitter - returns prediction and prediction probability
    text_pred, text_prob = prediction.text_only_predict(df['content'])
    text_prob = text_prob[0]

    # predict using full survey data - returns prediction and prediction probability
    full_pred, full_prob = prediction.predict_recommend(df)
    full_prob = full_prob[0]

    text_data = {"Recommend": ['No', 'Yes'], "Probability": [text_prob[0], text_prob[1]], 'color': list(palettes.viridis(2))}
    full_data = {"Recommend": ['No', 'Yes'], "Probability": [full_prob[0], full_prob[1]], 'color': list(palettes.viridis(2))}

    # make visualization interactive
    text_hover = create_hover_tool()
    full_hover = create_hover_tool()

    # generate prediction probability bar charts
    text_plot = create_bar_chart(text_data, "Recommend Prob", "Recommend","Probability", text_hover)
    text_html = file_html(text_plot, CDN, "text_plot")
    cwd = os.getcwd()
    template_dir = "C:\\Users\\erroden\\Desktop\\Capstone\\microblog\\app\\templates"
    os.chdir(template_dir)
    with open("text_chart.html", "w") as f:
        f.write(text_html)

    # generate prediction probability bar charts
    full_plot = create_bar_chart(full_data, "Recommend Prob", "Recommend","Probability", full_hover)
    full_html = file_html(full_plot, CDN, "full_plot")
    with open("full_chart.html", "w") as f:
        f.write(full_html)

    os.chdir(cwd)
    # render results template with prediction data
    return render_template('results.html', record=record, topics=topic,
        text_pred=text_pred, full_pred=full_pred, full_html=full_html,
        text_html=text_html, best_topic=best_topic)
