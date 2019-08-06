from typing import Dict, Any


def require(expected_args, output):
    def side_effect(*args):
        if args != expected_args:
            raise AssertionError(f'{args} != {expected_args}')
        return output
    return side_effect


def switch(options: Dict[tuple, Any]):
    def side_effect(*args):
        for (opt, out) in options.items():
            if args == opt:
                return out
        raise AssertionError(f'{args} did not match any option')

    return side_effect
