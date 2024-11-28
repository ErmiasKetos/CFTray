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

    def calculate_tests(self, reagent_volume, chamber_capacity):
        return int((chamber_capacity * 1000) / reagent_volume)

    def get_total_volume_per_test(self, experiment):
        return sum(r["vol"] for r in experiment["reagents"])

    def find_optimal_reagent_distribution(self, reagent, available_locations, target_tests):
        locations = []
        total_tests = 0
        remaining_locations = available_locations.copy()

        while total_tests < target_tests and remaining_locations:
            location = remaining_locations[0]
            capacity = 270 if location < 4 else 140
            tests_here = self.calculate_tests(reagent["vol"], capacity)
            
            locations.append({
                "location": location,
                "tests": tests_here,
                "capacity": capacity
            })
            
            total_tests += tests_here
            remaining_locations = remaining_locations[1:]

        return {"locations": locations, "total_tests": total_tests}

    def optimize_tray_configuration(self, selected_experiments):
        # Sort experiments by total volume requirements (descending)
        sorted_experiments = sorted(
            selected_experiments,
            key=lambda x: self.get_total_volume_per_test(self.experiment_data[x]),
            reverse=True
        )

        tray_locations = [None] * 16
        results = {}
        available_locations = list(range(16))

        # Process each experiment
        for exp_num in sorted_experiments:
            experiment = self.experiment_data[exp_num]
            experiment_sets = []
            total_experiment_tests = 0

            # Keep trying to add sets while we have space
            while len(available_locations) >= len(experiment["reagents"]):
                set_config = {
                    "locations": [],
                    "tests_per_set": float('inf')
                }

                # Calculate optimal tests possible for this set
                set_locations = available_locations.copy()
                large_locations_count = sum(1 for loc in set_locations if loc < 4)
                
                # If we have enough large locations for a full set, use them first
                if large_locations_count >= len(experiment["reagents"]):
                    set_config["tests_per_set"] = min(
                        self.calculate_tests(reagent["vol"], 270)
                        for reagent in experiment["reagents"]
                    )
                else:
                    set_config["tests_per_set"] = min(
                        self.calculate_tests(reagent["vol"], 140)
                        for reagent in experiment["reagents"]
                    )

                # Try to place each reagent
                success = True
                temp_locations = []

                for reagent in experiment["reagents"]:
                    distribution = self.find_optimal_reagent_distribution(
                        reagent,
                        set_locations,
                        set_config["tests_per_set"]
                    )

                    if distribution["total_tests"] < set_config["tests_per_set"]:
                        success = False
                        break

                    for loc in distribution["locations"]:
                        temp_locations.append({
                            **loc,
                            "reagent_code": reagent["code"],
                            "reagent_vol": reagent["vol"]
                        })

                    # Remove used locations
                    set_locations = [loc for loc in set_locations 
                                   if loc not in [l["location"] for l in distribution["locations"]]]

                if not success:
                    break

                # Apply the set configuration
                for loc in temp_locations:
                    tray_locations[loc["location"]] = {
                        "reagent_code": loc["reagent_code"],
                        "experiment": exp_num,
                        "tests": loc["tests"],
                        "volume": loc["reagent_vol"],
                        "set_index": len(experiment_sets),
                        "capacity": loc["capacity"]
                    }

                    set_config["locations"].append({
                        "location": loc["location"],
                        "reagent_code": loc["reagent_code"],
                        "tests": loc["tests"]
                    })

                    # Remove from available locations
                    available_locations.remove(loc["location"])

                experiment_sets.append(set_config)
                total_experiment_tests += set_config["tests_per_set"]

            results[exp_num] = {
                "name": experiment["name"],
                "sets": experiment_sets,
                "total_tests": total_experiment_tests
            }

        return {"tray_locations": tray_locations, "results": results}

    def get_available_experiments(self):
        return [{"id": int(id_), "name": exp["name"]} 
                for id_, exp in self.experiment_data.items()]
