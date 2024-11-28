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

        # Sort experiments by total volume and number of reagents
        def sort_key(exp_num):
            exp = self.experiment_data[exp_num]
            total_vol = sum(r["vol"] for r in exp["reagents"])
            return (len(exp["reagents"]), total_vol)

        sorted_experiments = sorted(selected_experiments, key=sort_key, reverse=True)

        # Process each experiment
        for exp_num in sorted_experiments:
            experiment = self.experiment_data[exp_num]
            num_reagents = len(experiment["reagents"])
            
            # Initialize experiment result
            exp_result = {
                "name": experiment["name"],
                "sets": [],
                "total_tests": 0
            }

            # For Iron-like experiments (4 reagents, all same volume)
            if num_reagents == 4 and len(set(r["vol"] for r in experiment["reagents"])) == 1:
                # Try to place in 270mL locations first
                large_locs = [loc for loc in available_locations if loc < 4]
                if len(large_locs) >= 4:
                    # Place first set in 270mL locations
                    set_locs = large_locs[:4]
                    tests_per_set = self.calculate_tests(experiment["reagents"][0]["vol"], 270)
                    self.place_reagent_set(experiment, exp_num, set_locs, 270, 1, 
                                         tray_locations, available_locations, exp_result)

                # Place additional sets in 140mL locations
                small_locs = [loc for loc in available_locations if loc >= 4]
                while len(small_locs) >= 4:
                    set_locs = small_locs[:4]
                    tests_per_set = self.calculate_tests(experiment["reagents"][0]["vol"], 140)
                    self.place_reagent_set(experiment, exp_num, set_locs, 140, 
                                         len(exp_result["sets"]) + 1,
                                         tray_locations, available_locations, exp_result)
                    small_locs = small_locs[4:]

            # For Copper-like experiments (2 reagents, different volumes)
            elif num_reagents == 2:
                small_locs = [loc for loc in available_locations if loc >= 4]
                if len(small_locs) >= 4:
                    # Calculate optimal distribution
                    r1, r2 = experiment["reagents"]
                    r2_tests = self.calculate_tests(r2["vol"], 140)
                    r1_per_loc = self.calculate_tests(r1["vol"], 140)
                    needed_r1_locs = (r2_tests + r1_per_loc - 1) // r1_per_loc

                    if needed_r1_locs <= len(small_locs) - 1:
                        # Place reagents
                        r1_locs = small_locs[:needed_r1_locs]
                        r2_loc = small_locs[needed_r1_locs:needed_r1_locs+1]
                        
                        placements = []
                        # Place first reagent across multiple locations
                        for loc in r1_locs:
                            placements.append({
                                "location": loc,
                                "reagent_code": r1["code"],
                                "tests": self.calculate_tests(r1["vol"], 140)
                            })
                            tray_locations[loc] = {
                                "reagent_code": r1["code"],
                                "experiment": exp_num,
                                "tests_possible": self.calculate_tests(r1["vol"], 140),
                                "volume_per_test": r1["vol"],
                                "capacity": 140
                            }
                            available_locations.remove(loc)

                        # Place second reagent
                        r2_tests = self.calculate_tests(r2["vol"], 140)
                        placements.append({
                            "location": r2_loc[0],
                            "reagent_code": r2["code"],
                            "tests": r2_tests
                        })
                        tray_locations[r2_loc[0]] = {
                            "reagent_code": r2["code"],
                            "experiment": exp_num,
                            "tests_possible": r2_tests,
                            "volume_per_test": r2["vol"],
                            "capacity": 140
                        }
                        available_locations.remove(r2_loc[0])

                        exp_result["sets"].append({
                            "placements": placements,
                            "tests_per_set": r2_tests
                        })
                        exp_result["total_tests"] = r2_tests

            results[exp_num] = exp_result

        return {
            "tray_locations": tray_locations,
            "results": results
        }

    def place_reagent_set(self, experiment, exp_num, locations, capacity, set_number, 
                         tray_locations, available_locations, exp_result):
        placements = []
        tests_per_set = self.calculate_tests(experiment["reagents"][0]["vol"], capacity)

        for i, reagent in enumerate(experiment["reagents"]):
            loc = locations[i]
            tests = self.calculate_tests(reagent["vol"], capacity)
            
            placements.append({
                "location": loc,
                "reagent_code": reagent["code"],
                "tests": tests
            })
            
            tray_locations[loc] = {
                "reagent_code": reagent["code"],
                "experiment": exp_num,
                "tests_possible": tests,
                "volume_per_test": reagent["vol"],
                "capacity": capacity
            }
            
            available_locations.remove(loc)

        exp_result["sets"].append({
            "placements": placements,
            "tests_per_set": tests_per_set
        })
        exp_result["total_tests"] += tests_per_set

    def get_available_experiments(self):
        return [{"id": id_, "name": exp["name"]} 
                for id_, exp in self.experiment_data.items()]
