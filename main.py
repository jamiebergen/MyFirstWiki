import webapp2
import base
import users

from google.appengine.ext import db

class WikiPage(base.Handler):
    def get(self, path):
        wiki_content = db.GqlQuery("SELECT * FROM Wiki WHERE path = :1 ORDER BY created DESC ", path)

        if list(wiki_content):
            content = wiki_content[0].content
            if self.user:
                self.render('index.html', user = self.user.name, no_edit = True, content = content, path = path)
            else:
                self.render('index.html', user = None, no_edit = True, content = content, path = path)
        else:
            if self.user:
                self.redirect('/_edit%s' % path)
            else:
                self.redirect('/login')

class WikiPageArchive(base.Handler):
    def get(self, path, version):
        version = int(version)
        wiki_content = db.GqlQuery("SELECT * FROM Wiki " 
                                    "WHERE path = :path "
                                    "AND version = :version " 
                                    "ORDER BY created DESC ", path = path, version = version)
        content = wiki_content[0].content
        self.render('index.html', user = self.user.name, no_edit = True, content = content, path = path)


class EditPage(base.Handler):
    def get(self, path):
        #wiki_content = db.GqlQuery("SELECT * FROM Wiki " )
        #if list(wiki_content):
        #    content = wiki_content[0].content
        #else:
        #    content = ''

        wiki_content = db.GqlQuery("SELECT * FROM Wiki WHERE path = :1 ORDER BY created DESC ", path)
        if list(wiki_content):
            content = wiki_content[0].content

        #wiki_content = base.Wiki.latest_by_path(path)    # !!! get latest content for that path
        #if wiki_content:
        #    content = wiki_content.content
        else:
            content = ''
        self.render('index.html', user = self.user.name, edit = True, content = content, path = path)


    def post(self, path):
        #wiki_content = db.GqlQuery("SELECT * FROM Wiki " )
        #if list(wiki_content):
        #    wiki_content[0].delete() # !!!

        #wiki_content = base.Wiki.by_path(path)      # !!! don't need this anymore because we're not deleting
        #if wiki_content:
        #    wiki_content.delete()   

        wiki_content = db.GqlQuery("SELECT * FROM Wiki WHERE path = :1 ORDER BY created DESC ", path)
        version = len(list(wiki_content))

        content = self.request.get('content')
        if content:
            w = base.Wiki(content = content, path = path, version = version)  # makest latest entry for that path 
            w.put()
            self.redirect('//%s' % path)


class HistoryPage(base.Handler):
    def get(self, path):

        contents = db.GqlQuery("SELECT * FROM Wiki WHERE path = :1 ORDER BY created DESC ", path)
        if list(contents):
            self.render('index.html', user = self.user.name, contents = contents, path = path, history = True)
        else:
            self.redirect('/')   


#### Routing Table ####

PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'
#V_RE = r'(#v(?<![-.])\b[0-9]+\b(?!\.[0-9]))'
V_RE = r'!v([0-9]*)'
app = webapp2.WSGIApplication([
    ('/signup', users.Register),
    ('/login', users.Login),
    ('/logout' + PAGE_RE, users.Logout),
    ('/_history' + PAGE_RE, HistoryPage),
    ('/_edit' + PAGE_RE, EditPage),
    ('/wikiarchive' + PAGE_RE + V_RE, WikiPageArchive),
    (PAGE_RE, WikiPage)
], debug=True)
