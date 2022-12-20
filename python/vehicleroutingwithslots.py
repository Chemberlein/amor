import json
import math
import columngenerationsolverpy
import treesearchsolverpy
from elementaryshortestpathwithslots import Instance as SubInst
from elementaryshortestpathwithslots import BranchingScheme

class Location:
    id = None
    visit_intervals = None
    x = None
    y = None


class Instance:

    def __init__(self, filepath=None):
        self.locations = []
        if filepath is not None:
            with open(filepath) as json_file:
                data = json.load(json_file)
                locations = zip(
                        data["visit_intervals"],
                        data["xs"],
                        data["ys"])
                for (intervals, x, y) in locations:
                    self.add_location(intervals, x, y)

    def add_location(self, visit_intervals, x, y):
        location = Location()
        location.id = len(self.locations)
        location.visit_intervals = visit_intervals
        location.x = x
        location.y = y
        self.locations.append(location)

    def duration(self, location_id_1, location_id_2):
        xd = self.locations[location_id_2].x - self.locations[location_id_1].x
        yd = self.locations[location_id_2].y - self.locations[location_id_1].y
        d = round(math.sqrt(xd * xd + yd * yd))
        return d

    def write(self, filepath):
        data = {"visit_intervals": [location.visit_intervals
                                    for location in self.locations],
                "xs": [location.x for location in self.locations],
                "ys": [location.y for location in self.locations]}
        with open(filepath, 'w') as json_file:
            json.dump(data, json_file)

    def check(self, filepath):
        print("Checker")
        print("-------")
        with open(filepath) as json_file:
            data = json.load(json_file)
            # Compute total_distance.
            total_travelled_distance = 0
            on_time = True
            for locations in data["locations"]:
                current_time = -math.inf
                location_pred_id = 0
                for location_id in locations:
                    location = self.locations[location_id]
                    d = self.duration(location_pred_id, location_id)
                    total_travelled_distance += d
                    t = current_time + d
                    try:
                        interval = min(
                                (itrv for itrv in location.visit_intervals
                                 if itrv[0] >= t),
                                key=lambda interval: interval[1])
                        current_time = interval[1]
                    except ValueError:
                        on_time = False
                    location_pred_id = location_id
                total_travelled_distance += self.duration(location_pred_id, 0)
            # Compute number_of_locations.
            number_of_duplicates = len(locations) - len(set(locations))

            is_feasible = (
                    (number_of_duplicates == 0)
                    and (on_time)
                    and 0 not in locations)
            objective_value = total_travelled_distance
            print(f"Number of duplicates: {number_of_duplicates}")
            print(f"On time: {on_time}")
            print(f"Total travelled distance: {total_travelled_distance}")
            print(f"Feasible: {is_feasible}")
            return (is_feasible, objective_value)


class PricingSolver:

    def __init__(self, instance):
        self.instance = instance
        # TODO START
        self.visitedClients = None
        # TODO END

    def initialize_pricing(self, columns, fixed_columns):
        # TODO START
        self.visitedClients = [0] * len(instance.locations)
        for column_id, column_value in fixed_columns:
            column = columns[column_id]
            for row_index, row_coefficient in zip(column.row_indices,column.row_coefficients):
                self.visitedClients[row_index] += (column_value * row_coefficient)
        self.visitedClients[0] = 1
        # TODO END

    def solve_pricing(self, duals):
        # Build subproblem instance.
        # TODO START
        backTr = {}
        subInst = SubInst()
        # Add depot
        subInst.add_location(self.instance.locations[0].visit_intervals,self.instance.locations[0].x,self.instance.locations[0].y,0)
        ordr=1
        # We construct an el. short. path instance where values are the duals of the sol. to the master program
        for client_id, client in enumerate(self.instance.locations):
            value = duals[client_id]
            # We don't take clients that were already visited
            if self.visitedClients[client_id]<1:
                subInst.add_location(client.visit_intervals,client.x,client.y,value)
                backTr[ordr]=client.id
                ordr+=1
        # TODO END

        # Solve subproblem instance.
        # TODO START
        # Here we solve an el. short. path with slots instance to find the min. reduced cost column
        branching_scheme = BranchingScheme(subInst)
        output = treesearchsolverpy.iterative_beam_search(
                    branching_scheme,
                    # time_limit=5,
                    minimum_size_of_the_queue=256,
                    maximum_size_of_the_queue=256,
                    verbose=False)
        bt = branching_scheme.to_solution(output["solution_pool"].best)
        tmp = bt 
        bt = []
        for i in tmp:
            bt.append(backTr[i])

        # TODO END

        # Retrieve column.
        # TODO START
        # The problem is infeasible
        if (len(bt)==0):
            return []    

        # Reconstruct the solution of the el. short. path with slots instance
        dist = self.instance.duration(0,self.instance.locations[bt[0]].id) 
        for i in range(1,len(bt)):
            dist += instance.duration(instance.locations[bt[i-1]].id,instance.locations[bt[i]].id)
        dist += instance.duration(instance.locations[bt[-1]].id,0) 

        # Retrieve column from the el. short. path with slots instance solution
        column = columngenerationsolverpy.Column()
        column.objective_coefficient = dist
        for city in bt:
            column.row_indices.append(city)
            # Here we retrieve a_{ik} as defined in 3.3 in the report
            column.row_coefficients.append(1)
        # TODO END

        return [column]


def get_parameters(instance):
    # TODO START
    number_of_constraints = len(instance.locations)
    p = columngenerationsolverpy.Parameters(number_of_constraints)
    maximum_dist = 0
    for i in range(1,len(instance.locations)):
        maximum_dist += 2*instance.duration(0,instance.locations[i].id)
    p.objective_sense = "min"
    # Column bounds.
    p.column_lower_bound = 0
    p.column_upper_bound = maximum_dist
    # Row bounds.
    # Here we initialize constraints of the master program (section 3.3, equations 12-14 in the report).
    for city in instance.locations:
        p.row_lower_bounds[city.id] = 1
        p.row_upper_bounds[city.id] = 1
        p.row_coefficient_lower_bounds[city.id] = 0
        p.row_coefficient_upper_bounds[city.id] = 1
    p.row_lower_bounds[0] = 0
    p.row_upper_bounds[0] = 0
    p.row_coefficient_lower_bounds[0] = 0
    p.row_coefficient_upper_bounds[0] = 0
    # Dummy column objective coefficient.
    p.dummy_column_objective_coefficient = 2*maximum_dist
    # TODO END
    # Pricing solver.
    p.pricing_solver = PricingSolver(instance)
    return p


def to_solution(columns, fixed_columns):
    solution = []
    for column, value in fixed_columns:
        s = []
        for index, coef in zip(column.row_indices, column.row_coefficients):
            s += [index] * coef
        solution.append(s)
    return solution


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
            "-a", "--algorithm",
            type=str,
            default="column_generation",
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
                instance.add_location(
                        [(s1, s1 + p1), (s2, s2 + p2)], x, y)
            instance.write(
                    args.instance + "_" + str(number_of_locations) + ".json")

    elif args.algorithm == "column_generation":
        instance = Instance(args.instance)
        output = columngenerationsolverpy.column_generation(
                get_parameters(instance))

    else:
        instance = Instance(args.instance)
        if(len(instance.locations)<=1):
            solution = [[]]
            if args.certificate is not None:
                data = {"locations": solution}
                with open(args.certificate, 'w') as json_file:
                    json.dump(data, json_file)
                print()
                instance.check(args.certificate)    
        else:
            parameters = get_parameters(instance)
            if args.algorithm == "greedy":
                output = columngenerationsolverpy.greedy(
                        parameters)
            elif args.algorithm == "limited_discrepancy_search":
                output = columngenerationsolverpy.limited_discrepancy_search(
                        parameters)
            solution = to_solution(parameters.columns, output["solution"])
            if args.certificate is not None:
                data = {"locations": solution}
                with open(args.certificate, 'w') as json_file:
                    json.dump(data, json_file)
                print()
                instance.check(args.certificate)