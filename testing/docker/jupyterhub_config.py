from jupyterhub.auth import DummyAuthenticator
from jupyterhub.spawner import LocalProcessSpawner
import os, sys
from traitlets import Unicode


class SUIDSimpleLocalProcessSpawner(LocalProcessSpawner):
    home_path_template = Unicode(
        '/tmp/{userid}',
        config=True,
        help='Template to expand to set the user home. {userid} and {username} are expanded',
    )

    @property
    def home_path(self):
        return self.home_path_template.format(
            userid=self.user.id, username=self.user.name
        )

    def make_preexec_fn(self, name):
        home = self.home_path

        def preexec():
            try:
                os.setresgid(1000, 1000, 1000)
                os.setresuid(1000, 1000, 1000)
                os.makedirs(home, 0o755, exist_ok=True)
                os.chdir(home)
            except e:
                print(e)

        return preexec

    def user_env(self, env):
        env['USER'] = self.user.name
        env['HOME'] = self.home_path
        env['SHELL'] = '/bin/bash'
        return env


c.JupyterHub.authenticator_class = DummyAuthenticator
c.JupyterHub.spawner_class = SUIDSimpleLocalProcessSpawner

c.Authenticator.admin_users = {'rkevin'}

c.JupyterHub.services.append(
    {
        'name': 'ngshare',
        'url': 'http://127.0.0.1:10101',
        'command': [sys.executable, '/ngshare/ngshare.py', '--debug'],
    }
)
