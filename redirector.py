from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from random import choice
try:
    from simplejson import load as jsonfload
except:
    from json import load as jsonfload
from urlparse import urlparse
from os.path import getmtime

class Redirector(webapp.RequestHandler):
    def get(self):
        global config
        redirect_url = "http://%s%s"
        uri = self.request.uri
        up = urlparse(uri)
        podcast = up.hostname
        path = up.path
        try:
            redirect_path = choose_one(config.get(podcast))
            self.redirect(redirect_url % (redirect_path, path))
        except:
            self.error(500)
            
def choose_one(self, domains):
    return choice([key for key in domains for x in range(domains[key])])
        
class ConfigReload(webapp.RequestHandler):
    def get(self):
        global config
        config.load_config()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(str({'success': True, 'message': 'Done'}))
        
class Config():
    file_location = ""
    values = {}
    last_reload = 0
    def __init__(self, file_path="config.json"):
        self.file_location = file_path
        self.load_config()
        
    def get (self, key, default):
        if self.reload < self.last_modified():
            self.load_config()
        return self.values.get(key, default)
        
    def last_modified (self):
        return getmtime(self.file_location)
        
    def load_config(self):
        f = open(self.file_location, 'r')
        self.values = jsonfload(f)
        self.last_reload = self.last_modified
        
application = webapp.WSGIApplication([
                                        ('/reload', ConfigReload),
                                        ('/.*', Redirector)
                                    ],
                                    debug=True)
config = Config()

def main():
    run_wsgi_app(application)
    
if __name__ == "__main__":
    main()
