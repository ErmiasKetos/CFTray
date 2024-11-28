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
            16: {"name": "Iron (Dissolved)", "reagents": [{"code": "KR16E1", "vol": 1000}, {"code": "KR16E2", "vol": 1000}, {"code": "KR16E3", "vol": 1000}, {"code": "KR16E4", "vol": 1000}]},
            17: {"name": "Residual Chlorine", "reagents": [{"code": "KR17E1", "vol": 1000}, {"code": "KR17E2", "vol": 1000}, {"code": "KR17E3", "vol": 1000}]},
            18: {"name": "Zinc (HR)", "reagents": [{"code": "KR18E1", "vol": 1000}, {"code": "KR18E2", "vol": 1000}]},
            19: {"name": "Manganese  (HR)", "reagents": [{"code": "KR19E1", "vol": 1000}, {"code": "KR19E2", "vol": 1000}, {"code": "KR19E3", "vol": 1000}]},
            20: {"name": "Orthophosphates-P (HR) ", "reagents": [{"code": "KR20E", "vol": 850}]},
            21: {"name": "Total Alkalinity (HR)", "reagents": [{"code": "KR21E1", "vol": 1000}]},
            22: {"name": "Fluoride", "reagents": [{"code": "KR22E1", "vol": 1000},{"code": "KR22E2", "vol": 1000}]},
            27: {"name": "Molybdenum", "reagents": [{"code": "KR27E1", "vol": 1000}, {"code": "KR27E2", "vol": 1000}]},
            30: {"name": "Chromium (HR)", "reagents": [{"code": "KR30E1", "vol": 1000},{"code": "KR30E2", "vol": 1000}, {"code": "KR30E3", "vol": 1000}]},
            31: {"name": "Nitrite-N", "reagents": [{"code": "KR31E1", "vol": 1000}, {"code": "KR31E2", "vol": 1000}]},
            34: {"name": "Nickel (HR)", "reagents": [{"code": "KR34E1", "vol": 500}, {"code": "KR34E2", "vol": 500}]},
            35: {"name": "Copper (II) (HR)", "reagents": [{"code": "KR35E1", "vol": 1000}, {"code": "KR35E2", "vol": 1000}]},
            36: {"name": "Sulfate", "reagents": [{"code": "KR36E1", "vol": 1000}, {"code": "KR36E2", "vol": 2300}]},
            40: {"name": "Potassium", "reagents": [{"code": "KR40E1", "vol": 1000}, {"code": "KR40E2", "vol": 1000}]},
            42: {"name": "Aluminum-BB", "reagents": [{"code": "KR42E1", "vol": 1000}, {"code": "KR42E2", "vol": 1000}]}
        }

        self.MAX_LOCATIONS = 16

    def calculate_tests(self, volume_ul, capacity_ml):
        return int((capacity_ml * 1000) / volume_ul)

    def calculate_total_tests(self, exp_num, placements):
        """Calculate total tests possible for an experiment given its placements"""
        reagent_tests = {}
        for placement in placements:
            code = placement["reagent_code"]
            if code not in reagent_tests:
                reagent_tests[code] = 0
            reagent_tests[code] += placement["tests"]
        return min(reagent_tests.values())

    def place_reagent_set(self, exp_num, locations, config):
        """Place a set of reagents in specified locations"""
        exp = self.experiment_data[exp_num]
        placements = []
        
        for i, reagent in enumerate(exp["reagents"]):
            loc = locations[i]
            capacity = 270 if loc < 4 else 140
            tests = self.calculate_tests(reagent["vol"], capacity)
            
            placement = {
                "reagent_code": reagent["code"],
                "location": loc,
                "tests": tests,
                "volume": reagent["vol"]
            }
            placements.append(placement)
            
            config["tray_locations"][loc] = {
                "reagent_code": reagent["code"],
                "experiment": exp_num,
                "tests_possible": tests,
                "volume_per_test": reagent["vol"],
                "capacity": capacity
            }
            config["available_locations"].remove(loc)

        set_tests = min(p["tests"] for p in placements)
        
        if exp_num not in config["results"]:
            config["results"][exp_num] = {
                "name": exp["name"],
                "sets": [],
                "total_tests": 0
            }
        
        config["results"][exp_num]["sets"].append({
            "placements": placements,
            "tests_per_set": set_tests
        })
        config["results"][exp_num]["total_tests"] += set_tests
        
        return set_tests

    def optimize_tray_configuration(self, selected_experiments):
        try:
            # Validate total chambers needed
            total_chambers = sum(len(self.experiment_data[exp]["reagents"]) for exp in selected_experiments)
            if total_chambers > self.MAX_LOCATIONS:
                details = [
                    f"{self.experiment_data[exp]['name']}: {len(self.experiment_data[exp]['reagents'])} chambers" 
                    for exp in selected_experiments
                ]
                raise ValueError(
                    f"Configuration cannot be made. Total required chambers: {total_chambers}\n"
                    f"Available chambers: {self.MAX_LOCATIONS}\n\n"
                    f"Chamber requirements:\n" + "\n".join(details) + "\n\n"
                    f"Please remove some experiments from the list."
                )

            # Initialize configuration
            config = {
                "tray_locations": [None] * self.MAX_LOCATIONS,
                "results": {},
                "available_locations": set(range(self.MAX_LOCATIONS))
            }

            # Phase 1: Place initial sets for all experiments
            # Sort by volume requirements
            sorted_experiments = sorted(
                selected_experiments,
                key=lambda x: max(r["vol"] for r in self.experiment_data[x]["reagents"]),
                reverse=True
            )

            # Place first sets
            for exp_num in sorted_experiments:
                exp = self.experiment_data[exp_num]
                num_reagents = len(exp["reagents"])
                
                # Try 270mL locations first for high-volume reagents
                if max(r["vol"] for r in exp["reagents"]) > 800:
                    available_270 = [loc for loc in config["available_locations"] if loc < 4]
                    if len(available_270) >= num_reagents:
                        locations = sorted(available_270[:num_reagents])
                        self.place_reagent_set(exp_num, locations, config)
                        continue
                
                # Otherwise use available 140mL locations
                available_140 = [loc for loc in config["available_locations"] if loc >= 4]
                if len(available_140) >= num_reagents:
                    locations = sorted(available_140[:num_reagents])
                    self.place_reagent_set(exp_num, locations, config)
                else:
                    raise ValueError(f"Cannot place initial set for experiment {exp_num}")

            # Phase 2: Balance and maximize minimum tests
            while config["available_locations"]:
                # Calculate current tests for each experiment
                exp_tests = {
                    exp_num: config["results"][exp_num]["total_tests"]
                    for exp_num in sorted_experiments
                }
                
                # Find experiment with minimum tests
                min_exp = min(exp_tests.items(), key=lambda x: x[1])[0]
                min_tests = exp_tests[min_exp]
                
                # Try to add set for experiment with minimum tests
                exp = self.experiment_data[min_exp]
                num_reagents = len(exp["reagents"])
                
                if len(config["available_locations"]) >= num_reagents:
                    available = sorted(list(config["available_locations"]))
                    locations = available[:num_reagents]
                    added_tests = self.place_reagent_set(min_exp, locations, config)
                    
                    # If adding this set didn't improve balance, try next experiment
                    if added_tests < min_tests / 2:
                        # Try other experiments
                        for other_exp in sorted_experiments:
                            if other_exp != min_exp:
                                num_reagents = len(self.experiment_data[other_exp]["reagents"])
                                if len(config["available_locations"]) >= num_reagents:
                                    locations = sorted(list(config["available_locations"]))[:num_reagents]
                                    self.place_reagent_set(other_exp, locations, config)
                                    break
                else:
                    break

            # Verify no empty locations
            if any(loc is None for loc in config["tray_locations"]):
                raise ValueError("Could not fill all locations")

            return config

        except Exception as e:
            raise ValueError(str(e))

    def get_available_experiments(self):
        return [{"id": id_, "name": exp["name"]} 
                for id_, exp in self.experiment_data.items()]
