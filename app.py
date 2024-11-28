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

def get_reagent_color(reagent_code):
    color_map = {
        'gray': ['KR1E', 'KR1S', 'KR2S', 'KR3E', 'KR3S', 'KR4E', 'KR4S', 'KR5E', 'KR5S', 'KR6E1', 'KR6E2', 'KR6E3', 'KR13E1', 'KR13S', 'KR14E', 'KR14S', 'KR15E', 'KR15S'],
        'violet': ['KR7E1', 'KR7E2', 'KR8E1', 'KR8E2', 'KR19E1', 'KR19E2', 'KR19E3', 'KR20E', 'KR36E1', 'KR36E2', 'KR40E1', 'KR40E2'],
        'green': ['KR9E1', 'KR9E2', 'KR17E1', 'KR17E2', 'KR17E3', 'KR28E1', 'KR28E2', 'KR28E3'],
        'orange': ['KR10E1', 'KR10E2', 'KR10E3', 'KR12E1', 'KR12E2', 'KR12E3', 'KR18E1', 'KR18E2', 'KR22E1', 'KR27E1', 'KR27E2', 'KR42E1', 'KR42E2'],
        'white': ['KR11E', 'KR21E1'],
        'blue': ['KR16E1', 'KR16E2', 'KR16E3', 'KR16E4', 'KR30E1', 'KR30E2', 'KR30E3', 'KR31E1', 'KR31E2', 'KR34E1', 'KR34E2'],
        'red': ['KR29E1', 'KR29E2', 'KR29E3'],
        'yellow': ['KR35E1', 'KR35E2']
    }
    for color, reagents in color_map.items():
        if any(reagent_code.startswith(r) for r in reagents):
            return color
    return 'lightgray'  # Default color if not found

def create_tray_visualization(config):
    locations = config["tray_locations"]
    fig = go.Figure()

    for i, loc in enumerate(locations):
        row = i // 4
        col = i % 4
        color = get_reagent_color(loc['reagent_code']) if loc else 'lightgray'
        opacity = 0.8 if loc else 0.2

        fig.add_trace(go.Scatter(
            x=[col, col+1, col+1, col, col],
            y=[row, row, row+1, row+1, row],
            fill="toself",
            fillcolor=color,
            opacity=opacity,
            line=dict(color="black", width=1),
            mode="lines",
            name=f"LOC-{i+1}",
            text=f"LOC-{i+1}<br>{loc['reagent_code'] if loc else 'Empty'}<br>Tests: {loc['tests_possible'] if loc else 'N/A'}<br>Exp: #{loc['experiment'] if loc else 'N/A'}",
            hoverinfo="text"
        ))

        # Add text annotation
        fig.add_annotation(
            x=(col + col + 1) / 2,
            y=(row + row + 1) / 2,
           text=f"<b>LOC-{i+1}</b><br>{'<b>' + loc['reagent_code'] if loc else 'Empty</b>'}<br>Tests: {loc['tests_possible'] if loc else 'N/A'}<br>Exp: #{loc['experiment'] if loc else 'N/A'}",
            showarrow=False,
            font=dict(color="black", size=16),
            align="center",
            xanchor="center",
            yanchor="middle"
        )

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

def display_results(config, selected_experiments):
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
                "Total Tests": result['total_tests']
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

def reset_app():
    """Clears all session state variables to reset the app."""
    for key in list(st.session_state.keys()):
        if key.startswith('exp_'):
            st.session_state[key] = False
        else:
            del st.session_state[key]

def main():
    st.title("🧪 Reagent Tray Configurator")
    
    # Initialize session state
    if 'config' not in st.session_state:
        st.session_state.config = None
    if 'selected_experiments' not in st.session_state:
        st.session_state.selected_experiments = []

    optimizer = ReagentOptimizer()
    experiments = optimizer.get_available_experiments()

    # Reset Button
    if st.sidebar.button("Reset All", key="reset_button"):
        reset_app()
        st.rerun()

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

    optimize_button = st.sidebar.button("Optimize Configuration", key="optimize_button")

    if optimize_button:
        if not selected_experiments:
            st.sidebar.error("Please select at least one experiment")
        else:
            try:
                with st.spinner("Optimizing tray configuration..."):
                    config = optimizer.optimize_tray_configuration(selected_experiments)
                st.session_state.config = config
                st.session_state.selected_experiments = selected_experiments
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    if st.session_state.config is not None:
        display_results(st.session_state.config, st.session_state.selected_experiments)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### How to use")
    st.sidebar.markdown("""
    1. Select experiments using checkboxes or enter numbers manually
    2. Click 'Optimize Configuration'
    3. View the tray visualization and results summary
    4. Expand detailed results for each experiment
    5. Click 'Reset All' to start fresh
    """)

if __name__ == "__main__":
    main()

