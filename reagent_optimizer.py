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
            28: {"name": "Nitrates-N (HR)", "reagents": [{"code": "KR28E1", "vol": 1000}, {"code": "KR28E2", "vol": 2000}, {"code": "KR28E3", "vol": 2000}]},
            29: {"name": "Total Ammonia-N", "reagents": [{"code": "KR29E1", "vol": 850}, {"code": "KR29E2", "vol": 850}, {"code": "KR29E3", "vol": 850}]},
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

    def get_location_capacity(self, location):
        return 270 if location < 4 else 140

    def optimize_tray_configuration(self, selected_experiments):
        for exp in selected_experiments:
            if exp not in self.experiment_data:
                raise ValueError(f"Invalid experiment number: {exp}")

        total_reagents = sum(len(self.experiment_data[exp]["reagents"]) for exp in selected_experiments)
        if total_reagents > self.MAX_LOCATIONS:
            details = [f"{self.experiment_data[exp]['name']}: {len(self.experiment_data[exp]['reagents'])} reagents" 
                      for exp in selected_experiments]
            raise ValueError(
                f"Total reagents needed ({total_reagents}) exceeds available locations ({self.MAX_LOCATIONS}).\n"
                f"Experiment requirements:\n" + "\n".join(details)
            )

        config = {
            "tray_locations": [None] * self.MAX_LOCATIONS,
            "results": {},
            "available_locations": set(range(self.MAX_LOCATIONS))
        }

        sorted_experiments = sorted(
            selected_experiments,
            key=lambda x: (
                len(self.experiment_data[x]["reagents"]),
                max(r["vol"] for r in self.experiment_data[x]["reagents"])
            ),
            reverse=True
        )

        for exp in sorted_experiments:
            self._place_experiment_reagents(exp, config)

        self._fill_empty_locations(sorted_experiments, config)
        self._recalculate_total_tests(config)

        return config

    def _place_experiment_reagents(self, exp, config):
        exp_data = self.experiment_data[exp]
        num_reagents = len(exp_data["reagents"])
        
        if any(r["vol"] > 800 for r in exp_data["reagents"]):
            available_270 = [loc for loc in range(4) if loc in config["available_locations"]]
            if len(available_270) >= num_reagents:
                self._place_reagent_set(exp, available_270[:num_reagents], config)
                return

        available_locs = sorted(config["available_locations"])
        for i in range(len(available_locs) - num_reagents + 1):
            locations = available_locs[i:i + num_reagents]
            if all(self.get_location_capacity(loc) >= min(r["vol"] for r in exp_data["reagents"]) / 5 
                  for loc in locations):
                self._place_reagent_set(exp, locations, config)
                return
        
        available = sorted(config["available_locations"], 
                           key=lambda x: self.get_location_capacity(x), reverse=True)
        if len(available) >= num_reagents:
            self._place_reagent_set(exp, available[:num_reagents], config)
        else:
            raise ValueError(
                f"Could not place experiment {exp} ({exp_data['name']}). "
                f"Need {num_reagents} locations, but only {len(available)} available."
            )

    def _fill_empty_locations(self, experiments, config):
        empty_locations = [i for i, loc in enumerate(config["tray_locations"]) if loc is None]
        
        while empty_locations:
            exp_with_least_tests = min(
                experiments,
                key=lambda x: config["results"][x]["total_tests"] if x in config["results"] else float('inf')
            )
            
            best_reagent = max(
                self.experiment_data[exp_with_least_tests]["reagents"],
                key=lambda r: self.calculate_tests(r["vol"], self.get_location_capacity(empty_locations[0]))
            )
            
            self._place_single_reagent(exp_with_least_tests, best_reagent, empty_locations[0], config)
            empty_locations = [i for i, loc in enumerate(config["tray_locations"]) if loc is None]

    def _place_single_reagent(self, exp_num, reagent, location, config):
        capacity = self.get_location_capacity(location)
        tests = self.calculate_tests(reagent["vol"], capacity)
        
        config["tray_locations"][location] = {
            "reagent_code": reagent["code"],
            "experiment": exp_num,
            "tests_possible": tests,
            "volume_per_test": reagent["vol"],
            "capacity": capacity
        }
        
        if exp_num not in config["results"]:
            config["results"][exp_num] = {
                "name": self.experiment_data[exp_num]["name"],
                "placements": [],
                "total_tests": 0
            }
        
        config["results"][exp_num]["placements"].append({
            "reagent_code": reagent["code"],
            "location": location,
            "tests": tests,
            "volume": reagent["vol"]
        })
        config["available_locations"].remove(location)

    def _place_reagent_set(self, exp_num, locations, config):
        exp = self.experiment_data[exp_num]
        sorted_reagents = sorted(exp["reagents"], key=lambda r: r["vol"], reverse=True)

        for i, reagent in enumerate(sorted_reagents):
            loc = locations[i]
            self._place_single_reagent(exp_num, reagent, loc, config)

    def _recalculate_total_tests(self, config):
        for exp_num, result in config["results"].items():
            exp_data = self.experiment_data[exp_num]
            num_reagents = len(exp_data["reagents"])
            
            reagent_placements = defaultdict(list)
            for placement in result["placements"]:
                reagent_placements[placement["reagent_code"]].append(placement)
            
            complete_sets = []
            partial_set = []
            
            while all(len(placements) > 0 for placements in reagent_placements.values()):
                current_set = []
                for reagent in exp_data["reagents"]:
                    if reagent_placements[reagent["code"]]:
                        current_set.append(reagent_placements[reagent["code"]].pop(0))
                complete_sets.append(current_set)
            
            for placements in reagent_placements.values():
                partial_set.extend(placements)
            
            result["sets"] = []
            total_tests = 0
            
            for i, set_placements in enumerate(complete_sets):
                set_tests = min(p["tests"] for p in set_placements)
                total_tests += set_tests
                result["sets"].append({
                    "placements": set_placements,
                    "tests_per_set": set_tests
                })
            
            if partial_set:
                result["sets"].append({
                    "placements": partial_set,
                    "tests_per_set": 0
                })
            
            result["total_tests"] = total_tests

    def get_available_experiments(self):
        return [{"id": id_, "name": exp["name"]} 
                for id_, exp in self.experiment_data.items()]

