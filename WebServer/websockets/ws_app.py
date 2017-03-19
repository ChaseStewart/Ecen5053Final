import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
 
class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
	print("Checking Origin!");
        return True

    def open(self):
	print("We're Connected!");
        pass
 
    def on_message(self, message):
	# TODO TAKE IN DIFFERENT MESSAGES AND DO MYSQL QUERIES
        print("Received the message: " +  message)

	if "keep alive" in message:
		# do query
		print("keepalive")
		# get results
		

	# send back

 
    def on_close(self):
        pass
 
 
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', IndexPageHandler),
            (r'/websocket', WebSocketHandler)
        ]
 
        settings = {
            'template_path': 'templates'
        }
        tornado.web.Application.__init__(self, handlers, **settings)
 
 
if __name__ == '__main__':
    ws_app = Application()
    server = tornado.httpserver.HTTPServer(ws_app)
    server.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
