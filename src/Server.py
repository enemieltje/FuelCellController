import logging
import os
import socketserver
import json
from http import server
from Config import Config
from Power_System import Power_System
from Drone import Drone
from Database import Database

logger = logging.getLogger(__name__)


class Server(socketserver.ThreadingMixIn, server.HTTPServer):
    # A simple HTTP server allowing IO over a webpage

    instance: any
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, address, requestHandler):
        super().__init__(address, requestHandler)

    def run(self):
        logger.info('Server running at' +
                    str(Server.instance.server_address))
        try:
            # Set up and start the server
            self.serve_forever()
        finally:
            # Stop serving when the script is interrupted
            logger.info("Stream stopped.")

    def start():
        Server.port = Config.getWebPort()
        # This creates an instance of the server class and runs it
        logger.debug('starting server...')
        logger.debug('sever port %i', Server.port)
        address = ('', Server.port)
        Server.instance = Server(address, RequestHandler)
        Server.instance.run()

    def stop():
        # This shuts the instance down and stops all camera streams
        logger.debug('stopping server')
        Server.instance.shutdown()
        Server.instance.server_close()


class RequestHandler(server.SimpleHTTPRequestHandler):
    # This handles the requests sent to the http server (from the fetch function in index.js for example)
    # Requests always contain a path/url that describes what the request wants from the server

    def do_GET(self):
        logger.debug(f"Received GET: {self.path}")
        # read the request url and call the appropriate function
        if self.path == '/':
            self.redirectHome(permanently=True)

        elif self.path == '/favicon.ico':
            self.sendFile('src/client/favicon.ico')

        elif self.path == '/index.html':
            self.sendFile('src/client/index.html')

        elif self.path == '/index.js':
            self.sendFile('src/client/index.js')

        elif self.path == '/api/button/start':
            Power_System.enable()
            self.redirectHome()

        elif self.path == '/api/button/stop':
            Power_System.disable()
            self.redirectHome()

        elif self.path == '/api/button/startDrone':
            Drone.set_throttle(1.0)
            self.redirectHome()

        elif self.path == '/api/button/stopDrone':
            Drone.set_throttle(0.0)
            self.redirectHome()

        elif self.path == '/api/button/calibrateDrone':
            # Drone.arm()
            Drone.power.on()
            self.redirectHome()

        elif self.path == '/api/button/disableDrone':
            Drone.power.off()
            self.redirectHome()

        elif self.path == "/api/get/power/fuelcell":
            self.send_power(Power_System.fc_power)

        elif self.path == "/api/get/power/battery":
            self.send_power(Power_System.battery.power_meter)

        elif self.path == "/api/get/power/drone":
            self.send_power(Drone.power_meter)

        elif self.path == "/api/get/pressure":
            # self.send_value(Power_System.pressure_sensor.read_average())
            self.send_value(Database.get_latest(Database.PRESSURE))

        elif self.path == "/api/get/battery":
            # self.send_value(Power_System.battery.get_percentage())
            self.send_value(Database.get_latest(Database.BATTERY_SOC))

        elif self.path == "/api/get/thrust":
            # self.send_value(Drone.get_thrust())
            self.send_value(Database.get_latest(Database.THRUST))

        else:
            # An unknown request was sent
            server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        logger.debug(f"Received POST: {self.path}")

        # Get content length from headers
        content_length = int(self.headers.get('Content-Length', 0))

        # Read raw body bytes
        body = self.rfile.read(content_length)

        try:
            # Decode JSON body
            data = json.loads(body.decode("utf-8"))

            logger.debug(f"POST data: {data}")

            # Example endpoint
            if self.path == "/api/set/throttle":

                # Expect JSON like:
                # { "throttle": 0.75 }

                throttle = data.get("throttle")

                if throttle is None:
                    self.send_error(400, "Missing throttle value")
                    return

                Drone.set_throttle(float(throttle))

                # Send success response
                response = {
                    "status": "ok",
                    "throttle": throttle
                }

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()

                self.wfile.write(json.dumps(response).encode("utf-8"))
                return

            else:
                self.send_error(404, "Unknown POST endpoint")

        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")

    def redirectHome(self, permanently=False):
        if permanently:
            self.send_response(301)
        else:
            self.send_response(302)
        self.send_header('Location', '/index.html')
        self.end_headers()

    def sendPageNotFound(self):
        self.send_error(404)
        self.end_headers()

    def send_value(self, value):
        # Convert the data to a JSON string
        response_data = json.dumps(value)

        # Set the response headers and status
        self.send_response(server.HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        # Write the JSON response back to the client
        self.wfile.write(response_data.encode("utf-8"))

    def send_power(self, power_meter):
        # Get the sensor data
        data = {
            "power": power_meter.get_power(),
            "voltage": power_meter.get_voltage(),
            "current": power_meter.get_current(),
        }
        # Convert the data to a JSON string
        response_data = json.dumps(data)

        # Set the response headers and status
        self.send_response(server.HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        # Write the JSON response back to the client
        self.wfile.write(response_data.encode("utf-8"))


    def sendFile(self, filePath):
        # This opens a file on the raspberry and sends that to the webpage
        logger.debug("sending file: " + filePath)
        if not os.path.isfile(filePath):
            # If the file does not exist, send a warning and redirect to the home page
            logger.warn('File does not exist: ' + filePath)
            self.redirectHome()
            return

        # The built-in class "SimpleHTTPRequestHandler", which this class extends, already has this functionality
        # This wrapper allows us to have the request path and the file path not be the same, and handle non-existent files correctly as above
        self.path = filePath
        server.SimpleHTTPRequestHandler.do_GET(self)
