# Ansible project to manage Day Zero FlashArray configurations.

## Installation 

### Stand alone machine

Install python requirements

'pip3 install -r requirements.txt`

### Modify the variables in the template to show your site(s)
vim roles/copy-template/templates/vars_file_template.yml

### Modify the vault_file and add your array credentials
ansible-vault edit group_vars/all/vault_file

### Run some tests

### Run only the ntp play on the npc environment
ansible-playbook ./infra.yml -e site_env=npc --tags ntp

