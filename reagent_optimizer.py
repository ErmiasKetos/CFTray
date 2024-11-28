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
        return int((capacity_ml * 1000) / volume_ul)

    def optimize_tray_configuration(self, selected_experiments):
        try:
            total_chambers = sum(len(self.experiment_data[exp]["reagents"]) for exp in selected_experiments)
            if total_chambers > self.MAX_LOCATIONS:
                details = [f"{self.experiment_data[exp]['name']}: {len(self.experiment_data[exp]['reagents'])} chambers"
                          for exp in selected_experiments]
                raise ValueError(
                    f"Configuration cannot be made. Total required chambers: {total_chambers}\n"
                    f"Available chambers: {self.MAX_LOCATIONS}\n\n"
                    f"Chamber requirements:\n" + "\n".join(details)
                )

            tray_locations = [None] * self.MAX_LOCATIONS
            results = {}
            available_locations = list(range(self.MAX_LOCATIONS))

            if 16 in selected_experiments:
                iron_config = self._place_iron_experiment(available_locations, tray_locations)
                if iron_config:
                    results[16] = iron_config['results']
                    available_locations = [loc for loc in available_locations if tray_locations[loc] is None]

            remaining_exps = [exp for exp in selected_experiments if exp != 16]
            for exp_num in remaining_exps:
                exp_config = self._place_other_experiment(exp_num, available_locations, tray_locations)
                if exp_config:
                    results[exp_num] = exp_config['results']
                    available_locations = [loc for loc in available_locations if tray_locations[loc] is None]

            while available_locations:
                best_addition = self._find_best_additional_set(available_locations, selected_experiments, tray_locations)
                if not best_addition:
                    break

                exp_num = best_addition['experiment']
                for placement in best_addition['placements']:
                    loc = placement['location']
                    tray_locations[loc] = {
                        "reagent_code": placement['reagent_code'],
                        "experiment": exp_num,
                        "tests_possible": placement['tests'],
                        "volume_per_test": placement['volume'],
                        "capacity": 270 if loc < 4 else 140
                    }
                    available_locations.remove(loc)

                if exp_num not in results:
                    results[exp_num] = {"name": self.experiment_data[exp_num]["name"], "sets": [], "total_tests": 0}
                results[exp_num]["sets"].append({"placements": best_addition['placements'], "tests_per_set": best_addition['tests_per_set']})
                results[exp_num]["total_tests"] += best_addition['tests_per_set']

            return {"tray_locations": tray_locations, "results": results}

        except Exception as e:
            raise ValueError(str(e))

    def get_available_experiments(self):
        return [{"id": id_, "name": exp["name"]} for id_, exp in self.experiment_data.items()]
