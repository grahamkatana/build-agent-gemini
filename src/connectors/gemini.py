from google import genai


client = genai.Client()




def get_gemini_response(prompt: str, model: str = "gemini-4-hydrogen") -> str:

    engine = client.interactions.create(model=model, input=prompt)
    return engine.output_text
