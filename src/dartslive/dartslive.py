import requests
from bs4 import BeautifulSoup
import datetime
from getpass import getpass


class Dartslive:
    def __init__(self, username=None, password=None) -> None:
        if username is None:
            username = input("Input username : ")
        if password is None:
            password = getpass("Input password : ")
        self.session = requests.session()
        login_info = {
            "id": username,
            "ps": password,
        }
        url_login = "https://card.dartslive.com/entry/login/doLogin.jsp"
        res = self.session.post(url_login, data=login_info)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        if not soup or not soup.find(id="cardtop"):
            raise Exception("Login failed.")

    def get_today(self) -> datetime.date:
        return datetime.date.today()

    def get_yesterday(self) -> datetime.date:
        return datetime.date.today() - datetime.timedelta(1)

    def get_bonus(self) -> bool:
        login_bonus_url = "https://card.dartslive.com/account/bonus/index.jsp"
        res = self.session.get(login_bonus_url)
        soup = BeautifulSoup(res.text, "html.parser")
        return soup and bool(soup.find(id="coinBonus"))

    def get_player_data(self) -> tuple[str]:
        play_data_url = "https://card.dartslive.com/t/play/index.jsp"
        res = self.session.get(play_data_url)
        soup = BeautifulSoup(res.text, "html.parser")
        rating = soup.find("span", {"id": "refValue"}).contents[0].strip()
        stats01 = soup.find("td", {"class": "stats01"}).contents[0].strip()
        statsCri = soup.find("td", {"class": "statsCri"}).contents[0].strip()
        return rating, stats01, statsCri

    def get_latest_list(self) -> tuple[str]:
        recent_data_url = "https://card.dartslive.com/t/play/latest_list.jsp"
        res = self.session.get(recent_data_url)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "html.parser")
        dateBoxs = soup.find("ul", {"class": "list latestList"}).find_all("a")
        for dateBox in reversed(dateBoxs):
            playdate = dateBox.contents[0].strip()
            url = dateBox.attrs["href"]
            res = self.session.get("https://card.dartslive.com/t/play/" + url)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, "html.parser")
            game_list = soup.find_all("div", {"class": "title"})
            results = soup.find_all("ul", {"class": "result"})
            for l, sp in zip(game_list, results):
                game_name = l.contents[0].strip()
                # name_list = sp.find_all("div", {"class": "name own"})
                point_list = sp.find_all("div", {"class": "point own"})
                # names = [x.contents[0].strip() for x in name_list]
                points = [x.contents[1].contents[0].strip() for x in point_list]
                for pt in points:
                    yield playdate, game_name, pt

    def get_playdata(self, today=True, yesterday=True) -> tuple[str]:
        play_data_url = "https://card.dartslive.com/t/playdata.jsp"
        res = self.session.get(play_data_url)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "html.parser")

        for day in ("today", "yesterday"):
            if not eval(day):
                continue
            try:
                soup_day = (
                    soup.find("div", {"id": day})
                    .find("ul", {"class": "result"})
                    .find_all(["h3", "li"], recursive=False)
                )
            except AttributeError:
                soup_day = []
            date = self.get_today() if day == "today" else self.get_yesterday()
            playdate = f"{date:%Y.%m.%d}"
            game_name = ""
            for sp in soup_day:
                if sp.name == "h3":
                    game_name = sp.contents[0].strip()
                else:
                    # name = sp.find("div", {"class": "name own"}).contents[0].strip()
                    point = (
                        sp.find("div", {"class": "point own"})
                        .contents[1]
                        .contents[0]
                        .strip()
                    )
                    yield playdate, game_name, point
