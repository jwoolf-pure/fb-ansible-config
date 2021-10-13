#!env python
from ansible.module_utils.basic import *
from paramiko import SSHClient, SSHException

class FlashBladeConnect:

    def __init__(self, flashblade, password, new_password, module):
        self.module = module
        self.flashblade = flashblade
        self.new_password = new_password
        self.client = SSHClient()
        self.client.load_system_host_keys()
        self.client.connect(flashblade, password=password, username='ir',
                            allow_agent=False, look_for_keys=False)

    def change_password(self):
        try:
            stdin, stdout, stderr = self.client.exec_command('sudo chpass_helper.py -x1-2 ir')
            stdin.write(self.new_password + '\n')
            stdin.write(self.new_password + '\n')
            stdin.flush()

            exit_status = stdout.channel.recv_exit_status()

            if exit_status == 0:
                self.module.exit_json(success=True, changed=True, flashblade=self.flashblade, content="exited successfullly.")
            else:
                self.module.fail_json(msg="did not exit successfully.")

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


    flashBlade = FlashBladeConnect(fb_url, old_password, new_password, module)
    flashBlade.change_password()


if __name__ == '__main__':
    main()
