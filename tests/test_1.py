from steps import *

test_1 = [
    print_message("hello, world!"),
    set_var("printed_message", True),
    assert_var_equal("printed_message", True)
]

test_2 = [
    print_message("hello, world!"),
    set_var("printed_message", False),
    assert_var_equal("printed_message", True)
]
