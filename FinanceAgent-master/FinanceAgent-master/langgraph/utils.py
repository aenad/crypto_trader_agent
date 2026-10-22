from typing import Any, Dict
from langgraph.graph import StateGraph

def save_graph_visualization(app, filename="sql_agent_graph.png"):
    """Save the graph visualization to a file"""
    try:
        # Create the graph visualization
        graph = app.get_graph(xray=True)
        png_data = graph.draw_mermaid_png()
        with open("mermaid_"+filename, "wb") as f:
            f.write(png_data)
        png_data = graph.draw_png()
        # Save to file
        with open(filename, "wb") as f:
            f.write(png_data)
        print(f"Graph visualization saved to {filename}")
    except Exception as e:
        print(f"Error saving graph visualization: {e}")

def update_request_status(status: str, details: Dict[str, Any]) -> None:
    """
    Update the status of a request.
    
    Args:
        status: The new status
        details: Additional details about the status
    """
    # Implementation of status update logic
    pass 