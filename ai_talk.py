

from openai import OpenAI

client = OpenAI(
    api_key="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",
)

completion= client.chat.completions.create(
    model = "gpt-3.5-turbo",
    messages=[
        { "role": "system","content":"you are a vitrtual assistent named jarvvis skilled in general task like alexa and google"},
        {"role": "user","content":"compose a poem that explain the concept of recursion in programming"}
    ]
)
print(completion.choices[0].message.content)


