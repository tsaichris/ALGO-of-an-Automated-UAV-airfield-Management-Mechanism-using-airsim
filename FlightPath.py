from PointTool import getgpsDataByName, create_geo_point, getNedDataByName,distance_between_gps_points
import math



def FlightPath(intention, direction_start, direction_end):
    # Use the first point(initial point) and last point(target path or direction) to find the enter and leaving waypoint
    #  then append the path 
    pathList = []
    waypoints = ["waypoint1","waypoint2", "waypoint3", "waypoint4", "waypoint5", "waypoint6",
                "waypoint7", "waypoint8", "waypoint9", "waypoint10", "waypoint11", "waypoint12"]
    def closetWaypointAssign(original_point, waypoints):
        temp = math.inf
        target_point = "None"
        for point in waypoints:
            point_gps = getgpsDataByName(point)
            result = distance_between_gps_points(original_point, point_gps,alt=False)
            #print(point, result)
            if result < temp:
                temp = result
                target_point = point
        if target_point != "None":
            return target_point # str, point name
        else:
            raise ValueError(f"Can't find closet waypoint on P{original_point}")

    def circle_sequence(waypoints, start_point, end_point,pathList):
        # Find the indices of the start and end points
        start_index = waypoints.index(start_point)
        end_index = waypoints.index(end_point)

        # Determine the direction for counterclockwise movement
        if start_index >= end_index:
            # Direct counterclockwise movement
            sequence = waypoints[end_index+1:start_index][::-1]
        else:
            # Wrap around the list to move counterclockwise
            sequence = waypoints[end_index+1:] + waypoints[:start_index]
            sequence = sequence[::-1]
        
        # form path
        pathList.append(getgpsDataByName(start_point))
        for point_name in sequence:
            gpsPoint = getgpsDataByName(point_name)
            pathList.append(gpsPoint)
        pathList.append(getgpsDataByName(end_point))
    

        return pathList

    if intention == "Approach":
        pathList.append(direction_start)
        outCircle_point = getgpsDataByName("waypoint1")
        enterCircle_point = closetWaypointAssign(direction_start, waypoints) # str, point name
        pathList = circle_sequence(waypoints, enterCircle_point, "waypoint1", pathList) # return gpsPoints path
        pathList.append(getgpsDataByName("enter"))
        pathList.append(direction_end)
        return pathList

    elif intention =="Departure":
        pathList.append(direction_start)
        pathList.append(getgpsDataByName("leave"))
        outCircle_point = closetWaypointAssign(direction_end, waypoints) # str, point name
        pathList = circle_sequence(waypoints, "waypoint7", outCircle_point, pathList)
        pathList.append(direction_end)
        return pathList
        
    elif intention =="Passing":
        #print("do check passing")
        #print(pathList)
        pathList.append(direction_start)
        enterCircle_point = closetWaypointAssign(direction_start,waypoints)
        outCircle_point = closetWaypointAssign(direction_end, waypoints)
        #print(enterCircle_point,outCircle_point)
        pathList = circle_sequence(waypoints, enterCircle_point, outCircle_point, pathList)
        pathList.append(direction_end)  
        #print(pathList)
        return pathList
    else:
        raise ValueError(f"Wrong intention: {intention}")

def FlightPath_OD(intention, left = False):
    
    if left:
        direction_approach_start = [47.640929010829026,-122.14016499999998,121.521]
    else:
        direction_approach_start = [47.64146, -122.140165, 160]
    #if random 
    #direction_approach_start = random()
    direction_approach_end = [47.64110097309533, -122.13914115070773, 121.321] # tower
    
    direction_departure_start = [47.64110097309533, -122.13914115070773, 121.521] # tower
    direction_departure_end = [47.6405, -122.1370, 130]
    #direction_departure_end = random()
    
    direction_passing_start = [47.64146, -122.140165, 160]
    #direction_passing_start = random()
    direction_passing_end = [47.64346, -122.1370, 130]
    #direction_passing_end = random()
    if intention == "Approach":
        return(direction_approach_start, direction_approach_end)
    elif intention =="Departure":
        return(direction_departure_start, direction_departure_end)
    elif intention =="Passing":
        return(direction_passing_start, direction_passing_end)
    else:
        raise ValueError(f"Wrong intention: {intention}")

    