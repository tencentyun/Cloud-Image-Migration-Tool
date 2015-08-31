#!/usr/bin/env python

import ConfigParser

class ConfigLoader(object):
    @staticmethod
    def load(filename):
        config = ConfigParser.ConfigParser()
        config.read(filename)

        result = dict()

        for section in config.sections():
            result[section.lower()] = dict()
            for option in config.options(section):
                if config.get(section, option):
                    result[section.lower()][option.lower()] = config.get(section, option)

        return result
