#!/usr/bin/env python

import webapp2 # web application framework
import jinja2  # template engine
import os 	   # access file system
import csv
from google.appengine.api import users	# Google account authentication
from google.appengine.ext import db		# datastore

# initialise template
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Contact(db.Expando): # allows for different number of fields
	''' User data model '''
	pid = db.StringProperty(required=True)  # string = 500 char, allow field to be indexed, perform faster
	name = db.StringProperty(required=True)
	class12 = db.StringProperty(required=True)
	email = db.EmailProperty(required=True)
	handphone = db.StringProperty(required=False)
	tickets_csjh = db.StringProperty(required=False)
	tickets_edssh = db.StringProperty(required=False)
	remark = db.TextProperty()

	
class MainHandler(webapp2.RequestHandler):
	''' Home page handler '''
	def get(self):
		''' Show home page '''
		# import data
		# check if valid Google account
		school_register = csv.reader(open('data.csv'),delimiter=',')
		found = False
		user = users.get_current_user()
	
		for student in school_register:	# if valid logged in user
			if student[0] == self.request.get('pid'):
				user = student
				found = True
				break

		if user: 
			# logout link
			url = users.create_logout_url(self.request.uri)
			# logout text
			url_linktext = 'Logout'
			# retrieve user record from datastore
			# may get multiple records, so in order to get one record:
			query = Contact.gql('WHERE pid = :1', user.nickname())
			result = query.fetch(1)
			if result: #if user record found
				contact = result[0]
				greeting = ("Welcome %s!" % (contact.name,)) #1 item in couple = put comma
			else: #not found
				contact = "Invalid dhs.sg user"
				greeting = ""
			
		else: # not logged in 
				# login link
			url = users.create_login_url(self.request.uri)
				# login text
			url_linktext = 'Login'
			contact = "Not authorised"
			greeting = "You need to"
			

					
		template_values = {
			'contact': contact,
			'greeting': greeting,
			'url': url,
			'url_linktext': url_linktext,
		}
		
		# create index.html template
		template = jinja_environment.get_template('index.html')
		# associate template values with template
		self.response.out.write(template.render(template_values))

class Submit(webapp2.RequestHandler):
	''' Submit form '''
	def post(self):
		updated_handphone = self.request.get('handphone')
		updated_tickets_csjh = self.request.get('tickets_csjh')
		updated_tickets_edssh = self.request.get('tickets_edssh')
		updated_remark = self.request.get('remark')
		user = users.get_current_user()
		if user:
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
			query = Contact.gql('WHERE pid = :1', user.nickname())
			result = query.fetch(1)
			if result: 
				contact = result[0]
				greeting = ("User: %s" % (contact.name,)) 
				contact.handphone = updated_handphone
				contact.tickets_csjh = updated_tickets_csjh
				contact.tickets_edssh = updated_tickets_edssh
				contact.remark = db.Text(updated_remark)
				contact.put()
			else: 	
				self.response.out.write('Reservation failed!')
		
		
		
		template_values = {
			'contact': contact,
			'greeting': greeting,
			'url': url,
			'url_linktext': url_linktext,
			'contact.handphone': updated_handphone,
			'contact.tickets_csjh': updated_tickets_csjh,
			'contact.tickets_edssh': updated_tickets_edssh,
			'contact.remark': updated_remark,
		}
		
		template = jinja_environment.get_template('submit.html')                
		self.response.out.write(template.render(template_values))
		
	
app = webapp2.WSGIApplication([('/', MainHandler), ('/submit', Submit)], 
								debug=True)

              
