# def is_solana_address(input_string: str) -> bool:
#     try:
#         Pubkey.from_string(input_string)
#         return True
#     except ValueError:
#         return False

import base58


def is_solana_address(address: str) -> bool:
    try:
        decoded = base58.b58decode(address)
        return len(decoded) == 32
    except Exception:
        return False
