import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError
import configparser
from math import ceil
import email_notifier

# Pull keys and other configurations
config = configparser.ConfigParser()
config.read('config.ini')
mailchimp_config = config['MAILCHIMP']

# API Reference https://github.com/mailchimp/mailchimp-marketing-python

DEFAULT_MEMBERS_COUNT = 500

class OnCampusJobList():
    def __init__(self):
        self._client = self.get_mailchimp_client()
        self._info = None
        self._members = None

    def get_mailchimp_client(self) -> MailchimpMarketing.Client:
        client = MailchimpMarketing.Client()
        client.set_config({
            "api_key": mailchimp_config['MAILCHIMP_API_KEY'],
            "server": mailchimp_config['MAILCHIMP_SERVER_PREFIX']
        })
        return client

    def get_list_id(self):
        return self.get_info()['id']

    def get_info(self):
        if self._info is None:
            mailchimp_lists = self._client.lists.get_all_lists()['lists']
            def custom_filter_lambda(
                x): return x['name'] == mailchimp_config['LIST_NAME']
            gt_on_campus_list = list(
                filter(custom_filter_lambda, mailchimp_lists))
            if len(gt_on_campus_list) == 1:
                self._info = gt_on_campus_list[0]
            else:
                raise f"Failed to find a unique list for '{GT_ON_CAMPUS_LIST_ID}'"

        return self._info

    def get_members(self):
        if self._members is None:
            list_id = self.get_list_id()
            members_info = self._client.lists.get_list_members_info(list_id, count=DEFAULT_MEMBERS_COUNT)
            
            total_members = members_info['total_items']
            self._members = members_info['members']

            if total_members > len(self._members):                
                max_offset = ceil(total_members / DEFAULT_MEMBERS_COUNT)
                for i in range(1, max_offset):
                    current_offset = DEFAULT_MEMBERS_COUNT * i
                    current_members = self._client.lists.get_list_members_info(list_id, count=DEFAULT_MEMBERS_COUNT, offset=current_offset)['members']
                    self._members += current_members
            
        return self._members

    def get_email_list(self):
        members = self.get_members()
        return [x['email_address'] for x in members if x['status'] == "subscribed"]

    def add_list_member(self, email):
        list_id = self.get_list_id()
        params = {
            'email_address': email,
            'status': 'subscribed'
        }
        return self._client.lists.add_list_member(list_id, body=params)


if __name__ == "__main__":
    custom_list = OnCampusJobList()
    members = custom_list.get_email_list()
    print("Email list currently has {} members:\n".format(len(members)) + str([x for x in members]))
