"""
String utils
"""
import re


class StrUtils:

    # Case conversions
    # https://stackoverflow.com/a/1176023/3824328
    @staticmethod
    def camel_to_snake(name: str) -> str:
        """
        Convert camel-case string into snake-case string.
        :param name: string like 'CamelCaseString'
        :return: string like 'camel_case_string'
        """
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

    @staticmethod
    def snake_to_camel(name: str) -> str:
        """
        Convert snake-case string into camel-case.
        :param name: string like 'camel_case_string'
        :return: string like 'CamelCaseString'
        """
        return ''.join(word.title() for word in name.split('_'))
