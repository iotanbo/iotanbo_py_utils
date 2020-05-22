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

    @staticmethod
    def strip_symbol(text: str, left_side_sym: str, right_side_sym: str,
                     strip_whitespace_before: bool = True,
                     strip_whitespace_after: bool = False) -> str:
        """
        Remove 'left_side_sym' from the beginning and 'right_side_sym' from the end of the text
        if those symbols exist.
        Strip whitespaces according to params.
        Return stripped string.


        :param text:
        :param left_side_sym:
        :param right_side_sym:
        :param strip_whitespace_before:
        :param strip_whitespace_after:
        :return: str
        """
        if strip_whitespace_before:
            text = text.strip()
        text = text.lstrip(left_side_sym)
        text = text.rstrip(right_side_sym)
        if strip_whitespace_after:
            text = text.strip()
        return text

