import logging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
urllib3_log = logging.getLogger("urllib3")
urllib3_log.setLevel(logging.CRITICAL)
from ansible.module_utils.basic import *
import os
import configparser
from ansible_vault import Vault
from purity_fb import PurityFb, Admin, rest


class LocalVault:
    def __init__(self, array_name, module):

        self.array_name = array_name
        self.module = module

        # Search of ansible.cfg file in the order ansible does.
        ansible_cfg_file = os.environ.get('ANSIBLE_CONFIG', False)
        if not ansible_cfg_file:

            if os.path.isfile('./ansible.cfg'):
                ansible_cfg_file = './ansible.cfg'
            elif os.path.isfile('~/.ansible.cfg'):
                ansible_cfg_file = '~/.ansible.cfg'
            elif os.path.isfile('/etc/ansible/ansible.cfg'):
                ansible_cfg_file = "/etc/ansible/ansible.cfg"
            else:
                module.fail_json(msg="No Ansible Cfg File Found.")
        config = configparser.ConfigParser()
        config.read(ansible_cfg_file)
        vault_password_file = config['defaults'].get('vault_password_file', False)
        if not vault_password_file:
            module.fail_json(msg="No vault_password_file entry in ansible.cfg")
        try:
            passwd = open(vault_password_file).read()
            passwd = passwd.rstrip('\n')
            self.vault = Vault(passwd)
            data = self.vault.load(open('./files/tokens/' + array_name).read())
            if data == None:
                self.file_data = {}
            else:
                self.file_data = data
        except:
            self.file_data = {}

    def write_encrypted_file(self, data):

        if os.path.isfile('./files/tokens/' + self.array_name):
            try:
                os.unlink('./files/tokens/' + self.array_name)
            except OSError:
                self.module.fail_json(msg='Can not remove ./files/tokens/' + self.array_name)


        with open('./files/tokens/' + self.array_name, 'w') as f:
            f.write(self.vault.dump(data))


class ApiTokenGenerator:

    def __init__(self, ip, key, module):
        self.fb = PurityFb(ip)
        self.fb.disable_verify_ssl()
        self.module = module
        self.ip = ip
        try:
            self.fb.login(key)
        except rest.ApiException as e:
            module.fail_json(msg='Failed to connect to FlashBlade. Check Credentials')


    def return_new_token(self, user, force_generate=False):

        localAdmin = Admin()
        localAdmin.create_api_token = True
        try:
            res = self.fb.admins.update_admins(names=[user], admin=localAdmin).to_dict()
        except rest.ApiException:
            if force_generate:
                try:
                    localAdmin = Admin( delete_api_token=True )
                    res = self.fb.admins.update_admins(names=[user], admin=localAdmin)

                    localAdmin = Admin( create_api_token=True )
                    res = self.fb.admins.update_admins(names=[user], admin=localAdmin).to_dict()

                except:
                    #self.module.fail_json(msg='Updated failed.  Unknown Error.')
                    self.module.fail_json(msg=res)
            else:
                self.module.exit_json(changed=False, msg='Update failed.  force_update not enabled. Exiting.')
        try:
            self.result_token = res['items'][0]['api_token']['token']
        except KeyError:
            self.module.fail_json(msg='Did not return expected data structure. Keyerror.')

        return self.result_token

    def delete_token(self, user):
        localAdmin = Admin()
        localAdmin.delete_api_token = True

        try:
            res = self.fb.admins.update_admins(names=[user], admin=localAdmin).to_dict()
        except rest.ApiException:
            self.module.fail_json(msg="Failed to delete token for: " + user + " on " + self.ip)


def delete_keys(**kwargs):
    names = kwargs.get('names', False)
    force_update = kwargs.get('force_update', False)
    fb_url = kwargs.get('fb_url', False)
    array_name = kwargs.get('array_name', False)
    api_token = kwargs.get('api_token', False)
    module = kwargs.get('module', False)

    exit_data = {}
    for name in names:
        vaultFile = LocalVault(array_name, module)
        vault_data = vaultFile.file_data
        tokenGenerator = ApiTokenGenerator(fb_url, api_token, module)
        tokenGenerator.delete_token(name)
        try:
            del vault_data[name]
        except KeyError:
            pass
        try:
            del exit_data[name]
        except:
            pass
        exit_data.update(vault_data)
        vaultFile.write_encrypted_file(vault_data)
    module.exit_json(changed=True, key_data=exit_data)

def add_keys(**kwargs):
    names = kwargs.get('names', False)
    force_update = kwargs.get('force_update', False)
    fb_url = kwargs.get('fb_url', False)
    array_name = kwargs.get('array_name', False)
    api_token = kwargs.get('api_token', False)
    module = kwargs.get('module', False)


    exit_data = {}
    for name in names:
        vaultFile = LocalVault(array_name, module)
        vault_data = vaultFile.file_data
        tokenGenerator = ApiTokenGenerator(fb_url, api_token, module)
        result_token = tokenGenerator.return_new_token(name, force_generate=force_update)
        new_data = {name: result_token}
        vault_data.update(new_data)
        exit_data.update(new_data)
        vaultFile.write_encrypted_file(vault_data)

    module.exit_json(changed=True, key_data=exit_data)

def main():

    module = AnsibleModule(argument_spec={
        'names': {'type': 'list', 'required': True},
        'operation': {'type': 'str', 'required': True},
        'force_update': {'type': 'bool', 'required': True},
        'fb_url': {'type': 'str', 'required': True},
        'api_token': {'type': 'str', 'required': True},
        'array_name': {'type': 'str', 'required': True},
    })
    names = module.params['names']
    operation = module.params['operation']
    force_update = module.params['force_update']
    fb_url = module.params['fb_url']
    api_token = module.params['api_token']
    array_name = module.params['array_name']

    module_kwargs = {
        'names': names,
        'force_update': force_update,
        'fb_url': fb_url,
        'api_token': api_token,
        'array_name': array_name,
        'module': module
    }

    if operation.lower() == 'add' or operation.lower() == 'create':
        add_keys(**module_kwargs)

    if operation.lower() == 'delete' or operation.lower() == 'remove':
        delete_keys(**module_kwargs)


if __name__ == "__main__":
    main()