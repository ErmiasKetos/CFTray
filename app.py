import streamlit as st
import pandas as pd
from reagent_optimizer import ReagentOptimizer

@st.cache_resource
def get_optimizer():
    return ReagentOptimizer()

def render_location_card(location, data):
    capacity = "270mL" if location < 4 else "140mL"
    st.markdown(f"### LOC-{location + 1}")
    st.markdown(f"**Capacity:** {capacity}")
    
    if data:
        st.markdown(f"""
        **Reagent:** {data['reagent_code']}  
        **Tests possible:** {data['tests']}  
        **Volume per test:** {data['volume']}µL  
        **Experiment:** #{data['experiment']}
        """)
    else:
        st.markdown("*Empty*")
    st.markdown("---")

def main():
    st.title("Reagent Tray Configurator")
    
    optimizer = get_optimizer()
    
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
        placeholder="e.g., 1, 3, 16, 13"
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
            
            # Calculate total tests across all experiments
            total_tests = sum(result["total_tests"] for result in config["results"].values())
            st.metric("Total Tests Possible (All Experiments)", total_tests)
            
            # Show details for each experiment
            for exp_num, result in config["results"].items():
                with st.expander(f"{result['name']} (#{exp_num}) - {result['total_tests']} tests"):
                    for placement in result["reagent_placements"]:
                        st.markdown(f"**{placement['reagent_code']}** - Total tests: {placement['total_tests']}")
                        for loc in placement["placements"]:
                            st.markdown(
                                f"- LOC-{loc['location'] + 1} "
                                f"({loc['capacity']}mL): {loc['tests']} tests"
                            )
                    
                    st.markdown(f"**Maximum tests possible:** {result['total_tests']}")
            
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
