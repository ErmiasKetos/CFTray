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
        """Calculate number of tests possible given reagent volume and chamber capacity"""
        return int((capacity_ml * 1000) / volume_ul)

    def calculate_required_locations(self, target_tests, volume_ul, available_small_locs, available_large_locs):
        """Calculate how many and which locations needed to achieve target tests"""
        large_loc_tests = self.calculate_tests(volume_ul, 270)
        small_loc_tests = self.calculate_tests(volume_ul, 140)
        
        required_locs = []
        remaining_tests = target_tests
        
        # Use large locations first if they give better efficiency
        while remaining_tests > 0 and available_large_locs:
            required_locs.append(available_large_locs[0])
            remaining_tests -= large_loc_tests
            available_large_locs = available_large_locs[1:]
            
        # Then use small locations if still needed
        while remaining_tests > 0 and available_small_locs:
            required_locs.append(available_small_locs[0])
            remaining_tests -= small_loc_tests
            available_small_locs = available_small_locs[1:]
            
        return required_locs

    def optimize_tray_configuration(self, selected_experiments):
        # Sort experiments by volume requirements (higher volumes first)
        sorted_experiments = sorted(
            selected_experiments,
            key=lambda x: sum(r["vol"] for r in self.experiment_data[x]["reagents"]),
            reverse=True
        )
        
        tray_locations = [None] * 16
        results = {}
        
        # Track available locations
        available_large_locs = list(range(4))  # 270mL locations
        available_small_locs = list(range(4, 16))  # 140mL locations
        
        for exp_num in sorted_experiments:
            experiment = self.experiment_data[exp_num]
            exp_results = {
                "name": experiment["name"],
                "reagent_placements": [],
                "total_tests": 0
            }
            
            # Calculate maximum possible tests based on limiting reagent
            max_possible_tests = float('inf')
            for reagent in experiment["reagents"]:
                large_loc_tests = len(available_large_locs) * self.calculate_tests(reagent["vol"], 270)
                small_loc_tests = len(available_small_locs) * self.calculate_tests(reagent["vol"], 140)
                max_possible_tests = min(max_possible_tests, large_loc_tests + small_loc_tests)

            # Place each reagent
            for reagent in experiment["reagents"]:
                # Calculate locations needed for this reagent
                locs = self.calculate_required_locations(
                    max_possible_tests,
                    reagent["vol"],
                    available_small_locs.copy(),
                    available_large_locs.copy()
                )
                
                placements = []
                for loc in locs:
                    capacity = 270 if loc < 4 else 140
                    tests = self.calculate_tests(reagent["vol"], capacity)
                    
                    tray_locations[loc] = {
                        "reagent_code": reagent["code"],
                        "experiment": exp_num,
                        "tests": tests,
                        "volume": reagent["vol"],
                        "capacity": capacity
                    }
                    
                    # Remove used location from available pools
                    if loc < 4:
                        available_large_locs.remove(loc)
                    else:
                        available_small_locs.remove(loc)
                    
                    placements.append({
                        "location": loc,
                        "tests": tests,
                        "capacity": capacity
                    })
                
                exp_results["reagent_placements"].append({
                    "reagent_code": reagent["code"],
                    "placements": placements,
                    "total_tests": sum(p["tests"] for p in placements)
                })
            
            # Calculate total tests possible for this experiment
            exp_results["total_tests"] = min(
                rp["total_tests"] for rp in exp_results["reagent_placements"]
            )
            
            results[exp_num] = exp_results

        return {
            "tray_locations": tray_locations,
            "results": results
        }

    def get_available_experiments(self):
        return [
            {"id": id_, "name": exp["name"]} 
            for id_, exp in self.experiment_data.items()
        ]
