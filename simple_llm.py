from hf_client import generate_text


def main():
    prompt_txt = "How to be a good Data Scientist?"
    response = generate_text(prompt_txt, max_tokens=256, temperature=0.7)
    print(response)


if __name__ == "__main__":
    main()