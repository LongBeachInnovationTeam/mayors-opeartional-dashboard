from flask import Blueprint, render_template
import requests
from requests_oauthlib import OAuth1
import json
import collections

social = Blueprint('social', __name__)

FB_ACCESS_TOKEN = 'CAACEdEose0cBAMZB23nc3yrzRzyukmXruZAQfLroMlKcVXL97vC4rDkBXFkfhWDjsRPGTzZCOf6dUJUgEd62cukjvFbJMCQtUButhRZAvEFCdzNpgf3S8ef79HHTnixIKRWN4FdFo21qWhZCniyPmhyBXGwM5Hkg5C2a5K6VNSn4arkgtnYBYyUciCZAUY6NsZD'
FB_DATA_URL = 'https://graph.facebook.com/v2.5/LBMayorsOffice?fields=insights,posts%7Bid%2Cmessage%2Ctype%2Cinsights%7D&access_token=' + FB_ACCESS_TOKEN

def get_page_stats(insights_data):
	page_stats = {}
	for i in range(0, len(insights_data)):
		metric = insights_data[i]
		if metric['name'] == 'page_posts_impressions_unique' and metric['period'] == 'days_28':
			page_stats['posts_impressions_unique'] = metric['values']
		if metric['name'] == 'page_impressions_by_story_type_unique' and metric['period'] == 'days_28':
			page_stats['impressions_by_story_type_unique'] = metric['values']
		if metric['name'] == 'page_impressions_by_age_gender_unique' and metric['period'] == 'days_28':
			page_stats['impressions_by_age_gender_unique'] = metric['values']
		if metric['name'] == 'page_impressions_by_city_unique' and metric['period'] == 'days_28':
			page_stats['impressions_by_city_unique'] = metric['values']
		if metric['name'] == 'page_fans' and metric['period'] == 'lifetime':
			page_stats['fans'] = metric['values']
	return page_stats

def get_top_posts(posts_data):

	top_posts = {}
	for i in range(0, len(posts_data)):

		# Get post and insights data from response
		post = posts_data[i]
		insights_data = post['insights']['data']

		# Instantiate default attributes that might not be defined for a post
		message = ''
		unique_impressions = 0
		engaged_users = 0
		shares = 0
		likes = 0
		comments = 0

		for i in insights_data:
			if i['name'] == 'post_story_adds_by_action_type':
				values = i['values']
				post_values = values[0]['value']
				if 'like' in post_values:
					likes = post_values['like']
				if 'comment' in post_values:
					comments = post_values['comment']
				if 'share' in post_values:
					shares = post_values['share']
			if i['name'] == 'post_impressions_unique':
				values = i['values']
				unique_impressions = values[0]['value']
			if i['name'] == 'engaged_users':
				engaged_users = values[0]['value']

		# Get attributes for a post
		post_id = post['id']
		post_type = post['type']

		if 'message' in post:
			message = post['message']
			message = message[0:130] + '...'

		# Add post and its attributes to our dictionary
		top_posts[post_id] = {
			'post_type': post_type,
			'message': message,
			'unique_impressions': unique_impressions,
			'engaged_users': engaged_users,
			'shares': shares,
			'likes': likes,
			'comments': comments
		}

	# Order posts by unique_impressions
	ordered_top_posts = collections.OrderedDict(
		sorted(
			top_posts.items(),
			key=lambda t: t[1]['unique_impressions'],
			reverse=True
		)
	)

	return ordered_top_posts

@social.route('/social')
def index():

	# Fetch Facebook data from their API
	r = requests.get(FB_DATA_URL)
	fb_json = r.json()
	fb_posts_data = fb_json['posts']['data']
	fb_insights_data = fb_json['insights']['data']

	top_posts = get_top_posts(fb_posts_data)
	page_stats = get_page_stats(fb_insights_data)

	return render_template('social/social_media.html', top_facebook_posts=top_posts)