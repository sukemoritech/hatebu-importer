from dotenv import load_dotenv
from typing import List, Tuple
import os

from bs4 import BeautifulSoup, Tag
from requests_oauthlib import OAuth1Session

# Endpoints
REQUEST_TOKEN_URL_BASE = "https://www.hatena.com/oauth/initiate"
AUTHORIZATION_URL_BASE = "https://www.hatena.ne.jp/oauth/authorize"
ACCESS_TOKEN_URL = "https://www.hatena.com/oauth/token"
API_URL_BASE = "https://bookmark.hatenaapis.com/rest/1/my/bookmark"


def main() -> None:
    load_dotenv()

    # HTMLを解析してブックマークのURLリストを作成する
    bookmark_urls = parse_bookmark_urls()
    print(f"Import {len(bookmark_urls)} bookmarks")

    # ユーザーのキーを取得する
    consumer_key = os.getenv("CONSUMER_KEY") or ""
    consumer_secret = os.getenv("CONSUMER_SECRET") or ""

    # Request token を取得する
    session, request_token_key, request_token_secret = get_request_token(
        consumer_key, consumer_secret
    )

    # 認証用URLにリダイレクトする
    verifier = redirect_to_authorization_url(session)

    # Access token を取得する
    access_token, access_token_secret = get_access_token(
        consumer_key, consumer_secret, request_token_key, request_token_secret, verifier
    )

    # はてなの OAuth 対応 API を利用する
    for i, bookmark_url in enumerate(bookmark_urls):
        add_bookmark(bookmark_url, consumer_key, consumer_secret, access_token, access_token_secret)
        print(f"({i+1}/{len(bookmark_urls)}) Added:{bookmark_url}")


def parse_bookmark_urls() -> List[str]:
    BOOKMARKS_HTML = os.getenv("BOOKMARKS_HTML") or ""
    with open(BOOKMARKS_HTML, "r", encoding="utf-8") as f:
        contents = f.read()
    soup = BeautifulSoup(contents, "html.parser")
    dl = soup.find("dl")
    urls = []
    if isinstance(dl, Tag):
        dt_list = dl.find_all("dt")
        for dt in dt_list:
            urls.append(dt.a["href"])
    urls.reverse()
    return urls


def get_request_token(consumer_key: str, consumer_secret: str) -> Tuple[OAuth1Session, str, str]:
    session = OAuth1Session(
        client_key=consumer_key, client_secret=consumer_secret, callback_uri="oob"
    )
    scope = "write_public"
    request_token_url = f"{REQUEST_TOKEN_URL_BASE}?scope={scope}"
    response = session.fetch_request_token(request_token_url)
    request_token_key = response.get("oauth_token")
    request_token_secret = response.get("oauth_token_secret")
    return (session, request_token_key, request_token_secret)


def redirect_to_authorization_url(session: OAuth1Session) -> str:
    authorization_url = session.authorization_url(AUTHORIZATION_URL_BASE)
    print(f"Please go here and authorize: {authorization_url}")
    verifier = input("Paste the verifier:")
    return verifier


def get_access_token(
    consumer_key: str,
    consumer_secret: str,
    request_token_key: str,
    request_token_secret: str,
    verifier: str,
) -> Tuple[str, str]:
    session = OAuth1Session(
        client_key=consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=request_token_key,
        resource_owner_secret=request_token_secret,
        verifier=verifier,
    )
    response = session.fetch_access_token(ACCESS_TOKEN_URL)
    access_token = response.get("oauth_token")
    access_token_secret = response.get("oauth_token_secret")
    return (access_token, access_token_secret)


def add_bookmark(
    bookmark_url: str,
    consumer_key: str,
    consumer_secret: str,
    access_token: str,
    access_token_secret: str,
):
    session = OAuth1Session(
        client_key=consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )
    api_url = f"{API_URL_BASE}?url={bookmark_url}"
    response = session.post(api_url)
    if response.status_code != 200:
        raise Exception(f"Error: {response.content}")


if __name__ == "__main__":
    main()
