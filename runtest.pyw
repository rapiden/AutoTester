import sys
import argparse
sys.path.append('./src')
from TestGUI import *
from Exceptions import TestError


def main():
    # Check if test was executed from cmd
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description='AutoTester.')
        parser.add_argument('--test_name', type=str,
                            help='Test name')
        parser.add_argument('--svn_download', action="store_true",
                            help='download test files from svn (default: off)')
        parser.add_argument('--svn_commit', action="store_true",
                            help='upload test results to svn (default: off)')
        parser.add_argument('--host_env', action="store_true",
                            help='enable this if working on pc environment (default: off)')
        parser.add_argument('--ci', action="store_true",
                            help='enable this if working on continues integration environment (default: off)')
        parser.add_argument('--ins', action="store_true",
                            help='enable this to record instrumented history file (default: off)')
        args = parser.parse_args()

        try:
            test = TestClass(args.test_name, args.svn_download, args.svn_commit, _executed=True, _host_env=args.host_env
                             , _ci=args.ci, _instrumented=args.ins)
            print(f'Starting test run for \"{test.test_name}\",Download from SVN: {test.SVNDownload},Commit to SVN:'
                  f'{test.SVNResults},Host ENV: {test.host_env},CI: {test.ci}, Instrumented: {test.instrumented}')
            test.run_test()
        except TestError as error:
            print(error.message)
    else:
        run_with_gui()


if __name__ == "__main__":
    main()
