# app/core/exaption_messages.py

"""Central place for reusable message strings.

This follows the same idea as utils/Messages.java in the Spring project:
all commonly used error or info messages live here.
"""

class Messages:
    # ===== Auth and user related messages =====
    CREDENTIALS_NOT_VALID = "Could not validate credentials."
    USERNAME_TAKEN = "Username is already taken."
    EMAIL_REGISTERED = "Email is already registered."
    INCORRECT_USERNAME_OR_PASSWORD = "Incorrect username or password."

    # ===== Group related messages =====
    GROUP_NOT_FOUND = "Group not found."
    GROUP_NOT_ADMIN = "You are not an admin of this group."
    GROUP_MEMBER_NOT_FOUND = "Member is not part of this group."
    MUST_JOIN_TO_VIEW = "You must join the group to see its posts."
    MUST_JOIN_TO_POST = "You must join the group to create posts."
    ALREADY_MEMBER = "Already a member of this group."
    NOT_A_MEMBER = "You are not a member of this group."

    