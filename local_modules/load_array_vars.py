#!env python
from ansible.module_utils.basic import *
from ansible_vault import Vault
import yaml
from yaml import FullLoader
import configparser

import os


class LocalVault:
    def __init__(self, vault_file, module):

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
            vault = Vault(passwd)
            data = vault.load(open(vault_file).read())
            self.file_data = data
        except:
            self.file_data = False



def main():

    module = AnsibleModule(argument_spec={
                               'site': {'type': 'str', 'required': False},
                               'flashblade': {'type': 'str', 'required': False}
                                },
                            required_one_of=['site', 'flashblade']
    )
    site = module.params['site']
    flashblade = module.params['flashblade']

    if flashblade and flashblade.lower() == 'false':
        flashblade = False

    dir = os.getcwd()
    if site and site.lower() == 'false':
        site = False

    if site:
        site_dir = dir + '/host_variables/' + site
        files = os.listdir(site_dir)

    output = []
    if flashblade:
        base_dir = dir + '/host_variables/'
        all_blades = {}
        dir = os.listdir(base_dir)
        for each in dir:
            if os.path.isdir(base_dir + each):
                dir_to_search = base_dir + each + '/'
                all_files = os.listdir(dir_to_search)

                for file in all_files:
                    if os.path.isfile(dir_to_search + file):
                        all_blades[file] = {
                            'file': dir_to_search + file,
                            'site': each
                        }
        if flashblade not in all_blades.keys():
            module.fail_json(msg="No file for " + flashblade)


        vaultClass = LocalVault(all_blades[flashblade]['file'], module)
        if vaultClass.file_data:
            module.exit_json(
                success=True,
                changed=False,
                target_arrays=[vaultClass.file_data],
                site=all_blades[flashblade]['site']
            )

        with open(all_blades[flashblade]['file']) as f:
            loaded = yaml.load(f, Loader=FullLoader)
            output.append(loaded)
            module.exit_json(
                success=True,
                changed=False,
                target_arrays=output,
                site=all_blades[flashblade]['site']
            )

    for file in files:
        vaultClass = LocalVault(site_dir + '/' + file, module)
        if vaultClass.file_data:
            output.append(vaultClass.file_data)
        else:
            with open(site_dir + '/' + file) as f:
                loaded = yaml.load(f, Loader=FullLoader)
                output.append(loaded)

    module.exit_json(success=True,
                     changed=True,
                     target_arrays=output,
                     flashblade=flashblade,
                     site=site
                     )

if __name__ == '__main__':
    main()
