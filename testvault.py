from ansible import constants as C
from ansible.cli import CLI
from ansible.parsing.vault import VaultLib
from ansible.parsing.dataloader import DataLoader
import pprint


cfgfile = "./group_vars/all/vault_file"
loader = DataLoader()
vault_secrets = CLI.setup_vault_secrets(loader=loader,
             vault_ids=C.DEFAULT_VAULT_IDENTITY_LIST)
loader.set_vault_secrets(vault_secrets)
data = loader.load_from_file(cfgfile)
loader = DataLoader()
vault_secrets = CLI.setup_vault_secrets(loader=loader,
            vault_ids=C.DEFAULT_VAULT_IDENTITY_LIST)
loader.set_vault_secrets(vault_secrets)
data = loader.load_from_file(cfgfile)
pprint.pprint(data)
