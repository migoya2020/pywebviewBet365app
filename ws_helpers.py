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
from prettytable import PrettyTable
import html
from distanceConverter import *





target_tona_id = None
tona_id = ""
course_id =""

# def tree(src):
#     return [
#         (
#             root,
#             map(
#                 lambda f: os.path.join(root, f),
#                 filter(lambda f: os.path.splitext(f)[1] != ".map", files),
#             ),
#         )
#         for (root, dirs, files) in os.walk(os.path.normpath(src))
#     ]


ROOT_DIR = os.path.abspath(os.curdir)

pt = PrettyTable(border=True,padding_width=3)
players_table=PrettyTable(border=True,padding_width=3)

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
group_table =inhouse_db.table("groups")
holes_and_distance =inhouse_db.table("holes_distance")
holes_par =inhouse_db.table('holes_par')
active_holes_table =inhouse_db.table("active_holes")
removed_payers_table=inhouse_db.table("removed_payers")
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
    def printTournamentTable(tona_list):
        pt.field_names = ["Id", "Name", "Round", "Status","Start", "End"]
        assert len(tona_list), "Tonament List is Empty"
        for item in tona_list:
            raw_item =[item["tona_id"], item['name'], item['tona_round'], item['tona_round_status'],item['start_time'], item['end_time']]
            pt.add_row(raw_item)
        hTmlTable =pt.get_html_string(attributes={"id":"tonas_table", "class":"table is-bordered is-striped is-narrow is-hoverable is-fullwidth"})
        encoded_html_table = str(html.escape(hTmlTable)).split()
        clean_table = " ".join(encoded_html_table) 
        return clean_table
    
    @staticmethod
    def printPlayersTable(players_list):
        players_table.field_names = ["team_id", "Last Name","First Name", "Country"]
        assert len(players_list), "Players List is Empy"
        for item in players_list:
            raw_item =[item["team_id"], item["last_name"].upper(), item["first_name"], item["player_country"]]
            players_table.add_row(raw_item)
        hTmlTable =players_table.get_html_string(sortby="Last Name", attributes={"id":"players_table", "class":"table is-bordered is-striped is-narrow is-hoverable"})
        encoded_html_table = str(html.escape(hTmlTable)).split()
        clean_players_table = " ".join(encoded_html_table) 
        return clean_players_table
    
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
        myclass = Ws_Helpers()
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
                try:
                    tournament_course_id =each["custom_fields"]["bg"]["tournament_courses"][0]['id']
                except:
                    tournament_course_id ="n/a"
                # print("COURSE ID: ", tournament_course_id)
                start_time = each["start_at_iso"]
                end_time = each["end_at_iso"]
                tournament_ids_table.insert(
                    {
                        "system_id": syst_id,
                        "name": name,
                        "tona_id": tournament_id,
                        "tona_round": tournament_round,
                        "tona_round_status": tournament_round_status,
                        "course_id": tournament_course_id,
                        "start_time": start_time,
                        "end_time": end_time,
                    }
                )
                
                # print({"name":name,'tona_id':tournament_id,"start_time": start_time, "end_time": end_time})
            print("Response..")
            response = tournament_ids_table.all()
            print("Tonas Added to Db")
            tonament_html_table = myclass.printTournamentTable(tona_list=tournament_ids_table.all())
            # print(tonament_html_table)
            webview.windows[0].evaluate_js(
                f"""
               showTournamentTable("{tonament_html_table}"); 
               enableBtn();       
                """)
            
            return response
        else:
            print("No tournaments found")
            return

    @staticmethod
    def processTournamentPlayers(message: str):
        myclass = Ws_Helpers()
        splitString = message.split("{", 1)[0].strip()
        players_dirty = message.split("/", 3)[3].rsplit("l-t", 1)[0].strip()
        players_clean = "".join(filter(lambda x: x in printable, players_dirty))
        players_list = players_clean.split(splitString)
        print("Total tournament Players:", len(players_list))
        
        players_name_coutries_list =[{"team_id": int(json.loads(player)["id"]),"player_id": int(json.loads(player)["players"][0]["id"]),"first_name": json.loads(player)["players"][0]["name"][0], "last_name": json.loads(player)["players"][0]["name"][1],"player_country": json.loads(player)["players"][0]["country"]} for player in players_list]
        tournament_players_table.insert_multiple(players_name_coutries_list)   
        # print(tournament_players_table.all())
        

    @staticmethod
    def subscribeToLeaderboard(ws, tona_id, course_id):
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

        # send l-r-p-279-1/sub/1626956496/ #SUBSCRIBE TO HOLES DETAILS
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
        #subscribe to all 18 holes
        #l-h-p-361-4-38-18/sub/1630248742/
         
        for hole in range(1, 18+1):
            ws.send(
            "l-h-"
            + str(tona_id)
            + "-"
            + myclass.getSelectedTonaRound(tona_id=tona_id)
            +"-"
            + str(course_id)
            +"-"
            +str(hole)
            + "/sub/"
            + server_time
            + "/"
        )

        #Un Subscribe to holes
        for hole in range(1, 18+1):
            print("Un Subscribe ", hole)
            ws.send(
            "l-h-"
            + str(tona_id)
            + "-"
            + myclass.getSelectedTonaRound(tona_id=tona_id)
            +"-"
            + str(course_id)
            +"-"
            +str(hole)
            + "/unsub/"
            + server_time
            + "/"
        )
    @staticmethod
    def saveActiveHoles(payload):
        UserQuery =Query()
        server_time = str(int(time.time()))
        #l-lbd-p-360-1/globallbd/1631180290/{"id":43,"hole":"11","total":3,"today":3,"round":0,"activeHole":12,"startingHole":1,"provider":"dde","receivedTime":1631180290373,"createdTime":1631180290352}
        globallbd=payload.rsplit("/",1)[1].strip()
        clean_global ="".join(filter(lambda x: x in string.printable,globallbd))
        globallbd_json =json.loads(clean_global)
        team_id =globallbd_json['id']
        if active_holes_table.search(UserQuery.id ==team_id ):
            active_holes_table.update({"activeHole": globallbd_json["activeHole"]}, UserQuery.id ==team_id)
            # print("Active Hole Updated :", globallbd_json['id'])
        else:
            active_holes_table.insert({"id":globallbd_json['id'],"activeHole": globallbd_json["activeHole"]})
            # print("Active Hole Inserted :",globallbd_json['id'] )
        
        return
        
    @staticmethod
    def saveHolesintoDB(payload_msg):
        #l-r-p-361-3/holes/1630148120/{"courseId":"38","holes":[{"no":1,"hole":1,"par":4},{"no":2,"hole":2,"par":4},{"no":3,"hole":3,"par":3},{"no":4,"hole":4,"par":4},{"no":5,"hole":5,"par":4},{"no":6,"hole":6,"par":4},{"no":7,"hole":7,"par":4},{"no":8,"hole":8,"par":3},{"no":9,"hole":9,"par":5},{"no":10,"hole":10,"par":4},{"no":11,"hole":11,"par":3},{"no":12,"hole":12,"par":4},{"no":13,"hole":13,"par":3},{"no":14,"hole":14,"par":5},{"no":15,"hole":15,"par":5},{"no":16,"hole":16,"par":3},{"no":17,"hole":17,"par":4},{"no":18,"hole":18,"par":4}],"provider":"dde","receivedTime":1630089136280}l-r-p-361-3/group/1630148120/{"id":1,"hole":18,"course":"38","teams":[95,135],"status":"Finished","teeTime":1630130100000,"provider":"dde","receivedTime":1630144315166}l-r-p-361-3/group/1630148120/{"id":2,"hole":18,"course":"38","teams":[57,85],"status":"Finished","teeTime":1630130640000,"provider":"dde","receivedTime":1630145035169}l-r-p-361-3/group/1630148120/{"id":3,"hole":18,"course":"38","teams":[70,145,17],"status":"Finished","teeTime":1630131180000,"provider":"dde","receivedTime":1630146475195}l-r-p-361-3/group/1630148120/{"id":25,"hole":2,"course":"38","teams":[49,3,76],"status":"InProgress","teeTime":1630146000000,"provider":"dde","receivedTime":1630146955166}l-r-p-361-3/group/1630148120/{"id":22,"hole":4,"course":"38","teams":[88,41,18],"status":"InProgress","teeTime":1630144020000,"provider":"dde","receivedTime":1630147195138}l-r-p-361-3/group/1630148120/{"id":12,"hole":11,"course":"38","teams":[43,63,105],"status":"InProgress","teeTime":1630137120000,"provider":"dde","receivedTime":1630147315136}l-r-p-361-3/group/1630148120/{"id":19,"hole":6,"course":"38","teams":[7,46,128],"status":"InProgress","teeTime":1630142040000,"provider":"dde","receivedTime":1630147315136}l-r-p-361-3/group/1630148120/{"id":11,"hole":12,"course":"38","teams":[114,21,71],"status":"InProgress","teeTime":1630136460000,"provider":"dde","receivedTime":1630147315136}l-r-p-361-3/group/1630148120/{"id":16,"hole":9,"course":"38","teams":[142,130,74],"status":"InProgress","teeTime":1630140060000,"provider":"dde","receivedTime":1630147435098}l-r-p-361-3/group/1630148120/{"id":14,"hole":10,"course":"38","teams":[153,29,127],"status":"InProgress","teeTime":1630138440000,"provider":"dde","receivedTime":1630147435098}l-r-p-361-3/group/1630148120/{"id":9,"hole":14,"course":"38","teams":[20,119,92],"status":"InProgress","teeTime":1630135140000,"provider":"dde","receivedTime":1630147435098}l-r-p-361-3/group/1630148120/{"id":21,"hole":5,"course":"38","teams":[84,55,112],"status":"InProgress","teeTime":1630143360000,"provider":"dde","receivedTime":1630147555323}l-r-p-361-3/group/1630148120/{"id":5,"hole":18,"course":"38","teams":[19,26,32],"status":"InProgress","teeTime":1630132500000,"provider":"dde","receivedTime":1630147675370}l-r-p-361-3/group/1630148120/{"id":4,"hole":18,"course":"38","teams":[113,146,58],"status":"InProgress","teeTime":1630131840000,"provider":"dde","receivedTime":1630147675370}l-r-p-361-3/group/1630148120/{"id":23,"hole":4,"course":"38","teams":[36,98,34],"status":"InProgress","teeTime":1630144680000,"provider":"dde","receivedTime":1630147795144}l-r-p-361-3/group/1630148120/{"id":8,"hole":15,"course":"38","teams":[136,147,51],"status":"InProgress","teeTime":1630134480000,"provider":"dde","receivedTime":1630147795144}l-r-p-361-3/group/1630148120/{"id":18,"hole":8,"course":"38","teams":[1,131,6],"status":"InProgress","teeTime":1630141380000,"provider":"dde","receivedTime":1630147915275}l-r-p-361-3/group/1630148120/{"id":17,"hole":9,"course":"38","teams":[30,28,66],"status":"InProgress","teeTime":1630140720000,"provider":"dde","receivedTime":1630147915275}l-r-p-361-3/group/1630148120/{"id":6,"hole":17,"course":"38","teams":[134,97,123],"status":"InProgress","teeTime":1630133160000,"provider":"dde","receivedTime":1630147915275}l-r-p-361-3/group/1630148120/{"id":20,"hole":6,"course":"38","teams":[2,59,38],"status":"InProgress","teeTime":1630142700000,"provider":"dde","receivedTime":1630147915275}l-r-p-361-3/group/1630148120/{"id":24,"hole":3,"course":"38","teams":[24,13,40],"status":"InProgress","teeTime":1630145340000,"provider":"dde","receivedTime":1630147915275}l-r-p-361-3/group/1630148120/{"id":15,"hole":10,"course":"38","teams":[8,65,120],"status":"InProgress","teeTime":1630139100000,"provider":"dde","receivedTime":1630148035171}l-r-p-361-3/group/1630148120/{"id":7,"hole":16,"course":"38","teams":[205,72,62],"status":"InProgress","teeTime":1630133820000,"provider":"dde","receivedTime":1630148035171}l-r-p-361-3/group/1630148120/{"id":10,"hole":14,"course":"38","teams":[56,31,27],"status":"InProgress","teeTime":1630135800000,"provider":"dde","receivedTime":1630148035171}l-r-p-361-3/group/1630148120/{"id":13,"hole":11,"course":"38","teams":[211,152,126],"status":"InProgress","teeTime":1630137780000,"provider":"dde","receivedTime":1630148086220}l-r-p-361-3/eoc/1630148120/
        received_msg_1 = payload_msg.split('"holes":', 1)[1].strip()
        received_msg_2 = received_msg_1.split("]", 1)[0].strip()
        clean_msg = "".join(filter(lambda x: x in string.printable,received_msg_2))
        holes =clean_msg+"]"
        # print("CLEAN: ", holes )
        received_holes = json.loads(holes)
        holes_par.insert_multiple(received_holes)
        print("Holes and Par Done.. ")
        
        
    @staticmethod
    def saveHolesDetails(payload_msg):
        #l-h-p-361-4-38-8/hole/1630229132/{"par":3,"yardage":175,"tees":[{"type":"Black","tee":[7.4593498,46.3001712,0]}],"pin":[7.4587349,46.3015296,0],"holeLabel":8,"teesUTM":[{"type":"Black","tee":{"zone":32,"hemisphere":"N","easting":381351.262138,"northing":5128552.866127}}],"pinUTM":{"zone":32,"hemisphere":"N","easting":381306.843978,"northing":5128704.720241},"provider":"dde","receivedTime":1630219787545}l-h-p-361-4-38-8/eoc/1630229132/
        hole =payload_msg.split("{", 1)[1].split(',"tees"',1)[0].strip()
        hole_number =payload_msg.split("/", 1)[0].rsplit("-",1)[1].strip()
        hole_yardage ="{"+'"hole"'+":"+hole_number+","+hole+"}".strip()
        # print( "HOLE HARDS", hole_yardage)
        hole_yardage_json =json.loads(hole_yardage)
        # print("HOLE",hole_yardage_json )
        holes_and_distance.insert(hole_yardage_json)
        #Unsubscribe immedeately
        # print("Holes Done...")
        return
        
    @staticmethod
    def initializeActiveHoles(payload_msg):
        myclass= Ws_Helpers()
        shotlbd_splitText=""
        globallbd_splitText=""
        orderlbd_splitText=""
        first_splitText =payload_msg.split("{", 1)[0].strip()
        # print("first_splitText",first_splitText)
        if "globallbd" in first_splitText:
            shotlbd_splitText =first_splitText.replace("globallbd", 'shotlbd')
            globallbd_splitText=first_splitText
            orderlbd_splitText=first_splitText.replace("globallbd", 'orderlbd')
            
        elif 'shotlbd' in first_splitText:
            shotlbd_splitText =first_splitText
            globallbd_splitText =first_splitText.replace('shotlbd',"globallbd")
            orderlbd_splitText  =first_splitText.replace('shotlbd', 'orderlbd')
            
        elif 'orderlbd' in first_splitText:
            shotlbd_splitText =first_splitText.replace( 'orderlbd','shotlbd')
            globallbd_splitText =first_splitText.replace('orderlbd',"globallbd")
            orderlbd_splitText  =first_splitText
                    
        # print("globallbd_splitText",globallbd_splitText)
      
        # print("orderlbd_splitText",orderlbd_splitText)
  
        # print("shotlbd_splitText",shotlbd_splitText)
       
        mainText =payload_msg.rsplit("}",1)[0].split("/",3)[3].replace(str(orderlbd_splitText),",").replace(str(globallbd_splitText),",").replace(str(shotlbd_splitText), ",").strip()+"}"
        # print("mainText: ", mainText)
        clean_msg = "".join(filter(lambda x: x in string.printable,mainText))
        # print("Clean: ", clean_msg)
        mainText_list_json = json.loads("["+clean_msg+"]")

        active_Hol =[active_holes_table.insert({"id":item['id'],"activeHole": item["activeHole"]}) for item in mainText_list_json if  'activeHole' in item]
        print("Initial Active Holes added", len(active_Hol))
        #Now we can add the Players table
        players_html_table=myclass.printPlayersTable(players_list=tournament_players_table.all())
        print("Done Processing players: --D")
        # print(players_html_table)
        webview.windows[0].evaluate_js(
            f"""
            showTonaPlayersTable("{players_html_table}");         
            """)
       
    @staticmethod
    def postNotifications(message: dict):

        webview.windows[0].evaluate_js(
            f"""
                var notify_section = document.getElementById('notify-section');
                var default_tag = document.getElementById('notification-default');
                default_tag.style.display = "none";

                let notification_div = document.createElement('div');
                notification_div.classList.add("notification","is-link");
                var notify_btn_el =document.createElement('button');
                notify_btn_el.classList.add("delete");
                
                var content_div =document.createElement("div");
                content_div.classList.add("content", "is-normal");
                
                var text_parag_tag =document.createElement("p");
                
                text_parag_tag.innerHTML ="{message['time']} : "+ "<b> STATUS : "+ "{message['status'] } </b>" +"<br>" +"<b> {message['last_name']} " + " {message['first_name']} </b>"  +"<br>"+ "<b>Hole No: </b>"+ " {message['activeHole']}"  + "<b>"+"  SHOT: " +"</b>"+ " {message['shot']}" +"<b> PAR :"+" {message['hole_par']} </b>" ;
                
                content_div.appendChild(text_parag_tag);
                
                notification_div.appendChild(notify_btn_el);
                notification_div.appendChild(content_div);
                notify_section.prepend(notification_div);
                notify_section.addEventListener("change", makeLight, false);
                addClickEventToNotifications();
                console.log("Appended Notifications to Frontend..");
            """
        )
    @staticmethod
    def notificationsWaterPenalty(message: dict):
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
                notification_div.classList.add("notification","is-danger");
                var notify_btn_el =document.createElement('button');
                notify_btn_el.classList.add("delete");
                
                var content_div =document.createElement("div");
                content_div.classList.add("content", "is-normal");
                
                var text_parag_tag =document.createElement("p");
                
                text_parag_tag.innerHTML ="{message['time']} : "+ "<b> STATUS : "+ "{message['status'] } </b>" +"<br>" +"<b> {message['last_name']} " + " {message['first_name']} </b>"  +"<br>"+ "<b>Hole No: </b>"+ " {message['activeHole']}"  + "<b>"+"  SHOT: " +"</b>"+ " {message['shot']}" +"<b> PAR :"+" {message['hole_par']} </b>" ;
                
                content_div.appendChild(text_parag_tag);
                
                notification_div.appendChild(notify_btn_el);
                notification_div.appendChild(content_div);
                notify_section.prepend(notification_div);
                notify_section.addEventListener("change", makeLight, false);
                addClickEventToNotifications();
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
                
                span_icon_tag.classList.add("icon","holed");
                icon_tag.classList.add("mdi", "mdi-golf","mdi-48px");
                
                span_icon_tag.appendChild(icon_tag);
                media_left_div.appendChild(span_icon_tag)
                
                var mediacontent_div =document.createElement("div");
                mediacontent_div.classList.add("media-content");
                
                var content_div =document.createElement("div");
                content_div.classList.add("content", "is-normal");
                
                var text_parag_tag =document.createElement("p");
 
                text_parag_tag.innerHTML = "{message['time']}: "+ "<b>"+"STATUS: "+ "{message['status'] }"+"</b>" + "<br>"+"<b>"+"{message['last_name']} " + " {message['first_name']}" +"</b>"+"<br>" +"<b>"+"HOLE No: "+"</b>"+ "{message['activeHole']} "+ " <b>"+" SHOT :"+"</b> "+ "{message['shot']} :"+ "<b>"+" PAR :"+" {message['hole_par']} </b>";
                
                
                content_div.appendChild(text_parag_tag);
                mediacontent_div.appendChild(content_div);
                article_div.appendChild(media_left_div);
                article_div.appendChild(mediacontent_div);
                column_div.appendChild(article_div);
                
                notification_div.appendChild(notify_btn_el);
                notification_div.appendChild(column_div);
                notify_section.prepend(notification_div);
                addClickEventToNotifications();
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
        received_msg = payload.rsplit("/", 1)[1].strip()
        clean_msg = "".join(filter(lambda x: x in string.printable, received_msg))
        # print("CLEAN: ", clean_msg)
        received_msg_json = json.loads(clean_msg)
        player_team_id = received_msg_json["id"]
        #Chek if ID is in X-unwanted notifications table
        if not removed_payers_table.contains(Query().team_id ==player_team_id):
            try:
                # l-lbd-p-282-3/shotlbd/1628968448/{"id":122,"shot":3,"status":"hit","surface":"OGR","distance":1.067,"provider":"dde","receivedTime":1628968448574,"createdTime":1628968447780}
                # print("received_msg_json: ",received_msg_json)
                ##---------------------------------------------------------------
                # FILTER messages for HOLED Notifications
                # print("received_msg_json_ID", received_msg_json["id"])
                player_active_hole =""
                hole_par =""
                holedStatus =""
                shotstatus =""
                try:
                    active_hole_query =Query()
                    active_hole = active_holes_table.search(active_hole_query.id ==received_msg_json["id"])[0]
                    # print("ACTIVE HOLE FROM DB:", active_hole)
                    player_active_hole =active_holes_table.search(active_hole_query.id ==received_msg_json["id"])[0]["activeHole"]
                    hole_par =holes_par.search(active_hole_query.hole==player_active_hole)[0]["par"]
                    # print("HOLE PAR:" , hole_par)
                except:
                    player_active_hole="N/A"
                    hole_par ="N/A"
                if received_msg_json["status"] == "holed" :
                    # print("RECEIVED JSON: ",received_msg_json)
                    player_team_id = received_msg_json["id"]
                    player= tournament_players_table.search(
                        Query()["team_id"] == player_team_id
                    )[0]
                    if received_msg_json["shot"] < int(hole_par):
                        difference =int(hole_par) -received_msg_json["shot"]
                        holedStatus ="HOLED "+ str(difference)+" Below PAR."
                    elif received_msg_json["shot"] > int(hole_par):
                        difference =received_msg_json["shot"]-int(hole_par)
                        holedStatus = "HOLED "+ str(difference)+" Above PAR."
                    elif received_msg_json["shot"] == int(hole_par):
                        # difference =received_msg_json["shot"] -hole_par
                        holedStatus = "HOLED"+" At PAR."
                        
                        
                    timestamp = datetime.fromtimestamp(
                        received_msg_json["receivedTime"] / 1000.0
                    ).strftime("%Y-%m-%d %H:%M:%S")
                    notify_message = {
                        "first_name": player["first_name"],
                        "last_name": player["last_name"].upper(),
                        'activeHole':player_active_hole,
                        "shot": str(received_msg_json["shot"]),
                        "status": holedStatus,
                        "hole_par": str(hole_par),
                        "time": timestamp,
                    }
                    print("Front-End Notified...")
                    # post to Frontend API
                    return myclass.holed(notify_message)
                
                ##-------------------------------------------------------------------------
                ## FILTER messages for BALL GOES Into WAter
                # l-lbd-p-358-2/shotlbd/1630686084/{"id":11,"shot":2,"status":"approach","surface":"OFW","distance":276.768860892705,"provider":"dde","receivedTime":1630686084050,"createdTime":1630686083000}
                elif (
                    received_msg_json["surface"] == "OWA" and received_msg_json["status"] =="lie"
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
                    ).strftime("%Y-%m-%d %H:%M:%S")
                    notify_message = {
                        "first_name": player["first_name"],
                        "last_name": player["last_name"].upper(),
                        "shot": str(received_msg_json["shot"]),
                        "status": "IN WATER",
                        "distance":convert(received_msg_json["distance"]),
                        "hole_par": str(hole_par),
                        "activeHole": player_active_hole,
                        "time": timestamp,
                    }
                    
                    print("Front-End Notified...")
                    # post to Frontend API
                    return myclass.notificationsWaterPenalty(notify_message)
                
                elif received_msg_json["status"] =="penalty":
                    player_team_id = received_msg_json["id"]
                    player = tournament_players_table.search(Query()["team_id"] == player_team_id)[0]
                    print("PLAYER: ", player)
                    timestamp = datetime.fromtimestamp(
                            received_msg_json["receivedTime"] / 1000.0
                        ).strftime("%Y-%m-%d %H:%M:%S")
                    surface =received_msg_json["surface"]
                    shotstatus ="Penalty on "+surface
                    notify_message = {
                            "first_name": player["first_name"],
                            "last_name": player["last_name"].upper(),
                            "shot": str(received_msg_json["shot"]),
                            "status": shotstatus,
                            "distance":convert(received_msg_json["distance"]),
                            "hole_par": str(hole_par),
                            "activeHole": player_active_hole,
                            "time": timestamp,
                        }
                    print("Front-End Notified...")
                    return myclass.notificationsWaterPenalty(notify_message)
                    
                elif (
                    received_msg_json["surface"] == "OGR" and received_msg_json['status']=="lie"
                ):
                    if (int(hole_par)-received_msg_json["shot"]) ==2:
                        shotstatus ="OGR in 2 shots less than Par"
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
                        ).strftime("%Y-%m-%d %H:%M:%S")
                        notify_message = {
                            "first_name": player["first_name"],
                            "last_name": player["last_name"].upper(),
                            "shot": str(received_msg_json["shot"]),
                            "status": shotstatus,
                            "distance":convert(received_msg_json["distance"]),
                            "hole_par": str(hole_par),
                            "activeHole": player_active_hole,
                            "time": timestamp,
                        }
                        
                        print("Front-End Notified...")
                        # post to Frontend API
                        return myclass.postNotifications(notify_message)
                    else:
                        pass
                
                ##-------------------------------------------------------------------------
                ## FILTER messages for  
                # elif received_msg_json["shot"] == None:
                #     pass
            except (Exception) as err:
                print("Front end NOT Notified... ERROR: ", err)
                print("Payload : ", payload)
                print(err)
                pass

    @staticmethod
    def on_message(ws, payload):
        myclass = Ws_Helpers()
        global tona_id, course_id
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
            # WAIT FOR TONA ID TO BE FOUND, THEN CONTINUE
            while True:
                try:
                    target_tona_id = selected_tournament_table.all()[0]["tona_id"]
                    tona_id = target_tona_id
                    break
                except:
                    sleep(1)
                    print("Waiting for Tona Id to be loaded...")
            target_course_id =myclass.getCurrentSelectedTona(tona_id)
            
            course_id =target_course_id['course_id']
            print("Course ID ", course_id)
            # subscribe to leaderboard Notifications
            myclass.subscribeToLeaderboard(ws, tona_id, course_id)
        
        
        elif  str(payload).startswith("l-lbd-"+tona_id+"-"+str(myclass.getSelectedTonaRound(tona_id=tona_id))+"/shotlbd/") and "/globallbd/" in  payload or str(payload).startswith("l-lbd-"+tona_id+"-"+str(myclass.getSelectedTonaRound(tona_id=tona_id))+"/globallbd/") and "/orderlbd/" in payload or  str(payload).startswith("l-lbd-"+tona_id+"-"+str(myclass.getSelectedTonaRound(tona_id=tona_id))+"/orderlbd/")  and "/globallbd/" in payload:
            print("Initializing Active holes..")
            # print(payload)
            myclass.initializeActiveHoles(payload_msg=payload)

        elif "l-t-" + tona_id + "/team/" and "players" in payload:
            print("processing players...")
            myclass.processTournamentPlayers(payload)
            #l-r-p-361-3/holes/1630148120/{"courseId
        elif 'l-r-'+ str(tona_id)+"-" and "/holes/" and "courseId" in payload:
            #save  holes and Par intoDB 
            print('processing holes and par only...')
            myclass.saveHolesintoDB(payload_msg=payload)
            
        elif "l-h-"+ str(tona_id)+"-" and "/hole/" in payload:
            #l-h-p-361-4-38-8/hole/1630229132/{"par":3,"yardage":175,"tees":[{"type":"Black","tee":[7.4593498,46.3001712,0]}],"pin":[7.4587349,46.3015296,0],"holeLabel":8,"teesUTM":[{"type":"Black","tee":{"zone":32,"hemisphere":"N","easting":381351.262138,"northing":5128552.866127}}],"pinUTM":{"zone":32,"hemisphere":"N","easting":381306.843978,"northing":5128704.720241},"provider":"dde","receivedTime":1630219787545}l-h-p-361-4-38-8/eoc/1630229132/
            print('processing holes and yardage...')
            # print(payload)
            myclass.saveHolesDetails(payload_msg=payload)
            
        
            
        # Notify Frontend
        elif "l-lbd-p-" and "shotlbd" in payload and "orderlbd" not in payload:
            # l-lbd-p-282-3/shotlbd/
            # print("# Notify Frontend")
            myclass.notifyFrontend(payload)
           
            
        elif "l-lbd-"+str(tona_id)+"-" and  '/globallbd/' in payload and '/shotlbd/' not in payload:
            #print("l-lbd-"+str(tona_id)+"-"+str(myclass.getSelectedTonaRound(tona_id=tona_id))+'/globallbd/')
            #l-lbd-p-360-1/globallbd/1631180290/{"id":43,"hole":"11","total":3,"today":3,"round":0,"activeHole":12,"startingHole":1,"provider":"dde","receivedTime":1631180290373,"createdTime":1631180290352}
            # print("processing Active  Holes ...")
            # print(payload)
            myclass.saveActiveHoles(payload=payload)

        else:
            # pass
            print("Payload passed")
            # print(payload)

    @staticmethod
    def on_error(ws, error):
        print(error)

    @staticmethod
    def on_close(ws):  # Handle the close stus code and  close msg later
        print("### Connection Closed ###")

    @staticmethod
    def on_open(ws):
        print("thread strating...")
