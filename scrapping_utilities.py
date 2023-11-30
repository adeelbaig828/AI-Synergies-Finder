import json
import copy
scrapped_data_format = {
    "url": '',
    "name": "",
    "bio": "",
    "company_name": "",
    "dob_from_contact_info": "",
    "location": "",
    "company_url": "",
    "followers_count": "",
    "connects_count": "",
    "mutual_connects": "",
    "open_to_work_status": "",
    "job_preferences": "",
    "about": "",
    "experiences": [],
    "education": [],
    "skills": [],
    "languages": [],
    "top_5_voices": [],
    "top_5_companies": [],
    "top_5_groups": [],
    "top_5_schools": []
}
person_experience_format = {"job_title": "",
                            "company_name": "",
                            "work_duration": "",
                            "company_location": ""
                            }
person_education_format = {"institute_name": "",
                           "degree_title": "", "duration": ""}
top_statistics_format = {"title": "", "link": ""}
company_about_format = {
    "overview": "",
    "other_info_list":[]
}
company_employee_information_format = {
    "name": "",
    "bio": ""
}
scrapped_company_data_format = {
    "name": "",
    "bio": "",
    "locations": "",
    "followers_count": "",
    "employee_count": "",
    "industry":"",
    "website_url":"",
    "company_about": company_about_format,
    "top_5_posts": [],
    "company_employee_statistics": []
}
script_to_slowly_scroll = '''
            function slowScroll(duration) {
            const scrollHeight = document.documentElement.scrollHeight;
            const windowHeight = window.innerHeight;
            const scrollStep = (scrollHeight - windowHeight) / (duration / 60);
            let scrollPos = 0;
            let startTime = null;

            function scrollToBottom(timestamp) {
                if (!startTime) {
                startTime = timestamp;
                }

                const elapsed = timestamp - startTime;
                scrollPos = scrollStep * elapsed / 15;

                if (scrollPos <= scrollHeight) {
                window.scrollTo(0, scrollPos);
                window.requestAnimationFrame(scrollToBottom);
                }
            }

            window.requestAnimationFrame(scrollToBottom);
            }

            // Call the slowScroll function with a duration of 5000 milliseconds (5 seconds)
            slowScroll(3000);

            '''

def remove_newlines(text):
    return text.replace('\n', '')

def object_to_text(obj):
    text = ""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                text += object_to_text(value)
            else:
                text += f"{key}: {str(value)}*___*"
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                text += object_to_text(item)
            else:
                text += f"- {str(item)}*___*"

    # if heading:
    #     text = heading + ":\n" + text
    text = remove_newlines(text)
    return text.strip()

def generate_text_description(data):
    text = "The Person Profile Data\n"
    text += object_to_text(data.get("person_profile_data"))
    text += "\n\n\nThe Company Profile Data\n"
    text += object_to_text(data.get("company_profile_data"))
    return text


def optimize_response(json_data):
    try:
        data_dict = json.loads(json_data)
        person_profile_data = data_dict.get("person_profile_data", {})
        company_profile_data = data_dict.get("company_profile_data", {})
        
        person_profile_data["experiences"] = person_profile_data.get("experiences", [])[:5]
        person_profile_data["education"] = person_profile_data.get("education", [])[:5]
        person_profile_data["top_5_voices"] =copy.deepcopy(person_profile_data["top_5_voices"][:5])
        person_profile_data["top_5_companies"] =copy.deepcopy(person_profile_data["top_5_companies"][:5])
        person_profile_data["top_5_groups"] =copy.deepcopy(person_profile_data["top_5_groups"][:5])
        person_profile_data["top_5_schools"] =copy.deepcopy(person_profile_data["top_5_schools"][:5])
        
        #--------------------------------------------------------------------------------------------
        company_profile_data["top_5_posts"] =company_profile_data.get("top_5_posts", [])[:5]
        object_to_return = {
            "person_profile_data": person_profile_data,
            "company_profile_data": company_profile_data,
        }
        return object_to_return
    except json.JSONDecodeError:
        print("Error: Invalid JSON data.")
        return {}  
    except Exception as ex:
        print(f"Error occurred during response optimization: {str(ex)}")
        return {}  


import json

def remove_text_after_newline(json_data):
    def process_value(value):
        if isinstance(value, str):
            newline_index = value.find("\n")
            if newline_index != -1:
                value = value[:newline_index]
        return value

    def traverse(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                obj[key] = process_value(value)
                traverse(value)
        elif isinstance(obj, list):
            for index, item in enumerate(obj):
                obj[index] = process_value(item)
                traverse(item)

    try:
        data_dict = json.loads(json_data)
        traverse(data_dict)
        return json.dumps(data_dict)
    except json.JSONDecodeError:
        print("Error: Invalid JSON data.")
        return None
    except Exception as ex:
        print(f"Error occurred during text removal: {str(ex)}")
        return None
