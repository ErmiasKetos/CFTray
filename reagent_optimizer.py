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
        """Find optimal configuration maximizing tray life"""
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

            # Sort experiments by reagent volume requirements
            sorted_experiments = sorted(
                selected_experiments,
                key=lambda x: max(r["vol"] for r in self.experiment_data[x]["reagents"]),
                reverse=True
            )

            # Initialize best configuration tracking
            best_configuration = None
            best_tray_life = 0
            
            def get_exp_tests(exp_placements):
                """Calculate total tests for an experiment's placements"""
                reagent_tests = {}
                for placement in exp_placements:
                    code = placement["reagent_code"]
                    if code not in reagent_tests:
                        reagent_tests[code] = 0
                    reagent_tests[code] += placement["tests"]
                return min(reagent_tests.values())

            def try_configuration(remaining_270, remaining_140, config=None):
                nonlocal best_configuration, best_tray_life
                
                if config is None:
                    config = {
                        "tray_locations": [None] * self.MAX_LOCATIONS,
                        "results": {}
                    }

                # If all locations used, evaluate configuration
                if not remaining_270 and not remaining_140:
                    tray_life = min(
                        result["total_tests"] 
                        for result in config["results"].values()
                    )
                    if tray_life > best_tray_life:
                        best_tray_life = tray_life
                        best_configuration = {
                            "tray_locations": config["tray_locations"].copy(),
                            "results": {
                                k: {
                                    "name": v["name"],
                                    "sets": [s.copy() for s in v["sets"]],
                                    "total_tests": v["total_tests"]
                                }
                                for k, v in config["results"].items()
                            }
                        }
                    return

                # Try each experiment that hasn't been fully placed
                for exp_num in sorted_experiments:
                    if exp_num not in config["results"]:
                        exp = self.experiment_data[exp_num]
                        num_reagents = len(exp["reagents"])

                        # Try placing in 270mL locations
                        if len(remaining_270) >= num_reagents:
                            placements = []
                            locations = remaining_270[:num_reagents]
                            
                            for i, reagent in enumerate(exp["reagents"]):
                                tests = self.calculate_tests(reagent["vol"], 270)
                                placements.append({
                                    "reagent_code": reagent["code"],
                                    "location": locations[i],
                                    "tests": tests,
                                    "volume": reagent["vol"]
                                })

                            # Create new configuration with this placement
                            new_config = {
                                "tray_locations": config["tray_locations"].copy(),
                                "results": config["results"].copy()
                            }
                            
                            for placement in placements:
                                new_config["tray_locations"][placement["location"]] = {
                                    "reagent_code": placement["reagent_code"],
                                    "experiment": exp_num,
                                    "tests_possible": placement["tests"],
                                    "volume_per_test": placement["volume"],
                                    "capacity": 270
                                }
                            
                            new_config["results"][exp_num] = {
                                "name": exp["name"],
                                "sets": [{
                                    "placements": placements,
                                    "tests_per_set": min(p["tests"] for p in placements)
                                }],
                                "total_tests": min(p["tests"] for p in placements)
                            }
                            
                            # Recursive call with remaining locations
                            try_configuration(
                                [loc for loc in remaining_270 if loc not in locations],
                                remaining_140,
                                new_config
                            )

                        # Try placing in 140mL locations
                        if len(remaining_140) >= num_reagents:
                            placements = []
                            locations = remaining_140[:num_reagents]
                            
                            for i, reagent in enumerate(exp["reagents"]):
                                tests = self.calculate_tests(reagent["vol"], 140)
                                placements.append({
                                    "reagent_code": reagent["code"],
                                    "location": locations[i],
                                    "tests": tests,
                                    "volume": reagent["vol"]
                                })

                            new_config = {
                                "tray_locations": config["tray_locations"].copy(),
                                "results": config["results"].copy()
                            }
                            
                            for placement in placements:
                                new_config["tray_locations"][placement["location"]] = {
                                    "reagent_code": placement["reagent_code"],
                                    "experiment": exp_num,
                                    "tests_possible": placement["tests"],
                                    "volume_per_test": placement["volume"],
                                    "capacity": 140
                                }
                            
                            new_config["results"][exp_num] = {
                                "name": exp["name"],
                                "sets": [{
                                    "placements": placements,
                                    "tests_per_set": min(p["tests"] for p in placements)
                                }],
                                "total_tests": min(p["tests"] for p in placements)
                            }
                            
                            try_configuration(
                                remaining_270,
                                [loc for loc in remaining_140 if loc not in locations],
                                new_config
                            )
                    else:
                        # Try adding another set of this experiment
                        exp = self.experiment_data[exp_num]
                        num_reagents = len(exp["reagents"])

                        # Try 270mL locations for additional set
                        if len(remaining_270) >= num_reagents:
                            placements = []
                            locations = remaining_270[:num_reagents]
                            
                            for i, reagent in enumerate(exp["reagents"]):
                                tests = self.calculate_tests(reagent["vol"], 270)
                                placements.append({
                                    "reagent_code": reagent["code"],
                                    "location": locations[i],
                                    "tests": tests,
                                    "volume": reagent["vol"]
                                })

                            new_config = {
                                "tray_locations": config["tray_locations"].copy(),
                                "results": {
                                    k: {
                                        "name": v["name"],
                                        "sets": [s.copy() for s in v["sets"]],
                                        "total_tests": v["total_tests"]
                                    }
                                    for k, v in config["results"].items()
                                }
                            }
                            
                            for placement in placements:
                                new_config["tray_locations"][placement["location"]] = {
                                    "reagent_code": placement["reagent_code"],
                                    "experiment": exp_num,
                                    "tests_possible": placement["tests"],
                                    "volume_per_test": placement["volume"],
                                    "capacity": 270
                                }
                            
                            new_config["results"][exp_num]["sets"].append({
                                "placements": placements,
                                "tests_per_set": min(p["tests"] for p in placements)
                            })
                            new_config["results"][exp_num]["total_tests"] += min(p["tests"] for p in placements)
                            
                            try_configuration(
                                [loc for loc in remaining_270 if loc not in locations],
                                remaining_140,
                                new_config
                            )

                        # Try 140mL locations for additional set
                        if len(remaining_140) >= num_reagents:
                            placements = []
                            locations = remaining_140[:num_reagents]
                            
                            for i, reagent in enumerate(exp["reagents"]):
                                tests = self.calculate_tests(reagent["vol"], 140)
                                placements.append({
                                    "reagent_code": reagent["code"],
                                    "location": locations[i],
                                    "tests": tests,
                                    "volume": reagent["vol"]
                                })

                            new_config = {
                                "tray_locations": config["tray_locations"].copy(),
                                "results": {
                                    k: {
                                        "name": v["name"],
                                        "sets": [s.copy() for s in v["sets"]],
                                        "total_tests": v["total_tests"]
                                    }
                                    for k, v in config["results"].items()
                                }
                            }
                            
                            for placement in placements:
                                new_config["tray_locations"][placement["location"]] = {
                                    "reagent_code": placement["reagent_code"],
                                    "experiment": exp_num,
                                    "tests_possible": placement["tests"],
                                    "volume_per_test": placement["volume"],
                                    "capacity": 140
                                }
                            
                            new_config["results"][exp_num]["sets"].append({
                                "placements": placements,
                                "tests_per_set": min(p["tests"] for p in placements)
                            })
                            new_config["results"][exp_num]["total_tests"] += min(p["tests"] for p in placements)
                            
                            try_configuration(
                                remaining_270,
                                [loc for loc in remaining_140 if loc not in locations],
                                new_config
                            )

            # Start optimization with all locations available
            try_configuration(list(range(4)), list(range(4, 16)))

            if not best_configuration:
                raise ValueError("Could not find a valid configuration")

            return best_configuration

        except Exception as e:
            raise ValueError(str(e))

    def get_available_experiments(self):
        return [{"id": id_, "name": exp["name"]} 
                for id_, exp in self.experiment_data.items()]
