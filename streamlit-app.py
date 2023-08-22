import streamlit as st
import json
import requests
import openai
import time


def text_inputbox():
    input = st.text_area(label="Write your code request", height=200, key="text_area")
    return input


def model_selection():
    return st.multiselect("Select model", [
        "tiiuae/falcon-7b-instruct",
        "bigcode/starcoder",
        "text-davinci-003",
        "gpt-3.5-turbo",
        "text-davinci-002",
        # "openchat/openchat_v2_openorca_preview"
        "NinedayWang/PolyCoder-0.4B",
        "bigscience/bloom"
    ])


def send_button():
    prompt = text_inputbox()
    bt = st.button("send")
    if bt:
        s = len(st.session_state["models"])
        tab_labels = [str(st.session_state["models"][i]) for i in range(s)]

        for i, tab_label in enumerate(tab_labels):
            with st.expander(tab_label):  # Use st.expander instead of st.tabs to create headings
                if "/" in tab_label:
                    start_time = time.time()
                    generated_text = connect_to_llm(tab_label, prompt)
                    end_time = time.time()
                    response_time = end_time - start_time
                    generated_text = generated_text[0].values()
                    st.write(f"API Response Time: {response_time:.2f} seconds")
                    display_code(*generated_text)
                else:
                    start_time = time.time()
                    generated_text = connect_to_op(prompt, st.session_state.OP_KEY, tab_label)
                    end_time = time.time()
                    response_time = end_time - start_time
                    st.write(f"API Response Time: {response_time:.2f} seconds")
                    display_code(generated_text)


def save_apis():
    openai_key = st.text_input("Enter OPENAI key", type="password")
    if openai_key:
        st.session_state["OP_KEY"] = openai_key

    huggingface_token = st.text_input("Enter HUGGINGFACE API Token", type="password")
    if huggingface_token:
        st.session_state["HG_KEY"] = huggingface_token


def side():
    with st.sidebar:
        save_apis()
        models = model_selection()
        st.session_state["models"] = models


def display_code(content):
    return st.code(content)


def connect_to_op(prompt, api_key, model):
    openai.api_key = api_key
    if model == "gpt-3.5-turbo":
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}]
        )

        return response['choices'][0]['message']['content'].strip()
    else:
        response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        max_tokens=200
    )

    return response['choices'][0]['text'].strip()


def connect_to_llm(model,prompt):
    API_URL = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {st.session_state.HG_KEY}"}


    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
    
    output = query({
	"inputs": f"{prompt}",
})  
    return output

if __name__ == "__main__":
    side()
    send_button()
