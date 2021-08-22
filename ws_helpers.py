# This Python file uses the following encoding: utf-8

import json
from time import sleep
import string

# from time import sleep
# import pandas as pd
from tinydb import TinyDB, Query
import os
from os.path import dirname, join
from pathlib import Path
import time
from datetime import datetime
import webview
import shutil
import sys
import glob


target_tona_id = None


def tree(src):
    return [
        (
            root,
            map(
                lambda f: os.path.join(root, f),
                filter(lambda f: os.path.splitext(f)[1] != ".map", files),
            ),
        )
        for (root, dirs, files) in os.walk(os.path.normpath(src))
    ]


ROOT_DIR = os.path.abspath(os.curdir)


MYDIR = "assets/data"
CHECK_FOLDER = os.path.isdir(MYDIR)

# If folder doesn't exist, then create it.
if not CHECK_FOLDER:
    os.makedirs(MYDIR)
    print("created folder : ", MYDIR)

else:
    print(MYDIR, "folder already exists.")


mydatafile = join("/assets/data/" "v353Golfdata.json")
mypath_to_data = Path(ROOT_DIR + mydatafile)


db_path = ""
if mypath_to_data.is_file():
    # remove the path
    files = glob.glob(ROOT_DIR + "/assets/data/*")
    print("removing existing history DB..")
    for f in files:
        os.remove(f)
    # create a fresh  data file
    print("creating new data file..")
    db_path = Path(join(ROOT_DIR + "/assets/data/", "v353Golfdata.json"))
else:
    print("just creating new data file..")
    db_path = mypath_to_data


inhouse_db = TinyDB(db_path)


printable = set(string.printable)
project_uuid = "b730b076-5f92-4f49-96f3-75677f1909b2"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
clientInfo = "|8|enmassejs-23.2.1," + USER_AGENT + ",lvis-23.7.3"

tournament_ids_table = inhouse_db.table("tournamentIds")
selected_tournament_table = inhouse_db.table("current_tona")
tournament_players_table = inhouse_db.table("tournament_players")


class Ws_Helpers:
    #    def __init__(self):
    #        print("lets go..")
    @staticmethod
    def getSelectedTonaSystemID(tona_id):
        for tona in tournament_ids_table.all():

            if tona["tona_id"] == tona_id:
                # print("TONAAA: ", tona['system_id'])
                return tona["system_id"]

    @staticmethod
    def getSelectedTonaRound(tona_id):
        for tona in tournament_ids_table.all():
            # print("TONAAA: ", tona)
            if tona["tona_id"] == tona_id:
                # print("TONA Round", tona["tona_round"])
                return tona["tona_round"]

    @staticmethod
    def getCurrentSelectedTona(tona_id):
        for tona in tournament_ids_table.all():
            # print("TONAAA: ", tona)
            if tona["tona_id"] == tona_id:
                # print("SELECTED TONNAA: ", tona)
                return tona

    @staticmethod
    def parseSSCP(sscp):
        data = {"channel": 0, "klass": "", "sent_at": 0, "body": []}
        separator1 = sscp.index("/")
        if separator1 != -1:
            separator2 = sscp.index("/", separator1 + 1)
            if separator2 != -1:
                data["channel"] = sscp[0:separator1]
                data["klass"] = sscp[separator1 + 1 : separator2]

                separator3 = sscp.index("/", separator2 + 1)
                if separator3 != -1:
                    data["sent_at"] = int(sscp[separator2 + 1 : separator3])
                    body = sscp[separator3 + 1 :]
                    if body:
                        values = body.split("|")
                        for v in values:

                            data["body"].append(v)

        return data

    # Tournament details
    @staticmethod
    def tournamentDetails(rx_payload: str):
        assert (
            rx_payload is not None
        ), "## Error, Check internet Connection or Check if Tounament Data is Available and try again"
        if "uuid" in rx_payload:
            print("uuid -- available")
            tournament_details = rx_payload.split("/", 3)[3].rsplit("l-b", 1)[0]

            events = (
                tournament_details.split('"events":')[1]
                .split('"assets":')[0]
                .rsplit(",", 1)[0]
                .strip()
            )

            events_list = json.loads(events)
            for each in events_list:
                # print("TOURNAMENT: ", each)
                syst_id = each["id"]
                name = each["name"]
                tournament_id = each["custom_fields"]["bg"]["tournament_id"]
                tournament_round = each["custom_fields"]["bg"]["tournament_round"]
                tournament_round_status = each["custom_fields"]["bg"]["round_status"]
                start_time = each["start_at_iso"]
                end_time = each["end_at_iso"]
                tournament_ids_table.insert(
                    {
                        "system_id": syst_id,
                        "name": name,
                        "tona_id": tournament_id,
                        "tona_round": tournament_round,
                        "tona_round_status": tournament_round_status,
                        "start_time": start_time,
                        "end_time": end_time,
                    }
                )
                # print({"name":name,'tona_id':tournament_id,"start_time": start_time, "end_time": end_time})

            response = tournament_ids_table.all()
            print("Tonas Added to Db")
            return response
        else:
            print("No tournaments found")
            return

    @staticmethod
    def processTournamentPlayers(message: str):
        splitString = message.split("{", 1)[0].strip()
        players_dirty = message.split("/", 3)[3].rsplit("l-t", 1)[0].strip()
        players_clean = "".join(filter(lambda x: x in printable, players_dirty))
        players_list = players_clean.split(splitString)
        print("Total tournament Players:", len(players_list))
        # for player in players_list:
        #     # print(player)
        #     playerJson = json.loads(player)
        #     team_id = playerJson["id"]
        #     player_id = playerJson["players"][0]["id"]
        #     first_name = playerJson["players"][0]["name"][0]
        #     last_name = playerJson["players"][0]["name"][1]
        #     player_country = playerJson["players"][0]["country"]
            
        #     tournament_players_table.insert(
        #         {
        #             "team_id": int(team_id),
        #             "player_id": int(player_id),
        #             "first_name": first_name,
        #             "last_name": last_name,
        #             "player_country": player_country,
        #         }
        #     )
        players_name_coutries_list =[{"team_id": int(json.loads(player)["id"]),"player_id": int(json.loads(player)["players"][0]["id"]),"first_name": json.loads(player)["players"][0]["name"][0], "last_name": json.loads(player)["players"][0]["name"][1],"player_country": json.loads(player)["players"][0]["country"]} for player in players_list]
        tournament_players_table.insert_multiple(players_name_coutries_list)   
            
            # ws_tournament_players.append({"team_id": int(team_id), "player_id": int(player_id), "first_name": first_name, "last_name": last_name, "player_country": player_country})
        print("Done Processing players: --D")

    @staticmethod
    def subscribeToLeaderboard(ws, tona_id):
        print("Subscribing to Leaderboard now...")
        myclass = Ws_Helpers()
        server_time = str(int(time.time()))
        # send l-s-p-279/sub/1626956496/
        ws.send("l-s-" + str(tona_id) + "/sub/" + server_time + "/")

        # send request for  Players/Team details
        ws.send(
            "l-t-" + str(tona_id) + "/sub/" + server_time + "/"
        )  # l-t-p-268/sub/1620991156/

        # send l-c-p-279/sub/1626956496/
        ws.send("l-c-" + str(tona_id) + "/sub/" + server_time + "/")

        # send p-c61471a0-0f52-4c7c-a0fb-a94af538401d/sub/1626956496/
        # c61471a0-0f52-4c7c-a0fb-a94af538401d this is the tona system_ID
        ws.send(
            "p-"
            + str(myclass.getSelectedTonaSystemID(tona_id))
            + "/sub/"
            + server_time
            + "/"
        )

        # send l-c61471a0-0f52-4c7c-a0fb-a94af538401d/sub/1626956496/
        # c61471a0-0f52-4c7c-a0fb-a94af538401d this is the tona system_ID
        ws.send(
            "l-"
            + str(myclass.getSelectedTonaSystemID(tona_id))
            + "/sub/"
            + server_time
            + "/"
        )

        # send l-r-p-279-1/sub/1626956496/
        # print("Sending:", 'l-r-'+str(tona_id)+'-'+getSelectedTonaRound(tona_id=tona_id)+'/sub/'+server_time+'/')
        ws.send(
            "l-r-"
            + str(tona_id)
            + "-"
            + str(myclass.getSelectedTonaRound(tona_id=tona_id))
            + "/sub/"
            + server_time
            + "/"
        )

        # send l-lbd-p-279-1/sub/1626956496/ subscribe to leaderbpard stream for the Active  Rond
        # print("Sending:", 'l-lbd-'+str(tona_id)+'-'+str(getSelectedTonaRound(tona_id=tona_id)+'/sub/'+server_time+'/'))
        ws.send(
            "l-lbd-"
            + str(tona_id)
            + "-"
            + myclass.getSelectedTonaRound(tona_id=tona_id)
            + "/sub/"
            + server_time
            + "/"
        )

    @staticmethod
    def postNotifications(message: dict):
        # text_parag_tag.innerHTML =message['time'] +": " + message['last_name'] +" "+message['first_name'] +"<br>"+ "SHOT "+message['shot'] +"STATUS :"+message['status']
        # +" "+ "Distance :"+ message['distance'] +"<br>" +" Surface :"+message['surface']
        # print(webview.windows[0])
        # print("Sending to Frontend python function")
        # notify_section.addEventListener("change", makeLight, false);
        webview.windows[0].evaluate_js(
            f"""
                var notify_section = document.getElementById('notify-section');
                var default_tag = document.getElementById('notification-default');
                default_tag.style.display = "none";

                let notification_div = document.createElement('div');
                notification_div.classList.add("notification","is-link");
                var notify_btn_el =document.createElement('button');
                notify_btn_el.classList.add("delete");
                var text_parag_tag =document.createElement("p");
                text_parag_tag.innerHTML = "{message['time']}: "+  "{message['last_name']} " + " {message['first_name']}" +"<br>" + "SHOT "+ "{message['shot']} " +"STATUS: "+ "{message['status'] }" + " Distance:"+ "{message['distance']}" +"<br>" +"Surface :"+ "{message['surface']}" ;
                
                notification_div.appendChild(notify_btn_el);
                notification_div.appendChild(text_parag_tag);
                notify_section.prepend(notification_div);
                notify_section.addEventListener("change", makeLight, false)
                console.log("Appended Notifications to Frontend..");
            """
        )

    @staticmethod
    def holed(message: dict):
        # text_parag_tag.innerHTML =message['time'] +": " + message['last_name'] +" "+message['first_name'] +"<br>"+ "SHOT "+message['shot'] +"STATUS :"+message['status']
        # +" "+ "Distance :"+ message['distance'] +"<br>" +" Surface :"+message['surface']
        # print(webview.windows[0])
        # print("Sending to Frontend python function")
        # notify_section.addEventListener("change", makeLight, false);
        webview.windows[0].evaluate_js(
            f"""
                var notify_section = document.getElementById('notify-section');
                var default_tag = document.getElementById('notification-default');
                default_tag.style.display = "none";

                let notification_div = document.createElement('div');
                notification_div.classList.add("notification","is-success");
                
                var notify_btn_el =document.createElement('button');
                notify_btn_el.classList.add("delete");
                
                var column_div =document.createElement("div");
                column_div.classList.add("column");
                
                var article_div =document.createElement("article");
                article_div.classList.add("media");
                
                var media_left_div =document.createElement("div");
                media_left_div.classList.add("media-left");
                
                
                var span_icon_tag =document.createElement("span");
                var icon_tag =document.createElement("i");
                
                span_icon_tag.classList.add("icon", "is-large","holed");
                icon_tag.classList.add("mdi", "mdi-golf","mdi-48px");
                
                span_icon_tag.appendChild(icon_tag);
                media_left_div.appendChild(span_icon_tag)
                
                var mediacontent_div =document.createElement("div");
                mediacontent_div.classList.add("media-content");
                
                var content_div =document.createElement("div");
                content_div.classList.add("content");
                
                var text_parag_tag =document.createElement("p");
                text_parag_tag.innerHTML = "{message['time']}: "+  "{message['last_name']} " + " {message['first_name']}" +"<br>" + "SHOT "+ "{message['shot']} " +"STATUS: "+ "{message['status'] }" + " Distance:"+ "{message['distance']}";
                
                
                content_div.appendChild(text_parag_tag);
                mediacontent_div.appendChild(content_div);
                article_div.appendChild(media_left_div);
                article_div.appendChild(mediacontent_div);
                column_div.appendChild(article_div);
                notification_div.appendChild(notify_btn_el);
                notification_div.appendChild(column_div);
                notify_section.prepend(notification_div);
                
                 
                console.log("Appended Notifications to Frontend..");
            """
        )

    @staticmethod
    def notifyFrontend(payload):
        # Add simulation Below
        ############################################################
        # payload = """l-lbd-p-282-3/shotlbd/1628968448/{"id":122,"shot":3,"status":"approach","surface":"OGR","distance":1.067,"provider":"dde","receivedTime":1628968448574,"createdTime":1628968447780}"""
        ##########################################################################################################
        myclass = Ws_Helpers()
        try:
            received_msg = payload.rsplit("/", 1)[1].strip()
            clean_msg = "".join(filter(lambda x: x in string.printable, received_msg))

            # print("CLEAN: ", clean_msg)
            received_msg_json = json.loads(clean_msg)
            # l-lbd-p-282-3/shotlbd/1628968448/{"id":122,"shot":3,"status":"hit","surface":"OGR","distance":1.067,"provider":"dde","receivedTime":1628968448574,"createdTime":1628968447780}

            # FILTER messages
            if received_msg_json["status"] == "holed":
                player_team_id = received_msg_json["id"]
                player = tournament_players_table.search(
                    Query()["team_id"] == player_team_id
                )[0]
                timestamp = datetime.fromtimestamp(
                    received_msg_json["receivedTime"] / 1000.0
                ).strftime("%Y-%m-%d %H:%M:%S.%f")
                notify_message = {
                    "first_name": player["first_name"],
                    "last_name": player["last_name"],
                    "shot": str(received_msg_json["shot"]),
                    "status": "HOLED",
                    "distance": str(received_msg_json["distance"]),
                    "time": " At: " + timestamp,
                }
                print("FrontEnd Notified...")
                # post to Frontend API
                return myclass.holed(notify_message)

            elif (
                received_msg_json["shot"] >= 2
                and received_msg_json["status"] == "approach"
            ):

                player_team_id = received_msg_json["id"]
                # print("PLAYER TEAM ID :", player_team_id)
                player = tournament_players_table.search(
                    Query()["team_id"] == player_team_id
                )[
                    0
                ]  # Should return only 1 player in a List
                # print("PLAYER Found: ", player)
                # {'team_id': 4, 'player_id': 3434, 'first_name': 'Brian', 'last_name': 'Stuard', 'player_country': 'USA'}
                timestamp = datetime.fromtimestamp(
                    received_msg_json["receivedTime"] / 1000.0
                ).strftime("%Y-%m-%d %H:%M:%S.%f")
                notify_message = {
                    "first_name": player["first_name"],
                    "last_name": player["last_name"],
                    "shot": str(received_msg_json["shot"]),
                    "status": received_msg_json["status"],
                    "surface": received_msg_json["surface"],
                    "distance": str(received_msg_json["distance"]),
                    "time": timestamp,
                }
                # {'first_name': 'Kevin', 'last_name': 'Kisner', 'shot': '4', 'status': 'approx', 'surface': 'OGR', 'distance': '0.483', 'time': '2021-08-14 23:34:43.028000'}
                print("FrontEnd Notified...")
                # post to Frontend API
                return myclass.postNotifications(notify_message)
            elif received_msg_json["shot"] == None:
                pass
        except (Exception) as err:
            print("Front end NOT Notified...")
            # print("Payload : ", payload)
            print(err)
            pass

    @staticmethod
    def on_message(ws, payload):
        myclass = Ws_Helpers()
        tona_id = ""
        # print("Rayload: "+ payload)
        if "/auth/" in payload:
            data = myclass.parseSSCP(payload)
            # print("DATA: ",data)
            enmasse_session_id = data["body"][0]
            channel = data["channel"]
            sent_at = data["sent_at"]
            klass = data["klass"]
            if klass == "auth":
                ws.send(
                    channel
                    + "/authr/"
                    + str(sent_at)
                    + "/"
                    + enmasse_session_id
                    + clientInfo
                )
        elif "/authok/" in payload:
            sent_at = payload.split("/")[2].strip()
            # send request for Tournament details
            ws.send(
                "l-" + project_uuid + "/sub/" + sent_at + "/"
            )  # l-b730b076-5f92-4f49-96f3-75677f1909b2/sub/1620991154/
        elif "/listings/" in payload:
            server_time = payload.split("/", 3)[2].strip()
            # sleep(2)
            # Tournments Details
            myclass.tournamentDetails(payload)
            # WAIT FOR TONA ID TOBE FOUND, THEN CONTINUE
            while True:
                try:
                    target_tona_id = selected_tournament_table.all()[0]["tona_id"]
                    tona_id = target_tona_id
                    break
                except:
                    sleep(1)
                    print("Waiting for  Tona Id to be loaded...")

            # subscribe to leaderboard Notifications
            myclass.subscribeToLeaderboard(ws, tona_id)

        elif "l-t-" + tona_id + "/team/" and "players" in payload:
            print("processing players...")
            myclass.processTournamentPlayers(payload)

        # Subscribe to shot leaderboard
        elif "l-lbd-p-" and "shotlbd" in payload:
            # l-lbd-p-282-3/shotlbd/
            myclass.notifyFrontend(payload)

        else:
            print(payload)

    @staticmethod
    def on_error(ws, error):
        print(error)

    @staticmethod
    def on_close(ws):  # Handle the close stus code and  close msg later
        print("### Connection Closed ###")

    @staticmethod
    def on_open(ws):
        print("thread strating...")
