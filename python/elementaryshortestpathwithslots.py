import json
import math
import treesearchsolverpy
from functools import total_ordering


class Location:
    id = None
    visit_intervals = None
    x = None
    y = None
    value = None


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
                    self.add_location(intervals, x, y, value)

    def add_location(self, visit_intervals, x, y, value):
        location = Location()
        location.id = len(self.locations)
        location.visit_intervals = visit_intervals
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
            for location_id in data["locations"] + [0]:
                location = self.locations[location_id]
                t = current_time + self.duration(location_pred_id, location_id)
                try:
                    interval = min(
                            (interval for interval in location.visit_intervals
                             if interval[0] >= t),
                            key=lambda interval: interval[1])
                    current_time = interval[1]
                except ValueError:
                    on_time = False
                total_cost += self.cost(location_pred_id, location_id)
                location_pred_id = location_id
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


class BranchingScheme:

    @total_ordering
    class Node:

        id = None
        father = None
        # TODO START
        visited = None
        number_of_locations = None
        j = None
        cost = None
        time = None
        # TODO END
        guide = None
        next_child_pos = 0

        def __lt__(self, other):
            if self.guide != other.guide:
                return self.guide < other.guide
            return self.id < other.id

    def __init__(self, instance):
        self.instance = instance
        self.id = 0

    def root(self):
        node = self.Node()
        node.father = None
        node.visited = (1 << 0)
        node.number_of_locations = 1
        node.j = 0
        node.cost = 0
        node.time = -math.inf
        node.guide = 0
        node.id = self.id
        self.id += 1
        return node

    def next_child(self, father):
        # TODO START
        # Find the next location to add to the partial tour.
        j_next = father.next_child_pos
        # Update node.next_child_pos.
        father.next_child_pos += 1
        # If this location has already been visited, return.
        if (father.visited >> j_next) & 1:
            return None
        
        # Check if all predecessors have been visited
        # if we cant go to the customer in time in time  or if we can't reach depot after customer j_next
        ts1Inposible = (father.time + self.instance.duration(j_next,father.j) > self.instance.locations[j_next].visit_intervals[0][0]
            or (self.instance.locations[j_next].visit_intervals[0][1]+ self.instance.duration(j_next,0) > self.instance.locations[0].visit_intervals[0][0]
                and self.instance.locations[j_next].visit_intervals[0][1]+ self.instance.duration(j_next,0) > self.instance.locations[0].visit_intervals[1][0]
                )
            )
        ts2Inposible = (father.time + self.instance.duration(j_next,father.j) > self.instance.locations[j_next].visit_intervals[1][0]
                or (self.instance.locations[j_next].visit_intervals[1][1]+ self.instance.duration(j_next,0) > self.instance.locations[0].visit_intervals[0][0]
                and self.instance.locations[j_next].visit_intervals[1][1]+ self.instance.duration(j_next,0) > self.instance.locations[0].visit_intervals[1][0]
                )
            )
        if   ts1Inposible and ts2Inposible:
            return None
        
        # Build child node.
        child = self.Node()
        child.father = father
        child.visited = father.visited + (1 << j_next)
        child.number_of_locations = father.number_of_locations + 1
        child.j = j_next
        child.cost = father.cost + self.instance.cost(father.j, j_next)
        if ts1Inposible:
            child.time=self.instance.locations[j_next].visit_intervals[1][1]
        elif ts2Inposible:
            child.time= self.instance.locations[j_next].visit_intervals[0][1] # fix
        else:
            child.time= min(self.instance.locations[j_next].visit_intervals[1][1],self.instance.locations[j_next].visit_intervals[0][1]) # fix
        child.guide = child.cost
        child.id = self.id
        self.id += 1
        return child

        # TODO END

    def infertile(self, node):
        # TODO START
        return  node.next_child_pos == len(self.instance.locations) 
        # TODO END

    def leaf(self, node):
        # TODO START   may be just true 
        return True
        # TODO END

    def bound(self, node_1, node_2):
        # TODO START
        # Check if node_2 is feasible. ?????????
        return node_2.time + self.instance.duration(0,node_2.j) > self.instance.locations[0].visit_intervals[0][0] and node_2.time + self.instance.duration(0,node_2.j) > self.instance.locations[0].visit_intervals[0][1]
        # TODO END

    # Solution pool.

    def better(self, node_1, node_2):
        # TODO START
        if  node_1.cost + self.instance.cost(0,node_1.j) > node_2.cost+self.instance.cost(0,node_2.j) :
            return False
        return True
        # TODO END

    def equals(self, node_1, node_2):
        # TODO START
        # I don't undestand well this method may be usefull to chek and return true if visited and time equals
        return False
        # TODO END

    # Dominances.

    def comparable(self, node):
        # TODO START
        return True
        # TODO END

    class Bucket:
        def __init__(self, node):
            self.node = node
        def __hash__(self):
            # TODO START
            return hash((self.node.j, self.node.visited,self.node.time))
            # TODO END
        def __eq__(self, other):
            # TODO START
            return (
                # Same last location.
                self.node.j == other.node.j
                # Same visited locations.
                and self.node.visited == other.node.visited
                # Same time.
                and self.node.time == other.node.time)
            # TODO END


    def dominates(self, node_1, node_2):
        # TODO START # and node_1.time <= node_2.time
        if node_1.cost + self.instance.cost(0,node_1.j) < node_2.cost+self.instance.cost(0,node_2.j) :
            return True
        if (node_1.cost + self.instance.cost(0,node_1.j) == node_2.cost+self.instance.cost(0,node_2.j) and node_1.number_of_locations>node_2.number_of_locations):
            return True
        if (node_1.cost + self.instance.cost(0,node_1.j) == node_2.cost+self.instance.cost(0,node_2.j) and node_1.time<node_2.time):
            return True
        return False
        # TODO END

    # Outputs.
    def display(self, node):
        # TODO START
        # Check if node is feasible.
        if node.number_of_locations < len(self.instance.locations):
            return ""
        # Compute the objective value of node.
        d = node.cost + self.instance.cost(node.j, 0)
        return str(d)
        # TODO END

    def to_solution(self, node):
        # TODO START
        locations = []
        node_tmp = node
        while node_tmp.father is not None:
            locations.append(node_tmp.j)
            node_tmp = node_tmp.father
        locations.reverse()
        return locations
        # TODO END

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
            "-a", "--algorithm",
            type=str,
            default="iterative_beam_search",
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

    if args.algorithm == "checker":
        instance = Instance(args.instance)
        instance.check(args.certificate)

    elif args.algorithm == "generator":
        import random
        random.seed(0)
        for number_of_locations in range(101):
            instance = Instance()
            total_weight = 0
            for location_id in range(number_of_locations):
                s1 = random.randint(0, 1000)
                p1 = random.randint(0, 100)
                s2 = random.randint(0, 1000)
                p2 = random.randint(0, 100)
                x = random.randint(0, 100)
                y = random.randint(0, 100)
                value = random.randint(0, 100)
                instance.add_location(
                        [(s1, s1 + p1), (s2, s2 + p2)], x, y, value)
            instance.write(
                    args.instance + "_" + str(number_of_locations) + ".json")

    else:
        instance = Instance(args.instance)
        branching_scheme = BranchingScheme(instance)
        if args.algorithm == "greedy":
            output = treesearchsolverpy.greedy(
                    branching_scheme)
        elif args.algorithm == "best_first_search":
            output = treesearchsolverpy.best_first_search(
                    branching_scheme,
                    time_limit=30)
        elif args.algorithm == "iterative_beam_search":
            output = treesearchsolverpy.iterative_beam_search(
                    branching_scheme,
                    time_limit=30)
        solution = branching_scheme.to_solution(output["solution_pool"].best)
        if args.certificate is not None:
            data = {"locations": solution}
            with open(args.certificate, 'w') as json_file:
                json.dump(data, json_file)
            print()
            instance.check(args.certificate)
