import logging
import requests

_logger = logging.getLogger(__name__)


REQUEST_TIMEOUT = 10
UNICOBROS_API_ENDPOINT = 'https://api.unicobros.com.ar/p/pos/'


class UnicobrosPosRequest:
    def __init__(self, uni_bearer_token, uni_api_key_entity):
        self.uni_bearer_token = uni_bearer_token
        self.uni_api_key_entity = uni_api_key_entity

    def call_unicobros(self, method, endpoint, payload):
        """ Make a request to Unicobros API.
        :param method: "GET", "POST", ...
        :param endpoint: The endpoint to be reached by the request.
        :param payload: The payload of the request.
        :return The JSON-formatted content of the response.
        """
        endpoint = UNICOBROS_API_ENDPOINT + endpoint
        
        header = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'x-api-key': self.uni_api_key_entity,
            'x-access-token': self.uni_bearer_token,
        }
        
        try:
            response = requests.request(method, endpoint, headers=header, json=payload, timeout=REQUEST_TIMEOUT)
            return response.json()
        except requests.exceptions.RequestException as error:
            _logger.warning("Cannot connect with Unicobros POS. Error: %s", error)
            return {'errorMessage': str(error)}
        except ValueError as error:
            _logger.warning("Cannot decode response json. Error: %s", error)
            return {'errorMessage': f"Cannot decode Unicobros POS response. Error: {error}"}
