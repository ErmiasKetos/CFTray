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

def main():
    st.title("Reagent Tray Configurator")
    
    optimizer = ReagentOptimizer()
    
    # Show available experiments
    st.subheader("Available Experiments")
    experiments = optimizer.get_available_experiments()
    for exp in experiments:
        st.text(f"{exp['id']}: {exp['name']}")
    
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
            experiments = [
                int(num.strip()) 
                for num in selected_experiments.split(',') 
                if num.strip()
            ]
            
            # Validate input
            available_ids = [exp["id"] for exp in optimizer.get_available_experiments()]
            invalid_experiments = [exp for exp in experiments if exp not in available_ids]
            
            if invalid_experiments:
                st.error(f"Invalid experiment numbers: {', '.join(map(str, invalid_experiments))}")
                return
            
            # Get optimized configuration
            config = optimizer.optimize_tray_configuration(experiments)
            
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
            
            for exp_num, result in config["results"].items():
                with st.expander(f"{result['name']} (#{exp_num}) - {result['total_tests']} total tests"):
                    for set_idx, set_info in enumerate(result["sets"], 1):
                        st.markdown(f"**Set {set_idx}:**")
                        st.markdown(f"Tests per set: {set_info['tests_per_set']}")
                        for placement in set_info["placements"]:
                            st.markdown(
                                f"- {placement['reagent_code']} "
                                f"(LOC-{placement['location'] + 1}): "
                                f"{placement['tests']} tests possible"
                            )
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
