"""
Scenarios
"""

from google.appengine.ext.db import Model
from google.appengine.ext.db import BooleanProperty, FloatProperty, DateProperty
from google.appengine.ext.db import TextProperty, StringProperty
from google.appengine.ext.db import UserProperty, ReferenceProperty, SelfReferenceProperty


class Scenario(Model):
	owner = UserProperty(required=True)

    name = StringProperty(required=True, default=u'Default Portfolio')
    description = TextProperty()

	start_date = DateProperty(required=True)

def user_scenarios(user, limit=None):
	Scenario.all().filter('owner =', user).fetch(limit)
