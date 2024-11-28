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
        
        self.MAX_LOCATIONS = 16

    def validate_experiment_selection(self, selected_experiments):
        """
        Validate if the selected experiments can fit in the tray
        Returns (bool, str): (is_valid, error_message)
        """
        total_chambers = 0
        chamber_details = []
        
        for exp_num in selected_experiments:
            num_chambers = len(self.experiment_data[exp_num]["reagents"])
            total_chambers += num_chambers
            chamber_details.append(
                f"{self.experiment_data[exp_num]['name']}: {num_chambers} chambers"
            )

        if total_chambers > self.MAX_LOCATIONS:
            error_msg = (
                f"Configuration cannot be made. Total required chambers: {total_chambers}\n"
                f"Available chambers: {self.MAX_LOCATIONS}\n\n"
                f"Chamber requirements:\n" + "\n".join(chamber_details) + "\n\n"
                f"Please remove some experiments from the list."
            )
            return False, error_msg

        return True, None

    def calculate_tests(self, volume_ul, capacity_ml):
        return int((capacity_ml * 1000) / volume_ul)

    def get_location_capacity(self, location):
        return 270 if location < 4 else 140

    def evaluate_configuration_life(self, configuration):
        """Calculate tray life (minimum total tests across all experiments)"""
        if not configuration or "results" not in configuration:
            return 0
        return min(result["total_tests"] for result in configuration["results"].values())

    def generate_location_partitions(self, selected_experiments):
        """Generate possible ways to partition tray locations among experiments"""
        from itertools import permutations
        
        # Get base requirements for each experiment
        exp_requirements = {
            exp_num: len(self.experiment_data[exp_num]["reagents"])
            for exp_num in selected_experiments
        }
        
        # Generate different orderings of experiments
        partitions = []
        for exp_order in permutations(selected_experiments):
            # Try different arrangements of 270mL vs 140mL locations
            current_partition = []
            available_270 = list(range(4))
            available_140 = list(range(4, 16))
            
            for exp_num in exp_order:
                req_chambers = exp_requirements[exp_num]
                
                # Try using 270mL locations first if available
                if len(available_270) >= req_chambers:
                    locations = available_270[:req_chambers]
                    available_270 = available_270[req_chambers:]
                    current_partition.append((exp_num, locations))
                    continue
                
                # Then try 140mL locations
                if len(available_140) >= req_chambers:
                    locations = available_140[:req_chambers]
                    available_140 = available_140[req_chambers:]
                    current_partition.append((exp_num, locations))
                    continue
                
                # Try mix of both if needed
                total_available = available_270 + available_140
                if len(total_available) >= req_chambers:
                    locations = total_available[:req_chambers]
                    for loc in locations:
                        if loc < 4:
                            available_270.remove(loc)
                        else:
                            available_140.remove(loc)
                    current_partition.append((exp_num, locations))
            
            if len(current_partition) == len(selected_experiments):
                partitions.append(current_partition)
        
        return partitions

    def create_configuration(self, selected_experiments, partition):
        tray_locations = [None] * self.MAX_LOCATIONS
        results = {}
        
        # First place primary sets as before
        # ... (existing primary set placement code)
        
        # Then identify and fill empty locations
        empty_locations = [i for i, loc in enumerate(tray_locations) if loc is None]
        
        while empty_locations:
            # Try to fit the largest possible set from any experiment
            best_fill = None
            for exp_num in selected_experiments:
                exp = self.experiment_data[exp_num]
                num_reagents = len(exp["reagents"])
                
                if len(empty_locations) >= num_reagents:
                    # Calculate tests possible for this placement
                    locations = empty_locations[:num_reagents]
                    placements = []
                    for reagent, loc in zip(exp["reagents"], locations):
                        capacity = self.get_location_capacity(loc)
                        tests = self.calculate_tests(reagent["vol"], capacity)
                        placements.append({
                            "reagent_code": reagent["code"],
                            "location": loc,
                            "tests": tests,
                            "volume": reagent["vol"]
                        })
                    
                    set_tests = min(p["tests"] for p in placements)
                    
                    if best_fill is None or set_tests > best_fill["tests"]:
                        best_fill = {
                            "experiment": exp_num,
                            "placements": placements,
                            "tests": set_tests,
                            "locations": locations
                        }
            
            if best_fill:
                # Apply the best fill option
                for placement in best_fill["placements"]:
                    loc = placement["location"]
                    tray_locations[loc] = {
                        "reagent_code": placement["reagent_code"],
                        "experiment": best_fill["experiment"],
                        "tests_possible": placement["tests"],
                        "volume_per_test": placement["volume"],
                        "capacity": self.get_location_capacity(loc)
                    }
                    
                    # Add to experiment results
                    if "sets" not in results[best_fill["experiment"]]:
                        results[best_fill["experiment"]]["sets"] = []
                    results[best_fill["experiment"]]["sets"].append({
                        "placements": best_fill["placements"],
                        "tests_per_set": best_fill["tests"]
                    })
                    results[best_fill["experiment"]]["total_tests"] += best_fill["tests"]
                
                # Update empty locations
                empty_locations = [i for i, loc in enumerate(tray_locations) if loc is None]
            else:
                break
        
        # Verify no empty locations
        if any(loc is None for loc in tray_locations):
            return None
        
        return {
            "tray_locations": tray_locations,
            "results": results
        }
    def optimize_tray_configuration(self, selected_experiments):
        """Find optimal configuration maximizing tray life"""
        # First validate the experiment selection
        is_valid, error_message = self.validate_experiment_selection(selected_experiments)
        if not is_valid:
            raise ValueError(error_message)

        best_configuration = None
        best_tray_life = 0
        
        # Generate and try different partitions
        partitions = self.generate_location_partitions(selected_experiments)
        
        for partition in partitions:
            config = self.create_configuration(selected_experiments, partition)
            tray_life = self.evaluate_configuration_life(config)
            
            if tray_life > best_tray_life:
                best_tray_life = tray_life
                best_configuration = config

        if not best_configuration:
            raise ValueError("Could not find a valid configuration")

        return best_configuration

    def get_available_experiments(self):
        return [{"id": id_, "name": exp["name"]} 
                for id_, exp in self.experiment_data.items()]
