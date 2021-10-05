from purity_fb import PurityFb, rest
import logging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
urllib3_log = logging.getLogger("urllib3")
urllib3_log.setLevel(logging.CRITICAL)

API_TOKEN = 'T-cbd0c419-1f88-493a-ae09-51e6687f6c25'

fb = PurityFb("172.29.10.190")
fb.disable_verify_ssl()
try:
    res = fb.login(API_TOKEN)
except rest.ApiException as e:
    print("Exception when logging in to the array: %s\n" % e)
if res:
    try:
        res = fb.login_banner.list_login_banner().to_dict()
        print(res)
    except rest.ApiException as e:
        print("Exception when listing banner settings: %s\n" % e)
