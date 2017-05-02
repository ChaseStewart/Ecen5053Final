import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import MySQLdb

 
class WebSocketHandler(tornado.websocket.WebSocketHandler):
    """
    This is the top level class for the WebSocket listener server
    It takes commands from the RPi, translates them to backend MySQL queries,
    Then returns the results
    """



    def check_origin(self, origin):
        """
        This must return True because of SOP- 
        """
	print("Checking Origin!");
        return True



    def open(self):
        """
        Callback on socket open
        """
        # print ("Connected!")
        pass
 


    def on_message(self, message):
        """
        Callback for message received- in our case
        this takes a message, does a corresponding query,
        and then returns results
        """
		
	db = MySQLdb.connect(host="localhost",user="root",db="users_data")
	cursor = db.cursor()

	# for set arm, set arm_state table to armed
	if "set_arm" in message:
		
		print("Setting ARM ")
		try:
			cursor.execute("""INSERT INTO arm_status (arm_state) VALUE (0) """)
			db.commit()
		except:
			print("MESSED UP!!")
			db.rollback()
	
	# for set disarm, set arm_state table to disarmed
	elif "set_dis" in message:
		
		print("Setting DISARM ")
		try:
			cursor.execute("""INSERT INTO arm_status (arm_state) VALUE (1) """)
			db.commit()
		except:
			print("MESSED UP!!")
			db.rollback()
	
	# for arm_status, query the arm_state table to return the ref result
	elif "arm_status" in message:

		db.query("""SELECT ref.name FROM arm_status a_s LEFT JOIN ref_arm_state ref ON ref.id = a_s.arm_state ORDER BY a_s.timestamp DESC limit 1""")
		
		result = db.store_result()
		output= result.fetch_row()[0][0]
		#print("Results: "+str(output))
		self.write_message("state:"+output+"\r\n")	

	# for login status, query the arm_state table to return the logged-in user's name
	elif "login_status" in message:
			
		db.query("""SELECT name FROM logged_in_users ORDER BY timestamp DESC limit 1""")
		result = db.store_result()
		
		output= result.fetch_row()[0][0]
		#print("Results: "+str(output))
		self.write_message("name:"+output+"\r\n")	
	else:
		print("ERROR: Unknown query!")


 
    def on_close(self):
        """
        Callback on connection close
        """

        # print("Disconnected!")
        pass
 
 
class Application(tornado.web.Application):
    """ 
    Tornado application class that connects /websocket to the websocket handler
    """



    def __init__(self):
        """
	setup handlers and settings for tornado, and start app
        """
        handlers = [
            (r'/websocket', WebSocketHandler)
        ]
 
        settings = {
            'template_path': 'templates'
        }
        tornado.web.Application.__init__(self, handlers, **settings)
 
 
if __name__ == '__main__':
    """
    If name == main, start the app and the HTTP listener
    """

    ws_app = Application()
    server = tornado.httpserver.HTTPServer(ws_app)
    server.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
