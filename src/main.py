from ollama import Client
import requests
import html2text
import json

def count_tokens(prompt, model="llama2"):
    url = "http://localhost:11434/api/tokenize"

    data = {
        "model": model,
        "prompt": prompt
    }

    response = requests.post(url, json=data)

    if response.status_code == 200:
        result = json.loads(response.text)
        return len(result['tokens'])
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")



print ("hi there")
exit(0)



client = Client(host='http://localhost:11434')

template = """Use the following web page export to answer the question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Use three sentences maximum and keep the answer as concise as possible.
    --- BEGIN CONTEXT --- 
    {context}
    --- END CONTEXT --- 
    Please summarize the web page in 3 to 4 sentences."""


def url_to_markdown(url):
    # Fetch the webpage content
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses

    # Convert HTML to markdown
    html_content = response.text
    markdown_converter = html2text.HTML2Text()
    markdown_converter.ignore_links = False
    markdown_content = markdown_converter.handle(html_content)

    return markdown_content


# web = url_to_markdown("https://github.com/dfsp-spirit")
raw = url_to_markdown("https://github.com/dfsp-spirit/freesurferformats")

web = raw[0:30000]

print (web)




print ("web page size was {size} btyes\n\n".format(size=len(web)))



stream = client.chat(
#    model='llama3.1',
    model='gemma2:2b',
#    model='phi',
    messages=[{'role': 'user', 'content': template.format(context=web)}],
    stream=True,
)


for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)
    if (chunk.keys().__contains__("done") and chunk['done']):
        t = (chunk["total_duration"] / 1000000000)
        intok = chunk['prompt_eval_count']
        outtok = chunk['eval_count']
        print ("\n\nTotal time {time} input tokens {intok} output tokens {outtok}".format(time=t,intok=intok,outtok=outtok))
