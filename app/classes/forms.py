# This file is where data entry forms are created. Forms are placed on templates 
# and users fill them out.  Each form is an instance of a class. Forms are managed by the 
# Flask-WTForms library.

from flask_wtf import FlaskForm
import mongoengine.errors
from wtforms.validators import URL, Email, DataRequired, NumberRange
from wtforms.fields.html5 import URLField, DateField, IntegerRangeField, EmailField
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, SelectField, FileField, RadioField
from wtforms_components import TimeField

class ProfileForm(FlaskForm):
    role = SelectField('Role',choices=[("Teacher","Teacher"),("Student","Student")])
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()]) 
    image = FileField("Image") 
    submit = SubmitField('Post')

class ConsentForm(FlaskForm):
    adult_fname = StringField('First Name',validators=[DataRequired()])
    adult_lname = StringField('Last Name',validators=[DataRequired()])
    adult_email = EmailField('Email',validators=[Email()])
    consent = RadioField('Do you want your parents or teachers to see your sleep data/graph', choices=[(True,"True"),(False,"False")])
    submit = SubmitField('Submit')

class SleepForm(FlaskForm):
    rating = SelectField("How would you rate your sleep: 5 is great, 1 is poor", choices=[(None,'---'),(1,1),(2,2),(3,3),(4,4),(5,5)], validators=[DataRequired()])
    starttime = TimeField("Start Time")   
    endtime = TimeField("End Time")   
    feel = SelectField("How did you feel when you woke up: 5 is great, 1 is poor", choices=[(None,'---'),(1,1),(2,2),(3,3),(4,4),(5,5)], validators=[DataRequired()])
    sleep_date = DateField("What date did you go to sleep")
    wake_date = DateField("What date did you wake up")
    minstosleep = IntegerField("How many minutes did it take you to fall asleep?", validators=[NumberRange(min=0,max=180, message="Enter a number between 0 and 180.")])
    submit = SubmitField("Submit")

class BlogForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired()])
    content = TextAreaField('Blog', validators=[DataRequired()])
    tag = StringField('Tag', validators=[DataRequired()])
    rating = IntegerField('Number Rating', validators=[DataRequired()] )
    submit = SubmitField('Blog')

class MeditationForm(FlaskForm):
    meditationfile = FileField("download then attach your meditation")
    meditationUrl = StringField("copy paste the url here")
    starttime = TimeField("Start Time of Meditation") 
    name = StringField("Name your meditation")
    endtime = TimeField("End Time of Meditation")  
    takeaway = StringField('What are some Takeaways?', validators=[DataRequired()])
    pride = StringField('What are you proud of?', validators=[DataRequired()])
    submit = SubmitField('Submit')
    

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Comment')
    
class ClinicForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    streetAddress = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    zipcode = StringField('Zipcode',validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')