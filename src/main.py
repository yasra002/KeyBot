#!/usr/bin/env python
# KeyBot main executor
import argparse,os

from gitlab_keys import GitlabKeys
from user_utils import UserUtils


def main():
    parser = argparse.ArgumentParser()
    parser.description = "KeyBot will help automatically set up users from Gitlab as users on an Ubuntu box."
    parser.add_argument("--gitlab-group", help="Group name from Gitlab that users will be pulled from. Use name from URL/Group page, not decorated name.", default="group")
    parser.add_argument("--system-group", help="Group name on box that Gitlab users will be put into.", default="keybot")
    parser.add_argument("--gitlab-token", help="Private token from account page on Gitlab. Can also set using env variable KEYBOT_GITLAB_TOKEN.", default="")
    args = parser.parse_args()
    gitlab_token = os.environ.get("KEYBOT_GITLAB_TOKEN", args.gitlab_token)
    gitlab = GitlabKeys(gitlab_token,args.gitlab_group)
    users = UserUtils(args.system_group)

    #Now things are set up, time to get Gitlab users and start trying to set them up on system
    gitlab_users = gitlab.get_usernames_from_group_json(gitlab.get_users_in_group_id(gitlab.get_group_id_from_group_name()))
    system_users = users.get_users_in_group()

    #Go through each gitlab user to do work on
    print "Creating/Updating users"
    for gl_user in gitlab_users:

        #check if gitlab user is active
        if gitlab.is_user_active(gitlab.get_user_id_from_username(gl_user)) and not(gitlab.is_user_external(gl_user)):

            #If a user exists on the system already, make sure their keys match from gitlab.
            if gl_user in system_users:

                #Just in case gitlab token isn't an admin, don't crash on getting keys and instead print out keys will not be updated.
                try:
                    users.write_authorized_keys_for_user(gl_user,gitlab.assemble_authorized_keys_from_keys_json(gitlab.get_keys_for_user(gitlab.get_user_id_from_username(gl_user))))
                except EnvironmentError:
                    print "Gitlab token does not have admin permission. Keys for user "+gl_user+" will not be added/updated."
            else:

                #User not made yet. Create user, put in group, and add in keys.
                users.add_user(gl_user)

                #Make sure group exists before adding to.
                if users.get_group_by_name(users.managing_group) is None:
                    users.add_group(users.managing_group)
                users.add_user_to_existing_group(gl_user,users.managing_group)

                #If docker is installed, add users to the docker group too
                if not(users.get_group_by_name("docker") is None):
                    users.add_user_to_existing_group(gl_user,"docker")

                #If user is an admin or is an owner of current group, make them have sudo permission
                if gitlab.is_admin(gl_user) or gitlab.get_user_auth_level_from_group_members(gl_user) == GitlabKeys.GitlabAuthLevels.OWNER:
                    users.add_user_to_existing_group(gl_user, "sudo")
                    users.add_passwordless_sudoers_file(gl_user)

                #Just in case gitlab token isn't an admin, don't crash on getting keys and instead print out keys will not be updated.
                try:
                    users.write_authorized_keys_for_user(gl_user,gitlab.assemble_authorized_keys_from_keys_json(gitlab.get_keys_for_user(gitlab.get_user_id_from_username(gl_user))))
                except EnvironmentError:
                    print "Gitlab token does not have admin permission. Keys for user " + gl_user + " will not be added/updated."
        else:

            #User isn't active or is external. If user exists on system, remove them.
            if gl_user in system_users:
                users.remove_user_from_existing_group(gl_user,users.managing_group)
                users.remove_user(gl_user)
                if gl_user in users.get_users_in_group("sudo"):
                    users.remove_user_from_existing_group(gl_user, "sudo")
                    users.remove_passwordless_sudoers_file(gl_user)
    print "Finished"


def test():
    token = os.environ.get("KEYBOT_GITLAB_TOKEN","")
    gitlab = GitlabKeys(token)
    users = UserUtils()

    #Run Gitlab tests
    if(not(gitlab.am_admin())):
        raise Exception("Token is not for an admin")
    print "Listing blocked users"
    for user in gitlab.get_users_in_group_id(gitlab.get_group_id_from_group_name()):
        if(user["state"] == "blocked"):
            print user["username"]+":blocked"

    #Run some user tests
    users.add_user("dumbtest")
    users.add_group("keybot")
    users.add_user_to_existing_group("dumbtest","keybot")
    users.write_authorized_keys_for_user("dumbtest","key here")
    if(not(users.get_user_by_name("dumbtest") is None)):
        print "User made"
    if("dumbtest" in users.get_users_in_group()):
        print "User in right group"
    if(os.access("/home/dumbtest/.ssh/authorized_keys",os.F_OK)):
        print "Keys file made"
    users.remove_user_from_existing_group("dumbtest","keybot")
    users.remove_user("dumbtest")

if __name__ == '__main__':
    if("KEYBOT_RUN_TESTS" in os.environ):
        test()
    else:
        main()
