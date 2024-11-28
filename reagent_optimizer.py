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

    def get_experiment_max_volume(self, exp_num):
        """Get the maximum reagent volume for an experiment"""
        return max(r["vol"] for r in self.experiment_data[exp_num]["reagents"])

    def get_volume_sorted_experiments(self, selected_experiments):
        """Sort experiments by their highest volume reagent"""
        return sorted(
            selected_experiments,
            key=lambda exp: self.get_experiment_max_volume(exp),
            reverse=True
        )

    def get_reagent_sets(self, exp_num):
        """Get all reagents for an experiment as a set"""
        experiment = self.experiment_data[exp_num]
        return sorted(experiment["reagents"], key=lambda r: r["vol"], reverse=True)

    def optimize_tray_configuration(self, selected_experiments):
        """Optimize tray configuration considering volume requirements and maximizing minimum tests"""
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

            # Sort experiments by volume requirements
            volume_sorted_experiments = self.get_volume_sorted_experiments(selected_experiments)
            
            # Initialize configuration
            best_configuration = None
            best_tray_life = 0
            
            def try_configuration(remaining_270ml, remaining_140ml, config=None, used_exps=None):
                nonlocal best_configuration, best_tray_life
                
                if config is None:
                    config = {
                        "tray_locations": [None] * self.MAX_LOCATIONS,
                        "results": {}
                    }
                if used_exps is None:
                    used_exps = set()

                # If all locations are filled, evaluate configuration
                if not remaining_270ml and not remaining_140ml:
                    tray_life = min(
                        result["total_tests"] 
                        for result in config["results"].values()
                    )
                    if tray_life > best_tray_life:
                        best_tray_life = tray_life
                        best_configuration = {
                            "tray_locations": config["tray_locations"].copy(),
                            "results": {k: v.copy() for k, v in config["results"].items()}
                        }
                    return

                # Try placing each experiment's reagents
                for exp_num in volume_sorted_experiments:
                    if exp_num in used_exps:
                        continue

                    experiment = self.experiment_data[exp_num]
                    reagents = experiment["reagents"]
                    num_reagents = len(reagents)

                    # Check if we have enough locations
                    available_270 = len(remaining_270ml)
                    available_140 = len(remaining_140ml)
                    
                    if available_270 + available_140 < num_reagents:
                        continue

                    # Try different combinations of 270mL and 140mL locations
                    for use_270 in range(min(available_270 + 1, num_reagents + 1)):
                        use_140 = num_reagents - use_270
                        if use_140 > available_140:
                            continue

                        # Get locations to use
                        locs_270 = remaining_270ml[:use_270]
                        locs_140 = remaining_140ml[:use_140]
                        locations = sorted(locs_270 + locs_140)

                        # Calculate tests possible
                        placements = []
                        min_tests = float('inf')
                        
                        for i, reagent in enumerate(reagents):
                            loc = locations[i]
                            capacity = 270 if loc < 4 else 140
                            tests = self.calculate_tests(reagent["vol"], capacity)
                            min_tests = min(min_tests, tests)
                            
                            placements.append({
                                "reagent_code": reagent["code"],
                                "location": loc,
                                "tests": tests,
                                "volume": reagent["vol"]
                            })

                        # Update configuration
                        new_config = {
                            "tray_locations": config["tray_locations"].copy(),
                            "results": config["results"].copy()
                        }

                        for placement in placements:
                            loc = placement["location"]
                            new_config["tray_locations"][loc] = {
                                "reagent_code": placement["reagent_code"],
                                "experiment": exp_num,
                                "tests_possible": placement["tests"],
                                "volume_per_test": placement["volume"],
                                "capacity": 270 if loc < 4 else 140
                            }

                        if exp_num not in new_config["results"]:
                            new_config["results"][exp_num] = {
                                "name": experiment["name"],
                                "sets": [],
                                "total_tests": 0
                            }
                        
                        new_config["results"][exp_num]["sets"].append({
                            "placements": placements,
                            "tests_per_set": min_tests
                        })
                        new_config["results"][exp_num]["total_tests"] = min_tests

                        # Recursive call with remaining locations
                        new_270 = [loc for loc in remaining_270ml if loc not in locs_270]
                        new_140 = [loc for loc in remaining_140ml if loc not in locs_140]
                        try_configuration(new_270, new_140, new_config, used_exps | {exp_num})

            # Start optimization with all locations available
            try_configuration(list(range(4)), list(range(4, 16)))

            if not best_configuration:
                raise ValueError("Could not find a valid configuration")

            return best_configuration

        except Exception as e:
            raise ValueError(str(e))

    def get_available_experiments(self):
        """Get list of available experiments"""
        return [{"id": id_, "name": exp["name"]} 
                for id_, exp in self.experiment_data.items()]
