import gradio as gr

from hf_client import generate_text


def generate_cover_letter(company_name, position_name, job_description, resume_content):
    prompt = (
        f"Write a customized cover letter for {position_name} at {company_name}.\n\n"
        f"Job description:\n{job_description}\n\n"
        f"Resume:\n{resume_content}\n\n"
        f"Use only the information provided. Do not invent experience, metrics, or skills. "
        f"Keep the tone natural, professional, concise, and ATS-friendly. "
        f"Avoid generic AI-sounding phrases, unusual punctuation, decorative symbols, and filler language. "
        f"Make it sound like a real applicant wrote it."
    )
    return generate_text(prompt, max_tokens=512, temperature=0.7)


def build_ui():
    return gr.Interface(
        fn=generate_cover_letter,
        flagging_mode="never",
        inputs=[
            gr.Textbox(label="Company Name", placeholder="Enter the name of the company..."),
            gr.Textbox(label="Position Name", placeholder="Enter the name of the position..."),
            gr.Textbox(label="Job Description Information", placeholder="Paste the job description here...", lines=10),
            gr.Textbox(label="Resume Content", placeholder="Paste your resume content here...", lines=10),
        ],
        outputs=gr.Textbox(label="Customized Cover Letter"),
        title="Customized Cover Letter Generator",
        description="Generate a customized cover letter by entering the company name, position name, job description, and your resume.",
    )
