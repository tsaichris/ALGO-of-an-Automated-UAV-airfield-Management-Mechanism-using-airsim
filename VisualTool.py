
from PointTool import getNedDataByName
import os
import csv

def initial_csv(drone_names):

    def create_unique_csv_file(file_path, points, getNedDataByName, drone_names):
        n = 1
        while os.path.exists(os.path.join(file_path, f'log{n}_{drone_names}.csv')):
            n += 1

        file_name = os.path.join(file_path, f'log{n}_{drone_names}.csv')

        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['name', 'x', 'y', 'z'])  # column headers
            '''
            for point_name in points:
                p_lat, p_lon, p_alt = getNedDataByName(point_name)
                writer.writerow([point_name, p_lat, p_lon, p_alt])
            '''
        return file_name

    file_path = "C:/Users/User/Desktop/airsim/PlotLog"
    points = ["tower", "enter", "leave", "waypoint1", "waypoint2", "waypoint3", "waypoint4", 
            "waypoint5", "waypoint6", "waypoint7", "waypoint8", "waypoint9", "waypoint10", 
            "waypoint11", "waypoint12"]

    # Assuming getGpsDataByName is defined as in your initial code
    csv_file_name = create_unique_csv_file(file_path, points, getNedDataByName, drone_names)

    print(f"Created CSV file: {csv_file_name}")
    return csv_file_name
   

