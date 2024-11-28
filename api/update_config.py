from http.server import BaseHTTPRequestHandler
import json
from reagent_optimizer import ReagentOptimizer

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        # Get the current config and selected experiments from session state
        config = self.server.app.session_state.config
        selected_experiments = self.server.app.session_state.selected_experiments

        # Update the config
        source = data['source']
        target = data['target']
        optimizer = ReagentOptimizer()
        updated_config = update_config_after_manual_change(config, source, target)

        # Save the updated config to session state
        self.server.app.session_state.config = updated_config

        # Send the response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = json.dumps({
            'success': True,
            'config': updated_config,
            'selected_experiments': selected_experiments
        })
        self.wfile.write(response.encode('utf-8'))

def update_config_after_manual_change(config, source, target):
    source_loc = config["tray_locations"][source]
    target_loc = config["tray_locations"][target]
    
    config["tray_locations"][source], config["tray_locations"][target] = target_loc, source_loc

    # Recalculate total tests and update sets
    optimizer = ReagentOptimizer()
    optimizer._recalculate_total_tests(config)

    return config

