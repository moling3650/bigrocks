#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-05-05 10:20:40
# @Author  : moling li (moling3650@gmail.com)
# @Version : 0.2

import os
from flask import Flask, redirect, url_for, request, session, render_template, flash
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import StringField, SelectField, SubmitField, TextAreaField
from wtforms.validators import Length
from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug import secure_filename
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SECRET_KEY'] = 'hard to guess string'

UPLOAD_FOLDER = 'images/'
FIELDS = ['Name', 'Function', 'OTSR', 'Commitment']
IMAGES = ['jpg', 'jpeg', 'png', 'gif', 'bmp']

# table class
class User(db.Model):
    __tablename__ = 'users'
    id         = db.Column(db.Integer, primary_key=True)
    Name       = db.Column(db.Unicode(24), index=True)
    Function   = db.Column(db.String(8))
    image      = db.Column(db.String(64))
    OTSR       = db.Column(db.String(24))
    Commitment = db.Column(db.Unicode(256))
    # openID     = db.Column(db.Integer)

# from class
class SubmitForm(Form):
    Name       = StringField('Name', validators=[Length(1, 20)])
    Function   = SelectField('Function', choices=[('IT', 'IT'),
                                                  ('CMK', 'CMK'),
                                                  ('PS', 'PS'),
                                                  ('HR', 'HR'),
                                                  ('Finance', 'Finance'),
                                                  ('Other', 'Others')])
    image      = FileField('Photo')
    upload     = SubmitField('Upload')
    OTSR       = SelectField('O-TSR', choices=[('Sales Growth', 'Sales Growth'),
                                               ('Margin Improvement', 'Margin Improvement'),
                                               ('Asset Efficiency', 'Asset Efficiency')])
    Commitment = TextAreaField(validators=[Length(10, 140)])
    submit     = SubmitField('Submit')

    def image_validata(self):
        return self.image.validate(self, [FileRequired(),
                                          FileAllowed(IMAGES, 'Image only!')])


@app.route('/', methods=['GET', 'POST'])
def index():
    form = SubmitForm()
    # check validata on upload
    if form.upload.data and form.image_validata():
        image = UPLOAD_FOLDER + secure_filename(form.image.data.filename)
        form.image.data.save(os.path.join(app.static_folder, image))
        session['image'] = image    
    # check validata on submit
    if form.submit.data and form.validate():
        # check image is uploaded
        if session.get('image'):            
            # save the data of form in the session
            data = {field: form[field].data for field in FIELDS}        
            data['image'] = session.pop('image')
            session['data'] = data
            # insert the user's data into the database
            db.session.add(User(**data))
            db.session.commit()
            return redirect(url_for('success'))
        else:
            flash('you must upload your image!')

    return render_template('index.html', form=form, image=session.get('image'))

@app.route('/success')
def success():    
    return render_template('success.html', form=session.get('data'))

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')
    
if __name__ == '__main__':
    # db.drop_all()
    db.create_all()
    app.run()