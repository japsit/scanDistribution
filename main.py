# Scan Distribution collects data and creates a TreadTracker report in a computer readable form.
# According to the developer's documentation the user cannot make a request for data but only setup the endpoint
# where the data will be sent.
# The data will be sent to https://domain/apiV5.3/ScanDistribution/<<DealerID>>
# This is a 3rd party program for receiving tire profile data from a preconfigured device
import os.path
from configparser import ConfigParser
from http.server import BaseHTTPRequestHandler, HTTPServer
from scan_distribution import ScanDistribution
from datetime import datetime
import simplejson


DATADIR="data"
FILENAME_PREFIX="json_"
FILENAME_DATETIME_FORMAT="%Y%m%d_%H%M%S_%f"

# Create directory for data
if not os.path.exists(DATADIR):
    os.makedirs(DATADIR)


class HttpHandler(BaseHTTPRequestHandler):
    """Handles all GET and POST requests"""
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()

        message = 'Endpoint for the service is ' \
                  + 'http://' + self.host + self.uri
        self.wfile.write(bytes(message, "utf8"))

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_POST(self):
        # Receive post data
        if self.path == self.uri or self.path == self.uri + "/":
            content_length = int(self.headers['Content-Length'])  # Get the size of data
            post_data = self.rfile.read(content_length)  # Get the data itself
            self._set_response() # Send response 200

            ## save JSON
            json_data = simplejson.loads(post_data)
            now = datetime.now()
            filename = self.filename + now.strftime(self.dateformat)
            scan_distribution = ScanDistribution()
            scan_distribution.save_json(json_data, filename)

            self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))


class Main():
    # Read configuration
    def __init__(self):
        self.server = None
        self.handler = HttpHandler

        # Load config
        configuration = ConfigParser()
        configuration.read('config.ini')
        server = configuration['SERVER']
        endpoint = configuration['ENDPOINT']
        data = configuration['DATA']

        # Read server variables
        self.host = server.get('HOSTNAME', '127.0.0.1')
        self.handler.host = self.host
        self.port = int(server.get('PORT', '8000'))

        # Read EndPoint variables
        self.version = endpoint.get('VERSION')
        self.service = endpoint.get('SERVICE')
        self.dealerid = endpoint.get('DEALERID')
        self.handler.uri = "/" + self.version + "/ScanDistribution/" + self.dealerid

        # Data data variables for saving JSON
        self.datadir = data.get('DATADIR')
        self.filename_prefix = data.get('FILENAME_PREFIX')
        self.handler.dateformat = "%Y%m%d_%H%M%S_%f"
        self.handler.filename = self.datadir + "/" + self.filename_prefix + "_"
        self.run_server()


    def run_server(self):
        self.server = MyHTTPServer((self.host, self.port), HttpHandler, self.handler)
        self.server.serve_forever()


class MyHTTPServer(HTTPServer):
    """Use this class to allow passing custom handlers"""
    def __init__(self, server_address, RequestHandlerClass, handler):
        HTTPServer.__init__(self, server_address, RequestHandlerClass)
        self.handler = handler


if __name__ == "__main__":
    Main()
