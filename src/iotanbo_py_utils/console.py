"""
Console utils
"""

# from prompt_toolkit import prompt
import io

from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.styles import Style

# Style for colored console input
# https://python-prompt-toolkit.readthedocs.io/en/master/pages/asking_for_input.html
style = Style.from_dict({
    # User input (default text).
    # '':          '#777777 bold',

    'description':      '#02AA02 bold',
    'def_val':          '#777777 bold',
    'custom_red':       '#CC2222 bold',
    'custom_green':     '#02AA02 bold',
    'custom_blue':      '#2255BB bold',
    'custom_orange':    '#FFA522 bold',
})

# Convenience type aliases
BoolVal = bool
NumVal = float  # Numeric value
StrVal = str
Metadata = str


class Console:

    @staticmethod
    def input(msg: str, default_val="", color: str = "green") -> str:
        """
        Get string value from user.
        :param msg: text prompt
        :param default_val: default value to be displayed
        :param color: one of ('red', 'green', 'blue', 'orange')
        :return: user entered text
        """
        style_class = "class:custom_" + color

        tip = [
            (style_class, msg),
        ]
        return prompt(tip, default=default_val, style=style)

    @staticmethod
    def print(msg: str, color: str = "green", end: str = "\n") -> None:
        """
        Print message with color specified:
        :param msg: arbitrary text
        :param color: one of ('red', 'green', 'blue', 'orange')
        :param end: string ending
        :return: None
        """

        style_class = "class:custom_" + color

        text = FormattedText([
            (style_class, msg),
        ])
        try:
            print_formatted_text(text, style=style, end=end)
        except io.UnsupportedOperation:
            # This may happen when stdout is modified (e.g. by pytest)
            # Just use normal print
            print(msg, end=end)
        except Exception:
            print(msg, end=end)
            # print(f"Console::print Exception: {e.__class__.__name__}, {str(e)}", end=end)

    @staticmethod
    def print_test():
        Console.print("This is red", color="red")
        Console.print("This is green", color="green")
        Console.print("This is blue", color="blue")
        Console.print("This is orange", color="orange")

    @staticmethod
    def input_num_ex(_prompt: str = "", *,
                     default_val: str = "",
                     skip_val: str = "",
                     min_val=None,
                     max_val=None,
                     black_list: list = None,
                     white_list: list = None,
                     validation_func: callable = None,
                     is_float: bool = False
                     ) -> (NumVal, Metadata):
        """
        Interactively ask user to enter/confirm one int value.
        'key_attribs' are used to nicely format the prompt and verify if the value is correct.

        :param _prompt: prompt to be displayed
        :param default_val: default value
        :param skip_val: if empty, no skip is allowed, otherwise if user enters this value,
                         metadata="skip" is returned
        :param is_float: if True, floating point numbers are allowed
        :param min_val:
        :param max_val:
        :param black_list: list of values that are disallowed as an input
        :param white_list: list of values that are allowed as an input
        :param validation_func: callable, receives user input as int and returns bool if it is valid

        :return: str: (NumVal: int, Metadata: str); if metadata is empty, the value is valid.
                 Otherwise the value is not valid and metadata contains the description.
        """
        skip_msg = ""
        if skip_val:
            skip_msg = f" ('{skip_val}' to skip)"
        bad_input_msg = "Bad input, try again"

        while True:
            # Format the prompt
            tip = [
                ('class:description', _prompt),
                ('class:description', f"{skip_msg}: "),
            ]

            # Get for user input
            result = prompt(tip, default=default_val, style=style)

            # Check if skip value was entered
            if skip_val:
                if result == skip_val:
                    return False, "skip"
            result = result.lower()

            # Try converting to number

            try:
                if is_float:
                    result = float(result)
                else:
                    result = int(result)
            except ValueError:
                Console.print(bad_input_msg, color="orange")
                continue

            # Validate the input
            # Check with validation_func
            if validation_func:
                validated = validation_func(result)
                if validated:
                    return result, ""
                else:
                    Console.print(bad_input_msg, color="orange")
                    continue

            # Check if blacklisted
            if black_list:
                if result in black_list:
                    Console.print(bad_input_msg, color="orange")
                    continue

            # Check if whitelisted
            if white_list:
                if result in white_list:
                    return result, ""
                else:
                    # If min_val and max_val not specified, return the result
                    if min_val is None and max_val is None:
                        Console.print(bad_input_msg, color="orange")
                        continue

            # Finally check the min/max range
            if min_val is not None:
                if result < min_val:
                    Console.print(bad_input_msg, color="orange")
                    continue
            if max_val is not None:
                if result > max_val:
                    Console.print(bad_input_msg, color="orange")
                    continue

            return result, ""

    @staticmethod
    def input_bool_ex(_prompt: str = "", *,
                      default_val: str = "",
                      skip_val: str = "",
                      ) -> (BoolVal, Metadata):
        """
        Extended user input.
        Interactively ask user to enter/confirm one value,
        'key_attribs' are used to nicely format the prompt and verify if the value is correct.

        :param _prompt: prompt to be displayed
        :param default_val: default value
        :param skip_val: if empty, no skip is allowed, otherwise if user enters this value,
                         metadata="skip" is returned

        :return: str: (BoolVal: bool, Metadata: str); if metadata is empty, the value is valid.
                 Otherwise the value is not valid and metadata contains the description.
        """
        skip_msg = ""
        if skip_val:
            skip_msg = f" or '{skip_val}' to skip"

        while True:
            # Format the prompt
            tip = [
                ('class:description', _prompt),
                ('class:description', f" (y/n{skip_msg}): "),
            ]
            # Get for user input
            result = prompt(tip, default=default_val, style=style)
            # Check if skip value was entered
            if skip_val:
                if result == skip_val:
                    return False, "skip"
            result = result.lower()
            if result == 'y' or result == 'yes':
                return True, ""
            if not result:
                Console.print("Bad input, try again", color="orange")
                continue

            return False, ""

    @staticmethod
    def input_str_ex(_prompt: str = "", *,
                     default_val: str = "",
                     skip_val: str = "",
                     min_len: int = 1,
                     max_len: int = 1024,
                     black_list: list = None,
                     white_list: list = None,
                     validation_re=None,
                     validation_func: callable = None,
                     ) -> (StrVal, Metadata):
        """
        Interactively ask user to enter/confirm one int value.
        'key_attribs' are used to nicely format the prompt and verify if the value is correct.

        :param _prompt: prompt to be displayed
        :param default_val: default value
        :param skip_val: if empty, no skip is allowed, otherwise if user enters this value,
                         metadata="skip" is returned
        :param min_len: minimum input length, default is 1
        :param max_len: max input length, default is 1024
        :param black_list: list of values that are disallowed as an input
        :param white_list: list of values that are allowed as an input
        :param validation_re: regular expression to be validated against
        :param validation_func: callable, receives user input as int and returns bool if it is valid

        :return: str: (StrVal: int, Metadata: str); if metadata is empty, the value is valid.
                 Otherwise the value is not valid and metadata contains the description.
        """
        skip_msg = ""
        if skip_val:
            skip_msg = f" ('{skip_val}' to skip)"
        bad_input_msg = "Bad input, try again"

        while True:
            # Format the prompt
            tip = [
                ('class:description', _prompt),
                ('class:description', f"{skip_msg}: "),
            ]

            # Get for user input
            result = prompt(tip, default=default_val, style=style)

            # Check if skip value was entered
            if skip_val:
                if result == skip_val:
                    return False, "skip"

            # Validate the input
            # Check with validation_func
            if validation_func:
                validated = validation_func(result)
                if validated:
                    return result, ""
                else:
                    Console.print(bad_input_msg, color="orange")
                    continue

            # Check if blacklisted
            if black_list:
                if result in black_list:
                    Console.print(bad_input_msg, color="orange")
                    continue

            # Check if whitelisted
            if white_list:
                if result in white_list:
                    return result, ""
                else:
                    Console.print(bad_input_msg, color="orange")
                    continue

            # TODO: check against RE

            # Finally check the min/max range
            res_len = len(result)
            if res_len < min_len:
                Console.print(bad_input_msg, color="orange")
                continue

            if res_len > max_len:
                Console.print(bad_input_msg, color="orange")
                continue

            return result, ""



    # @staticmethod
    # def input_ex(_key: str, key_attribs: dict) -> str:
    #     """
    #     Extended user input.
    #     Interactively ask user to enter/confirm one value,
    #     'key_attribs' are used to nicely format the prompt and verify if the value is correct.
    #     :param _key: single key
    #     :param key_attribs: {'val': str, 'val_type': str, 'desc': str, 'allow_empty': bool }
    #                             val: default value
    #                             val_type: value type ('str', 'int', 'bool')
    #                             desc: description to be shown to user
    #                             allow_empty: if True, user is allowed to enter empty string as a value
    #                             TODO: use 'validation_re' key to optionally check against regular expression
    #     :return: str: user confirmed value
    #     """
    #     if key_attribs["allow_empty"]:
    #         tip = [
    #             ('class:description', key_attribs["desc"]),
    #             ('class:description', ": ?"),
    #             ('class:def_val', ' []: '),
    #         ]
    #         user_confirmed_val = prompt(tip, default=key_attribs["val"], style=style)
    #     else:
    #         while True:
    #             tip = [
    #                 ('class:description', key_attribs["desc"]),
    #                 ('class:description', ": ?"),
    #                 ('class:def_val', ' ['),
    #                 ('class:def_val', key_attribs["val"]),
    #                 ('class:def_val', ']: '),
    #             ]
    #             user_confirmed_val = prompt(tip, style=style)
    #             if user_confirmed_val or key_attribs["val"]:
    #                 break
    #             else:
    #                 print("This value can't be empty. Try again.")
    #         if not user_confirmed_val:
    #             user_confirmed_val = key_attribs["val"]
    #     return user_confirmed_val
