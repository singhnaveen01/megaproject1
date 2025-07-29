import openai

openai.api_key = "sk-..."  # use your real key

try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Hello, who are you?"}
        ]
    )
    print("✅ Response:", response.choices[0].message.content)

except Exception as e:
    print("❌ Error:", e)
