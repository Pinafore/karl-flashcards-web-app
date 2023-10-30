from enum import Enum


class DeckType(str, Enum):
    default = "default"
    public = "public"
    hidden = "hidden"
    deleted = "deleted"
