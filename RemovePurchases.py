import ConfigParser
import os
import sys
import requests

APP_DIR = os.path.abspath(os.path.dirname(__file__))
CC = ConfigParser.RawConfigParser()
CONFIGFILE = os.path.join(APP_DIR, 'script.cfg')

if os.path.isfile(CONFIGFILE):
    CC.readfp(open(CONFIGFILE, "r"))
    RETRY = int(CC.get('settings', 'retry'))
    VENDOR = str(CC.get('settings', 'vendor'))


else:
    print '\n[!] Cannot find config file!'
    print '\tExiting...'
    sys.exit()


class Device42rest:
    def __init__(self, params):
        self.username = params['username']
        self.password = params['password']
        self.url = params['url']

    def get_data(self, path, params):
        url = self.url + path
        for x in range(RETRY):
            try:
                r = requests.get(url, auth=(self.username, self.password), params=params, verify=False)
                print r.json()
                return r.json()
            except requests.RequestException as e:
                msg = str(e)
                print '\n[!] HTTP error. Message was: %s' % msg

    def remove_data(self, path):
        url = self.url + path
        for x in range(RETRY):
            try:
                r = requests.delete(url, auth=(self.username, self.password), verify=False)
                print r.json()
            except requests.RequestException as e:
                msg = str(e)
                print '\n[!] HTTP error. Message was: %s' % msg

    def get_all_purchases_by_vendor(self, vendor):
        purchase_endpoint = '/api/1.0/purchases/'
        try:
            return self.get_data(purchase_endpoint, {'vendor': str(vendor)})
        except Exception:
            raise Exception('No purchases for the specified vendor was returned')

    def remove_purchase_by_id(self, purchase_id):
        purchase_endpoint = '/api/1.0/purchases/' + str(purchase_id) + '/'
        try:
            return self.remove_data(purchase_endpoint)
        except Exception:
            raise Exception('Failed to remove purchase with id %s' % purchase_id)


class Config:
    def __init__(self):
        self.cc = CC

    def get_settings_cfg(self):
        # Device42 -----------------------------------------
        d42_username = self.cc.get('device42', 'username')
        d42_password = self.cc.get('device42', 'password')
        d42_url = self.cc.get('device42', 'url')

        return {
            'username': d42_username,
            'password': d42_password,
            'url': d42_url,
        }


if __name__ == '__main__':
    # script
    cfg = Config()
    settings = cfg.get_settings_cfg()
    rest = Device42rest(settings)
    all_purchases_for_vendor = rest.get_all_purchases_by_vendor(VENDOR)  # get all the purchases for a vendor

    purchase_ids = []  # list that contains all the ids for purchases for a vendor

    # get all the purchase ids for a vendor
    if 'purchases' in all_purchases_for_vendor:
        for purchase in all_purchases_for_vendor['purchases']:
            if 'purchase_id' in purchase:
                purchase_ids.append(purchase['purchase_id'])
    else:
        print 'No purchases for the specified vendor %s was returned' % VENDOR

    # iterate all of the purchase ids and remove them
    for po_id in purchase_ids:
        rest.remove_purchase_by_id(po_id)

    print('Done..')
