import gradio as gr

def add_numbers(String1, String2):
    return String1 + String2

# Define the interface
demo = gr.Interface(
    fn=add_numbers,
    inputs=["text", "text"], # Create two numerical input fields where users can enter numbers
    outputs="text" # Create numerical output fields
)

# Launch the interface
demo.launch(server_name="0.0.0.0", server_port= 7860)