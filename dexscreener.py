"""
Client for DexScreener APIs
"""

from decimal import Decimal
from typing import Any

import requests

from common import PriceInfo, TokenOverview
from custom_exceptions import InvalidSolanaAddress, InvalidTokens, NoPositionsError
from utils.helpers import is_solana_address
from vars.constants import SOL_MINT


class DexScreenerClient:
    """
    Handler class to assist with all calls to DexScreener API
    """

    @staticmethod
    def _validate_token_address(token_address: str):
        """
        Validates token address to be a valid solana address

        Args:
            token_address (str): Token address to validate

        Returns:
            None: If token address is valid

        Raises:
            NoPositionsError: If token address is empty
            InvalidSolanaAddress: If token address is not a valid solana address
        """
        if not token_address:
            raise NoPositionsError()

        is_valid = is_solana_address(token_address)

        if not is_valid:
            raise InvalidSolanaAddress()

    def _validate_token_addresses(self, token_addresses: list[str]):
        """
        Validates token addresses to be a valid solana address

        Args:
            token_addresses (list[str]): Token addresses to validate

        Returns:
            None: If token addresses are valid

        Raises:
            NoPositionsError: If token addresses are empty
            InvalidSolanaAddress: If any token address is not a valid solana address
        """
        if not token_addresses:
            raise NoPositionsError()

        for token_address in token_addresses:
            self._validate_token_address(token_address)

    @staticmethod
    def _validate_response(resp: requests.Response):
        """
        Validates response from API to be 200

        Args:
            resp (requests.Response): Response from API

        Returns:
            None: If response is 200

        Raises:
            InvalidTokens: If response is not 200
        """
        if resp.status_code != 200:
            raise InvalidTokens()

    def _call_api(self, token_address: str) -> dict[str, Any]:
        """
        Calls DexScreener API for a single token

        Args:
            token_address (str): Token address for which to fetch data

        Returns:
            dict[str, Any]: JSON response from API

        Raises:
            InvalidTokens: If response is not 200
            NoPositionsError: If token address is empty
            InvalidSolanaAddress: If token address is not a valid solana address
        """
        self._validate_token_address(token_address)

        # TODO: Check and Update for the valid API endpoint of DexScreener
        res = requests.get(
            f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
        )
        self._validate_response(res)

        return res.json()

    def _call_api_bulk(self, token_addresses: list[str]) -> dict[str, Any]:
        """
        Calls DexScreener API for multiple tokens

        Args:
            token_addresses (list[str]): Token addresses for which to fetch data

        Returns:
            dict[str, Any]: JSON response from API

        Raises:
            InvalidTokens: If response is not 200
            NoPositionsError: If token addresses are empty
            InvalidSolanaAddress: If any token address is not a valid solana address
        """
        self._validate_token_addresses(token_addresses)

        res = requests.get(
            f"https://api.dexscreener.com/latest/dex/tokens/{','.join(token_addresses)}"
        )
        self._validate_response(res)

        return res.json()

    def fetch_prices_dex(
        self, token_addresses: list[str]
    ) -> dict[str, PriceInfo[Decimal, Decimal]]:
        """
        For a list of tokens fetches their prices
        via multi API ensuring each token has a price

        Args:
            token_addresses (list[str]): A list of tokens for which to fetch prices

        Returns:
           dict[str, dict[Decimal, PriceInfo[str, Decimal]]: Mapping of token to a named tuple PriceInfo with price and liquidity in Decimal

        """
        res = self._call_api_bulk(token_addresses)

        prices = {}
        for token_address, data in res.items():
            prices[token_address] = PriceInfo(
                Decimal(data["price"]),
                Decimal(data["liquidity"]),
            )

        return prices

    def fetch_token_overview(self, address: str) -> TokenOverview:
        """
        For a token fetches their overview
        via Dex API ensuring each token has a price

        Args:
        address (str): A token address for which to fetch overview

        Returns:
        TokenOverview: Overview with a lot of token information I don't understand
        """

        res = self._call_api(address)

        return TokenOverview(
            price=Decimal(res["price"]),
            symbol=res["symbol"],
            decimals=res["decimals"],
            lastTradeUnixTime=res["lastTradeUnixTime"],
            liquidity=Decimal(res["liquidity"]),
            supply=Decimal(res["supply"]),
        )

    @staticmethod
    def find_largest_pool_with_sol(token_pairs, address):
        max_entry = {}
        max_liquidity_usd = -1

        for entry in token_pairs:
            # Check if the baseToken address matches the specified address
            if (
                entry.get("baseToken", {}).get("address") == address
                and entry["quoteToken"]["address"] == SOL_MINT
            ):
                liquidity_usd = float(entry.get("liquidity", {}).get("usd", 0))
                if liquidity_usd > max_liquidity_usd:
                    max_liquidity_usd = liquidity_usd
                    max_entry = entry
        return max_entry

# TODO: Uncomment the code below to test the DexScreenerClient
# if __name__ == "__main__":
#     be_client = DexScreenerClient()
#     test_tokens = [
#         "WskzsKqEW3ZsmrhPAevfVZb6PuuLzWov9mJWZsfDePC",
#         "2uvch6aviS6xE3yhWjVZnFrDw7skUtf6ubc7xYJEPpwj",
#         "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
#     ]
#     print(be_client.fetch_prices_dex(token_addresses=test_tokens))
#     print(be_client.fetch_token_overview(address=test_tokens[0]))
