from enum import Enum


class Permission(str, Enum):
    owner = "owner"
    viewer = "viewer"
