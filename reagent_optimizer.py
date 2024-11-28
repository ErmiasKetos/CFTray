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

    def get_experiment_reagents(self, exp_num):
        """Get all reagents for an experiment with their volumes"""
        experiment = self.experiment_data[exp_num]
        return [{
            "experiment": exp_num,
            "exp_name": experiment["name"],
            "code": reagent["code"],
            "volume": reagent["vol"],
            "sequence": idx
        } for idx, reagent in enumerate(experiment["reagents"])]

    def get_sorted_reagents(self, selected_experiments):
        """Get all reagents from selected experiments, sorted by volume"""
        all_reagents = []
        for exp_num in selected_experiments:
            all_reagents.extend(self.get_experiment_reagents(exp_num))
        return sorted(all_reagents, key=lambda x: x["volume"], reverse=True)

    def evaluate_configuration(self, config):
        """Calculate minimum tests across all experiments in configuration"""
        if not config["results"]:
            return 0
        return min(result["total_tests"] for result in config["results"].values())

    def optimize_tray_configuration(self, selected_experiments):
        """Optimize tray configuration based on reagent volumes"""
        try:
            # Validate total chambers needed
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
            results = {exp: {
                "name": self.experiment_data[exp]["name"],
                "sets": [],
                "total_tests": 0
            } for exp in selected_experiments}

            # Get sorted reagents by volume
            sorted_reagents = self.get_sorted_reagents(selected_experiments)
            
            # Track available locations
            available_270 = list(range(4))
            available_140 = list(range(4, 16))
            
            # First pass: Place highest volume reagents in best locations
            assigned_exps = set()
            for reagent in sorted_reagents:
                exp_num = reagent["experiment"]
                exp = self.experiment_data[exp_num]
                num_reagents = len(exp["reagents"])
                
                # Skip if we've already handled this experiment
                if exp_num in assigned_exps:
                    continue
                
                # Calculate tests possible in different capacities
                tests_270 = self.calculate_tests(reagent["volume"], 270)
                tests_140 = self.calculate_tests(reagent["volume"], 140)
                
                # Decide where to place this experiment's reagents
                if tests_270 > tests_140 * 1.5 and len(available_270) >= num_reagents:
                    # Place in 270mL locations
                    locations = available_270[:num_reagents]
                    capacity = 270
                    available_270 = available_270[num_reagents:]
                elif len(available_140) >= num_reagents:
                    # Place in 140mL locations
                    locations = available_140[:num_reagents]
                    capacity = 140
                    available_140 = available_140[num_reagents:]
                else:
                    continue
                
                # Place reagents
                placements = []
                for idx, r in enumerate(exp["reagents"]):
                    loc = locations[idx]
                    tests = self.calculate_tests(r["vol"], capacity)
                    placements.append({
                        "reagent_code": r["code"],
                        "location": loc,
                        "tests": tests
                    })
                    tray_locations[loc] = {
                        "reagent_code": r["code"],
                        "experiment": exp_num,
                        "tests_possible": tests,
                        "volume_per_test": r["vol"],
                        "capacity": capacity
                    }
                
                # Record set
                min_tests = min(p["tests"] for p in placements)
                results[exp_num]["sets"].append({
                    "placements": placements,
                    "tests_per_set": min_tests
                })
                results[exp_num]["total_tests"] += min_tests
                assigned_exps.add(exp_num)

            # Second pass: Fill remaining locations with additional sets
            while available_270 or available_140:
                best_addition = None
                best_tests = 0
                best_exp = None
                
                for exp_num in selected_experiments:
                    exp = self.experiment_data[exp_num]
                    num_reagents = len(exp["reagents"])
                    
                    # Try 270mL locations if available
                    if len(available_270) >= num_reagents:
                        locations = available_270[:num_reagents]
                        tests = min(self.calculate_tests(r["vol"], 270) for r in exp["reagents"])
                        if tests > best_tests:
                            best_tests = tests
                            best_exp = exp_num
                            best_addition = (locations, 270)
                    
                    # Try 140mL locations
                    if len(available_140) >= num_reagents:
                        locations = available_140[:num_reagents]
                        tests = min(self.calculate_tests(r["vol"], 140) for r in exp["reagents"])
                        if tests > best_tests:
                            best_tests = tests
                            best_exp = exp_num
                            best_addition = (locations, 140)
                
                if best_addition:
                    locations, capacity = best_addition
                    exp = self.experiment_data[best_exp]
                    placements = []
                    
                    for idx, r in enumerate(exp["reagents"]):
                        loc = locations[idx]
                        tests = self.calculate_tests(r["vol"], capacity)
                        placements.append({
                            "reagent_code": r["code"],
                            "location": loc,
                            "tests": tests
                        })
                        tray_locations[loc] = {
                            "reagent_code": r["code"],
                            "experiment": best_exp,
                            "tests_possible": tests,
                            "volume_per_test": r["vol"],
                            "capacity": capacity
                        }
                    
                    # Update available locations
                    if capacity == 270:
                        available_270 = [loc for loc in available_270 if loc not in locations]
                    else:
                        available_140 = [loc for loc in available_140 if loc not in locations]
                    
                    # Record set
                    results[best_exp]["sets"].append({
                        "placements": placements,
                        "tests_per_set": best_tests
                    })
                    results[best_exp]["total_tests"] += best_tests
                else:
                    break

            return {
                "tray_locations": tray_locations,
                "results": results
            }

        except Exception as e:
            raise ValueError(str(e))

    def get_available_experiments(self):
        return [{"id": id_, "name": exp["name"]} 
                for id_, exp in self.experiment_data.items()]
