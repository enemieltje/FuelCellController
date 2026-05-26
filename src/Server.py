import logging
import os
import socketserver
import json
from http import server
from urllib.parse import urlparse
from Config import Config
from Power_System import Power_System
from Drone import Drone
from Database import Database, SENSOR_ID

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
        # logger.debug(f"Received GET: {self.path}")
        path = urlparse(self.path).path

        # read the request url and call the appropriate function
        if path == '/':
            self.redirectHome(permanently=True)

        elif path == '/favicon.ico':
            self.sendFile('src/client/favicon.ico')

        elif path == '/index.html':
            self.sendFile('src/client/index.html')

        elif path == '/index.js':
            self.sendFile('src/client/index.js')

        elif path == '/api/button/start':
            Power_System.enable()
            self.redirectHome()

        elif path == '/api/button/stop':
            Power_System.disable()
            self.redirectHome()

        elif path == '/api/button/enableDrone':
            Drone.power.on()
            self.redirectHome()

        elif path == '/api/button/disableDrone':
            Drone.power.off()
            self.redirectHome()

        elif path == '/api/button/armDrone':
            Drone.arm()
            self.redirectHome()

        elif path == '/api/button/calibrateDrone':
            Drone.calibrate()
            self.redirectHome()

        elif path == "/api/get/power/fuelcell":
            self.send_power(SENSOR_ID.FUELCELL_POWER)

        elif path == "/api/get/power/battery":
            self.send_power(SENSOR_ID.BATTERY_POWER)

        elif path == "/api/get/power/drone":
            self.send_power(SENSOR_ID.LOAD_POWER)

        elif path == "/api/get/pressure":
            self.send_value(SENSOR_ID.PRESSURE)

        elif path == "/api/get/battery":
            self.send_value(SENSOR_ID.BATTERY_SOC)

        elif path == "/api/get/thrust":
            self.send_value(SENSOR_ID.THRUST)

        elif path == "/api/runs":
            self.send_json(Database.get_runs())

        elif path == "/api/runs/current":
            self.send_json(Database.get_current_run())

        elif path.startswith("/api/runs/") and path.endswith("/csv"):
            parts = path.strip("/").split("/")

            if len(parts) != 4:
                self.send_error(404, "Unknown run CSV endpoint")
                return

            try:
                run_id = int(parts[2])
            except ValueError:
                self.send_error(400, "Invalid run id")
                return

            self.send_csv(run_id)

        else:
            # An unknown request was sent
            server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        # logger.debug(f"Received POST: {self.path}")
        path = urlparse(self.path).path

        # Get content length from headers
        content_length = int(self.headers.get('Content-Length', 0))

        # Read raw body bytes
        body = self.rfile.read(content_length)

        try:
            # Decode JSON body
            data = json.loads(body.decode("utf-8"))

            logger.debug(f"POST data: {data}")

            # Example endpoint
            if path == "/api/set/throttle":

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

            elif path == "/api/runs/start":
                logger.debug("api runs start")
                run = Database.start_run(
                    name=data.get("name"),
                    notes=data.get("notes"),
                )
                self.send_json(run)
                return

            elif path == "/api/runs/current":
                current_run = Database.get_current_run()

                if current_run is None:
                    self.send_error(404, "No active run")
                    return

                run = Database.update_run(
                    current_run["id"],
                    name=data.get("name"),
                    notes=data.get("notes"),
                )
                self.send_json(run)
                return

            elif path == "/api/runs/stop":
                run = Database.stop_run()
                self.send_json(run)
                return

            elif path.startswith("/api/runs/"):
                parts = path.strip("/").split("/")

                if len(parts) != 3:
                    self.send_error(404, "Unknown run endpoint")
                    return

                try:
                    run_id = int(parts[2])
                except ValueError:
                    self.send_error(400, "Invalid run id")
                    return

                run = Database.update_run(
                    run_id,
                    name=data.get("name"),
                    notes=data.get("notes"),
                )
                self.send_json(run)
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

    def send_value(self, sensor_id):
        # Convert the data to a JSON string
        response_data = json.dumps(Database.get_latest(sensor_id))

        # Set the response headers and status
        self.send_response(server.HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        # Write the JSON response back to the client
        self.wfile.write(response_data.encode("utf-8"))

    def send_power(self, sensor_id):
        # Get the sensor data
        data = {
            "power": Database.get_latest(sensor_id),
            "voltage": Database.get_latest(sensor_id + 1),
            "current": Database.get_latest(sensor_id + 2),
        }
        # Convert the data to a JSON string
        response_data = json.dumps(data)

        # Set the response headers and status
        self.send_response(server.HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        # Write the JSON response back to the client
        self.wfile.write(response_data.encode("utf-8"))

    def send_json(self, data):
        response_data = json.dumps(data)

        self.send_response(server.HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        self.wfile.write(response_data.encode("utf-8"))


    def send_csv(self, run_id):
        csv_text = Database.export_run_csv(run_id)
        filename = f"run-{run_id}.csv"

        self.send_response(server.HTTPStatus.OK)
        self.send_header("Content-Type", "text/csv")
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()

        self.wfile.write(csv_text.encode("utf-8"))


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

    def end_headers(self):
        # Prevent browsers from cacheing old versions
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()
