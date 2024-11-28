import streamlit as st
from reagent_optimizer import ReagentOptimizer

def render_location_card(location, data):
    capacity = "270mL" if location < 4 else "140mL"
    
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

def validate_experiment_numbers(input_string, available_ids):
    """Validate and parse experiment numbers from input string"""
    if not input_string.strip():
        return None, "Please enter experiment numbers"
    
    try:
        # Split input and remove empty strings
        numbers = [num.strip() for num in input_string.split(',') if num.strip()]
        # Convert to integers
        experiments = [int(num) for num in numbers]
        
        # Check for valid experiment numbers
        invalid = [num for num in experiments if num not in available_ids]
        if invalid:
            return None, f"Invalid experiment numbers: {', '.join(map(str, invalid))}"
        
        # Check for duplicates
        if len(experiments) != len(set(experiments)):
            return None, "Please enter each experiment number only once"
        
        return experiments, None
        
    except ValueError:
        return None, "Please enter valid numbers separated by commas"

def main():
    st.title("Reagent Tray Configurator")
    
    optimizer = ReagentOptimizer()
    
    # Show available experiments
    st.subheader("Available Experiments")
    experiments = optimizer.get_available_experiments()
    available_ids = [exp["id"] for exp in experiments]
    
    # Display available experiments in a more readable format
    st.markdown("Select from the following experiments:")
    for exp in experiments:
        st.text(f"#{exp['id']}: {exp['name']}")
    
    # Input for experiment selection
    selected_experiments = st.text_input(
        "Enter experiment numbers (comma-separated)",
        placeholder="e.g., 1, 16"
    )
    
    if st.button("Optimize Configuration"):
        # Validate input
        experiments, error = validate_experiment_numbers(selected_experiments, available_ids)
        
        if error:
            st.error(error)
            return
            
        try:
            # Show optimization progress
            with st.spinner('Optimizing tray configuration...'):
                config = optimizer.optimize_tray_configuration(experiments)
            
            if not config:
                st.error("Could not find a valid configuration")
                return
            
            # Display tray configuration
            st.subheader("Tray Configuration")
            
            # Create 4x4 grid
            for row in range(4):
                cols = st.columns(4)
                for col in range(4):
                    location = row * 4 + col
                    with cols[col]:
                        render_location_card(location, config["tray_locations"][location])
            
            # Display results summary
            st.subheader("Results Summary")
            
            # Find tray life (minimum tests across experiments)
            tray_life = min(result["total_tests"] for result in config["results"].values())
            st.metric("Tray Life (Tests)", tray_life)
            
            for exp_num, result in config["results"].items():
                with st.expander(f"{result['name']} (#{exp_num}) - {result['total_tests']} total tests"):
                    for i, set_info in enumerate(result["sets"]):
                        if i == 0:
                            st.markdown("Primary Set:")
                        else:
                            st.markdown(f"Additional Set {i}:")
                            
                        for placement in set_info["placements"]:
                            st.markdown(
                                f"- {placement['reagent_code']} "
                                f"(LOC-{placement['location'] + 1}): "
                                f"{placement['tests']} tests possible"
                            )
                        st.markdown(f"Tests from this set: {set_info['tests_per_set']}")
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    st.set_page_config(
        page_title="Reagent Tray Configurator",
        page_icon="🧪",
        layout="wide",
        initial_sidebar_state="auto",
        menu_items={
            'About': "# Reagent Tray Configuration Optimizer\nOptimizes reagent placement for maximum tray life."
        }
    )
    main()
