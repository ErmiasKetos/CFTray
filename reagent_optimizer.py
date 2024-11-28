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

    def optimize_tray_configuration(self, selected_experiments):
        tray_locations = [None] * 16
        results = {}
        available_locations = list(range(16))
        
        # First, handle high-volume multi-reagent experiments (like Iron)
        high_volume_exps = [exp_num for exp_num in selected_experiments 
                          if len(self.experiment_data[exp_num]["reagents"]) >= 4]
        
        # Then handle other experiments
        remaining_exps = [exp_num for exp_num in selected_experiments 
                         if exp_num not in high_volume_exps]
        
        # Process high-volume experiments first
        for exp_num in high_volume_exps:
            experiment = self.experiment_data[exp_num]
            result = self.optimize_multi_reagent_experiment(
                exp_num, experiment, available_locations, tray_locations
            )
            results[exp_num] = result
            
        # Process remaining experiments
        for exp_num in remaining_exps:
            experiment = self.experiment_data[exp_num]
            if len(experiment["reagents"]) == 2:
                result = self.optimize_two_reagent_experiment(
                    exp_num, experiment, available_locations, tray_locations
                )
                results[exp_num] = result
            
        return {
            "tray_locations": tray_locations,
            "results": results
        }

    def optimize_multi_reagent_experiment(self, exp_num, experiment, available_locations, tray_locations):
        result = {
            "name": experiment["name"],
            "sets": [],
            "total_tests": 0
        }
        
        num_reagents = len(experiment["reagents"])
        
        # Try to place first set in 270mL locations
        large_locs = [loc for loc in available_locations if loc < 4]
        if len(large_locs) >= num_reagents:
            set_locs = large_locs[:num_reagents]
            set_info = {
                "locations": set_locs,
                "tests_per_set": 270,
                "placements": []
            }
            
            for i, reagent in enumerate(experiment["reagents"]):
                loc = set_locs[i]
                set_info["placements"].append({
                    "location": loc,
                    "reagent_code": reagent["code"],
                    "tests": 270
                })
                tray_locations[loc] = {
                    "reagent_code": reagent["code"],
                    "experiment": exp_num,
                    "tests_possible": 270,
                    "volume_per_test": reagent["vol"],
                    "capacity": 270
                }
                available_locations.remove(loc)
            
            result["sets"].append(set_info)
            result["total_tests"] += 270
        
        # Place additional sets in 140mL locations
        remaining_locs = [loc for loc in available_locations if loc >= 4]
        while len(remaining_locs) >= num_reagents:
            set_locs = remaining_locs[:num_reagents]
            set_info = {
                "locations": set_locs,
                "tests_per_set": 140,
                "placements": []
            }
            
            for i, reagent in enumerate(experiment["reagents"]):
                loc = set_locs[i]
                set_info["placements"].append({
                    "location": loc,
                    "reagent_code": reagent["code"],
                    "tests": 140
                })
                tray_locations[loc] = {
                    "reagent_code": reagent["code"],
                    "experiment": exp_num,
                    "tests_possible": 140,
                    "volume_per_test": reagent["vol"],
                    "capacity": 140
                }
                available_locations.remove(loc)
                remaining_locs.remove(loc)
            
            result["sets"].append(set_info)
            result["total_tests"] += 140
        
        return result

    def optimize_two_reagent_experiment(self, exp_num, experiment, available_locations, tray_locations):
        result = {
            "name": experiment["name"],
            "sets": [],
            "total_tests": 0
        }
        
        # Get available 140mL locations
        small_locs = [loc for loc in available_locations if loc >= 4]
        if len(small_locs) >= 4:  # Need at least 4 locations
            r1, r2 = experiment["reagents"]
            
            # Use last location for second reagent
            r2_loc = small_locs[-1]
            r2_tests = self.calculate_tests(r2["vol"], 140)
            
            # Use three locations for first reagent
            r1_locs = small_locs[-4:-1]
            r1_tests_per_loc = self.calculate_tests(r1["vol"], 140)
            r1_total_tests = r1_tests_per_loc * 3
            
            set_info = {
                "locations": r1_locs + [r2_loc],
                "tests_per_set": min(r1_total_tests, r2_tests),
                "placements": []
            }
            
            # Place first reagent in three locations
            for loc in r1_locs:
                set_info["placements"].append({
                    "location": loc,
                    "reagent_code": r1["code"],
                    "tests": r1_tests_per_loc
                })
                tray_locations[loc] = {
                    "reagent_code": r1["code"],
                    "experiment": exp_num,
                    "tests_possible": r1_tests_per_loc,
                    "volume_per_test": r1["vol"],
                    "capacity": 140
                }
                available_locations.remove(loc)
            
            # Place second reagent
            set_info["placements"].append({
                "location": r2_loc,
                "reagent_code": r2["code"],
                "tests": r2_tests
            })
            tray_locations[r2_loc] = {
                "reagent_code": r2["code"],
                "experiment": exp_num,
                "tests_possible": r2_tests,
                "volume_per_test": r2["vol"],
                "capacity": 140
            }
            available_locations.remove(r2_loc)
            
            result["sets"].append(set_info)
            result["total_tests"] = min(r1_total_tests, r2_tests)
        
        return result

    def get_available_experiments(self):
        return [{"id": id_, "name": exp["name"]} 
                for id_, exp in self.experiment_data.items()]
