from google import genai

API_KEY = "***********************************"

client = genai.Client(api_key=API_KEY)

response = client.models.generate_content(
    model="gemini-2.0-flash",
)

print(response.text)
