from pytest import fail


def print_message(message):
    def print_message(vars):
        print(message)
    return print_message


def assert_var_equal(var_name, value):
    def assert_var_equal(vars):
        assert vars[var_name] == value
        if vars[var_name] != value:
            fail(f"{var_name} should be {repr(value)}")
    return assert_var_equal


def set_var(var_name, value):
    def set_var(vars):
        vars[var_name] = value
    return set_var
