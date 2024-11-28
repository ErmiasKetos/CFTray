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

    def calculate_tests(self, volume_ul, capacity_ml):
        return int((capacity_ml * 1000) / volume_ul)

    def get_experiment_max_vol(self, exp_num):
        return max(r["vol"] for r in self.experiment_data[exp_num]["reagents"])

    def place_reagent_set(self, exp_num, locations, config):
        """Place a complete set of reagents in specified locations"""
        exp = self.experiment_data[exp_num]
        placements = []
        
        for i, reagent in enumerate(exp["reagents"]):
            loc = locations[i]
            capacity = 270 if loc < 4 else 140
            tests = self.calculate_tests(reagent["vol"], capacity)
            
            placement = {
                "reagent_code": reagent["code"],
                "location": loc,
                "tests": tests,
                "volume": reagent["vol"]
            }
            placements.append(placement)
            
            config["tray_locations"][loc] = {
                "reagent_code": reagent["code"],
                "experiment": exp_num,
                "tests_possible": tests,
                "volume_per_test": reagent["vol"],
                "capacity": capacity
            }
            
        return placements

    def optimize_tray_configuration(self, selected_experiments):
        try:
            # Validate total chambers needed
            total_chambers = sum(len(self.experiment_data[exp]["reagents"]) for exp in selected_experiments)
            if total_chambers > self.MAX_LOCATIONS:
                details = [
                    f"{self.experiment_data[exp]['name']}: {len(self.experiment_data[exp]['reagents'])} chambers" 
                    for exp in selected_experiments
                ]
                raise ValueError(
                    f"Configuration cannot be made. Total required chambers: {total_chambers}\n"
                    f"Available chambers: {self.MAX_LOCATIONS}\n\n"
                    f"Chamber requirements:\n" + "\n".join(details) + "\n\n"
                    f"Please remove some experiments from the list."
                )

            # Initialize configuration
            config = {
                "tray_locations": [None] * self.MAX_LOCATIONS,
                "results": {}
            }

            # Sort experiments by volume requirements
            sorted_experiments = sorted(
                selected_experiments,
                key=lambda x: (
                    self.get_experiment_max_vol(x),
                    len(self.experiment_data[x]["reagents"])
                ),
                reverse=True
            )

            # Initialize results for all experiments
            for exp_num in sorted_experiments:
                config["results"][exp_num] = {
                    "name": self.experiment_data[exp_num]["name"],
                    "sets": [],
                    "total_tests": 0
                }

            available_locations = set(range(self.MAX_LOCATIONS))

            # First pass: Place primary sets for each experiment
            for exp_num in sorted_experiments:
                exp = self.experiment_data[exp_num]
                num_reagents = len(exp["reagents"])

                # Try to use 270mL locations first if beneficial
                available_270 = sorted([loc for loc in available_locations if loc < 4])
                if len(available_270) >= num_reagents and max(r["vol"] for r in exp["reagents"]) > 800:
                    locations = available_270[:num_reagents]
                    placements = self.place_reagent_set(exp_num, locations, config)
                    min_tests = min(p["tests"] for p in placements)
                    
                    config["results"][exp_num]["sets"].append({
                        "placements": placements,
                        "tests_per_set": min_tests
                    })
                    config["results"][exp_num]["total_tests"] += min_tests
                    
                    for loc in locations:
                        available_locations.remove(loc)

            # Second pass: Fill remaining locations with additional sets
            while available_locations:
                best_addition = None
                best_exp = None
                best_tests = 0

                for exp_num in sorted_experiments:
                    exp = self.experiment_data[exp_num]
                    num_reagents = len(exp["reagents"])
                    
                    # Find consecutive available locations
                    avail_list = sorted(list(available_locations))
                    for i in range(len(avail_list) - num_reagents + 1):
                        locations = avail_list[i:i + num_reagents]
                        if max(j - i for i, j in zip(locations[:-1], locations[1:])) == 1:
                            # Calculate tests possible
                            min_tests = float('inf')
                            for j, reagent in enumerate(exp["reagents"]):
                                loc = locations[j]
                                capacity = 270 if loc < 4 else 140
                                tests = self.calculate_tests(reagent["vol"], capacity)
                                min_tests = min(min_tests, tests)
                            
                            if min_tests > best_tests:
                                best_tests = min_tests
                                best_exp = exp_num
                                best_addition = locations

                if best_addition:
                    placements = self.place_reagent_set(best_exp, best_addition, config)
                    config["results"][best_exp]["sets"].append({
                        "placements": placements,
                        "tests_per_set": best_tests
                    })
                    config["results"][best_exp]["total_tests"] += best_tests
                    
                    for loc in best_addition:
                        available_locations.remove(loc)
                else:
                    break

            # Verify all locations are filled
            if any(loc is None for loc in config["tray_locations"]):
                raise ValueError("Could not fill all locations")

            return config

        except Exception as e:
            raise ValueError(str(e))

    def get_available_experiments(self):
        return [{"id": id_, "name": exp["name"]} 
                for id_, exp in self.experiment_data.items()]
