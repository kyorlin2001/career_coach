import gradio as gr

from hf_client import generate_text


def generate_response(prompt_txt):
    return generate_text(prompt_txt, max_tokens=512, temperature=0.1)


chat_application = gr.Interface(
    fn=generate_response,
    flagging_mode="never",
    inputs=gr.Textbox(label="Input", lines=2, placeholder="Type your question here..."),
    outputs=gr.Textbox(label="Output"),
    title="Hugging Face Chatbot",
    description="Ask any question and the chatbot will try to answer.",
)

chat_application.launch(server_name="0.0.0.0")
