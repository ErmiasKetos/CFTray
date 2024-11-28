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

    # Initialize session state for selected experiments
    if "selected_experiments" not in st.session_state:
        st.session_state.selected_experiments = []

    if "experiment_input" not in st.session_state:
        st.session_state.experiment_input = ""

    st.subheader("Available Experiments")
    experiments = optimizer.get_available_experiments()

    # Checkbox list for experiments
    selected_experiments = []
    for exp in experiments:
        if st.checkbox(f"{exp['id']}: {exp['name']}", key=f"exp_{exp['id']}"):
            selected_experiments.append(exp['id'])

    # Text input for manual experiment selection
    st.text_input(
        "Or enter experiment numbers (comma-separated)", 
        placeholder="e.g., 1, 16",
        key="experiment_input"
    )

    # Add selected experiments from text input to checkbox selections
    if st.session_state.experiment_input:
        selected_experiments.extend(
            [int(num.strip()) for num in st.session_state.experiment_input.split(',') if num.strip()]
        )

    # Reset Button to Clear Checkboxes and Input Box
    if st.button("Reset Selection"):
        # Clear all checkboxes
        for exp in experiments:
            st.session_state[f"exp_{exp['id']}"] = False
        # Clear text input
        st.session_state.experiment_input = ""
        st.session_state.selected_experiments = []
        st.experimental_rerun()

    # Optimize Configuration Button
    if st.button("Optimize Configuration"):
        if not selected_experiments:
            st.error("Please select or enter experiment numbers")
            return

        try:
            config = optimizer.optimize_tray_configuration(selected_experiments)
            st.subheader("Tray Configuration")
            for row in range(4):
                cols = st.columns(4)
                for col in range(4):
                    location = row * 4 + col
                    with cols[col]:
                        render_location_card(location, config["tray_locations"][location])

            st.subheader("Results Summary")
            tray_life = min(result["total_tests"] for result in config["results"].values())
            for exp_num, result in config["results"].items():
                with st.expander(f"{result['name']} (#{exp_num}) - {result['total_tests']} total tests"):
                    for i, set_info in enumerate(result["sets"]):
                        set_label = "Primary Set:" if i == 0 else f"Additional Set {i}:"
                        st.markdown(set_label)
                        for placement in set_info["placements"]:
                            st.markdown(
                                f"- {placement['reagent_code']} "
                                f"(LOC-{placement['location'] + 1}): "
                                f"{placement['tests']} tests possible"
                            )
                        st.markdown(f"Tests from this set: {set_info['tests_per_set']}")

            st.metric("Tray Life (Tests)", tray_life)

        except ValueError as e:
            st.error(str(e))
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
