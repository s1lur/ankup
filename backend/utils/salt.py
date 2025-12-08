import requests
import time
from django.conf import settings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import logging

logger = logging.getLogger(__name__)

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class SaltClient:
    def __init__(self, login=False):
        self.base_url = settings.SALT_API_URL
        self.session = requests.Session()

        if login:
            self.login()

    def login(self):
        payload = {
            'username': settings.SALT_API_USER,
            'password': settings.SALT_API_PASSWORD,
            'eauth': 'pam'
        }
        try:
            response = self.session.post(
                f"{self.base_url}/login",
                json=payload,
                verify=False,
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Salt Login Error: {e}")
            raise

    def run_sync(self, tgt, fun, arg=None, tgt_type='glob'):
        payload = {
            'client': 'local',
            'tgt': tgt,
            'fun': fun,
            'tgt_type': tgt_type
        }
        if arg:
            payload['arg'] = arg

        response = self.session.post(
            f"{self.base_url}/run",
            json=payload,
            verify=False
        )
        return response.json()

    def run_async(self, tgt, fun, arg=None, tgt_type='list'):
        payload = {
            'client': 'local_async',
            'tgt': tgt,
            'fun': fun,
            'tgt_type': tgt_type
        }
        if arg:
            payload['arg'] = arg

        response = self.session.post(
            f"{self.base_url}/run",
            json=payload,
            verify=False
        )
        data = response.json()
        return data['return'][0]['jid']

    def ping_minions(self, target='*'):
        if isinstance(target, list):
            tgt_arg = ','.join(target)
            tgt_type = 'list'
        else:
            tgt_arg = target
            tgt_type = 'glob'

        result = self.run_sync(tgt=tgt_arg, fun='test.ping', tgt_type=tgt_type)

        return result.get('return', [{}])[0]

    def wait_for_job(self, jid, timeout=600, sleep_interval=5):
        start_time = time.time()

        while time.time() - start_time < timeout:
            response = self.session.get(
                f"{self.base_url}/jobs/{jid}",
                verify=False,
            )

            if response.status_code == 200:
                data = response.json()
                return_data = data.get('return', [{}])[0]

                if return_data:
                    return return_data

            time.sleep(sleep_interval)

        raise TimeoutError(f"Job {jid} timed out")
