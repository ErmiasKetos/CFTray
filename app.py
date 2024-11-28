import streamlit as st
import pandas as pd
from reagent_optimizer import ReagentOptimizer

def render_location_card(location, data):
    capacity = "270mL" if location < 4 else "140mL"
    
    cols = st.columns([2, 1])
    with cols[0]:
        st.markdown(f"### LOC-{location + 1}")
        st.markdown(f"**Capacity:** {capacity}")
    
    if data:
        st.markdown(f"""
        **Reagent:** {data['reagent_code']}  
        **Tests possible:** {data['tests_possible']}  
        **Volume per test:** {data['volume_per_test']}µL  
        **Experiment:** #{data['experiment']}
        """)
    else:
        st.markdown("*Empty*")
    st.markdown("---")

def main():
    st.title("Reagent Tray Configurator")
    
    optimizer = ReagentOptimizer()
    
    # Show available experiments
    st.subheader("Available Experiments")
    experiments_df = pd.DataFrame(optimizer.get_available_experiments())
    st.dataframe(
        experiments_df,
        column_config={
            "id": "Experiment #",
            "name": "Experiment Name"
        },
        hide_index=True
    )
    
    # Input for experiment selection
    selected_experiments = st.text_input(
        "Enter experiment numbers (comma-separated)",
        placeholder="e.g., 1, 16"
    )
    
    if st.button("Optimize Configuration"):
        if not selected_experiments:
            st.error("Please enter experiment numbers")
            return
        
        try:
            # Parse and validate input
            experiments = [
                int(num.strip()) 
                for num in selected_experiments.split(',') 
                if num.strip()
            ]
            
            available_ids = [exp["id"] for exp in optimizer.get_available_experiments()]
            invalid_experiments = [
                exp for exp in experiments 
                if exp not in available_ids
            ]
            
            if invalid_experiments:
                st.error(f"Invalid experiment numbers: {', '.join(map(str, invalid_experiments))}")
                return
            
            # Get optimized configuration
            config = optimizer.optimize_tray_configuration(experiments)
            
            # Display tray configuration
            st.subheader("Tray Configuration")
            cols = st.columns(4)
            
            # Render tray grid
            for i in range(16):
                with cols[i % 4]:
                    render_location_card(i, config["tray_locations"][i])
            
            # Display results summary
            st.subheader("Results Summary")
            
            # Show details for each experiment
            for exp_num, result in config["results"].items():
                with st.expander(f"{result['name']} (#{exp_num}) - {result['total_tests']} total tests"):
                    for set_info in result["sets"]:
                        st.markdown(f"""
                        **Set {set_info['set_number']}:**
                        - Capacity: {set_info['capacity']}mL
                        - Tests per set: {set_info['tests_per_set']}
                        """)
                        
                        for placement in set_info["placements"]:
                            st.markdown(f"""
                            {placement['reagent_code']} (LOC-{placement['location'] + 1}):
                            - Tests possible: {placement['tests']}
                            """)
                    
                    st.markdown(f"**Total tests possible: {result['total_tests']}**")
            
        except ValueError:
            st.error("Please enter valid experiment numbers")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    st.set_page_config(
        page_title="Reagent Tray Configurator",
        layout="wide"
    )
    main()
