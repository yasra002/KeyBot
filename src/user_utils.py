"""
Python class to deal with managing users on the running system
"""
import os,libuser


class UserUtils(object):

    def __init__(self, group_to_manage="keybot"):
        self.managing_group = group_to_manage

    def get_users_in_group(self, group=None):
        if(group is None):
            group = self.managing_group
        users = libuser.admin().enumerateUsersByGroup(group)
        return users

    def get_user_by_name(self, username):
        return libuser.admin().lookupUserByName(username)

    def get_group_by_name(self, group_name):
        return libuser.admin().lookupGroupByName(group_name)

    # region Creation tools
    def add_user_to_existing_group(self, username, group_name):
        group = self.get_group_by_name(group_name)
        user_list = group.get(libuser.MEMBERNAME)
        if(username not in user_list):
            user_list.append(username)
            group.set(libuser.MEMBERNAME,user_list)
            libuser.admin().modifyGroup(group)

    def add_user(self, username):
        user = libuser.admin().initUser(username)
        user.set(libuser.LOGINSHELL,"/bin/bash") #might want to allow picking in future
        #currently does not give user it's own group. Might reconsider
        libuser.admin().addUser(user)

    def add_group(self, group_name):
        group = libuser.admin().initGroup(group_name)
        libuser.admin().addGroup(group)

    def add_passwordless_sudoers_file(self, username):
        sudo_file = open(os.path.join("/etc/sudoers.d/", username),"w")
        sudo_file.write(username + " ALL=NOPASSWD: ALL")
        sudo_file.close()

    def remove_passwordless_sudoers_file(self, username):
        if os.access(os.path.join("/etc/sudoers.d/", username),os.F_OK):
            os.remove(os.path.join("/etc/sudoers.d/", username))
    # endregion

    # region Removal tools
    def remove_user_from_existing_group(self, username, group_name):
        group = self.get_group_by_name(group_name)
        user_list = group.get(libuser.MEMBERNAME)
        if (username in user_list):
            user_list.remove(username)
            group.set(libuser.MEMBERNAME, user_list)
            libuser.admin().modifyGroup(group)

    def remove_user(self, username):
        user = libuser.admin().lookupUserByName(username)
        libuser.admin().deleteUser(user, True, True)
    # endregion

    def write_authorized_keys_for_user(self, username, keys):
        user = libuser.admin().lookupUserByName(username)
        home_dir = "/root"
        if(len(user.get(libuser.HOMEDIRECTORY)) > 0):
            home_dir = user.get(libuser.HOMEDIRECTORY)[0]
        if(not os.access(os.path.join(home_dir, "/.ssh/authorized_keys"),os.F_OK)):
            os.mkdir(os.path.join(home_dir, "/.ssh"),0700)
        with open(os.path.join(home_dir, "/.ssh/authorized_keys"),"w") as keys_file:
            keys_file.write(keys)
        user_uid = user.get(libuser.UIDNUMBER)[0]
        user_gid = user.get(libuser.GIDNUMBER)[0]
        os.chown(keys_file.name,user_uid, user_gid)
        os.chown(os.path.dirname(keys_file.name), user_uid, user_gid)
        os.chmod(keys_file.name, 0700)
