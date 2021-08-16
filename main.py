import webview
import os

 
from homeFunction import HomeFunctions

from time import sleep

homePath = os.path.abspath(os.getcwd())


api = HomeFunctions()


def expose(window):
    window.expose(api.getTournaments())  # expose a function during the runtime


if __name__ == "__main__":
    # api = HomeFunctions()
    window = webview.create_window(
        "Bet365 Golf Notify App:",
        "assets/html/index.html",
        width=1024,
        height=820,
        js_api=api,
        on_top=True,
        min_size=(768, 820)
        
    )
    # print(window)
    webview.start(expose, window, debug=True)
