from enum import Enum


class DeckType(str, Enum):
    default = "default"
    public = "public"
    public_mnemonic = "public_mnemonic"
    hidden = "hidden"
    deleted = "deleted"
