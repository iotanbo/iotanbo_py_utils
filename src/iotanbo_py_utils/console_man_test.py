"""
Console tests
"""

from iotanbo_py_utils.console import Console


# BOOL INPUT TESTS
def input_bool_ex_test():
    choice, meta = Console.input_bool_ex("Do you think TEST1 is cool")
    if 'skip' == meta:
        print("Skipped.")
    else:
        print(f"Selected: {choice}")

    choice, meta = Console.input_bool_ex("Do you think TEST2 is cool",
                                         skip_val='s', default_val='Yes')
    if 'skip' == meta:
        print("Skipped.")
    else:
        print(f"Selected: {choice}")


# NUMERIC INPUT TESTS
def input_num_ex_basic_test():

    # Test validation_func
    choice, meta = Console.input_num_ex("Select an int")
    if 'skip' == meta:
        print("Skipped.")
    else:
        print(f"Selected: {choice}")


def input_num_ex_min_max_test():

    # Test validation_func
    choice, meta = Console.input_num_ex("Select an int [1-3]", min_val=1, max_val=3)
    if 'skip' == meta:
        print("Skipped.")
    else:
        print(f"Selected: {choice}")


def input_num_ex_min_max_float_test():

    # Test validation_func
    choice, meta = Console.input_num_ex("Select float [1.0 - 3.0]",
                                        min_val=1.0, max_val=3.0,
                                        skip_val='s',
                                        is_float=True)
    if 'skip' == meta:
        print("Skipped.")
    else:
        print(f"Selected: {choice}")


def input_num_ex_test_validation_func():

    # Test validation_func
    choice, meta = Console.input_num_ex("Select int [0..5]",
                                        validation_func=lambda val: 0 <= val <= 5)
    if 'skip' == meta:
        print("Skipped.")
    else:
        print(f"Selected: {choice}")


def input_num_ex_test_white_list():

    # Test validation_func
    choice, meta = Console.input_num_ex("Select int [1, 3, 5]",
                                        white_list=[1, 3, 5],
                                        skip_val="0")
    if 'skip' == meta:
        print("Skipped.")
    else:
        print(f"Selected: {choice}")


def input_num_ex_test_black_list():

    # Test validation_func
    choice, meta = Console.input_num_ex("Select int [1 - 5] except 4",
                                        min_val=1,
                                        max_val=5,
                                        black_list=[4],
                                        skip_val="0")
    if 'skip' == meta:
        print("Skipped.")
    else:
        print(f"Selected: {choice}")


# STRING INPUT TESTS
def input_str_ex_basic_test():

    # Test validation_func
    choice, meta = Console.input_str_ex("Enter a string")
    if 'skip' == meta:
        print("Skipped.")
    else:
        print(f"Selected: {choice}")


def input_str_ex_skip_test():

    # Test validation_func
    choice, meta = Console.input_str_ex("Enter a string",
                                        skip_val='s')
    if 'skip' == meta:
        print("Skipped.")
    else:
        print(f"Selected: {choice}")


def input_str_ex_length_limit_test():

    # Test validation_func
    choice, meta = Console.input_str_ex("Enter a string [0-5] chars long",
                                        min_len=0, max_len=5)
    if 'skip' == meta:
        print("Skipped.")
    else:
        print(f"Selected: {choice}")


def input_str_ex_blacklist_test():
    # Test validation_func
    choice, meta = Console.input_str_ex("Enter a string [0-5] chars long, 'no' is not accepted",
                                        min_len=0, max_len=5,
                                        black_list=["no"])
    if 'skip' == meta:
        print("Skipped.")
    else:
        print(f"Selected: {choice}")


def input_str_ex_whitelist_test():
    # Test validation_func
    choice, meta = Console.input_str_ex("Select ['one', 'two', 'three']",
                                        min_len=0, max_len=5,
                                        skip_val="s",
                                        default_val="one",
                                        white_list=['one', 'two', 'three'])
    if 'skip' == meta:
        print("Skipped.")
    else:
        print(f"Selected: {choice}")


def input_str_ex_validation_func_test():
    # Test validation_func
    choice, meta = Console.input_str_ex("Select ['one', 'two', 'three']",
                                        validation_func=lambda val: val in ['one', 'two', 'three'])
    if 'skip' == meta:
        print("Skipped.")
    else:
        print(f"Selected: {choice}")


if __name__ == '__main__':

    # # BOOL INPUT TESTS
    # input_bool_ex_test()

    # NUMERIC INPUT TESTS
    # input_num_ex_basic_test()
    # input_num_ex_min_max_test()
    # input_num_ex_test_validation_func()
    # input_num_ex_test_white_list()
    # input_num_ex_test_black_list()
    # input_num_ex_min_max_float_test()

    # STRING INPUT TESTS
    # input_str_ex_basic_test()
    # input_str_ex_skip_test()
    # input_str_ex_length_limit_test()
    # input_str_ex_blacklist_test()
    # input_str_ex_whitelist_test()
    input_str_ex_validation_func_test()
