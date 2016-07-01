"""
Python class for getting gitlab user list and keys.
"""
import requests
from enum import Enum


class GitlabKeys(object):

    class GitlabAuthLevels(Enum):
        GUEST = 10
        REPORTER = 20
        DEVELOPER = 30
        MASTER = 40
        OWNER = 50

    def __init__(self, token="", group="group"):
        self.auth_token = token
        self.group = group
        self.__auth_header__ = "PRIVATE-TOKEN"
        self.__gitlab_base_url__ = "https://gitlab.com/api/v3"
        self.__gitlab_user_self_path__ = "/user"
        self.__gitlab_user_details_path_template__ = "/users/{0}"
        self.__gitlab_group_member_list_path_template__ = "/groups/{0}/members"
        self.__gitlab_user_ssh_keys_path_template__ = "/users/{0}/keys"
        self.__gitlab_username_path_template__ = "/users?username={0}"
        self.__gitlab_group_search_path_template__ = "/groups?search={0}"
        try:
            self.__am_admin__ = self.am_admin()
        except Exception:
            self.__am_admin__ = False

    def __get_auth_header__(self):
        return {self.__auth_header__:self.auth_token}

    def am_admin(self):
        gitlab_self_request = requests.get(self.__gitlab_base_url__ + self.__gitlab_user_self_path__, headers=self.__get_auth_header__())
        if(gitlab_self_request.ok):
            return gitlab_self_request.json()["is_admin"]
        else:
            raise Exception("Error contacting gitlab:{0}".format(gitlab_self_request.status_code))

    def is_admin(self, username):
        gitlab_user = requests.get(self.__gitlab_base_url__ + self.__gitlab_username_path_template__.format(username), headers=self.__get_auth_header__())
        if(gitlab_user.ok):
            return list(gitlab_user.json())[0]["is_admin"]
        else:
            raise Exception("Error contacting gitlab:{0}".format(gitlab_user.status_code))

    def is_user_active(self, user_id):
        gitlab_user_details = requests.get(self.__gitlab_base_url__ + self.__gitlab_user_details_path_template__.format(user_id), headers=self.__get_auth_header__())
        if(gitlab_user_details.ok):
            return gitlab_user_details.json()["state"] == "active"
        else:
            raise Exception("Error contacting gitlab:{0}".format(gitlab_user_details.status_code))

    def is_user_external(self, username):
        gitlab_user = requests.get(self.__gitlab_base_url__ + self.__gitlab_username_path_template__.format(username), headers=self.__get_auth_header__())
        if(gitlab_user.ok):
            return list(gitlab_user.json())[0]["external"]
        else:
            raise Exception("Error contacting gitlab:{0}".format(gitlab_user.status_code))

    # region Group Utils
    def get_users_in_group_id(self,group_id):
        gitlab_user_group_list = requests.get(self.__gitlab_base_url__ + self.__gitlab_group_member_list_path_template__.format(group_id), headers=self.__get_auth_header__())
        if(gitlab_user_group_list.ok):
            return gitlab_user_group_list.json()
        else:
            raise Exception("Error contacting gitlab:{0}".format(gitlab_user_group_list.status_code))

    def get_usernames_from_group_json(self,group_json):
        users = []
        for group_user in group_json:
            users.append(group_user["username"])
        return users

    def get_user_ids_from_group_json(self,group_json):
        user_ids = []
        for group_user in group_json:
            user_ids.append(group_user["id"])
        return user_ids

    def get_user_id_from_username(self, username):
        gitlab_user = requests.get(self.__gitlab_base_url__ + self.__gitlab_username_path_template__.format(username), headers=self.__get_auth_header__())
        if gitlab_user.ok:
            if len(gitlab_user.json()) > 0:
                return list(gitlab_user.json())[0]["id"]
            else:
                return None
        else:
            raise Exception("Error contacting gitlab:{0}".format(gitlab_user.status_code))

    def get_user_auth_level_from_group_members(self, username):
        gitlab_users = self.get_users_in_group_id(self.get_group_id_from_group_name())
        for user in gitlab_users:
            if user["username"] == username:
                return GitlabKeys.GitlabAuthLevels(user["access_level"])
        return None

    def get_group_id_from_group_name(self, group_name=None):
        #Default to group set when making class object if none passed.
        if(group_name is None):
            group_name = self.group
        gitlab_group_results = requests.get(self.__gitlab_base_url__ + self.__gitlab_group_search_path_template__.format(group_name), headers=self.__get_auth_header__())
        if(gitlab_group_results.ok):
            return list(gitlab_group_results.json())[0]["id"]
        else:
            raise Exception("Error contacting gitlab:{0}".format(gitlab_group_results.status_code))
    # endregion

    # region Key Utils
    def get_keys_for_user(self,user_id):
        if(self.__am_admin__):
            gitlab_user_keys = requests.get(self.__gitlab_base_url__ + self.__gitlab_user_ssh_keys_path_template__.format(user_id), headers=self.__get_auth_header__())
            if(gitlab_user_keys.ok):
                return gitlab_user_keys.json()
            else:
                raise Exception("Error contacting gitlab:{0}".format(gitlab_user_keys.status_code))
        else:
            raise EnvironmentError("Must be admin to get keys")

    def assemble_authorized_keys_from_keys_json(self,keys_json):
        return '\n'.join(key['key'] for key in keys_json) + '\n'
    # endregion
