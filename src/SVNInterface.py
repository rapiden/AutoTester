import svn.remote
from Utilities import *
from Exceptions import SVNError


class SVNInterface:
    def __init__(self, _testname, ci=False):
        self.testname = _testname
        self.attach_path = f'{Utilities.get_svn_path_attach()}/{_testname}'
        if not ci:
            self.result_path = f'{Utilities.get_svn_path_result()}/{_testname}'
        else:
            self.result_path = f'{Utilities.get_svn_path_result_ci()}/{_testname}'
        self.client = svn.remote.RemoteClient(self.attach_path)

        self.user = Utilities.get_svn_user()
        self.password = Utilities.get_svn_password()

    def export(self, folder):
        if self.exists() is False:
            raise SVNError("SVN", "Could not export test's folder.")
        self.client.export(folder)

    def upload(self, folder, file_name, message="AutoTester commit"):
        cmd = [f"-m {message}", "--username", self.user, "--password", self.password, folder,
               f'{self.result_path}/{file_name}', "--no-auth-cache", "--non-interactive"]
        self.client.run_command('import', cmd)

    def upload_file(self, file_path, file_name, message="AutoTester commit"):
        cmd = [f"-m {message}", "--username", self.user, "--password", self.password, f'{file_path}',
               f'{self.result_path}/{file_name}', "--no-auth-cache", "--non-interactive"]
        self.client.run_command('import', cmd)

    def exists(self):
        try:
            self.client.info()
            return True
        except svn.exception.SvnException:
            return False

    def list(self):
        return self.client.list(False)

