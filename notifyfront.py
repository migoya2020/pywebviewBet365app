def notifyFrontendForHoled(message_json):
    received_msg_json_holed=message_json
    active_hole_query_holed =Query()
    player_active_holed =""
    player_holed_par =""
    try:
        player_active_holed = active_holes_table.search(active_hole_query_holed.id ==received_msg_json_holed["id"])[0]
        # print("ACTIVE HOLE FROM DB:", active_hole)
        
        player_holed_par =holes_par.search(active_hole_query_holed.hole==player_active_holed)[0]["par"]
        # print("HOLE PAR:" , hole_par)
    except:
        player_active_holed="N/A"
        player_holed_par ="N/A"
        
    holedStatus=""
    player_team_id = received_msg_json_holed["id"]
    player= tournament_players_table.search(
        Query()["team_id"] == player_team_id
    )[0]
    if received_msg_json_holed["shot"] < int(player_holed_par):
        difference =int(player_holed_par)-received_msg_json_holed["shot"]
        if difference ==1:
            holedStatus ="Birdie"
        elif difference ==2:
            holedStatus="Eagle"
        else:
            holedStatus="Unknown"
            
    elif received_msg_json_holed["shot"] > int(player_holed_par):
        difference =received_msg_json_holed["shot"]-int(player_holed_par)
        if difference ==1:
            holedStatus ="Bogey"
        elif difference >=2:
            holedStatus="D Bogey +"
        else:
            holedStatus="Unknown"
            
    elif received_msg_json_holed["shot"] == int(player_holed_par):
        # difference =received_msg_json["shot"] -player_holed_par
        holedStatus = "HOLED"+" At PAR."
        
        
    timestamp = datetime.fromtimestamp(
        received_msg_json_holed["receivedTime"] / 1000.0
    ).strftime("%Y-%m-%d %H:%M:%S")
    notify_message = {
        "first_name": player["first_name"],
        "last_name": player["last_name"].upper(),
        'activeHole':player_active_holed,
        "shot": str(received_msg_json_holed["shot"]),
        "status": holedStatus,
        "hole_par": str(player_holed_par),
        "time": timestamp,
    }
    # print("Front-End Notified...")
    # post to Frontend API
    return myclass.holed(notify_message)
    