from enum import Enum


class DeckType(str, Enum):
    default = "default"
    public = "public"
    public_mnemonic = "public_mnemonic"
    sanity_check = "sanity_check"
    hidden = "hidden"
    deleted = "deleted"
