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
        """Calculate number of tests possible for given volume and capacity"""
        return int((chamber_capacity * 1000) / reagent_volume)

    def collect_all_reagents(self, experiments):
        """Collect all reagents from selected experiments with their requirements"""
        all_reagents = []
        for exp_num in experiments:
            experiment = self.experiment_data[exp_num]
            for reagent in experiment["reagents"]:
                all_reagents.append({
                    "experiment": exp_num,
                    "exp_name": experiment["name"],
                    "code": reagent["code"],
                    "volume": reagent["vol"],
                    "tests_270": self.calculate_tests(reagent["vol"], 270),
                    "tests_140": self.calculate_tests(reagent["vol"], 140)
                })
        return all_reagents

    def calculate_reagent_distribution(self, reagent, target_tests, available_locations):
        """Calculate optimal distribution of a reagent across locations to achieve target tests"""
        locations = []
        total_tests = 0
        remaining_locs = available_locations.copy()

        # Try to use 270mL locations first
        large_locs = [loc for loc in remaining_locs if loc < 4]
        while total_tests < target_tests and large_locs:
            loc = large_locs.pop(0)
            tests = self.calculate_tests(reagent["volume"], 270)
            locations.append({"location": loc, "tests": tests, "capacity": 270})
            total_tests += tests
            remaining_locs.remove(loc)

        # Then use 140mL locations if needed
        small_locs = [loc for loc in remaining_locs if loc >= 4]
        while total_tests < target_tests and small_locs:
            loc = small_locs.pop(0)
            tests = self.calculate_tests(reagent["volume"], 140)
            locations.append({"location": loc, "tests": tests, "capacity": 140})
            total_tests += tests
            remaining_locs.remove(loc)

        return locations, remaining_locs

    def optimize_tray_configuration(self, selected_experiments):
        tray_locations = [None] * 16
        results = {}
        available_locations = set(range(16))

        # First, handle experiments with highest volume requirements
        for exp_num in sorted(selected_experiments, 
                            key=lambda x: sum(r["vol"] for r in self.experiment_data[x]["reagents"]),
                            reverse=True):
            experiment = self.experiment_data[exp_num]
            exp_result = {"name": experiment["name"], "reagent_placements": [], "total_tests": 0}

            # Calculate maximum possible tests based on available locations
            max_possible = float('inf')
            for reagent in experiment["reagents"]:
                tests_possible = 0
                for loc in available_locations:
                    capacity = 270 if loc < 4 else 140
                    tests_possible += self.calculate_tests(reagent["vol"], capacity)
                max_possible = min(max_possible, tests_possible)

            # Place each reagent to achieve the target tests
            for reagent in experiment["reagents"]:
                placements, available_locations = self.calculate_reagent_distribution(
                    {"code": reagent["code"], "volume": reagent["vol"]},
                    max_possible,
                    available_locations
                )

                for place in placements:
                    tray_locations[place["location"]] = {
                        "reagent_code": reagent["code"],
                        "experiment": exp_num,
                        "tests_possible": place["tests"],
                        "volume_per_test": reagent["vol"],
                        "capacity": place["capacity"]
                    }

                exp_result["reagent_placements"].append({
                    "reagent_code": reagent["code"],
                    "placements": placements,
                    "total_tests": sum(p["tests"] for p in placements)
                })

            exp_result["total_tests"] = min(rp["total_tests"] for rp in exp_result["reagent_placements"])
            results[exp_num] = exp_result

        return {
            "tray_locations": tray_locations,
            "results": results
        }

    def get_available_experiments(self):
        return [{"id": id_, "name": exp["name"]} 
                for id_, exp in self.experiment_data.items()]
