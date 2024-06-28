import requests
from decimal import Decimal

from config import Config
from common import PriceInfo, TokenOverview
from custom_exceptions import (
    NoPositionsError,
    DecimalsNotFoundError,
    InvalidSolanaAddress,
    InvalidTokens,
    NO_LIQUDITY,
)
from utils.helpers import is_solana_address


class BirdEyeClient:
    """
    Handler class to assist with all calls to BirdEye API
    """

    @property
    def _headers(self):
        return {
            "accept": "application/json",
            "x-chain": "solana",
            "X-API-KEY": Config.BIRD_EYE_TOKEN,
        }

    def _make_api_call(
        self, method: str, query_url: str, *args, **kwargs
    ) -> requests.Response:
        match method.upper():
            case "GET":
                query_method = requests.get
            case "POST":
                query_method = requests.post
            case _:
                raise ValueError(
                    f'Unrecognised method "{method}" passed for query - {query_url}'
                )
        resp = query_method(query_url, *args, headers=self._headers, **kwargs)
        return resp

    def fetch_prices(
        self, token_addresses: list[str]
    ) -> dict[str, PriceInfo[Decimal, Decimal]]:
        """
        For a list of tokens fetches their prices
        via multi-price API ensuring each token has a price

        Args:
            token_addresses (list[str]): A list of tokens for which to fetch prices

        Returns:
           dict[str, dict[str, PriceInfo[Decimal, Decimal]]: Mapping of token to a named tuple PriceInfo with price and liquidity

        Raises:
            NoPositionsError: Raise if no tokens are provided
            InvalidToken: Raised if the API call was unsuccessful
        """

        if not token_addresses:
            raise NoPositionsError("No tokens provided for fetching prices")

        query_url = f"{Config.BIRD_EYE_URL}/multi_price"
        resp = self._make_api_call(
            "GET",
            query_url,
            params={"list_address": ",".join(token_addresses)},
        )

        if resp.status_code != 200:
            raise InvalidTokens(InvalidTokens.message)

        prices = resp.json()
        return prices

    def fetch_token_overview(self, address: str) -> TokenOverview:
        """
        For a token fetches their overview
        via multi-price API ensuring each token has a price

        Args:
            address (str): A token address for which to fetch overview

        Returns:
            dict[str, float | str]: Overview with a lot of token information I don't understand

        Raises:
            InvalidSolanaAddress: Raise if invalid solana address is passed
            InvalidToken: Raised if the API call was unsuccessful
        """

        is_valid_solana_address = is_solana_address(address)

        if not is_valid_solana_address:
            raise InvalidSolanaAddress("Invalid Solana address provided")

        query_url = f"{Config.BIRD_EYE_URL}/token_overview"
        resp = self._make_api_call(
            "GET",
            query_url,
            params={"address": address},
        )

        if resp.status_code != 200:
            raise InvalidTokens(InvalidTokens.message)

        overview = resp.json()
        return overview


# if __name__ == "__main__":
#     be_client = BirdEyeClient()
#     test_tokens = [
#         "WskzsKqEW3ZsmrhPAevfVZb6PuuLzWov9mJWZsfDePC",
#         "2uvch6aviS6xE3yhWjVZnFrDw7skUtf6ubc7xYJEPpwj",
#         "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
#     ]
#     print(be_client.fetch_prices(token_addresses=test_tokens))
