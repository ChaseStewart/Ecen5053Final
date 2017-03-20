import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import MySQLdb

 
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

	if "disarm" in message:
		
		print("Setting ARM Status")
		# do query
		db = MySQLdb.connect(host="localhost",user="root",db="users_data")
		cursor = db.cursor()

		try:
			cursor.execute("""INSERT INTO arm_status (arm_state) VALUE (0) """)
			db.commit()
		except:
			print("MESSED UP!!")
			db.rollback()
	
	if "arm_status" in message:
		print("Getting Arm Status User")
		db = MySQLdb.connect(host="localhost",user="root",db="users_data")
		db.query("""SELECT ref.name FROM arm_status a_s LEFT JOIN ref_arm_state ref ON ref.id = a_s.arm_state ORDER BY a_s.timestamp ASC limit 1""")
		
		result = db.store_result()
		output= result.fetch_row()[0][0]
		print("Results: "+str(output))
		self.write_message(output)	

	if "login_status" in message:
			
		print("Getting Logged-in User")
		# do query
		db = MySQLdb.connect(host="localhost",user="root",db="users_data")
		db.query("""SELECT name FROM logged_in_users ORDER BY timestamp ASC limit 1""")
		result = db.store_result()
		
		output= result.fetch_row()[0][0]
		print("Results: "+str(output))
		self.write_message(output)	

 
    def on_close(self):
        pass
 
 
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
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
