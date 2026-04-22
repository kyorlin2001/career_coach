import gradio as gr

from career_advisor import generate_career_advice
from cover_letter import generate_cover_letter
from resume_polisher import polish_resume, extract_resume_text
from hf_client import generate_text


def general_chat(prompt: str) -> str:
    prompt_text = (
        "You are a helpful career coach assistant.\n\n"
        f"User question:\n{prompt}\n\n"
        "Answer clearly, professionally, and concisely."
    )
    return generate_text(prompt_text, max_tokens=512, temperature=0.7)


def load_resume_into_textbox(resume_file):
    if not resume_file:
        return ""

    try:
        return extract_resume_text(resume_file, "")
    except Exception as exc:
        return f"Could not extract text from uploaded file: {exc}"


with gr.Blocks(title="Career Coach") as demo:
    gr.Markdown(
        """
        # Career Coach

        A unified Gradio app for career advice, cover letters, resume polishing, and general chat.
        """
    )

    with gr.Tabs():
        with gr.Tab("Career Advisor"):
            gr.Markdown("Get ATS-focused advice to improve a resume for a specific role.")
            position_applied = gr.Textbox(label="Position Applied For")
            job_description = gr.Textbox(label="Job Description", lines=10)
            resume_content = gr.Textbox(label="Resume Content", lines=10)
            advisor_output = gr.Textbox(label="Advice")
            advisor_button = gr.Button("Generate Advice")
            advisor_button.click(
                fn=generate_career_advice,
                inputs=[position_applied, job_description, resume_content],
                outputs=advisor_output,
            )

        with gr.Tab("Cover Letter"):
            gr.Markdown("Draft a tailored cover letter using the job and resume details you provide.")
            company_name = gr.Textbox(label="Company Name")
            position_name = gr.Textbox(label="Position Name")
            cover_job_description = gr.Textbox(label="Job Description", lines=10)
            cover_resume_content = gr.Textbox(label="Resume Content", lines=10)
            cover_output = gr.Textbox(label="Cover Letter")
            cover_button = gr.Button("Generate Cover Letter")
            cover_button.click(
                fn=generate_cover_letter,
                inputs=[company_name, position_name, cover_job_description, cover_resume_content],
                outputs=cover_output,
            )

        with gr.Tab("Resume Polisher"):
            gr.Markdown("Upload a resume file or paste text, then get a polished version and a downloadable PDF.")
            polish_position = gr.Textbox(label="Position Name")
            polish_file = gr.File(
    label="Resume File (Optional)",
    file_count="single",
    file_types=[".pdf", ".docx", ".odt", ".txt", ".md"],
    type="filepath",
)
            polish_resume_content = gr.Textbox(
                label="Resume Content (Optional)",
                lines=20,
                placeholder="Upload a resume file or paste resume text here...",
            )
            polish_instruction = gr.Textbox(label="Polish Instruction (Optional)", lines=2)
            polish_output = gr.Textbox(label="Polished Resume")
            polish_pdf = gr.File(label="Downloadable PDF")
            polish_button = gr.Button("Polish Resume")

            polish_file.upload(
                fn=load_resume_into_textbox,
                inputs=polish_file,
                outputs=polish_resume_content,
            )

            polish_button.click(
                fn=polish_resume,
                inputs=[polish_position, polish_file, polish_resume_content, polish_instruction],
                outputs=[polish_output, polish_pdf],
            )

        with gr.Tab("General Chat"):
            gr.Markdown("Ask a general career question or use it as a simple chatbot demo.")
            chat_input = gr.Textbox(label="Your Question", lines=3)
            chat_output = gr.Textbox(label="Answer")
            chat_button = gr.Button("Ask")
            chat_button.click(
                fn=general_chat,
                inputs=chat_input,
                outputs=chat_output,
            )

    gr.Markdown(
        """
        ## Notes

        - Uses a shared Hugging Face inference helper
        - Keeps the individual tools separate while presenting them in one app
        - Designed for Hugging Face Spaces deployment
        """
    )

demo.launch(server_name="0.0.0.0")