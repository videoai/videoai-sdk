import unittest
import requests
import os
import configparser
import base64

#HOST = 'http://localhost:5000'
HOST = 'https://api.videoai.net'

def print_http_response(r):
    '''
    Print the http response
    :param r: The response of a request
    :return:
    '''
    print("HTTP/1.0 {} OK".format(r.status_code))
    print("Content-Type: {}".format(r.headers['content-type']))
    print("Content-Length: {}".format(r.headers['content-length']))
    print("Server: {}".format(r.headers['server']))
    print("Date: {}".format(r.headers['date']))
    print(r.text)

def get_key():
    home = os.path.expanduser("~")
    key_file = os.path.join(home, '.videoai')
    config = configparser.ConfigParser()
    config.read(key_file)
    keys = config['videoai.net']
    return keys['apiKey_id'], keys['apiKey_secret']


def get_header(api_id, api_secret):
    api_key = "{0}:{1}".format(api_id, api_secret)
    basic_auth_header = "Basic {0}".format(base64.b64encode(api_key))
    return {'Authorization': basic_auth_header}


def get_valid_header():
    api_id, api_secret = get_key()
    return get_header(api_id=api_id, api_secret=api_secret)


def get_url(end_point=''):
    return '{}/{}'.format(HOST, end_point)


class TestErrors(unittest.TestCase):

    def test_valid_key(self):
        """
        200 authorised OK
        """
        header = get_valid_header()
        r = requests.get(get_url(), headers=header)
        print_http_response(r)
        self.assertEqual(r.status_code, 200)

    def test_invalid_key(self):
        """
        401 not authorised error
        """
        header = get_header('absolutely', 'rubbish')
        r = requests.get(get_url(), headers=header)
        print_http_response(r)
        self.assertEqual(r.status_code, 401)

    def test_invalid_key2(self):
        """
        401 not authorised error
        """
        api_id, api_secret = get_key()
        header = get_header(api_secret, api_id)
        r = requests.get(get_url(), headers=header)
        print_http_response(r)
        self.assertEqual(r.status_code, 401)

    def test_invalid_key3(self):
        """
        401 not authorised error
        """
        api_id, api_secret = get_key()
        header = get_header(api_id, 'rubbish')
        r = requests.get(get_url(), headers=header)
        print_http_response(r)
        self.assertEqual(r.status_code, 401)

    def test_invalid_endpoint(self):
        """
        404 not found error
        """
        header = get_valid_header()
        r = requests.get(get_url('rubbish'), headers=header)
        print_http_response(r)
        self.assertEqual(r.status_code, 404)

    def test_invalid_endpoint2(self):
        """
        404 not found error
        """
        header = get_valid_header()
        r = requests.get(get_url('\\%'), headers=header)
        print_http_response(r)
        self.assertEqual(r.status_code, 404)


if __name__ == '__main__':
    unittest.main()




