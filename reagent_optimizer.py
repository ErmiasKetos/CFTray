from itertools import combinations, permutations
from typing import List, Dict, Set, Tuple

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
        """Get capacity of a location in mL"""
        return 270 if location < 4 else 140

    def generate_placement_combinations(self, exp_num: int, available_locations: Set[int]) -> List[Dict]:
        """Generate all valid placement combinations for an experiment"""
        experiment = self.experiment_data[exp_num]
        reagents = experiment["reagents"]
        num_reagents = len(reagents)
        
        if num_reagents == 1:
            return self.generate_single_reagent_placements(reagents[0], available_locations)
        elif num_reagents == 2:
            return self.generate_two_reagent_placements(reagents, available_locations)
        else:
            return self.generate_multi_reagent_placements(reagents, available_locations)

    def generate_single_reagent_placements(self, reagent: Dict, available_locations: Set[int]) -> List[Dict]:
        """Generate placements for single reagent experiments"""
        placements = []
        for loc in available_locations:
            capacity = self.get_location_capacity(loc)
            tests = self.calculate_tests(reagent["vol"], capacity)
            placements.append({
                "locations": [loc],
                "tests": tests,
                "reagent_placements": [{
                    "reagent_code": reagent["code"],
                    "location": loc,
                    "tests": tests
                }]
            })
        return placements

    def generate_two_reagent_placements(self, reagents: List[Dict], available_locations: Set[int]) -> List[Dict]:
        """Generate placements for two-reagent experiments"""
        placements = []
        locations = sorted(list(available_locations))
        
        # Try different numbers of locations for first reagent
        for num_r1_locs in range(1, len(locations) - 1):
            for r1_locs in combinations(locations, num_r1_locs):
                remaining_locs = set(locations) - set(r1_locs)
                
                # Try each remaining location for second reagent
                for r2_loc in remaining_locs:
                    # Calculate tests possible
                    r1_tests = sum(self.calculate_tests(reagents[0]["vol"], 
                                                      self.get_location_capacity(loc)) 
                                 for loc in r1_locs)
                    r2_tests = self.calculate_tests(reagents[1]["vol"], 
                                                  self.get_location_capacity(r2_loc))
                    
                    total_tests = min(r1_tests, r2_tests)
                    if total_tests > 0:
                        placements.append({
                            "locations": list(r1_locs) + [r2_loc],
                            "tests": total_tests,
                            "reagent_placements": [
                                *[{
                                    "reagent_code": reagents[0]["code"],
                                    "location": loc,
                                    "tests": self.calculate_tests(reagents[0]["vol"], 
                                                                self.get_location_capacity(loc))
                                } for loc in r1_locs],
                                {
                                    "reagent_code": reagents[1]["code"],
                                    "location": r2_loc,
                                    "tests": r2_tests
                                }
                            ]
                        })
        return placements

    def generate_multi_reagent_placements(self, reagents: List[Dict], available_locations: Set[int]) -> List[Dict]:
        """Generate placements for experiments with multiple reagents"""
        placements = []
        locations = sorted(list(available_locations))
        
        # Try different consecutive location combinations
        for start_loc in range(len(locations) - len(reagents) + 1):
            selected_locs = locations[start_loc:start_loc + len(reagents)]
            
            # Calculate tests possible
            tests_per_reagent = []
            reagent_placements = []
            
            for reagent, loc in zip(reagents, selected_locs):
                capacity = self.get_location_capacity(loc)
                tests = self.calculate_tests(reagent["vol"], capacity)
                tests_per_reagent.append(tests)
                reagent_placements.append({
                    "reagent_code": reagent["code"],
                    "location": loc,
                    "tests": tests
                })
            
            total_tests = min(tests_per_reagent)
            if total_tests > 0:
                placements.append({
                    "locations": selected_locs,
                    "tests": total_tests,
                    "reagent_placements": reagent_placements
                })
        return placements

    def optimize_tray_configuration(self, selected_experiments: List[int]) -> Dict:
        """Find optimal configuration maximizing total tests across all experiments"""
        all_locations = set(range(16))
        best_configuration = None
        max_total_tests = 0
        
        def try_combinations(remaining_exps: List[int], 
                           available_locations: Set[int], 
                           current_config: Dict) -> None:
            nonlocal best_configuration, max_total_tests
            
            if not remaining_exps:
                total_tests = sum(exp_config["total_tests"] 
                                for exp_config in current_config["results"].values())
                if total_tests > max_total_tests:
                    max_total_tests = total_tests
                    best_configuration = current_config.copy()
                return
            
            exp_num = remaining_exps[0]
            placement_options = self.generate_placement_combinations(exp_num, available_locations)
            
            for placement in placement_options:
                # Create new configuration with this placement
                new_config = {
                    "tray_locations": current_config["tray_locations"].copy(),
                    "results": current_config["results"].copy()
                }
                
                # Update tray locations
                used_locations = set()
                for reagent_place in placement["reagent_placements"]:
                    loc = reagent_place["location"]
                    new_config["tray_locations"][loc] = {
                        "reagent_code": reagent_place["reagent_code"],
                        "experiment": exp_num,
                        "tests_possible": reagent_place["tests"],
                        "volume_per_test": self.experiment_data[exp_num]["reagents"][0]["vol"],
                        "capacity": self.get_location_capacity(loc)
                    }
                    used_locations.add(loc)
                
                # Update results
                new_config["results"][exp_num] = {
                    "name": self.experiment_data[exp_num]["name"],
                    "sets": [{
                        "placements": placement["reagent_placements"],
                        "tests_per_set": placement["tests"]
                    }],
                    "total_tests": placement["tests"]
                }
                
                # Recursive call with remaining experiments and locations
                new_available = available_locations - used_locations
                try_combinations(remaining_exps[1:], new_available, new_config)
        
        # Start optimization with empty configuration
        initial_config = {
            "tray_locations": [None] * 16,
            "results": {}
        }
        
        try_combinations(selected_experiments, all_locations, initial_config)
        return best_configuration

    def get_available_experiments(self):
        """Get list of available experiments"""
        return [{"id": id_, "name": exp["name"]} 
                for id_, exp in self.experiment_data.items()]
