"""
Generic performance and best practice tests
"""

# import timeit
import time


"""
SUMMARY

== ACCESSING VARIABLES ==
* If global variable is accessed millions of times from the function,
  small performance gain can be achieved making local copy:
  local_var = GLOBAL_VAR

== LOOPS AND RANGES ==
* Range - based iteration is about 2x faster than while loop;
    for i in range(1024 ** 2)  # BETTER (50 millisec)
    while i < 1024 ** 2:  # BAD (80 millisec)

== BYTE ARRAYS ==
* buf = bytearray(b'\x77' * 1024 ** 2)  # OK (1 millisec, 100 times faster than range iteration)
* Working with binary data in python seems to be very slow.


== LISTS AND DICTIONARIES ==

* Size of list and dict has practical limit of about 67 million elements.
    https://stackoverflow.com/a/62266754/3824328

* Iterating thru both list and dict is VERY EFFICIENT:
    * With 1000 elements: (38 millis vs 52 millis), (40 nanoseconds per element!)
    * With 50 million elements, iterating thru list is slightly faster (2 seconds vs 2.8 seconds)
      (40 nanoseconds per element!)
* CONCLUSION:
  * dict is a good choice when both efficient iteration and access to element is required

"""


TEST_BUF = bytearray(1024 ** 2)


def bytearray_fillin_range_test():  # Better
    buf = TEST_BUF
    for i in range(1024 ** 2):
        buf[i] = 0x77


def bytearray_fillin_loop_test():  # Worse
    buf = TEST_BUF
    i = 0
    top = 1024 ** 2
    while i < top:
        buf[i] = 0x77
        i += 1


def bytearray_fillin_literal_test():  # The best (80...100 times faster)
    buf = bytearray(b'\x77' * 1024 ** 2)
    assert buf[0] == 0x77


def list_ws_dict_iteration_test():
    lst = []
    d = {}
    total_iterations = 1000000

    for i in range(total_iterations):
        lst.append(i)
        d[str(i)] = i

    list_sum = 0
    dict_sum = 0

    # List performance check
    time_start = time.perf_counter()

    for i in lst:
        list_sum += i

    time_taken_list = (time.perf_counter() - time_start) * 1000
    print(f"time_taken_list: {time_taken_list} millis")

    # Dict performance check
    time_start = time.perf_counter()

    for _, val in d.items():
        dict_sum += val

    time_taken_dict = (time.perf_counter() - time_start) * 1000
    print(f"time_taken_dict: {time_taken_dict} millis")

    assert dict_sum == list_sum
    assert d["40000"] == 40000


if __name__ == '__main__':
    # print(f"* Range based fill in: {timeit.timeit(stmt=bytearray_fillin_range_test, number=10)}")
    # print(f"* Loop based fill in: {timeit.timeit(stmt=bytearray_fillin_loop_test, number=10)}")
    # print(f"* Bytearray literal fill in: {timeit.timeit(stmt=bytearray_fillin_literal_test, number=10)}")
    list_ws_dict_iteration_test()
