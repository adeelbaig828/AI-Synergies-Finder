import openai
import copy
import tiktoken
openai.api_key = "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"
open_ai_model = "gpt-3.5-turbo-16k"
gpt_response_format = {
    "success": True,
    "success_response": "",
    "input_tokens": 0,
    "total_tokens": 0,
    "error_message": "",
}


def num_tokens_from_messages(messages, model=open_ai_model):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-3.5-turbo-16k",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
    }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_message = 4
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print(
            "Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613."
        )
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print(
            "Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613."
        )
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def call_gpt_api(parameters):
    final_response = copy.deepcopy(gpt_response_format)
    my_personal_information = parameters["my_profile_data"]
    other_person_information = parameters["other_profile_data"]
    session_id = parameters["session_id"]
    messages = [
        {
            "role": "system",
            "content": "I want you to act as synergies finder between My Profile Data and Other Person Profile Data and based on these synergies you will generate a text message for the Other Person so I can connect with him on LinkedIn. The generated message is realistic. You will only generate message and nothing else.",
        },
        {
            "role": "user",
            "content": f"My Personal Data and My Company Data is\n {my_personal_information} and Other Person data and his Company Data is \n {other_person_information}",
        },
    ]
    tokens_counted_by_client = num_tokens_from_messages(messages)
    if tokens_counted_by_client > 15000:
        final_response["success"] = False
        final_response["input_tokens"] = tokens_counted_by_client
        final_response["error_message"] = "Input Tokens cannot be greater than 15000."
        return final_response

    with open(f"{session_id}_my_personal_information.txt", "w", encoding="utf-8") as f:
        f.write(my_personal_information)
    with open(f"{session_id}_other_person_information.txt", "w", encoding="utf-8") as f:
        f.write(other_person_information)
    try:
        response = openai.ChatCompletion.create(
            model=open_ai_model,
            messages=messages,
            temperature=0.7,
            # we're only counting input tokens here, so let's not waste tokens on the output
            max_tokens=16000 - tokens_counted_by_client,
        )
    except Exception as ex:
        final_response["success"] = False
        final_response[
            "error_message"
        ] = f"An Error Occured while Calling API : {str(ex)}"
        return final_response
    print("========================================================================")
    final_response["input_tokens"] = response["usage"]["prompt_tokens"]
    final_response["total_tokens"] = response["usage"]["total_tokens"]
    final_response["success_response"] = response["choices"][0]["message"]["content"]
    print(response)
    print(final_response)
    return final_response
    print("========================================================================")
