import unittest

from repoze.bfg.configuration import Configurator
from repoze.bfg import testing

class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = Configurator()
        self.config.begin()

    def tearDown(self):
        self.config.end()

    def test_my_view(self):
        from thinkfar.views import home
        request = testing.DummyRequest()
        info = home(request)
        self.assertEqual(info['project'], 'thinkfar')


