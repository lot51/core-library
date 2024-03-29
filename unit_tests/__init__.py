import os
import unittest
import sims4.commands
from lot51_core import get_mod_root, logger
from lot51_core.unit_tests.game_version import TestGameVersion


def run_tests():
    file_name = 'lot51_core.tests.log'

    # List of TestCase classes
    test_cases = (TestGameVersion,)

    # Generate list of tests for suite
    tests = list()
    for cls in test_cases:
        test = unittest.TestLoader().loadTestsFromTestCase(cls)
        tests.append(test)
    test_suite = unittest.TestSuite(tests)

    # Run test suites and output logs to file_name above
    with open(os.path.join(get_mod_root(__file__, depth=3), file_name), 'w') as f:
        runner = unittest.TextTestRunner(f, verbosity=2)
        runner.run(test_suite)


@sims4.commands.Command("lot51_core.run_tests", command_type=sims4.commands.CommandType.Cheat)
def _run_test_suites(_connection=None):
    try:
        run_tests()
    except:
        logger.exception("Failed running unit tests")