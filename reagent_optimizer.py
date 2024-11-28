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

    def calculate_tests(self, volume_ul, capacity_ml):
        return int((capacity_ml * 1000) / volume_ul)

    def calculate_total_volume_per_test(self, experiment):
        return sum(r["vol"] for r in experiment["reagents"])

    def get_available_locations(self, used_locations):
        """Get available locations sorted by capacity (270mL first, then 140mL)"""
        all_locations = set(range(16))
        available = sorted(list(all_locations - set(used_locations)))
        return {
            '270': [loc for loc in available if loc < 4],
            '140': [loc for loc in available if loc >= 4]
        }

    def optimize_tray_configuration(self, selected_experiments):
        tray_locations = [None] * 16
        results = {}
        used_locations = set()

        # Sort experiments by total volume and number of reagents (descending)
        sorted_experiments = sorted(
            selected_experiments,
            key=lambda x: (
                self.calculate_total_volume_per_test(self.experiment_data[x]),
                len(self.experiment_data[x]["reagents"])
            ),
            reverse=True
        )

        for exp_num in sorted_experiments:
            experiment = self.experiment_data[exp_num]
            available_locs = self.get_available_locations(used_locations)
            result = self.optimize_single_experiment(
                exp_num, experiment, available_locs, tray_locations, used_locations
            )
            results[exp_num] = result

        return {
            "tray_locations": tray_locations,
            "results": results
        }

    def optimize_single_experiment(self, exp_num, experiment, available_locs, tray_locations, used_locations):
        result = {
            "name": experiment["name"],
            "sets": [],
            "total_tests": 0
        }

        num_reagents = len(experiment["reagents"])
        remaining_270 = available_locs['270']
        remaining_140 = available_locs['140']

        # Try to place first set in 270mL locations if possible and if high-volume experiment
        if len(remaining_270) >= num_reagents and self.calculate_total_volume_per_test(experiment) >= 3000:
            set_locations = remaining_270[:num_reagents]
            set_info = self.place_reagent_set(
                exp_num, experiment, set_locations, 270,
                tray_locations, used_locations, set_number=1
            )
            result["sets"].append(set_info)
            result["total_tests"] += set_info["tests_per_set"]

        # Place additional sets in 140mL locations while possible
        current_set = len(result["sets"]) + 1
        while len(remaining_140) >= num_reagents:
            set_locations = remaining_140[:num_reagents]
            set_info = self.place_reagent_set(
                exp_num, experiment, set_locations, 140,
                tray_locations, used_locations, set_number=current_set
            )
            result["sets"].append(set_info)
            result["total_tests"] += set_info["tests_per_set"]
            current_set += 1
            remaining_140 = [loc for loc in remaining_140 if loc not in set_locations]

        # For experiments like Copper that need multiple locations per reagent
        if not result["sets"] and len(experiment["reagents"]) == 2:
            result = self.optimize_two_reagent_experiment(
                exp_num, experiment, available_locs,
                tray_locations, used_locations
            )

        return result

    def place_reagent_set(self, exp_num, experiment, locations, capacity, tray_locations, used_locations, set_number):
        set_info = {
            "set_number": set_number,
            "locations": locations,
            "capacity": capacity,
            "placements": [],
            "tests_per_set": float('inf')
        }

        for i, reagent in enumerate(experiment["reagents"]):
            location = locations[i]
            tests = self.calculate_tests(reagent["vol"], capacity)
            
            tray_locations[location] = {
                "reagent_code": reagent["code"],
                "experiment": exp_num,
                "tests_possible": tests,
                "volume_per_test": reagent["vol"],
                "capacity": capacity,
                "set_number": set_number
            }
            
            used_locations.add(location)
            set_info["placements"].append({
                "location": location,
                "reagent_code": reagent["code"],
                "tests": tests
            })
            set_info["tests_per_set"] = min(set_info["tests_per_set"], tests)

        return set_info

    def optimize_two_reagent_experiment(self, exp_num, experiment, available_locs, tray_locations, used_locations):
        result = {
            "name": experiment["name"],
            "sets": [],
            "total_tests": 0
        }

        # Calculate how many locations needed for each reagent
        reagent1, reagent2 = experiment["reagents"]
        available_140 = available_locs['140']
        
        if len(available_140) >= 4:  # Need at least 4 locations
            # Use last location for reagent2 (like KR1S)
            r2_location = available_140[-1]
            r2_tests = self.calculate_tests(reagent2["vol"], 140)
            
            # Use remaining locations for reagent1 (like KR1E)
            r1_locations = available_140[:-1][:3]  # Take up to 3 locations
            r1_tests_per_loc = self.calculate_tests(reagent1["vol"], 140)
            r1_total_tests = r1_tests_per_loc * len(r1_locations)
            
            # Place reagents
            for loc in r1_locations:
                tray_locations[loc] = {
                    "reagent_code": reagent1["code"],
                    "experiment": exp_num,
                    "tests_possible": r1_tests_per_loc,
                    "volume_per_test": reagent1["vol"],
                    "capacity": 140,
                    "set_number": 1
                }
                used_locations.add(loc)

            tray_locations[r2_location] = {
                "reagent_code": reagent2["code"],
                "experiment": exp_num,
                "tests_possible": r2_tests,
                "volume_per_test": reagent2["vol"],
                "capacity": 140,
                "set_number": 1
            }
            used_locations.add(r2_location)

            result["sets"].append({
                "set_number": 1,
                "tests_per_set": min(r1_total_tests, r2_tests),
                "placements": [
                    *[{
                        "location": loc,
                        "reagent_code": reagent1["code"],
                        "tests": r1_tests_per_loc
                    } for loc in r1_locations],
                    {
                        "location": r2_location,
                        "reagent_code": reagent2["code"],
                        "tests": r2_tests
                    }
                ]
            })
            result["total_tests"] = min(r1_total_tests, r2_tests)

        return result

    def get_available_experiments(self):
        return [{"id": id_, "name": exp["name"]} 
                for id_, exp in self.experiment_data.items()]
