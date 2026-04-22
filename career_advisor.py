import gradio as gr

from hf_client import generate_text


def generate_career_advice(position_applied, job_description, resume_content):
    prompt = (
        f"Write ATS-friendly career advice for the position: {position_applied}.\n\n"
        f"Job description:\n{job_description}\n\n"
        f"Resume:\n{resume_content}\n\n"
        f"Identify specific ways to improve the resume for this role. "
        f"Use only the information provided. Do not invent experience. "
        f"Keep the advice natural, professional, concise, and easy to scan."
    )
    return generate_text(prompt, max_tokens=1024, temperature=0.7)


def build_ui():
    return gr.Interface(
        fn=generate_career_advice,
        flagging_mode="never",
        inputs=[
            gr.Textbox(label="Position Applied For", placeholder="Enter the position you are applying for..."),
            gr.Textbox(label="Job Description Information", placeholder="Paste the job description here...", lines=10),
            gr.Textbox(label="Your Resume Content", placeholder="Paste your resume content here...", lines=10),
        ],
        outputs=gr.Textbox(label="Advice"),
        title="Career Advisor",
        description="Enter the position you're applying for, paste the job description, and your resume content to get advice on how to improve your application.",
    )
