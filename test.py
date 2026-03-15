from IPython.display import Image, display

from app.main_agent import main_agent
graph_png = main_agent.get_graph().draw_mermaid_png()

# Save the binary data to a file
with open("graph_image.png", "wb") as f:
    f.write(graph_png)