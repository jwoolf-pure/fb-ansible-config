#!env python
from ansible.module_utils.basic import *
from paramiko import SSHClient, SSHException

class FlashBladeConnect:

    def __init__(self, flashblade, password):
        self.client = SSHClient()
        self.client.load_system_host_keys()
        self.client.connect(flashblade, password=password, username='ir')

    def exec_command(self, command):
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
        except SSHException:
            pass

        return stdin, stdout, stderr


def main():

    module = AnsibleModule(argument_spec={
        'command': {'type': 'str', 'required': True, 'no_log': True},
        'password': {'type': 'str', 'required': False, 'no_log': True},
        'fb_url': {'type': 'str', 'required': True},
    })
    command = module.params['command']
    password = module.params['password']
    fb_url = module.params['fb_url']


    try:
        flashBlade = FlashBladeConnect(fb_url, password)
        stdin, stdout, stderr = flashBlade.exec_command(command)

        result_stdout = stdout.read().decode()
        result_stderr = stderr.read().decode()
    except:
        module.fail_json(msg="Faild to login/execute command")

    output = stdout.read().decode()
    module.exit_json(success=True, changed=True,  flashblade=fb_url, stdout=result_stdout, stderr=result_stderr)

if __name__ == '__main__':
    main()
