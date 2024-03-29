import airsim
import random
import logging
import threading
import time
from PointTool import getgpsDataByName, create_geo_point, getNedDataByName,distance_between_gps_points
from VisualTool import initial_csv
from FlightPath import FlightPath, FlightPath_OD
import csv
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import pandas as pd
import math
import queue
import sys

csv_files_plot = [
'C:/Users/User/Desktop/airsim/PlotLog/drone1.csv',
'C:/Users/User/Desktop/airsim/PlotLog/drone2.csv',
"C:/Users/User/Desktop/airsim/PlotLog/waypoint.csv",
"C:/Users/User/Desktop/airsim/PlotLog/tower.csv",
"C:/Users/User/Desktop/airsim/PlotLog/leave.csv",
"C:/Users/User/Desktop/airsim/PlotLog/enter.csv"]

csv_files_drone = ['C:/Users/User/Desktop/airsim/PlotLog/drone1.csv','C:/Users/User/Desktop/airsim/PlotLog/drone2.csv']
Flight_Level = {"170":True, "160":True, "155": True, "150": True, "145":True, "140":True,"130":True, "120":True}
#170 : out; 130: enter/leave point ; 120: tower point(ground)

def clean(csv_files_drone):
    # Define the columns to keep
    columns_to_keep = ['name', 'x', 'y', 'z']

    # Create an empty DataFrame with these columns
    df = pd.DataFrame(columns=columns_to_keep)

    for file in csv_files_drone:
        try:
            # Overwrite the file with the empty DataFrame
            df.to_csv(file, index=False)

        except FileNotFoundError:
            print(f"File not found: {file}")
        except Exception as e:
            print(f"Error processing {file}: {e}")


origin_gps = [47.641467999997424, -122.140165, 121.32066345214844]

# Initialize Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='real-time-graph'),
    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # in milliseconds (update every second)
        n_intervals=0
    )
])

@app.callback(
    Output('real-time-graph', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_graph(n):
    data = []
    csv_files_drone 
    for csv_file in csv_files_plot:
        try:
            # Determine the number of rows in the file
            total_rows = sum(1 for row in open(csv_file, 'r'))
            skip_rows = max(0, total_rows - 15)  # Skip all but last 15 rows

            df = pd.read_csv(csv_file, skiprows=range(1, skip_rows))
            if not df.empty:
                if csv_file == csv_files_drone[0] or csv_file == csv_files_drone[1]:
                    last_point_text = f"{df['name'].iloc[-1]}, {df['z'].iloc[-1]}"
                    text = [None] * (len(df) - 1) + [f"{df['name'].iloc[-1]}, {df['z'].iloc[-1]}"]
                    mode = 'markers+text'
                else:
                    text = df['z']
                    mode = 'markers+text'
                scatter = go.Scatter(
                    x=df['x'],
                    y=df['y'],
                    mode=mode,
                    text=text,
                    #text=df['z'],  # Assume 'z' is already in the desired format
                    textposition='top center',
                    name=df['name'].iloc[0] 
                )
                data.append(scatter)
        except pd.errors.EmptyDataError:
            logging.warning(f"Empty CSV file: {csv_file}")
        except FileNotFoundError:
            logging.error(f"File not found: {csv_file}")

    layout = go.Layout(
        title="Real-time Data Plot",
        xaxis={'title': 'X'},
        yaxis={'title': 'Y'}
    )

    return {'data': data, 'layout': layout}

def run_dash_server():
    app.run_server(debug=False)

def gps_to_ned(origin, point):
    # Constants for scaling lat/lon differences to meters
    lat_scale = 111319.488  # meters per degree latitude (approximation)
    lon_scale = 111319.488 * math.cos(math.radians(origin[0]))  # meters per degree longitude at given latitude

    # Calculate differences
    dNorth = (point[0] - origin[0]) * lat_scale
    dEast = (point[1] - origin[1]) * lon_scale
    dDown = -(point[2] - origin[2])  # Negative because 'down' is positive in NED
    path = [airsim.Vector3r(dNorth, dEast, dDown)]
    return path


# Create drone object
def createDrone(client, drone_name):
    client.enableApiControl(True, drone_name)
    client.armDisarm(True, drone_name)
    logging.info(f"{drone_name}: API Control enabled and armed")
    client.startRecording()
    recordingState = client.isRecording()
    logging.info(f"{drone_name} recording state: {recordingState}")
    return client


def generate_random_start_position():
    x = random.uniform(-50, 50)
    y = random.uniform(-50, 50)
    z = random.uniform(-10, -30)  # Negative values for altitude in AirSim
    return airsim.Vector3r(x, y, z)

    

def getPath_pointName(point_name):
    """
    Target_Gps_point: [latitude, longitude, altitude]
    path: [airsim.Vector3r(dNorth, dEast, dDown)]
    """
    Target_Gps_point =getgpsDataByName(point_name) 
    path = gps_to_ned(origin_gps, Target_Gps_point)
    return path, Target_Gps_point

def getPath_gps(Target_Gps_point):
    #print(Target_Gps_point)
    path = gps_to_ned(origin_gps, Target_Gps_point)
    return path, Target_Gps_point


def record(client,csv_file_name,Target_Gps_point,drone_name,Tower_dic, avoiding):
    with open(csv_file_name, 'a', newline='') as file:
        writer = csv.writer(file)
        gps_data = client.getGpsData(vehicle_name = drone_name)
        geo_point = gps_data.gnss.geo_point
        latitude = geo_point.latitude
        longitude = geo_point.longitude
        altitude = geo_point.altitude
        writer.writerow([drone_name, latitude, longitude, round(altitude-121.320,1)])
        # when the drone is flying to avoiding point, need to check for the Tower avoiding state
        if not avoiding:
            if distance_between_gps_points([latitude,longitude,altitude], Target_Gps_point)<2 and Tower_dic[drone_name]["avoidance"] == False: 
                return False,0
            elif Tower_dic[drone_name]["avoidance"] == True:
                return False,1
            else:
                return True,0
        # the returned state_avoid will be "0" so as to break the recursion
        else:
            dis = distance_between_gps_points([latitude,longitude,altitude], Target_Gps_point)
            if dis <2:
                print(f'{drone_name} keep flying to avoidance node, distace = {dis}')
                return False,0
            else:
                return True,0

def Tower_AssignPath(client, drone_name ,path, Target_Gps_point,csv_files_drone,Tower_dic, avoiding = False, FL_check = True):
    if FL_check:
        fl = Target_Gps_point[2]
        closest_key = min(Flight_Level.keys(), key=lambda k: abs(int(k) - fl))

        # get original fl and update FL dic
        originalFL = Tower_dic[drone_name]["flightLevel"] 
        if originalFL is not None:
            Flight_Level[str(originalFL)] = True 
        # use the target FL and update the FL dic
        Tower_dic[drone_name]["flightLevel"] = int(closest_key)
    if avoiding:
        print(f"{drone_name} here ready to cover last point")
    client.moveOnPathAsync(path, 5, 120, airsim.DrivetrainType.ForwardOnly, airsim.YawMode(False, 0), 5, vehicle_name = drone_name)
    
    state_fly, state_avoid = record(client,csv_files_drone, Target_Gps_point,drone_name,Tower_dic,avoiding)
    while state_fly:
        time.sleep(0.2)
        state_fly, state_avoid = record(client,csv_files_drone, Target_Gps_point,drone_name,Tower_dic,avoiding)
    # after reach the avoidance point, change the avoidance state of the drone
    if avoiding:
        Tower_dic[drone_name]['avoidance'] = False
        return
    
    if state_avoid == 1:
        print(f"{drone_name} state change to avoidance")
        # save the previous flypoint
        pre_path = path
        pre_Target_Gps_point = Target_Gps_point
        
        # get the temp fly node
        temp_gps = Tower_dic[drone_name]["tempNode"]
        #print(temp_gps)
        path, Target_Gps_point = getPath_gps(temp_gps)
        print(f"{drone_name} avoidance from{pre_Target_Gps_point} to {Target_Gps_point} ")
        # Directly cover the previous flypoint, and use the new point (avoiding point save in Tower_dic[drone_name]["tempNode"]) as the next fly point
        print(f"{drone_name} here enter 地回")
        Tower_AssignPath(client, drone_name ,path, Target_Gps_point,csv_files_drone,Tower_dic, avoiding = True,FL_check = False)

        # finish the previous flypoint
        Tower_AssignPath(client, drone_name ,pre_path, pre_Target_Gps_point,csv_files_drone,Tower_dic, avoiding = False)
    return



def run_drone_control(drone_name,csv_files_drone,client,flight_path_queue,Tower_dic):
    try:
        logging.info(f"{drone_name}: Taking off")
        path, Target_Gps_point = getPath_pointName('takeoff') # optional: getPath_gps
        Tower_AssignPath(client, drone_name ,path, Target_Gps_point,csv_files_drone,Tower_dic)
        
        try:
            while not flight_path_queue.empty():
                node = flight_path_queue.get()  # Retrieve the next waypoint
                print(f"{drone_name} is fly to node {node}")
                path, Target_Gps_point = getPath_gps(node)
                Tower_AssignPath(client, drone_name, path, Target_Gps_point, csv_files_drone,Tower_dic)
        except Exception as e:
            logging.error(f"Error in drone control for {drone_name}: {e}")



        client.landAsync().join()
        client.armDisarm(False)
        client.enableApiControl(False)

    except Exception as e:
        logging.error(f"Error in drone control for {drone_name}: {e}")

def Tower_avoidance(Tower_dic):
    while True:
        # Define the columns to map to latitude, longitude, altitude
        gpsList = []
        empty = False
        for file in csv_files_drone:
            try:
                row_count  = sum(1 for row in open(file, 'r'))
                skip_rows = row_count - 2  # Skip all but last 15 rows
                if row_count <= 1:
                    empty = True
                    continue
                # Use pandas to read the last row of the CSV file
                df = pd.read_csv(file, skiprows=range(1, skip_rows))
                if not df.empty:
                    # Print the last row (latitude, longitude, altitude)
                    gps_data = df.iloc[-1].tolist()
                    #print(gps_data)
                    gpsList.append(gps_data)

            except pd.errors.EmptyDataError:
                print(f"Empty CSV file: {file}")
            except FileNotFoundError:
                print(f"File not found: {file}")
            except Exception as e:
                print(f"Error reading {file}: {e}")
        if not empty:
            # Now, compare all gps data points in gpsList
            for i, gps1 in enumerate(gpsList):
                NO1_drone = gps1[0]
                for j, gps2 in enumerate(gpsList):
                    NO2_drone = gps2[0]
                    if i < j:  # ensures each pair is compared only once

                        del gps1[0]
                        del gps2[0]
                        # get their seperate FL
                        NO1_drone_FL = Tower_dic[NO1_drone]["flightLevel"]
                        NO2_drone_FL = Tower_dic[NO2_drone]["flightLevel"]
                        """
                        theoretically the tower should seperate their flight level, but we ignored this in order to test the avoidance funciton
                        if NO1_drone_FL == NO2_drone_FL:
                            updated_FL1, updated_FL2 = FL_check_ALGO(NO1_drone_FL, NO2_drone_FL, Flight_Level)
                        """

                        # check vertical and horizontal seperation
                        distance = distance_between_gps_points(gps1, gps2, alt= False)
                        #print(distance,NO1_drone_FL,NO2_drone_FL )
                        if NO1_drone_FL == NO2_drone_FL and distance < 10:
                            print("!!!!!!!")
                            # get what the node that the drone is currently flying to
                            #NO1_drone_target = Tower_dic[NO1_drone]["targetNode"]
                            #NO2_drone_target = Tower_dic[NO2_drone]["targetNode"]

                            # check the alt. avaliable or check the lower/ higher limit one(also if it can still fly toward up)
                            def FL_check_ALGO(FL1, FL2, Flight_Level,upper_limit = 160,lower_limit = 140):
                             
                                def find_available_FLs(current_FL, exclude_FL, Flight_Level, upper_limit, lower_limit):
                                    # Filter based on limits, availability, and excluding the other drone's FL
                                    available_levels = {int(k): v for k, v in Flight_Level.items() if v and lower_limit <= int(k) <= upper_limit and int(k) != exclude_FL and int(k) != current_FL}
                                    return list(available_levels.keys())

                                # Find available flight levels for both drones
                                available_FLs_1 = find_available_FLs(FL1,FL2, Flight_Level, upper_limit, lower_limit)
                                available_FLs_2 = find_available_FLs(FL2,FL1, Flight_Level, upper_limit, lower_limit)

                                # Remove common elements from both lists
                                available_FLs_1 = [fl for fl in available_FLs_1 if fl not in available_FLs_2]
                                available_FLs_2 = [fl for fl in available_FLs_2 if fl not in available_FLs_1]

                                # Randomly select a new flight level from the available options, if any
                                new_FL1 = FL1 if not available_FLs_1 else random.choice(available_FLs_1)
                                new_FL2 = FL2 if not available_FLs_2 else random.choice(available_FLs_2)

                                if new_FL1 == FL1 and new_FL2 == FL2:
                                    success = False
                                    #raise ValueError("none of the flight level are avaliabel")
                                else:
                                    success = True
                                    
                                return new_FL1, new_FL2, success

                            updated_FL1, updated_FL2, success = FL_check_ALGO(NO1_drone_FL, NO2_drone_FL, Flight_Level)
                            # if no avaliable flight level for vertical seperation, turn to horizontal seperation
                            if not success:
                                Tower_dic[NO1_drone]["wait"] = True

                            # set new flight level
                            Tower_dic[NO1_drone]["flightLevel"] = updated_FL1
                            Tower_dic[NO2_drone]["flightLevel"] = updated_FL2
                            
                            # Set tempNode
                            Tower_dic[NO1_drone]["tempNode"] = [gps1[0], gps1[1], updated_FL1]  
                            Tower_dic[NO1_drone]["avoidance"] = True             
                            time.sleep(0.2)
                            Tower_dic[NO2_drone]["tempNode"] = [gps2[0], gps2[1], updated_FL2]  # Set tempNode
                            Tower_dic[NO2_drone]["avoidance"] = True
                            
                            
                            '''
                            IMPORTANT
                            if there are more than two drone in test, the "for loop" of comparing two gps should continue
                            '''
                            while Tower_dic[NO1_drone]["avoidance"] == True and Tower_dic[NO2_drone]["avoidance"] == True:
                                time.sleep(2)
                            print("emergency end")
        

def main():

    # Initialize the AirSim client
    client1 = airsim.MultirotorClient()
    client1.confirmConnection()
    client1.enableApiControl(True,"Drone1")
    client1.armDisarm(True,"Drone1")
    client2 = airsim.MultirotorClient()
    client2.confirmConnection()
    client2.enableApiControl(True, "Drone2")
    client2.armDisarm(True, "Drone2")
    client3 = airsim.MultirotorClient()
    client3.confirmConnection()
    client3.enableApiControl(True, "Drone3")
    client3.armDisarm(True, "Drone3")
    client_names = [client1,client2]
    drone_names = ["Drone1","Drone2"]
    
    """
    [Intention, Direction]
    
    Intentino:
    1. Approach
    2. Departure
    3. Passing
    type:str

    Direction:
    [latitude, longitude, altitude]
    type: list
    """
    
    drone1_intention = "Departure"
    drone2_intention = "Approach"
    
    start1, end1 =FlightPath_OD(drone1_intention)
    start2, end2 =FlightPath_OD(drone2_intention)
    drone1_path = FlightPath(drone1_intention,start1, end1)
    drone2_path = FlightPath(drone2_intention,start2, end2)
    #print(drone1_path)
    #print(drone2_path)
    flight_path_queue_drone1 = queue.Queue()
    flight_path_queue_drone2 = queue.Queue()

    for point in drone1_path:
        flight_path_queue_drone1.put(point)
    for point in drone2_path:
        flight_path_queue_drone2.put(point)
    path = [flight_path_queue_drone1,flight_path_queue_drone2]
    # if intention contains "departure" ==> find the original delay
    # create dictionary for each drone to save the emergency state and temperary point to fly with

    Tower_dic = {
        "Drone1": {"avoidance": False,"targetNode": None, "tempNode": None, "flightLevel":None, "wait":False},
        "Drone2": {"avoidance": False,"targetNode": None,"tempNode": None, "flightLevel":None, "wait":False},
        # Add more drones as needed
    }



    dash_thread = threading.Thread(target=run_dash_server, daemon=True)
    dash_thread.start()

    tower_thread = threading.Thread(target=Tower_avoidance, args=(Tower_dic,), daemon=True)
    tower_thread.start()

    threads = []
    staggered_delay = 51  # seconds between starting each drone's control loop

    """
    Avoidance test
    
    scenario 1 :
    1 => "Departure"
    2 => "Approach"
    delay => 51
    thred => 7

    scenario 2 : 
    1 => "Departure"
    2 => "Passing"
    delay => 51
    thred => 7

    scenario 3 : 
    1 => "Approach", left = True
    2 => "Passing"
    delay => 25
    thred => 10
    
    """
    for i, drone_client in enumerate(client_names):

        t = threading.Thread(target=run_drone_control, args=(drone_names[i],csv_files_drone[i],drone_client,path[i],Tower_dic))
        t.start()
        threads.append(t)
        time.sleep(staggered_delay)
        
    

    for t in threads:
        t.join()
    
    
   


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Starting multi-drone mission")
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    clean(csv_files_drone)
    main()
