import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from reagent_optimizer import ReagentOptimizer

# Set page config
st.set_page_config(
    page_title="Reagent Tray Configurator",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #f0f2f6;
    }
    .main {
        padding: 2rem;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stExpander {
        background-color: white;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .css-1d391kg {
        padding-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

def get_experiment_color(experiment_name):
    color_map = {
        "Copper (II) (LR)": "gray",
        "Lead (II) Cadmium (II)": "gray",
        "Arsenic (III)": "gray",
        "Nitrates-N (LR)": "gray",
        "Chromium (VI) (LR)": "gray",
        "Manganese (II) (LR)": "gray",
        "Boron (Dissolved)": "violet",
        "Silica (Dissolved)": "violet",
        "Free Chlorine": "green",
        "Total Hardness": "orange",
        "Total Alkalinity (LR)": "white",
        "Orthophosphates-P (LR)": "orange",
        "Mercury (II)": "gray",
        "Selenium (IV)": "gray",
        "Zinc (II) (LR)": "gray",
        "Iron (Dissolved)": "blue",
        "Residual Chlorine": "green",
        "Zinc (HR)": "orange",
        "Manganese  (HR)": "violet",
        "Orthophosphates-P (HR)": "violet",
        "Total Alkalinity (HR)": "white",
        "Fluoride": "orange",
        "Boron (HR)": "gray",
        "Molybdenum": "orange",
        "Nitrates-N (HR)": "green",
        "Total Ammonia-N": "red",
        "Chromium (HR)": "blue",
        "Nitrite-N": "blue",
        "Nickel (LR)": "blue",
        "Nickel (HR)": "orange",
        "Copper (II) (HR)": "yellow",
        "Sulfate": "violet",
        "Potassium": "violet",
        "Aluminum-BB": "orange"
    }
    return color_map.get(experiment_name, "lightgray")

def create_tray_visualization(config):
    locations = config["tray_locations"]
    fig = go.Figure()

    for i, loc in enumerate(locations):
        row = i // 4
        col = i % 4
        capacity = "270mL" if i < 4 else "140mL"
        
        if loc:
            experiment_name = next((result["name"] for result in config["results"].values() if result["name"] == loc["experiment"]), "Unknown")
            color = get_experiment_color(experiment_name)
            text = f"LOC-{i+1}<br>{loc['reagent_code']}<br>Exp: {loc['experiment']}<br>{loc['tests_possible']} tests<br>{capacity}"
        else:
            color = "lightgray"
            text = f"LOC-{i+1}<br>Empty<br>{capacity}"

        fig.add_trace(go.Scatter(
            x=[col, col+1, col+1, col, col],
            y=[row, row, row+1, row+1, row],
            fill="toself",
            fillcolor=color,
            line=dict(color="black", width=1),
            mode="lines+text",
            name=f"LOC-{i+1}",
            text=text,
            textposition="middle center",
            textfont=dict(size=8, color="black"),
            hoverinfo="none"
        ))

    fig.update_layout(
        title="Tray Configuration",
        showlegend=False,
        height=600,
        width=800,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig

def main():
    st.title("🧪 Reagent Tray Configurator")
    
    optimizer = ReagentOptimizer()
    experiments = optimizer.get_available_experiments()

    st.sidebar.header("Available Experiments")
    selected_experiments = []
    for exp in experiments:
        if st.sidebar.checkbox(f"{exp['id']}: {exp['name']}", key=f"exp_{exp['id']}"):
            selected_experiments.append(exp['id'])

    st.sidebar.markdown("---")
    st.sidebar.markdown("Or enter experiment numbers manually:")
    manual_input = st.sidebar.text_input("Experiment numbers (comma-separated)", placeholder="e.g., 1, 16, 29")

    if manual_input:
        selected_experiments = [int(num.strip()) for num in manual_input.split(',') if num.strip()]

    if st.sidebar.button("Optimize Configuration", key="optimize_button"):
        if not selected_experiments:
            st.sidebar.error("Please select at least one experiment")
        else:
            try:
                with st.spinner("Optimizing tray configuration..."):
                    config = optimizer.optimize_tray_configuration(selected_experiments)

                col1, col2 = st.columns([3, 2])

                with col1:
                    st.subheader("Tray Configuration")
                    fig = create_tray_visualization(config)
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    st.subheader("Results Summary")
                    tray_life = min(result["total_tests"] for result in config["results"].values())
                    st.metric("Tray Life (Tests)", tray_life)

                    results_df = pd.DataFrame([
                        {
                            "Experiment": f"{result['name']} (#{exp_num})",
                            "Total Tests": result["total_tests"]
                        }
                        for exp_num, result in config["results"].items()
                    ])
                    st.dataframe(results_df, use_container_width=True)

                st.subheader("Detailed Results")
                for exp_num, result in config["results"].items():
                    with st.expander(f"{result['name']} (#{exp_num}) - {result['total_tests']} total tests"):
                        for i, set_info in enumerate(result["sets"]):
                            st.markdown(f"**{'Primary' if i == 0 else 'Additional'} Set {i+1}:**")
                            set_df = pd.DataFrame([
                                {
                                    "Reagent": placement["reagent_code"],
                                    "Location": f"LOC-{placement['location'] + 1}",
                                    "Tests Possible": placement["tests"]
                                }
                                for placement in set_info["placements"]
                            ])
                            st.dataframe(set_df, use_container_width=True)
                            st.markdown(f"**Tests from this set:** {set_info['tests_per_set']}")
                            st.markdown("---")

            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### How to use")
    st.sidebar.markdown("""
    1. Select experiments using checkboxes or enter numbers manually
    2. Click 'Optimize Configuration'
    3. View the tray visualization and results summary
    4. Expand detailed results for each experiment
    """)

if __name__ == "__main__":
    main()

