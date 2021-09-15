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
        'old_password': {'type': 'str', 'required': True, 'no_log': True},
        'new_password': {'type': 'str', 'required': False, 'no_log': True},
        'fb_url': {'type': 'str', 'required': True},
    })
    old_password = module.params['old_password']
    new_password = module.params['new_password']
    fb_url = module.params['fb_url']


    flashBlade = FlashBladeConnect(fb_url, old_password)
    stdin, stdout, stderr = flashBlade.exec_command('sudo passwd ir')

    stdin.write(new_password + '\n')
    stdin.write(new_password + '\n')
    stdin.flush()
    stdout.channel.set_combine_stderr(True)

    output = stdout.read().decode()
    if 'updated successfully' in output:
        module.exit_json(success=True, changed=True,  flashblade=fb_url, content=output)
    else:
        module.fail_json(msg=output, flashblade=fb_url)

if __name__ == '__main__':
    main()
