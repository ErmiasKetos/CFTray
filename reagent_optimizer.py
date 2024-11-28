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

    def optimize_tray_configuration(self, selected_experiments):
        """Optimize the tray configuration based on selected experiments"""
        tray_locations = [None] * self.MAX_LOCATIONS
        available_locations = list(range(self.MAX_LOCATIONS))
        results = {}

        # Place Iron (Experiment #16) first if selected
        if 16 in selected_experiments:
            iron_config = self._place_iron_experiment(available_locations, tray_locations)
            if iron_config:
                results[16] = iron_config['results']
                available_locations = [loc for loc in available_locations if tray_locations[loc] is None]

        # Place remaining experiments
        remaining_experiments = [exp for exp in selected_experiments if exp != 16]
        for exp in remaining_experiments:
            exp_config = self._place_other_experiment(exp, available_locations, tray_locations)
            if exp_config:
                results[exp] = exp_config['results']
                available_locations = [loc for loc in available_locations if tray_locations[loc] is None]

        return {"tray_locations": tray_locations, "results": results}

    def _place_iron_experiment(self, available_locations, tray_locations):
        """Place Iron experiment reagents in the tray"""
        iron = self.experiment_data[16]
        if len(available_locations) < 4:
            return None  # Not enough space for all reagents

        placements = []
        for i, reagent in enumerate(iron["reagents"]):
            loc = available_locations[i]
            tests = self.calculate_tests(reagent["vol"], 270)  # Iron uses 270mL locations
            tray_locations[loc] = {
                "reagent_code": reagent["code"],
                "experiment": 16,
                "tests_possible": tests,
                "volume_per_test": reagent["vol"],
                "capacity": 270
            }
            placements.append({"location": loc, "tests": tests, "reagent": reagent["code"]})

        return {
            "results": {
                "name": iron["name"],
                "sets": [{"placements": placements, "tests_per_set": min(p["tests"] for p in placements)}],
                "total_tests": min(p["tests"] for p in placements)
            }
        }

    def _place_other_experiment(self, exp_num, available_locations, tray_locations):
        """Place other experiments in the tray"""
        experiment = self.experiment_data[exp_num]
        num_reagents = len(experiment["reagents"])

        if len(available_locations) < num_reagents:
            return None  # Not enough space for all reagents

        placements = []
        min_tests = float("inf")
        for i, reagent in enumerate(experiment["reagents"]):
            loc = available_locations[i]
            capacity = 270 if loc < 4 else 140  # First 4 locations are 270mL, others are 140mL
            tests = self.calculate_tests(reagent["vol"], capacity)
            tray_locations[loc] = {
                "reagent_code": reagent["code"],
                "experiment": exp_num,
                "tests_possible": tests,
                "volume_per_test": reagent["vol"],
                "capacity": capacity
            }
            placements.append({"location": loc, "tests": tests, "reagent": reagent["code"]})
            min_tests = min(min_tests, tests)

        return {
            "results": {
                "name": experiment["name"],
                "sets": [{"placements": placements, "tests_per_set": min_tests}],
                "total_tests": min_tests
            }
        }

    def get_available_experiments(self):
        """Return a list of available experiments"""
        return [{"id": exp_id, "name": exp["name"]} for exp_id, exp in self.experiment_data.items()]
