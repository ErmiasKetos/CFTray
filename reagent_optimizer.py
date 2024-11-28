class ReagentOptimizer:
    def __init__(self):
        self.experiment_data = {
            1: {"name": "Copper (II) (LR)", "reagents": [{"code": "KR1E", "vol": 850}, {"code": "KR1S", "vol": 300}]},
            2: {"name": "Lead (II) Cadmium (II)", "reagents": [{"code": "KR1E", "vol": 850}, {"code": "KR2S", "vol": 400}]},
            3: {"name": "Arsenic (III)", "reagents": [{"code": "KR3E", "vol": 850}, {"code": "KR3S", "vol": 400}]},
            4: {"name": "Nitrates-N (LR)", "reagents": [{"code": "KR4E", "vol": 850}, {"code": "KR4S", "vol": 300}]},
            5: {"name": "Chromium (VI) (LR)", "reagents": [{"code": "KR5E", "vol": 500}, {"code": "KR5S", "vol": 400}]},
            6: {"name": "Manganese (II) (LR)", "reagents": [{"code": "KR6E1", "vol": 500}, {"code": "KR6E2", "vol": 500}, {"code": "KR6E3", "vol": 300}]},
            7: {"name": "Boron (Dissolved)", "reagents": [{"code": "KR7E1", "vol": 1100}, {"code": "KR7E2", "vol": 1860}]},
            8: {"name": "Silica (Dissolved)", "reagents": [{"code": "KR8E1", "vol": 500}, {"code": "KR8E2", "vol": 1600}]},
            9: {"name": "Free Chlorine", "reagents": [{"code": "KR9E1", "vol": 1000}, {"code": "KR9E2", "vol": 1000}]},
            10: {"name": "Total Hardness", "reagents": [{"code": "KR10E1", "vol": 1000}, {"code": "KR10E2", "vol": 1000}, {"code": "KR10E3", "vol": 1600}]},
            11: {"name": "Total Alkalinity (LR)", "reagents": [{"code": "KR11E", "vol": 1000}]},
            12: {"name": "Orthophosphates-P (LR)", "reagents": [{"code": "KR12E1", "vol": 500}, {"code": "KR12E2", "vol": 500}, {"code": "KR12E3", "vol": 200}]},
            13: {"name": "Mercury (II)", "reagents": [{"code": "KR13E1", "vol": 850}, {"code": "KR13S", "vol": 300}]},
            14: {"name": "Selenium (IV)", "reagents": [{"code": "KR14E", "vol": 500}, {"code": "KR14S", "vol": 300}]},
            15: {"name": "Zinc (II) (LR)", "reagents": [{"code": "KR15E", "vol": 850}, {"code": "KR15S", "vol": 400}]},
            16: {"name": "Iron (Dissolved)", "reagents": [{"code": "KR16E1", "vol": 1000}, {"code": "KR16E2", "vol": 1000}, {"code": "KR16E3", "vol": 1000}, {"code": "KR16E4", "vol": 1000}]}
        }

    def calculate_tests(self, volume_ul: float, capacity_ml: int) -> int:
        """Calculate number of tests possible for a given reagent volume and chamber capacity"""
        return int((capacity_ml * 1000) / volume_ul)

    def optimize_tray_configuration(self, selected_experiments):
        best_configuration = None
        best_tray_life = 0
        
        def get_location_capacity(loc):
            return 270 if loc < 4 else 140

        def calculate_experiment_tests(exp_placements):
            """Calculate total tests possible for an experiment given its reagent placements"""
            reagent_totals = {}
            for placement in exp_placements:
                reagent_code = placement["reagent_code"]
                if reagent_code not in reagent_totals:
                    reagent_totals[reagent_code] = 0
                reagent_totals[reagent_code] += placement["tests"]
            return min(reagent_totals.values())

        def try_configuration(remaining_locs, exp_configs=None, used_locs=None):
            nonlocal best_configuration, best_tray_life
            
            if exp_configs is None:
                exp_configs = {exp: {"placements": [], "sets": []} for exp in selected_experiments}
            if used_locs is None:
                used_locs = set()

            # Base case: all locations filled
            if not remaining_locs:
                # Calculate tests for each experiment
                experiment_tests = {}
                for exp_num, config in exp_configs.items():
                    total_tests = calculate_experiment_tests(config["placements"])
                    experiment_tests[exp_num] = total_tests

                # Calculate tray life (minimum tests across all experiments)
                tray_life = min(experiment_tests.values())
                
                if tray_life > best_tray_life:
                    # Convert placements into sets for the result format
                    final_config = {
                        "tray_locations": [None] * 16,
                        "results": {}
                    }
                    
                    for exp_num, config in exp_configs.items():
                        exp_sets = self.group_placements_into_sets(config["placements"])
                        final_config["results"][exp_num] = {
                            "name": self.experiment_data[exp_num]["name"],
                            "sets": exp_sets,
                            "total_tests": experiment_tests[exp_num]
                        }
                        
                        # Fill tray_locations
                        for placement in config["placements"]:
                            final_config["tray_locations"][placement["location"]] = {
                                "reagent_code": placement["reagent_code"],
                                "experiment": exp_num,
                                "tests_possible": placement["tests"],
                                "volume_per_test": placement["volume"],
                                "capacity": get_location_capacity(placement["location"])
                            }
                    
                    best_configuration = final_config
                    best_tray_life = tray_life
                return

            # Try placing reagents from each experiment in the next available location
            current_loc = min(remaining_locs)
            capacity = get_location_capacity(current_loc)

            for exp_num in selected_experiments:
                experiment = self.experiment_data[exp_num]
                
                # Try each reagent from this experiment
                for reagent in experiment["reagents"]:
                    # Calculate tests possible in this location
                    tests = self.calculate_tests(reagent["vol"], capacity)
                    
                    # Add placement
                    new_placement = {
                        "reagent_code": reagent["code"],
                        "location": current_loc,
                        "tests": tests,
                        "volume": reagent["vol"]
                    }
                    
                    exp_configs[exp_num]["placements"].append(new_placement)
                    new_remaining = remaining_locs - {current_loc}
                    
                    # Recursive call
                    try_configuration(new_remaining, exp_configs, used_locs | {current_loc})
                    
                    # Remove placement (backtrack)
                    exp_configs[exp_num]["placements"].pop()

        # Start optimization with all locations available
        try_configuration(set(range(16)))
        return best_configuration

    def group_placements_into_sets(self, placements):
        """Group placements into sets based on location proximity and capacity"""
        if not placements:
            return []
            
        sets = []
        current_set = []
        current_capacity = None
        
        sorted_placements = sorted(placements, key=lambda p: p["location"])
        
        for placement in sorted_placements:
            loc = placement["location"]
            cap = 270 if loc < 4 else 140
            
            if current_capacity is None:
                current_capacity = cap
                
            if cap != current_capacity or (current_set and loc > current_set[-1]["location"] + 1):
                # Start new set
                if current_set:
                    sets.append({
                        "placements": current_set.copy(),
                        "tests_per_set": min(p["tests"] for p in current_set)
                    })
                current_set = []
                current_capacity = cap
                
            current_set.append(placement)
            
        # Add final set
        if current_set:
            sets.append({
                "placements": current_set,
                "tests_per_set": min(p["tests"] for p in current_set)
            })
            
        return sets

    def get_available_experiments(self):
        return [{"id": id_, "name": exp["name"]} 
                for id_, exp in self.experiment_data.items()]
