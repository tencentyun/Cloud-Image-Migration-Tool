#!/usr/bin/env python

import ConfigParser

# TODO: case insensitive?
class ConfigLoader(object):
    @staticmethod
    def load(filename):
        config = ConfigParser.ConfigParser()
        config.read(filename)

        result = dict()

        for section in config.sections():
            result[section.lower()] = dict()
            for option in config.options(section):
                result[section.lower()][option] = config.get(section, option)

        return result
