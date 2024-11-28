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

    def calculate_tests(self, volume_ul: float, capacity_ml: int) -> int:
        """Calculate number of tests possible for a given reagent volume and chamber capacity"""
        return int((capacity_ml * 1000) / volume_ul)

    def get_location_capacity(self, location: int) -> int:
        """Get the capacity of a location in mL"""
        return 270 if location < 4 else 140

    def optimize_single_experiment(self, exp_num: int, start_loc: int, end_loc: int):
        """Optimize placement for a single experiment within a range of locations"""
        experiment = self.experiment_data[exp_num]
        num_reagents = len(experiment["reagents"])
        locations_needed = num_reagents

        if end_loc - start_loc + 1 < locations_needed:
            return None

        result = {
            "placements": [],
            "total_tests": 0,
            "locations_used": set()
        }

        # For multi-reagent experiments like Iron
        if num_reagents >= 4:
            # Try to place in consecutive locations
            for i, reagent in enumerate(experiment["reagents"]):
                loc = start_loc + i
                capacity = self.get_location_capacity(loc)
                tests = self.calculate_tests(reagent["vol"], capacity)
                
                result["placements"].append({
                    "reagent_code": reagent["code"],
                    "location": loc,
                    "tests": tests,
                    "volume": reagent["vol"]
                })
                result["locations_used"].add(loc)
            
            result["total_tests"] = min(p["tests"] for p in result["placements"])
            return result

        # For two-reagent experiments like Copper
        elif num_reagents == 2:
            r1, r2 = experiment["reagents"]
            available_locs = list(range(start_loc, end_loc + 1))
            
            # Try different combinations of locations
            best_result = None
            best_tests = 0

            for r2_loc in available_locs[-1:]:  # Last location for second reagent
                r2_capacity = self.get_location_capacity(r2_loc)
                r2_tests = self.calculate_tests(r2["vol"], r2_capacity)
                
                # Find best locations for first reagent
                r1_locs = []
                r1_total_tests = 0
                
                for loc in available_locs:
                    if loc != r2_loc and len(r1_locs) < 3:  # Up to 3 locations for first reagent
                        capacity = self.get_location_capacity(loc)
                        tests = self.calculate_tests(r1["vol"], capacity)
                        r1_total_tests += tests
                        r1_locs.append((loc, tests))
                        
                        if r1_total_tests >= r2_tests:
                            break

                if r1_locs:
                    total_tests = min(r1_total_tests, r2_tests)
                    if total_tests > best_tests:
                        best_tests = total_tests
                        best_result = {
                            "placements": [
                                *[{
                                    "reagent_code": r1["code"],
                                    "location": loc,
                                    "tests": tests,
                                    "volume": r1["vol"]
                                } for loc, tests in r1_locs],
                                {
                                    "reagent_code": r2["code"],
                                    "location": r2_loc,
                                    "tests": r2_tests,
                                    "volume": r2["vol"]
                                }
                            ],
                            "total_tests": total_tests,
                            "locations_used": set(loc for loc, _ in r1_locs) | {r2_loc}
                        }

            return best_result

        return None

    def optimize_tray_configuration(self, selected_experiments):
        tray_locations = [None] * 16
        results = {}
        available_locations = set(range(16))

        # Sort experiments by complexity and volume requirements
        sorted_experiments = sorted(
            selected_experiments,
            key=lambda x: (
                len(self.experiment_data[x]["reagents"]),
                sum(r["vol"] for r in self.experiment_data[x]["reagents"])
            ),
            reverse=True
        )

        # First pass: Place primary sets for each experiment
        for exp_num in sorted_experiments:
            remaining_locs = sorted(available_locations)
            if not remaining_locs:
                break

            result = self.optimize_single_experiment(
                exp_num, 
                min(remaining_locs), 
                max(remaining_locs)
            )

            if result:
                available_locations -= result["locations_used"]
                results[exp_num] = {
                    "name": self.experiment_data[exp_num]["name"],
                    "sets": [{
                        "placements": result["placements"],
                        "tests_per_set": result["total_tests"]
                    }],
                    "total_tests": result["total_tests"]
                }

                # Update tray locations
                for placement in result["placements"]:
                    tray_locations[placement["location"]] = {
                        "reagent_code": placement["reagent_code"],
                        "experiment": exp_num,
                        "tests_possible": placement["tests"],
                        "volume_per_test": placement["volume"],
                        "capacity": self.get_location_capacity(placement["location"])
                    }

        # Second pass: Fill remaining locations with additional sets
        while available_locations:
            best_addition = None
            best_exp = None
            best_tests = 0

            for exp_num in sorted_experiments:
                remaining_locs = sorted(available_locations)
                result = self.optimize_single_experiment(
                    exp_num,
                    min(remaining_locs),
                    max(remaining_locs)
                )

                if result and result["total_tests"] > best_tests:
                    best_addition = result
                    best_exp = exp_num
                    best_tests = result["total_tests"]

            if best_addition:
                available_locations -= best_addition["locations_used"]
                results[best_exp]["sets"].append({
                    "placements": best_addition["placements"],
                    "tests_per_set": best_addition["total_tests"]
                })
                results[best_exp]["total_tests"] += best_addition["total_tests"]

                # Update tray locations
                for placement in best_addition["placements"]:
                    tray_locations[placement["location"]] = {
                        "reagent_code": placement["reagent_code"],
                        "experiment": best_exp,
                        "tests_possible": placement["tests"],
                        "volume_per_test": placement["volume"],
                        "capacity": self.get_location_capacity(placement["location"])
                    }
            else:
                break

        return {
            "tray_locations": tray_locations,
            "results": results
        }

    def get_available_experiments(self):
        return [{"id": id_, "name": exp["name"]} 
                for id_, exp in self.experiment_data.items()]
