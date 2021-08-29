# This Python file uses the following encoding: utf-8
import websocket
import threading, time
from ws_helpers import *
 

helpers_func =Ws_Helpers()

ws_headers={
        'Cookie': 'rmbs=3; aps03=cf=N&cg=2&cst=0&ct=42&hd=N&lng=10&oty=2&tzi=27; session=processform=0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0'
    }

class HomeFunctions:
    def __init__(self):
        return
    
    def showTournamentsOnFrontend(self):
        try:
            assert tournament_ids_table.all(), "Waiting for  Tournaments to be loaded..."
            print("Eureka.. Tonas")
            response = {"message": tournament_ids_table.all()}
            return response
        except:
            return {"message": 'undefined'}
                 
    def setCurrentTonamentToDb(self, tona_id):
        current_subscribed_tona=None
        try:
            #search if already exist
            tonid = Query()
            if selected_tournament_table.search(tonid.tona_id.exists()):
                #Update
                print("Updated tona id")
                selected_tournament_table.update({"tona_id": tona_id})
                # Assign the new id to target_tona_id
                current_subscribed_tona =helpers_func.getCurrentSelectedTona(tona_id)
                #print(current_subscribed_tona)
                 
            else:
                print("Inserted Tona id")
                selected_tournament_table.insert({"tona_id": tona_id})
                # Assign the  id to target_tona_id
                current_subscribed_tona =helpers_func.getCurrentSelectedTona(tona_id)
                # print(current_subscribed_tona)
            print("Tona_ID Appended into DB sucessfully..")
            # print("Total Ids : ",len(selected_tournament_table.all()))
            # print("Total Ids : ", selected_tournament_table.all()[0])
            return  current_subscribed_tona
        except:
          raise Exception('Could not Add tona id into  DB.')
    
    
    def on_pywebview_closing(self):
        
        print('pywebview window is closing')

     
    def getTournaments(self):
         
        ws = websocket.WebSocketApp("wss://edgeservers-img.lvis.io/ws",header=ws_headers,
                              on_open=helpers_func.on_open,
                              on_message=helpers_func.on_message,
                              on_error=helpers_func.on_error,
                              on_close=helpers_func.on_close,
                              on_pong=helpers_func.on_message)
        wst = threading.Thread(target=ws.run_forever())
        # wst.daemon = True
        wst.start()
