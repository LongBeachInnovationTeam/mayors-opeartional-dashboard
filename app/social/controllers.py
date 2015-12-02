from flask import Blueprint, render_template
import requests

social = Blueprint('social', __name__)

@social.route('/social')
def index():
	print "hello"
	return render_template('social/social_media.html')