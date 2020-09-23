import telebot
import cherrypy

# WEBHOOK
WEBHOOK_HOST = '83.220.175.88'
WEBHOOK_PORT = 443 
WEBHOOK_LISTEN = '0.0.0.0'  
WEBHOOK_SSL_CERT = '../webhook_cert.pem'  
WEBHOOK_SSL_PRIV = '../webhook_pkey.pem'  
WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % ("721671579:AAFR4Fpn-xkJnyr8cDunU9fXRvCE7QsNlB8")

# cherrypy server
class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                        'content-type' in cherrypy.request.headers and \
                        cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)

bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))
cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})
def Webhook_listen():
  cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})
  
