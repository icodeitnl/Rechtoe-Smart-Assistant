
import os, requests, json,sys
from flask import Flask, session, render_template, request, redirect, abort, jsonify, flash, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from passlib.hash import pbkdf2_sha256
from termcolor import colored
import pdfkit
from passlib.hash import pbkdf2_sha256
import re
import pandas as pd
import spacy
from spacy import displacy
import nl_core_news_md
nlp = spacy.load('nl_core_news_md')

app = Flask(__name__)

# Configures session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.secret_key = "secret"

# Starts SQLAlchemy application. Creates a Dialect object tailored towards PostgreSQL located at Heroku.
engine = create_engine('postgres://luqgsycesqadey:53850e3d9d775e0e69631be7a4737d1925ea048324e296702d227ffe4b4f0671@'
                                 'ec2-79-125-6-250.eu-west-1.compute.amazonaws.com:5432/d774k5a0k1jeqp')
# Ensures multipler user access to database through different accounts
db = scoped_session(sessionmaker(bind=engine))




@app.route("/", methods=['GET', 'POST'])
def index():
    # TODO: login required
    # TODO: flash messages

    #Prompts user to log in as session variable ‘username’ is not set.
    return render_template("index.html")
@app.route("/notfoun", methods=['GET', 'POST'])
def notfound():    
    return render_template("notfound.html")
@app.route("/login", methods=['GET', 'POST'])
def login():

    # If form is submitted
    if request.method == "POST":
    # Retrieve user data
        username = request.form.get("username")
        pw = request.form.get("password")

        #Check if user is registered
        user_data=db.execute("SELECT psswrd, user_id FROM users WHERE username = :username", {"username": username}).fetchone()

        if user_data is None:

            flash ("No user was found")

        # Create session object (dictionary object containing key-value pairs of session variables and associated values).
        # Set ‘username’ as session variable  and key as the unique input from the user. 
        if pbkdf2_sha256.verify(pw, user_data.psswrd) == True:
            
            session["username"] = username
            session["logged_in"] = True
            session["user_id"] = user_data.user_id
            flash("You are logged in")
            return render_template("form.html")

    #If form is not submitted  
    else:      
        flash ("Enter your details to login.")
        return render_template("index.html")
           
@app.route("/register", methods=["POST"])
def register():
    # If form is submitted
    if request.method == "POST":

        # If the user is registered
        username = request.form.get("username")
        name = request.form.get("name")
        pw = request.form.get("password")

        new_user = db.execute("SELECT username, name FROM users WHERE username = :username AND name = :name", {"username": username, "name": name}).fetchone()
        
        if  new_user is None:
            hsh = pbkdf2_sha256.encrypt(pw, rounds=200000, salt_size=16)

            db.execute("INSERT INTO users (username, name, psswrd) VALUES (:username, :name, :pw)", {"username": username, "name": name, "pw": hsh})
            db.commit()

            return redirect(url_for("index"))
   
        else:    
            return render_template("notfound.html")
             #If form is not submitted  
    else:      
        flash ("Enter your details to login.")
        return render_template("notfound.html")  
   

@app.route('/logout')
def logout():
    # remove the username from the session if it is there (remove value from the value-key pair 
    # of session variables and associated values)
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for("index"))  

@app.route('/form',methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        rawtext = request.form['rawtext']
        docx = nlp(rawtext)
        redacted_sentences = []
        for ent in docx.ents:
            ent.merge()
        for token in docx:
            if token.ent_type_ == 'PERSON':
                redacted_sentences.append("[PERSON_NAME]")
            elif token.ent_type_ == 'DATE':
                redacted_sentences.append("[DATE]")
            elif token.ent_type_ == 'ORG':
                redacted_sentences.append("[ORG]")
            elif token.ent_type_ == 'GPE':
                redacted_sentences.append("[LOCATION]")
            elif token.ent_type_ == 'NORP':
                redacted_sentences.append("[REDACTED]")
            else:
                redacted_sentences.append(token.string)
        redacted_text = "".join(redacted_sentences)
    return render_template("form.html", redacted_text=redacted_text)
if __name__ == "__main__":
    app.run(debug = True)
