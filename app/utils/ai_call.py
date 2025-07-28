from openai import OpenAI

# custom imports
from app.config import gemini_api_key

client = OpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def process_image_with_ai(image_base64: str):
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            { 
                "type": "input_text", "text": "Based on the image, Roast the resume" 
            },
            {
                "type": "input_image",
                "image_url": f"data:image/jpeg;base64,{image_base64}",
            },
        ]
    )
    
    return response.choices[0].message.content if response.choices else None