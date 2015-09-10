import logging
logger = logging.getLogger(__name__)


class SeriesbutlerException(Exception):
    pass


class ConfigurationException(SeriesbutlerException):
    pass


class DataSourceException(SeriesbutlerException):
    pass


class Link(object):

    def __init__(self, url, hoster, unwrap):
        self.url = url
        self.hoster = hoster
        self.unwrap = unwrap

    def direct(self):
        return self.unwrap(self.url)

configuration_schema = {
    "type": "object",
    "properties": {
        "hosters": {
            "type": "object",
            "properties": {
                "ignored": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "prefered": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            },
            "required": ["prefered", "ignored"],
            "additionalProperties": False
        },
        "series": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "imdb": {
                        "type": "string",
                        "pattern": "^tt[0-9]*$"
                    },
                    "name": {
                        "type": "string"
                    },
                    "start_from": {
                        "type": "object",
                        "properties": {
                            "episode": {
                                "type": "number",
                                "minimum": 0
                            },
                            "season": {
                                "type": "number",
                                "minimum": 0
                            }
                        },
                        "required": ["episode", "season"],
                        "additionalProperties": False
                    }
                },
                "required": ["imdb", "name", "start_from"],
                "additionalProperties": True
            }
        }
    },
    "required": ["hosters", "series"],
    "additionalProperties": False
}
