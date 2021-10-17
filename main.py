import webview
import os
from homeFunction import HomeFunctions, helpers_func, ws


homePath = os.path.abspath(os.getcwd())


api = HomeFunctions()

def on_closing():
    print('pywebview window is closing')
    helpers_func.on_close(ws)

def expose(window):
    window.expose(api.getTournaments())  # expose a function during the runtime

if __name__ == "__main__":
    # api = HomeFunctions()
    window = webview.create_window(
        "Bet365 Golf Notify Me:",
        "assets/html/index.html",
        width=1112,
        height=720,
        js_api=api,
        on_top=True,
        min_size=(768, 750)
    )
    # print(window)
    window.closing += on_closing
    webview.start(expose, window, gui='cef', debug=False)
