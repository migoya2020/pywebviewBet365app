from datetime import datetime

timestamp = 1586507536367
 
dt_object = datetime.fromtimestamp(timestamp/1000.0).strftime("%Y-%m-%d %H:%M:%S")
print(dt_object)