import streamlit as st
import pandas as pd
from reagent_optimizer import ReagentOptimizer

# Initialize the optimizer
@st.cache_resource
def get_optimizer():
    return ReagentOptimizer()

def main():
    st.title("Reagent Tray Configurator")
    
    optimizer = get_optimizer()
    
    # Display available experiments
    st.subheader("Available Experiments")
    experiments_df = pd.DataFrame(optimizer.get_available_experiments())
    st.dataframe(experiments_df, hide_index=True)
    
    # Input for experiment selection
    experiment_input = st.text_input(
        "Enter experiment numbers (comma-separated)",
        placeholder="e.g., 1, 3, 16, 13"
    )
    
    if st.button("Optimize Configuration"):
        if not experiment_input:
            st.error("Please enter experiment numbers")
            return
            
        try:
            # Parse input
            selected_experiments = [
                int(num.strip()) 
                for num in experiment_input.split(',')
                if num.strip()
            ]
            
            # Validate input
            available_ids = [exp["id"] for exp in optimizer.get_available_experiments()]
            invalid_experiments = [exp for exp in selected_experiments if exp not in available_ids]
            
            if invalid_experiments:
                st.error(f"Invalid experiment numbers: {', '.join(map(str, invalid_experiments))}")
                return
                
            # Get configuration
            configuration = optimizer.optimize_tray_configuration(selected_experiments)
            
            # Display tray configuration
            st.subheader("Tray Configuration")
            
            # Create grid layout
            cols = st.columns(4)
            for i in range(16):
                col_idx = i % 4
                with cols[col_idx]:
                    location_data = configuration["tray_locations"][i]
                    capacity = "270mL" if i < 4 else "140mL"
                    
                    # Create a card-like display for each location
                    st.markdown("---")
                    st.markdown(f"### LOC-{i+1}")
                    st.markdown(f"Capacity: {capacity}")
                    
                    if location_data:
                        st.markdown(f"""
                        **Reagent:** {location_data['reagent_code']}  
                        **Tests:** {location_data['tests']}  
                        **Volume:** {location_data['volume']}µL/test  
                        **Exp #{location_data['experiment']} (Set {location_data['set_index'] + 1})**
                        """)
                    else:
                        st.markdown("*Empty*")
            
            # Display results summary
            st.subheader("Results Summary")
            for exp_num, result in configuration["results"].items():
                with st.expander(f"{result['name']} (Experiment #{exp_num})"):
                    st.markdown(f"**Total possible tests:** {result['total_tests']}")
                    
                    for idx, set_config in enumerate(result["sets"]):
                        st.markdown(f"\n**{'Primary' if idx == 0 else f'Additional Set {idx}'}: "
                                  f"{set_config['tests_per_set']} tests**")
                        
                        for loc in set_config["locations"]:
                            st.markdown(f"- {loc['reagent_code']} (LOC-{loc['location'] + 1}): "
                                      f"{loc['tests']} tests possible")
                            
        except ValueError as e:
            st.error("Please enter valid experiment numbers")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    st.set_page_config(
        page_title="Reagent Tray Configurator",
        layout="wide"
    )
    main()
