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
        """Calculate number of tests possible for a given reagent volume and chamber capacity"""
        return int((capacity_ml * 1000) / volume_ul)

    def optimize_tray_configuration(self, selected_experiments):
        try:
            # Validate total required chambers
            total_chambers = sum(len(self.experiment_data[exp]["reagents"]) for exp in selected_experiments)
            if total_chambers > self.MAX_LOCATIONS:
                details = [f"{self.experiment_data[exp]['name']}: {len(self.experiment_data[exp]['reagents'])} chambers" 
                          for exp in selected_experiments]
                raise ValueError(
                    f"Configuration cannot be made. Total required chambers: {total_chambers}\n"
                    f"Available chambers: {self.MAX_LOCATIONS}\n\n"
                    f"Chamber requirements:\n" + "\n".join(details) + "\n\n"
                    f"Please remove some experiments from the list."
                )

            # Initialize configuration
            tray_locations = [None] * self.MAX_LOCATIONS
            results = {}
            available_locations = list(range(self.MAX_LOCATIONS))

            # Place Iron first (4 reagents) if it's in the selection
            if 16 in selected_experiments:
                iron_config = self._place_iron_experiment(available_locations, tray_locations)
                if iron_config:
                    results[16] = iron_config['results']
                    available_locations = [loc for loc in available_locations if tray_locations[loc] is None]

            # Place other experiments
            remaining_exps = [exp for exp in selected_experiments if exp != 16]
            for exp_num in remaining_exps:
                exp_config = self._place_other_experiment(exp_num, available_locations, tray_locations)
                if exp_config:
                    results[exp_num] = exp_config['results']
                    available_locations = [loc for loc in available_locations if tray_locations[loc] is None]

            # Fill remaining locations with additional sets
            while available_locations:
                best_addition = self._find_best_additional_set(available_locations, selected_experiments, tray_locations)
                if not best_addition:
                    break
                    
                exp_num = best_addition['experiment']
                for placement in best_addition['placements']:
                    loc = placement['location']
                    tray_locations[loc] = {
                        "reagent_code": placement['reagent_code'],
                        "experiment": exp_num,
                        "tests_possible": placement['tests'],
                        "volume_per_test": placement['volume'],
                        "capacity": 270 if loc < 4 else 140
                    }
                    available_locations.remove(loc)
                
                if exp_num not in results:
                    results[exp_num] = {
                        "name": self.experiment_data[exp_num]["name"],
                        "sets": [],
                        "total_tests": 0
                    }
                results[exp_num]["sets"].append({
                    "placements": best_addition['placements'],
                    "tests_per_set": best_addition['tests_per_set']
                })
                results[exp_num]["total_tests"] += best_addition['tests_per_set']

            # Return complete configuration
            return {
                "tray_locations": tray_locations,
                "results": results
            }

        except Exception as e:
            raise ValueError(str(e))

    def _place_iron_experiment(self, available_locations, tray_locations):
        """Place Iron experiment reagents optimally"""
        large_locs = [loc for loc in available_locations if loc < 4]
        if len(large_locs) >= 4:
            experiment = self.experiment_data[16]
            placements = []
            for i, reagent in enumerate(experiment["reagents"]):
                loc = large_locs[i]
                tests = self.calculate_tests(reagent["vol"], 270)
                placements.append({
                    "reagent_code": reagent["code"],
                    "location": loc,
                    "tests": tests,
                    "volume": reagent["vol"]
                })
                tray_locations[loc] = {
                    "reagent_code": reagent["code"],
                    "experiment": 16,
                    "tests_possible": tests,
                    "volume_per_test": reagent["vol"],
                    "capacity": 270
                }
            return {
                "results": {
                    "name": experiment["name"],
                    "sets": [{
                        "placements": placements,
                        "tests_per_set": 270
                    }],
                    "total_tests": 270
                }
            }
        return None

    def _place_other_experiment(self, exp_num, available_locations, tray_locations):
        """Place non-Iron experiments optimally"""
        experiment = self.experiment_data[exp_num]
        num_reagents = len(experiment["reagents"])
        
        # Find best locations for this experiment
        best_locations = []
        best_tests = 0
        
        # Try different location combinations
        for i in range(len(available_locations) - num_reagents + 1):
            locations = available_locations[i:i + num_reagents]
            min_tests = float('inf')
            for j, reagent in enumerate(experiment["reagents"]):
                loc = locations[j]
                capacity = 270 if loc < 4 else 140
                tests = self.calculate_tests(reagent["vol"], capacity)
                min_tests = min(min_tests, tests)
            
            if min_tests > best_tests:
                best_tests = min_tests
                best_locations = locations
        
        if best_locations:
            placements = []
            for i, reagent in enumerate(experiment["reagents"]):
                loc = best_locations[i]
                capacity = 270 if loc < 4 else 140
                tests = self.calculate_tests(reagent["vol"], capacity)
                placements.append({
                    "reagent_code": reagent["code"],
                    "location": loc,
                    "tests": tests,
                    "volume": reagent["vol"]
                })
                tray_locations[loc] = {
                    "reagent_code": reagent["code"],
                    "experiment": exp_num,
                    "tests_possible": tests,
                    "volume_per_test": reagent["vol"],
                    "capacity": capacity
                }
            return {
                "results": {
                    "name": experiment["name"],
                    "sets": [{
                        "placements": placements,
                        "tests_per_set": best_tests
                    }],
                    "total_tests": best_tests
                }
            }
        return None

    def _find_best_additional_set(self, available_locations, selected_experiments, tray_locations):
        """Find best experiment set to place in remaining locations"""
        best_addition = None
        best_tests = 0
        
        for exp_num in selected_experiments:
            experiment = self.experiment_data[exp_num]
            num_reagents = len(experiment["reagents"])
            
            if len(available_locations) >= num_reagents:
                # Try placing this experiment's reagents
                placements = []
                min_tests = float('inf')
                
                for i, reagent in enumerate(experiment["reagents"][:num_reagents]):
                    loc = available_locations[i]
                    capacity = 270 if loc < 4 else 140
                    tests = self.calculate_tests(reagent["vol"], capacity)
                    placements.append({
                        "reagent_code": reagent["code"],
                        "location": loc,
                        "tests": tests,
                        "volume": reagent["vol"]
                    })
                    min_tests = min(min_tests, tests)
                
                if min_tests > best_tests:
                    best_tests = min_tests
                    best_addition = {
                        "experiment": exp_num,
                        "placements": placements,
                        "tests_per_set": min_tests
                    }
        
        return best_addition

    def get_available_experiments(self):
        """Get list of available experiments"""
        return [{"id": id_, "name": exp["name"]} 
                for id_, exp in self.experiment_data.items()]
