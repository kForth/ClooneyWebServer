from server import ClooneyServer

app = ClooneyServer(__name__, None)

app.run("0.0.0.0", debug=True)
