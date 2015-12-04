from flask import Blueprint, render_template
import requests
from requests_oauthlib import OAuth1
import json
import collections

social = Blueprint('social', __name__)

FB_ACCESS_TOKEN = '470735709779695|qgN3i_WmdasalQYkfa5yOHt7VuQ'
FB_DATA_URL = 'https://graph.facebook.com/v2.5/iteamlb?fields=insights,posts%7Bid%2Cshares%2Clikes%2Ccomments%2Cmessage%2Ctype%7D&access_token=' + FB_ACCESS_TOKEN

def get_top_posts():

	# Fetch response from HTTP request
	r = requests.get(FB_DATA_URL)
	posts_json = r.json()
	posts_data = posts_json['posts']['data']

	top_posts = {}
	for i in range(0, len(posts_data)):
		post = posts_data[i]

		# Instantiate default attributes that might not be defined for a post
		message = ''
		shares = 0
		likes = 0
		comments = 0

		# Get attributes for a post
		post_id = post['id']
		post_type = post['type']

		if 'message' in post:
			message = post['message']
		if 'shares' in post:
			shares = int(post['shares']['count'])
		if 'likes' in post:
			likes = int(len(post['likes']['data']))
		if 'comments' in post:
			comments = int(len(post['comments']['data']))

		# Add post and its attributes to our dictionary
		top_posts[post_id] = {
			'post_type': post_type,
			'message': message,
			'shares': shares,
			'likes': likes,
			'comments': comments,
			'popularity_score': shares + likes + comments
		}

	# Order posts by popularity_score
	ordered_top_posts = collections.OrderedDict(
		sorted(
			top_posts.items(),
			key=lambda t: t[1]['popularity_score'],
			reverse=True
		)
	)

	return ordered_top_posts

@social.route('/social')
def index():
	top_posts = get_top_posts()

	print top_posts

	# r = requests.get(FB_INSIGHTS_URL)
	# insights_json = r.json()
	# insights_data = insights_json['insights']['data']
	# for index in range(0, len(insights_data)):
	# 	metric_name = insights_data[index]['name']
	# 	if metric_name == 'page_impressions_by_story_type':
	# 		print insights_data[index]

	return render_template('social/social_media.html', top_facebook_posts=top_posts)