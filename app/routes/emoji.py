# These routes are an example of how to use data, forms and routes to create
# a forum where a blogs and comments on those blogs can be
# Created, Read, Updated or Deleted (CRUD)

from app import app
import mongoengine.errors
from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from app.classes.data import Emoji
from app.classes.forms import EmojiForm
from flask_login import login_required
import datetime as dt

# This is the route to list all blogs
@app.route('/emoji/list')
@app.route('/emojis')
# This means the user must be logged in to see this page
@login_required
def emojiList():
    # This retrieves all of the 'blogs' that are stored in MongoDB and places them in a
    # mongoengine object as a list of dictionaries name 'blogs'.
    emojis = Emoji.objects()
    # This renders (shows to the user) the blogs.html template. it also sends the blogs object 
    # to the template as a variable named blogs.  The template uses a for loop to display
    # each blog.
    return render_template('emojis.html',emojis=emojis)

# This route will get one specific blog and any comments associated with that blog.  
# The blogID is a variable that must be passsed as a parameter to the function and 
# can then be used in the query to retrieve that blog from the database. This route 
# is called when the user clicks a link on bloglist.html template.
# The angle brackets (<>) indicate a variable. 
@app.route('/emoji/<emojiID>')
# This route will only run if the user is logged in.
@login_required
def emoji(emojiID):
    # retrieve the blog using the blogID
    thisEmoji = Emoji.objects.get(id=emojiID)
    # If there are no comments the 'comments' object will have the value 'None'. Comments are 
    # related to blogs meaning that every comment contains a reference to a blog. In this case
    # there is a field on the comment collection called 'blog' that is a reference the Blog
    # document it is related to.  You can use the blogID to get the blog and then you can use
    # the blog object (thisBlog in this case) to get all the comments.
    # Send the blog object and the comments object to the 'blog.html' template.
    return render_template('emoji.html',emoji=thisEmoji)

# This route will delete a specific blog.  You can only delete the blog if you are the author.
# <blogID> is a variable sent to this route by the user who clicked on the trash can in the 
# template 'blog.html'. 
# TODO add the ability for an administrator to delete blogs. 
@app.route('/emoji/delete/<emojiID>')
# Only run this route if the user is logged in.
@login_required
def emojiDelete(emojiID):
    # retrieve the blog to be deleted using the blogID
    deleteEmoji = Emoji.objects.get(id=emojiID)
    # check to see if the user that is making this request is the author of the blog.
    # current_user is a variable provided by the 'flask_login' library.
    if current_user == deleteEmoji.author:
        # delete the blog using the delete() method from Mongoengine
        deleteEmoji.delete()
        # send a message to the user that the blog was deleted.
        flash('The Emoji was deleted.')
    else:
        # if the user is not the author tell them they were denied.
        flash("You can't delete a emoji you don't own.")
    # Retrieve all of the remaining blogs so that they can be listed.
    emojis = Emoji.objects()  
    # Send the user to the list of remaining blogs.
    return render_template('emojis.html',emojis=emojis)

# This route actually does two things depending on the state of the if statement 
# 'if form.validate_on_submit()'. When the route is first called, the form has not 
# been submitted yet so the if statement is False and the route renders the form.
# If the user has filled out and succesfully submited the form then the if statement
# is True and this route creates the new blog based on what the user put in the form.
# Because this route includes a form that both gets and blogs data it needs the 'methods'
# in the route decorator.
@app.route('/emoji/new', methods=['GET', 'POST'])
# This means the user must be logged in to see this page
@login_required
# This is a function that is run when the user requests this route.
def emojiNew():
    # This gets the form object from the form.py classes that can be displayed on the template.
    form = EmojiForm()

    # This is a conditional that evaluates to 'True' if the user submitted the form successfully.
    # validate_on_submit() is a method of the form object. 
    if form.validate_on_submit():

        # This stores all the values that the user entered into the new blog form. 
        # Blog() is a mongoengine method for creating a new blog. 'newBlog' is the variable 
        # that stores the object that is the result of the Blog() method.  
        newEmoji = Emoji(
            # the left side is the name of the field from the data table
            # the right side is the data the user entered which is held in the form object.
            emote = form.emote.data,
            location = form.location.data,
            time = form.time.data,
            author = current_user.id,
            dow = form.dow.data,
            # This sets the modifydate to the current datetime.
            modify_date = dt.datetime.utcnow
        )
        # This is a method that saves the data to the mongoDB database.
        newEmoji.save()

        # Once the new blog is saved, this sends the user to that blog using redirect.
        # and url_for. Redirect is used to redirect a user to different route so that 
        # routes code can be run. In this case the user just created a blog so we want 
        # to send them to that blog. url_for takes as its argument the function name
        # for that route (the part after the def key word). You also need to send any
        # other values that are needed by the route you are redirecting to.
        return redirect(url_for('emoji',emojiID=newEmoji.id))

    # if form.validate_on_submit() is false then the user either has not yet filled out
    # the form or the form had an error and the user is sent to a blank form. Form errors are 
    # stored in the form object and are displayed on the form. take a look at blogform.html to 
    # see how that works.
    return render_template('emojiform.html',form=form)


# This route enables a user to edit a blog.  This functions very similar to creating a new 
# blog except you don't give the user a blank form.  You have to present the user with a form
# that includes all the values of the original blog. Read and understand the new blog route 
# before this one. 
@app.route('/emoji/edit/<emojiID>', methods=['GET', 'POST'])
@login_required
def emojiEdit(emojiID):
    editEmoji = Emoji.objects.get(id=emojiID)
    # if the user that requested to edit this blog is not the author then deny them and
    # send them back to the blog. If True, this will exit the route completely and none
    # of the rest of the route will be run.
    if current_user != editEmoji.author:
        flash("You can't edit a emoji you don't own.")
        return redirect(url_for('emoji',emojiID=emojiID))
    # get the form object
    form = EmojiForm()
    # If the user has submitted the form then update the blog.
    if form.validate_on_submit():
        # update() is mongoengine method for updating an existing document with new data.
        editEmoji.update(
            emote = form.emote.data,
            location = form.location.data,
            time = form.time.data,
            dow = form.dow.data,
            
            modify_date = dt.datetime.utcnow
        )
        # After updating the document, send the user to the updated blog using a redirect.
        return redirect(url_for('emoji',emojiID=emojiID))

    # if the form has NOT been submitted then take the data from the editBlog object
    # and place it in the form object so it will be displayed to the user on the template.
    form.emote.data = editEmoji.emote
    form.location.data = editEmoji.location
    form.time.data = editEmoji.time
    form.dow.data = editEmoji.dow


    # Send the user to the blog form that is now filled out with the current information
    # from the form.
    return render_template('emojiform.html',form=form)

#####
# the routes below are the CRUD for the comments that are related to the blogs. This
# process is exactly the same as for blogs with one addition. Each comment is related to
# a specific blog via a field on the comment called 'blog'. The 'blog' field contains a 
# reference to the Blog document. See the @app.route('/blog/<blogID>') above for more details
# about how comments are related to blogs.  Additionally, take a look at data.py to see how the
# relationship is defined in the Blog and the Comment collections.

# @app.route('/comment/new/<blogID>', methods=['GET', 'POST'])
# @login_required
# def commentNew(blogID):
#     blog = Blog.objects.get(id=blogID)
#     form = CommentForm()
#     if form.validate_on_submit():
#         newComment = Comment(
#             author = current_user.id,
#             blog = blogID,
#             emoji = form.emoji.data
#         )
#         newComment.save()
#         return redirect(url_for('blog',blogID=blogID))
#     return render_template('commentform.html',form=form,blog=blog)

# @app.route('/comment/edit/<commentID>', methods=['GET', 'POST'])
# @login_required
# def commentEdit(commentID):
#     editComment = Comment.objects.get(id=commentID)
#     if current_user != editComment.author:
#         flash("You can't edit a comment you didn't write.")
#         return redirect(url_for('blog',blogID=editComment.blog.id))
#     blog = Blog.objects.get(id=editComment.blog.id)
#     form = CommentForm()
#     if form.validate_on_submit():
#         editComment.update(
#             emoji = form.emoji.data,
#             modifydate = dt.datetime.utcnow
#         )
#         return redirect(url_for('blog',blogID=editComment.blog.id))

#     form.content.data = editComment.content

#     return render_template('commentform.html',form=form,blog=blog)   

# @app.route('/comment/delete/<commentID>')
# @login_required
# def commentDelete(commentID): 
#     deleteComment = Comment.objects.get(id=commentID)
#     deleteComment.delete()
#     flash('The comments was deleted.')
#     return redirect(url_for('blog',blogID=deleteComment.blog.id)) 
