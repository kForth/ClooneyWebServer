from server import ClooneyServer

server = ClooneyServer()
server.run("0.0.0.0", debug=True, threaded=True)
