import json
import math


class Location:
    id = -1
    visit_interval = 0
    x = 0
    y = 0
    value = 0


class Instance:

    def __init__(self, filepath=None):
        self.locations = []
        if filepath is not None:
            with open(filepath) as json_file:
                data = json.load(json_file)
                locations = zip(
                        data["visit_intervals"],
                        data["xs"],
                        data["ys"],
                        data["values"])
                for (intervals, x, y, value) in locations:
                    self.add_location(intervals[0], x, y, value)

    def add_location(self, visit_interval, x, y, value):
        location = Location()
        location.id = len(self.locations)
        location.visit_interval = visit_interval
        location.x = x
        location.y = y
        location.value = value
        self.locations.append(location)

    def duration(self, location_id_1, location_id_2):
        xd = self.locations[location_id_2].x - self.locations[location_id_1].x
        yd = self.locations[location_id_2].y - self.locations[location_id_1].y
        d = round(math.sqrt(xd * xd + yd * yd))
        return d

    def cost(self, location_id_1, location_id_2):
        xd = self.locations[location_id_2].x - self.locations[location_id_1].x
        yd = self.locations[location_id_2].y - self.locations[location_id_1].y
        d = round(math.sqrt(xd * xd + yd * yd))
        return d - self.locations[location_id_2].value

    def write(self, filepath):
        data = {"visit_intervals": [location.visit_intervals
                                    for location in self.locations],
                "xs": [location.x for location in self.locations],
                "ys": [location.y for location in self.locations],
                "values": [location.value for location in self.locations]}
        with open(filepath, 'w') as json_file:
            json.dump(data, json_file)

    def check(self, filepath):
        print("Checker")
        print("-------")
        with open(filepath) as json_file:
            data = json.load(json_file)
            locations = data["locations"]
            on_time = True
            total_cost = 0
            current_time = -math.inf
            location_pred_id = 0
            for location_id in data["locations"]:
                location = self.locations[location_id]
                t = current_time + self.duration(location_pred_id, location_id)
                if t <= location.visit_interval[0]:
                    current_time = location.visit_interval[1]
                else:
                    on_time = False
                total_cost += self.cost(location_pred_id, location_id)
                location_pred_id = location_id
            total_cost += self.cost(location_pred_id, 0)
            number_of_duplicates = len(locations) - len(set(locations))
            is_feasible = (
                    (number_of_duplicates == 0)
                    and (on_time)
                    and 0 not in locations)
            print(f"Number of duplicates: {number_of_duplicates}")
            print(f"On time: {on_time}")
            print(f"Feasible: {is_feasible}")
            print(f"Cost: {total_cost}")
            return (is_feasible, total_cost)


def dynamic_programming(instance):
    # TODO START

    # Initialize the list of clients without the debot.
    tmpLoc = [item for item in instance.locations if item.id!=0]
    # Sort all clients by starting time.
    tmpLoc = sorted(tmpLoc,key = lambda x:x.visit_interval[0])
    # Initialize the table where i contains the opt. cost from depot to i.
    T = [math.inf for i in range(len(tmpLoc))]
    # Initialize the table where i contains all the previous loc. in the opt. path from depot to i.
    L = [[i.id] for i in tmpLoc]
    for i in range(len(tmpLoc)):
        # Initially the price is +inf.
        price = math.inf
        # A "live backtracking list" per location, so that we don't need to backtrack at the end.
        bt = []
        # For each other location j.
        for j in range(1,i):
            # Check if it's feasible.
            if tmpLoc[i-j].visit_interval[1]+instance.duration(tmpLoc[i].id,tmpLoc[i-j].id)<tmpLoc[i].visit_interval[0]:
                # Recurrence relation.
                if price > T[i-j]:
                    price = T[i-j]
                    bt = L[i-j]
        # If in the opt. sol. there are intermediate locations between the depot and i.
        if len(bt)>0 and price+instance.cost(bt[-1],tmpLoc[i].id) < instance.cost(0,tmpLoc[i].id):
            # Recurrence relation.
            T[i] = price+instance.cost(bt[-1],tmpLoc[i].id)
            L[i] = bt+L[i]
        else:
            # Recurrence relation.
            T[i] = instance.cost(0,tmpLoc[i].id)
    # Look for the opt. solution from depot to i and back to depot.
    opt_cost_id = -1
    m = math.inf
    for i in range(len(T)):
        T[i] = T[i]+instance.cost(tmpLoc[i].id,0)
        if (m>T[i]):
            opt_cost_id = i
            m = T[i]
    # There is no feasible solution.
    if opt_cost_id == -1:
        return []
    return L[opt_cost_id]

    # TODO END


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
            "-a", "--algorithm",
            type=str,
            default="dynamic_programming",
            help='')
    parser.add_argument(
            "-i", "--instance",
            type=str,
            help='')
    parser.add_argument(
            "-c", "--certificate",
            type=str,
            default=None,
            help='')

    args = parser.parse_args()

    if args.algorithm == "dynamic_programming":
        instance = Instance(args.instance)
        solution = dynamic_programming(instance)
        if args.certificate is not None:
            data = {"locations": solution}
            with open(args.certificate, 'w') as json_file:
                json.dump(data, json_file)
            print()
            instance.check(args.certificate)

    elif args.algorithm == "checker":
        instance = Instance(args.instance)
        instance.check(args.certificate)
