# These routes are an example of how to use data, forms and routes to create
# a forum where a blogs and comments on those blogs can be
# Created, Read, Updated or Deleted (CRUD)

from app import app
import mongoengine.errors
from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from app.classes.data import Meditation
from app.classes.forms import MeditationForm
from flask_login import login_required
import datetime as dt



@app.route('/meditation/list')
@app.route('/meditations')
# This means the user must be logged in to see this page
@login_required
def meditationList():
    # This retrieves all of the 'blogs' that are stored in MongoDB and places them in a
    # mongoengine object as a list of dictionaries name 'blogs'.
    meditations = Meditation.objects()
    # This renders (shows to the user) the blogs.html template. it also sends the blogs object 
    # to the template as a variable named blogs.  The template uses a for loop to display
    # each blog.
    return render_template('meditations.html',meditations=meditations)

@app.route('/meditation/<meditationID>')
# This route will only run if the user is logged in.
@login_required
def meditation(meditationID):
    # retrieve the blog using the blogID
    thismeditation = Meditation.objects.get(id=meditationID)
    # If there are no comments the 'comments' object will have the value 'None'. Comments are 
    # related to blogs meaning that every comment contains a reference to a blog. In this case
    # there is a field on the comment collection called 'blog' that is a reference the Blog
    # document it is related to.  You can use the blogID to get the blog and then you can use
    # Send the blog object and the comments object to the 'blog.html' template.
    return render_template('meditation.html',meditation=thismeditation)
# This route actually does two things depending on the state of the if statement 
# 'if form.validate_on_submit()'. When the route is first called, the form has not 
# been submitted yet so the if statement is False and the route renders the form.
# If the user has filled out and succesfully submited the form then the if statement
# is True and this route creates the new blog based on what the user put in the form.
# Because this route includes a form that both gets and blogs data it needs the 'methods'
# in the route decorator.
@app.route('/meditation/new', methods=['GET', 'POST'])
# This means the user must be logged in to see this page
@login_required
# This is a function that is run when the user requests this route.
def meditationNew():
    # This gets the form object from the form.py classes that can be displayed on the template.
    form = MeditationForm()

    # This is a conditional that evaluates to 'True' if the user submitted the form successfully.
    # validate_on_submit() is a method of the form object. 
    if form.validate_on_submit():
        current_date = dt.date.today()
        startT = dt.datetime.combine(current_date, form.starttime.data)
        endT = dt.datetime.combine(current_date, form.endtime.data)
        # This stores all the values that the user entered into the new blog form. 
        # Blog() is a mongoengine method for creating a new blog. 'newBlog' is the variable 
        # that stores the object that is the result of the Blog() method.  
        newMeditation = Meditation(
            # the left side is the name of the field from the data table
            # the right side is the data the user entered which is held in the form object.
            starttime = startT,
            endtime = endT,
            takeaway = form.takeaway.data,
            pride = form.pride.data,
            name = form.name.data,
            meditationfile = form.meditationfile.data,
            meditationUrl = form.meditationUrl.data,
            # This sets the modifydate to the current datetime.
            modify_date = dt.datetime.utcnow
        )
        # This is a method that saves the data to the mongoDB database.
        newMeditation.save()

        # Once the new blog is saved, this sends the user to that blog using redirect.
        # and url_for. Redirect is used to redirect a user to different route so that 
        # routes code can be run. In this case the user just created a blog so we want 
        # to send them to that blog. url_for takes as its argument the function name
        # for that route (the part after the def key word). You also need to send any
        # other values that are needed by the route you are redirecting to.
        return redirect(url_for('meditation',meditationID=newMeditation.id))

    # if form.validate_on_submit() is false then the user either has not yet filled out
    # the form or the form had an error and the user is sent to a blank form. Form errors are 
    # stored in the form object and are displayed on the form. take a look at blogform.html to 
    # see how that works.
    return render_template('meditationform.html',form=form)



# This route enables a user to edit a blog.  This functions very similar to creating a new 
# blog except you don't give the user a blank form.  You have to present the user with a form
# that includes all the values of the original blog. Read and understand the new blog route 
# before this one. 
@app.route('/meditation/delete/<meditation>')
# Only run this route if the user is logged in.
@login_required
def meditationDelete(meditationID):
    # retrieve the blog to be deleted using the blogID
    deletemeditation = Meditation.objects.get(id=meditationID)
    # check to see if the user that is making this request is the author of the blog.
    # current_user is a variable provided by the 'flask_login' library.
    if current_user == deletemeditation.parent:
        #DO I NEED PARENT???? BECAUSE I CHANGED IT TO AUTHOR AND GOT RID OF PARENT
        # delete the blog using the delete() method from Mongoengine
        deletemeditation.delete()
        # send a message to the user that the blog was deleted.
        flash('The meditaion was deleted.')
    else:
        # if the user is not the author tell them they were denied.
        flash("You can't delete a meditaion you don't own.")
    # Retrieve all of the remaining blogs so that they can be listed.
    meditations = Meditation.objects()  
    # Send the user to the list of remaining blogs.
    return render_template('meditations.html',meditations=meditations)
#SHOULD I EDIT '/deer/edit???
@app.route('/meditation/edit/<meditationID>', methods=['GET', 'POST'])
@login_required
def meditationEdit(meditationID):
    editmeditation = Meditation.objects.get(id=meditationID)
    # if the user that requested to edit this blog is not the author then deny them and
    # send them back to the blog. If True, this will exit the route completely and none
    # of the rest of the route will be run.
    if current_user != editmeditation.parent:
        #DO YOU NEED PARENT????
        flash("You can't edit a mediation you havnt done.")
        return redirect(url_for('meditation',meditationID=meditationID))
    # get the form object
    form = MeditationForm()
    # If the user has submitted the form then update the blog.
    if form.validate_on_submit():
        # update() is mongoengine method for updating an existing document with new data.
        editmeditation.update(
            starttime = form.starttime.data,
            endtime = form.endtime.data,
            takeaway = form.takeaway.data,
            pride = form.pride.data,
            submit = form.submit.data,
            modify_date = dt.datetime.utcnow
        )
        # After updating the document, send the user to the updated blog using a redirect.
        return redirect(url_for('meditation',meditationID=meditationID))

    # if the form has NOT been submitted then take the data from the editBlog object
    # and place it in the form object so it will be displayed to the user on the template.
    form.starttime.data = editmeditation.startime
    form.endtime.data = editmeditation.endtime
    form.takeaway.data = editmeditation.takeaway
    form.pride.data = editmeditation.pride
    form.submit.data = editmeditation.submit
    #DO I NEED MODIFY DATE? DO I NEED SUBMIT
 


    # Send the user to the blog form that is now filled out with the current information
    # from the form.
    return render_template('meditation.html',form=form)
