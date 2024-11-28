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
        """Calculate number of tests possible for a given reagent volume and chamber capacity"""
        return int((capacity_ml * 1000) / volume_ul)

    def optimize_tray_configuration(self, selected_experiments):
        # Initialize configuration
        tray_locations = [None] * 16
        results = {}
        remaining_locations = list(range(16))

        # Sort experiments by total volume and number of reagents (descending)
        def sort_key(exp_num):
            exp = self.experiment_data[exp_num]
            return (
                sum(r["vol"] for r in exp["reagents"]),
                len(exp["reagents"])
            )

        sorted_experiments = sorted(selected_experiments, key=sort_key, reverse=True)

        # Process each experiment
        for exp_num in sorted_experiments:
            experiment = self.experiment_data[exp_num]
            result = {
                "name": experiment["name"],
                "sets": [],
                "total_tests": 0
            }

            available_large = [loc for loc in remaining_locations if loc < 4]
            available_small = [loc for loc in remaining_locations if loc >= 4]
            
            # Try to place multiple complete sets
            while True:
                set_config = self.try_place_experiment_set(
                    exp_num,
                    experiment,
                    available_large,
                    available_small,
                    tray_locations
                )
                
                if not set_config:
                    break
                
                result["sets"].append(set_config)
                result["total_tests"] += set_config["tests_possible"]
                
                # Update available locations
                used_locations = [loc["location"] for loc in set_config["reagents"]]
                remaining_locations = [loc for loc in remaining_locations if loc not in used_locations]
                available_large = [loc for loc in remaining_locations if loc < 4]
                available_small = [loc for loc in remaining_locations if loc >= 4]

            results[exp_num] = result

        return {"tray_locations": tray_locations, "results": results}

    def try_place_experiment_set(self, exp_num, experiment, available_large, available_small, tray_locations):
        num_reagents = len(experiment["reagents"])
        
        # Try using large locations first if available
        if len(available_large) >= num_reagents:
            locations = available_large[:num_reagents]
            base_capacity = 270
        # Then try small locations
        elif len(available_small) >= num_reagents:
            locations = available_small[:num_reagents]
            base_capacity = 140
        else:
            return None

        # Calculate tests possible with these locations
        reagent_placements = []
        tests_possible = float('inf')

        for i, reagent in enumerate(experiment["reagents"]):
            loc = locations[i]
            tests = self.calculate_tests(reagent["vol"], base_capacity)
            tests_possible = min(tests_possible, tests)
            
            reagent_placements.append({
                "location": loc,
                "reagent_code": reagent["code"],
                "volume": reagent["vol"],
                "tests": tests
            })
            
            # Update tray locations
            tray_locations[loc] = {
                "reagent_code": reagent["code"],
                "experiment": exp_num,
                "tests": tests,
                "volume": reagent["vol"],
                "capacity": base_capacity
            }

        return {
            "reagents": reagent_placements,
            "tests_possible": tests_possible
        }

    def get_available_experiments(self):
        return [{"id": id_, "name": exp["name"]} 
                for id_, exp in self.experiment_data.items()]
