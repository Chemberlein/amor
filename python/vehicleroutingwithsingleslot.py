import json
import math
import columngenerationsolverpy


class Location:
    id = None
    visit_interval = None
    x = None
    y = None


class Instance:

    def __init__(self, filepath=None):
        self.locations = []
        self.locationsWD = []
        if filepath is not None:
            with open(filepath) as json_file:
                data = json.load(json_file)
                locations = zip(
                        data["visit_intervals"],
                        data["xs"],
                        data["ys"])
                for (intervals, x, y) in locations:
                    self.add_location(intervals[0], x, y)
        for i in self.locations:
            if(i.id!=0):
                self.locationsWD.append(i)

    def add_location(self, visit_interval, x, y):
        location = Location()
        location.id = len(self.locations)
        location.visit_interval = visit_interval
        location.x = x
        location.y = y
        self.locations.append(location)

    def duration(self, location_id_1, location_id_2):
        xd = self.locations[location_id_2].x - self.locations[location_id_1].x
        yd = self.locations[location_id_2].y - self.locations[location_id_1].y
        d = round(math.sqrt(xd * xd + yd * yd))
        return d

    def write(self, filepath):
        data = {"visit_intervals": [location.visit_interval
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
                for location_id in locations + [0]:
                    location = self.locations[location_id]
                    d = self.duration(location_pred_id, location_id)
                    total_travelled_distance += d
                    t = current_time + d
                    if t <= location.visit_interval[0]:
                        current_time = location.visit_interval[1]
                    else:
                        on_time = False
                    location_pred_id = location_id
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
        self.costMatrix=[[] for i in range(len(self.instance.locations))]
        for i in range(len(self.instance.locations)):
            for j in range(len(self.instance.locations)):
                self.costMatrix[i].append(self.instance.duration(i,j))
        print("Before")
        for i in  self.costMatrix:
            print(i)
        
    def initialize_pricing(self, columns, fixed_columns):
        # TODO START
        self.visitedClients = [0] * len(instance.locationsWD)
        for column_id, column_value in fixed_columns:
            column = columns[column_id]
            for row_index, row_coefficient in zip(column.row_indices,column.row_coefficients):
                self.visitedClients[row_index] += (column_value * row_coefficient)
        # TODO END

    def solve_pricing(self, duals):
        # Build subproblem instance.
        # TODO START
        cities=[]
        dualVars=[]
        # Here we construct a cost matrix to find the column of minimum reduced cost as described in 3.4 in the report.
        self.costMatrix=[[] for i in range(len(self.instance.locations))]
        for i in range(len(self.instance.locations)):
            for j in range(len(self.instance.locations)):
                if(i==0 or j==0):
                    self.costMatrix[i].append(0)
                else:
                    self.costMatrix[i].append(self.instance.duration(i,j))
        for client_id, client in enumerate(self.instance.locationsWD):
            dualVar = duals[client_id]
            print("Dualvar",dualVar)
            for i in self.instance.locationsWD:
                self.costMatrix[client.id][i.id] = self.costMatrix[client.id][i.id] - dualVar
        print("After")
        
        for i in  self.costMatrix:
            print(i)
        # TODO END
        # Solve subproblem instance.
        # TODO START 
        # Here we solve problem 1 with a different cost matrix as described in 3.4 in the report.
        bt = dynamic_programming(self.instance,self.costMatrix)
        # TODO END
        if (len(bt)==0):
            column = columngenerationsolverpy.Column()
            column.objective_coefficient = math.inf
            return [column]    

        dist = instance.duration(instance.locations[bt[0]].id,0) 
        for i in range(1,len(bt)):
            dist += instance.duration(instance.locations[i-1].id,instance.locations[i].id)
        dist += instance.duration(instance.locations[bt[-1]].id,0) 
    
        # Retrieve column.
        column = columngenerationsolverpy.Column()
        column.objective_coefficient = dist
        for city in self.instance.locationsWD:
            if city.id in bt:
                column.row_indices.append(city.id-1)
                # Here we retrieve a_{ik} as defined in 3.3 in the report.
                column.row_coefficients.append(1)
            else:
                column.row_indices.append(city.id-1)
                column.row_coefficients.append(0)
        print(column)
        return [column]



def dynamic_programming(instance,cost):
    # TODO START
    #Sorting instances in order of time slot start point
    tmpLoc = [item for item in instance.locations if item.id!=0]
    tmpLoc = sorted(tmpLoc,key = lambda x:x.visit_interval[0])
    dp = [ math.inf for i in range(len(tmpLoc))]
    backtracking = [[i.id] for i in tmpLoc]
    for i in range(len(tmpLoc)):
        price = math.inf
        bt = []
        for j in range(1,i):
            if tmpLoc[i-j].visit_interval[1]+instance.duration(tmpLoc[i].id,tmpLoc[i-j].id)<tmpLoc[i].visit_interval[0]:
                if price > dp[i-j]:
                    price = dp[i-j]
                    bt=backtracking[i-j]
        if tmpLoc[i].visit_interval[1]+instance.duration(tmpLoc[i].id,0)<instance.locations[0].visit_interval[0]:
            if len(bt)>0 and price+cost[bt[-1]][tmpLoc[i].id] < cost[0][tmpLoc[i].id]:
                dp[i]=price+cost[bt[-1]][tmpLoc[i].id]
                backtracking[i]=bt+backtracking[i]
            else:
                dp[i]= cost[0][tmpLoc[i].id]
    maxi=-1
    m = math.inf
    for i in range(len(dp)):
        dp[i]=dp[i]+cost[tmpLoc[i].id][0]
        if (m>dp[i]):
            maxi=i
            m=dp[i]
    if maxi == -1:
        return []
    print(backtracking[maxi])
    return backtracking[maxi]
    # TODO END

def get_parameters(instance):
    # TODO START
    number_of_constraints = len(instance.locationsWD)
    p = columngenerationsolverpy.Parameters(number_of_constraints)
    maximum_dist = 0
    for i in range(1,len(instance.locations)):
        maximum_dist += 2*instance.duration(0,instance.locations[i].id)
    p.objective_sense = "min"
    # Column bounds.
    p.column_lower_bound = 0
    #maximum_dist*2
    p.column_upper_bound = maximum_dist*50
    # Row bounds.
    # Here we initialize constraints of the master program (section 3.3, equations 12-14 in the report).
    for city in instance.locationsWD:
        p.row_lower_bounds[city.id-1] = 1
        p.row_upper_bounds[city.id-1] = 1
        p.row_coefficient_lower_bounds[city.id-1] = 0
        p.row_coefficient_upper_bounds[city.id-1] = 1
    # Dummy column objective coefficient.
    p.dummy_column_objective_coefficient = maximum_dist
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
        solution.append((value, s))
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

    elif args.algorithm == "column_generation":
        instance = Instance(args.instance)
        output = columngenerationsolverpy.column_generation(
                get_parameters(instance))
        print(output)
    else:
        instance = Instance(args.instance)
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
