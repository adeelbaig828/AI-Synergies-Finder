import random
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from Scrapping_API.gpt_utilities import call_gpt_api
from Scrapping_API.scrapping_utilities import generate_text_description
from Scrapping_API.scrapping_utilities import script_to_slowly_scroll as script
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import OTP
from Scrapping_API.scrapping_utilities import (
    scrapped_data_format,
    person_experience_format,
    person_education_format,
    top_statistics_format,
    scrapped_company_data_format,
    company_about_format,
    optimize_response,
    remove_text_after_newline,
    
)
from pdfminer.high_level import extract_text
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from io import BytesIO
from pdfminer.high_level import extract_text_to_fp
from django.shortcuts import render, redirect
from rest_framework import views
from django.shortcuts import render
from rest_framework.response import Response
from Scrapping_API.serializers import (
    URLSerializer,
    GPTSerializer,
    SignUpSerializer,
    ForgotPasswordSerializer,
    SetNewPasswordSerializer,
)
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import copy
import pickle
import json
import os
from django.http import JsonResponse
import openai
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.response import Response
from rest_framework import status


openai.api_key = "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"


chrome_driver_path = r"C:\chromedriver.exe"
cache_file_path = "LinkedInCache.pickle"
cache_exists = os.path.isfile(cache_file_path)

driver = webdriver.Chrome()
if cache_exists:
    driver.get("https://linkedin.com/")
    # time.sleep(2)
    cookies = pickle.load(open(cache_file_path, "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)
else:
    driver.get("https://linkedin.com/")
    time.sleep(2)
    linkedin_user = driver.find_element(By.XPATH, '//*[@id="session_key"]')
    linkedin_user.send_keys("lirm.imran@gmail.com")

    linkedin_pass = driver.find_element(By.XPATH, '//*[@id="session_password"]')
    linkedin_pass.send_keys("xfalcon9217")
    time.sleep(1.5)

    linkedin_login = driver.find_element(
        By.XPATH, '//*[@id="main-content"]/section[1]/div/div/form[1]/div[2]/button'
    )
    linkedin_login.click()
    time.sleep(5)
    pickle.dump(driver.get_cookies(), open(cache_file_path, "wb"))


def is_access_token_valid(request):
    try:
        if "access_token" in request.COOKIES:
            access_token = request.COOKIES["access_token"]
            jwt_object = JWTAuthentication()
            validated_token = jwt_object.get_validated_token(access_token)
            return True
        else:
            return False
    except AuthenticationFailed:
        return False

#dev-optimization
class URLView(views.APIView):
    # authentication_classes = [JWTAuthentication]  # Apply JWT authentication
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = URLSerializer(data=request.data)
        if serializer.is_valid():
            scrapped_data = copy.deepcopy(scrapped_data_format)
            errors_list = []

            scrapped_data["url"] = serializer.validated_data["url"]
            driver.get(scrapped_data["url"])
            time.sleep(0.5)

            try:
                Name = driver.find_element(By.CLASS_NAME, "text-heading-xlarge")
                scrapped_data["name"] = Name.text
            except Exception as ex:
                errors_list.append(f"Error Occured while scrapping Name : {str(ex)}")

            try:
                BIO = driver.find_element(By.CLASS_NAME, "text-body-medium")
                scrapped_data["bio"] = BIO.text
            except Exception as ex:
                errors_list.append(f"Error Occured while scrapping BIO : {str(ex)}")

            try:
                Location = driver.find_element(
                    By.CSS_SELECTOR,
                    "span.text-body-small.inline.t-black--light.break-words",
                )
                scrapped_data["location"] = Location.text
            except Exception as ex:
                errors_list.append(
                    f"Error Occured while scrapping Location : {str(ex)}"
                )

            try:
                Compnay_still_working = driver.find_element(
                    By.CSS_SELECTOR,
                    "div.inline-show-more-text.inline-show-more-text--is-collapsed.inline-show-more-text--is-collapsed-with-line-clamp.inline",
                )
                scrapped_data["company_name"] = Compnay_still_working.text
            except Exception as ex:
                errors_list.append(
                    f"Error Occured while scrapping Company Name : {str(ex)}"
                )
            # try:
            #     Web_url = driver.find_element(
            #         By.CSS_SELECTOR, "a.app-aware-link[data-test-app-aware-link]")
            #     Web_url = Web_url.get_attribute("href")
            #     scrapped_data["company_url"] = Web_url
            # except Exception as ex:
            #     errors_list.append(
            #         f"Error Occured while scrapping Company URL : {str(ex)}")

            try:
                about = driver.find_element(
                    By.CSS_SELECTOR, "div.pv-shared-text-with-see-more"
                )
                scrapped_data["about"] = about.text
            except Exception as ex:
                errors_list.append(f"Error Occured while scrapping About : {str(ex)}")

            # ---------- Connects
            try:
                followers_element = driver.find_element(
                    By.CSS_SELECTOR, "li.text-body-small.t-black--light.inline-block"
                )
                followers_count = followers_element.find_element(
                    By.CSS_SELECTOR, "span.t-bold"
                ).text
                followers_info = f"{followers_count} followers"

                connections_element = driver.find_element(
                    By.CSS_SELECTOR, "li.text-body-small:nth-of-type(2)"
                )
                connections_count = connections_element.find_element(
                    By.CSS_SELECTOR, "span.t-bold"
                ).text
                connections_info = f"{connections_count} Connections"
                scrapped_data["followers_count"] = followers_info
                scrapped_data["connects_count"] = connections_info
            except Exception as ex:
                errors_list.append(
                    f"Error Occured while scrapping follwers&connects count : {str(ex)}"
                )

            # ----------
            try:
                element = driver.find_element(
                    By.CSS_SELECTOR,
                    "span.t-normal.t-black--light.t-14.hoverable-link-text",
                )
                strong_text = element.find_element(By.CSS_SELECTOR, "strong").text
                additional_text = element.text.replace(strong_text, "").strip()
                scrapped_data["mutual_connects"] = strong_text + " " + additional_text
            except Exception as ex:
                errors_list.append(
                    f"Error Occured while scrapping mutual connects count : {str(ex)}"
                )

            # ----------If button is avalabale for more then Click
            driver.get(scrapped_data["url"] + "details/experience/")
            time.sleep(0.8)
            try:
                experence_container = driver.find_element(
                    By.CSS_SELECTOR, "div.pvs-list__container"
                )
                ul_element = experence_container.find_element(By.TAG_NAME, "ul")
                li_elements = ul_element.find_elements(
                    By.CSS_SELECTOR, "li.pvs-list__paged-list-item"
                )
                experience_index = 0
                for li in li_elements:
                    if experience_index == 0:
                        company_url = li.find_element(By.TAG_NAME, "a").get_attribute(
                            "href"
                        )

                        scrapped_data["company_url"] = company_url
                    # Extract the desired text from each li element
                    experience_information = copy.deepcopy(person_experience_format)
                    job_title = li.find_element(
                        By.CSS_SELECTOR,
                        "div.display-flex.align-items-center.mr1.t-bold",
                    )
                    experience_information["job_title"] = job_title.text

                    company_name = li.find_element(
                        By.CSS_SELECTOR, "span.t-14.t-normal"
                    )
                    experience_information["company_name"] = company_name.text

                    duration = li.find_element(
                        By.CSS_SELECTOR,
                        "span.t-14.t-normal.t-black--light:nth-child(3)",
                    )
                    experience_information["work_duration"] = duration.text

                    location_elements = li.find_elements(
                        By.CSS_SELECTOR,
                        "span.t-14.t-normal.t-black--light:nth-child(4)",
                    )
                    location = location_elements[0].text if location_elements else " "
                    experience_information["company_location"] = location
                    scrapped_data["experiences"].append(
                        copy.deepcopy(experience_information)
                    )
                    experience_index += 1
            except Exception as ex:
                errors_list.append(
                    f"Error Occured while scrapping experiences : {str(ex)}"
                )
            driver.get(scrapped_data["url"] + "details/education/")
            time.sleep(0.8)
            try:
                education_container = driver.find_element(
                    By.CSS_SELECTOR, "div.pvs-list__container"
                )
                ul_element = education_container.find_element(By.TAG_NAME, "ul")

                li_elements = ul_element.find_elements(
                    By.CSS_SELECTOR, "li.pvs-list__paged-list-item"
                )
                for li_element in li_elements:
                    person_education = copy.deepcopy(person_education_format)
                    university = li_element.find_element(
                        By.CSS_SELECTOR,
                        "div.display-flex.align-items-center.mr1.hoverable-link-text.t-bold",
                    ).text
                    degree = li_element.find_element(
                        By.CSS_SELECTOR, "span.t-14.t-normal"
                    ).text
                    education_duration = li_element.find_element(
                        By.CSS_SELECTOR, "span.t-14.t-normal.t-black--light"
                    ).text
                    person_education["institute_name"] = university
                    person_education["degree_title"] = degree
                    person_education["duration"] = education_duration

                    scrapped_data["education"].append(copy.deepcopy(person_education))
            except Exception as ex:
                errors_list.append(
                    f"Error Occured while scrapping education : {str(ex)}"
                )

            driver.get(scrapped_data["url"] + "details/skills/")
            time.sleep(0.8)
            try:
                skills_container = driver.find_element(
                    By.CSS_SELECTOR, "div.pvs-list__container"
                )
                skills_ul_element = skills_container.find_element(By.TAG_NAME, "ul")
                skills_li_elements = skills_ul_element.find_elements(
                    By.CSS_SELECTOR, "li.pvs-list__paged-list-item"
                )
                for li_element in skills_li_elements:
                    skill_name = li_element.find_element(
                        By.CSS_SELECTOR,
                        "div.display-flex.align-items-center.mr1.hoverable-link-text.t-bold",
                    ).text
                    scrapped_data["skills"].append(skill_name)
            except Exception as ex:
                errors_list.append(f"Error Occured while scrapping skills : {str(ex)}")

            driver.get(scrapped_data["url"] + "details/languages/")
            time.sleep(0.8)
            try:
                languages_container = driver.find_element(
                    By.CSS_SELECTOR, "div.pvs-list__container"
                )
                languages_ul_element = languages_container.find_element(
                    By.TAG_NAME, "ul"
                )

                languages_li_elements = languages_ul_element.find_elements(
                    By.CSS_SELECTOR, "li.pvs-list__paged-list-item"
                )
                for li_element in languages_li_elements:
                    language_name = li_element.find_element(
                        By.CSS_SELECTOR,
                        "div.display-flex.align-items-center.mr1.t-bold",
                    ).text
                    scrapped_data["languages"].append(language_name)
            except Exception as ex:
                errors_list.append(
                    f"Error Occured while scrapping education : {str(ex)}"
                )

            Top_Statistics_Tabs = [
                {"property_name": "top_5_voices", "index": 0},
                {"property_name": "top_5_companies", "index": 1},
                {"property_name": "top_5_groups", "index": 2},
                {"property_name": "top_5_schools", "index": 4},
            ]
            for item in Top_Statistics_Tabs:
                property_name = item["property_name"]
                index = item["index"]
                driver.get(
                    scrapped_data["url"]
                    + f"details/interests/?detailScreenTabIndex={index}"
                )
                time.sleep(2.5)
                try:
                    containers = driver.find_elements(
                        By.CSS_SELECTOR, "div.pvs-list__container"
                    )
                    main_container = containers[index]
                    interests_ul_element = main_container.find_element(
                        By.TAG_NAME, "ul"
                    )
                    intereset_li_elements = interests_ul_element.find_elements(
                        By.CSS_SELECTOR, "li.pvs-list__paged-list-item"
                    )
                    for li_ in intereset_li_elements:
                        statistic_data = copy.deepcopy(top_statistics_format)
                        title_element = li_.find_element(
                            By.CSS_SELECTOR,
                            "div.display-flex.align-items-center.mr1.hoverable-link-text.t-bold",
                        )
                        statistic_data["title"] = title_element.text
                        statistic_data["link"] = li_.find_elements(By.TAG_NAME, "a")[
                            0
                        ].get_attribute("href")
                        scrapped_data[property_name].append(
                            copy.deepcopy(statistic_data)
                        )

                except Exception as ex:
                    errors_list.append(
                        f"Error Occured while scrapping Top Statistics at Tab # {index} : {str(ex)}"
                    )

            print(errors_list)
            driver.get(scrapped_data["company_url"])
            time.sleep(0.8)
            scrapped_company_data = copy.deepcopy(scrapped_company_data_format)
            try:
                main_element = driver.find_element(By.TAG_NAME, "main")
                company_intro_section = main_element.find_element(
                    By.CSS_SELECTOR, "section.org-top-card"
                )
                company_intro_primary_content = company_intro_section.find_element(
                    By.CSS_SELECTOR, "div.org-top-card__primary-content"
                )
                company_name = company_intro_section.find_element(
                    By.TAG_NAME, "h1"
                ).text
                company_bio = company_intro_primary_content.find_element(
                    By.CSS_SELECTOR, "p.org-top-card-summary__tagline"
                ).text
                company_summary_info_list = company_intro_primary_content.find_element(
                    By.CSS_SELECTOR, "div.org-top-card-summary-info-list"
                )
                company_summary_info_items = company_summary_info_list.find_elements(
                    By.CLASS_NAME, "org-top-card-summary-info-list__info-item"
                )

                # ===========================
                if len(company_summary_info_items) > 0:
                    company_industry = company_summary_info_items[0].text
                if len(company_summary_info_items) > 1:
                    company_locations = company_summary_info_items[1].text
                if len(company_summary_info_items) > 2:
                    company_followers = company_summary_info_items[2].text
                if len(company_summary_info_items) > 3:
                    company_employees = company_summary_info_items[3].text

                scrapped_company_data["name"] = company_name
                scrapped_company_data["bio"] = company_bio
                scrapped_company_data["locations"] = company_locations
                scrapped_company_data["followers_count"] = company_followers
                scrapped_company_data["employee_count"] = company_employees
                scrapped_company_data["industry"] = company_industry

                company_primary_actions = company_intro_section.find_element(
                    By.CSS_SELECTOR, "div.org-top-card-primary-actions"
                )
                company_website_link = company_primary_actions.find_element(
                    By.TAG_NAME, "a"
                ).get_attribute("href")
                print(company_website_link)
                scrapped_company_data["website_url"] = company_website_link

            except Exception as ex:
                print(
                    f"An Error Occured while scrapping Company Intro Section : {str(ex)}"
                )
            company_about_data = copy.deepcopy(company_about_format)

            driver.get(scrapped_data["company_url"] + "about/")
            time.sleep(0.8)
            try:
                main_element = driver.find_element(By.TAG_NAME, "main")
                main_sections = main_element.find_elements(By.TAG_NAME, "section")

                if len(main_sections) > 1:
                    about_section = main_sections[1]
                if about_section is not None:
                    about_description = about_section.find_element(
                        By.TAG_NAME, "p"
                    ).text
                    company_about_data["overview"] = about_description
                    about_summary_dl = about_section.find_element(By.TAG_NAME, "dl")
                    about_summary_dt = about_summary_dl.find_elements(By.TAG_NAME, "dt")
                    about_summary_dd = about_summary_dl.find_elements(By.TAG_NAME, "dd")
                    dt_index = 0
                    dd_index = 0
                    for index in range(len(about_summary_dt)):
                        about_section_other_info_object = {
                            "info_heading": "",
                            "info_value": "",
                        }
                        about_section_other_info_object[
                            "info_heading"
                        ] = about_summary_dt[dt_index].text

                        if (
                            about_section_other_info_object["info_heading"]
                            == "Company size"
                        ):
                            value = about_summary_dd[dd_index].text
                            dd_index += 1
                            # TO DO --> Remove Span from dd and then get the text
                            value += " || " + about_summary_dd[dd_index].text
                        else:
                            value = about_summary_dd[dd_index].text
                        about_section_other_info_object["info_value"] = value
                        company_about_data["other_info_list"].append(
                            copy.deepcopy(about_section_other_info_object)
                        )
                        dt_index += 1
                        dd_index += 1
                scrapped_company_data["company_about"] = copy.deepcopy(
                    company_about_data
                )
            except Exception as ex:
                print(
                    f"An Error Occured while scrapping Company About Section : {str(ex)}"
                )

            driver.get(scrapped_data["company_url"] + "posts/?feedView=all")
            time.sleep(1)

            driver.execute_script(script)
            time.sleep(0.2)
            driver.execute_script(script)
            time.sleep(0.2)
            driver.execute_script(script)
            time.sleep(0.5)
            i = 1
            post_list = []
            for i in range(1, 15):
                try:
                    post_element = driver.find_element(
                        By.XPATH,
                        "/html/body/div[4]/div[3]/div/div[2]/div/div[2]/main/div[2]/div/div[2]/div[3]/div/div[1]/div["
                        + str(i)
                        + "]/div/div/div/div[4]/div/div/span/span/span",
                    )
                    post_text = post_element.text
                    print(
                        "=================================================================================",
                        i,
                    )
                    print(post_text)
                    print(
                        "=================================================================================",
                        i,
                    )
                    post_list.append(post_text)
                except:
                    print("Error has occured")
            print(post_list)
            scrapped_company_data["top_5_posts"] = post_list

            driver.get(scrapped_data["company_url"] + "people/")
            time.sleep(1)
            try:
                main_element = driver.find_element(By.TAG_NAME, "main")
                employee_insights_show_more_button = main_element.find_element(
                    By.CSS_SELECTOR, "button.org-people__show-more-button"
                )
                employee_insights_show_more_button.click()
                time.sleep(0.8)
                employee_insights_container = main_element.find_element(
                    By.CSS_SELECTOR, "div.org-people__insights-container"
                )
                employee_insights_next_button = (
                    employee_insights_container.find_element(
                        By.CSS_SELECTOR, "div.artdeco-carousel__heading"
                    ).find_elements(By.TAG_NAME, "button")[1]
                )

                employee_insights_ul = employee_insights_container.find_element(
                    By.TAG_NAME, "ul"
                )
                employee_insights_li_list = employee_insights_ul.find_elements(
                    By.TAG_NAME, "li"
                )
                for employee_insight_li in employee_insights_li_list:
                    insight_container = employee_insight_li.find_element(
                        By.CSS_SELECTOR, "div.insight-container"
                    )
                    insight_heading = insight_container.find_element(
                        By.CSS_SELECTOR, "div.insight-container__title"
                    ).text
                    insight_summary_list = insight_container.find_elements(
                        By.CSS_SELECTOR, "button.org-people-bar-graph-element"
                    )

                    insight_summary_data = []

                    for insight_summary in insight_summary_list:
                        try:
                            insight_summary_div = insight_summary.find_element(
                                By.CSS_SELECTOR,
                                "div.org-people-bar-graph-element__percentage-bar-info",
                            )
                            insight_summary_title = insight_summary_div.find_element(
                                By.CSS_SELECTOR,
                                "span.org-people-bar-graph-element__category",
                            ).text
                            insight_summary_value = insight_summary_div.find_element(
                                By.TAG_NAME, "strong"
                            ).text
                            insight_summary_data.append(
                                {
                                    "statistic_title": insight_summary_title,
                                    "statistic_value": insight_summary_value,
                                }
                            )
                        except:
                            pass
                    scrapped_company_data["company_employee_statistics"].append(
                        {
                            "statistics_type": insight_heading,
                            "statistics": insight_summary_data,
                        }
                    )
                    employee_insights_next_button.click()
                    time.sleep(0.2)
            except Exception as ex:
                print(
                    "An Error has occured while scrapping Company Employee Statistics : ",
                    str(ex),
                )
            print(scrapped_company_data["company_employee_statistics"])
            # return Response({"scrapped_data": scrapped_data, "errors_list": errors_list})
            object_to_return = {
                "person_profile_data": scrapped_data,
                "company_profile_data": scrapped_company_data,
            }
            
            
            pickle.dump(driver.get_cookies(), open(cache_file_path, "wb"))
            # scrapped_data_in_text_format = generate_text_description(
            #     copy.deepcopy(object_to_return)
            # )
            
            json_data = json.dumps(object_to_return)
            print(object_to_return)
            optimized_data = remove_text_after_newline(json_data)
            optimized_data_ = optimize_response(optimized_data)
            scrapped_data_in_text_format = generate_text_description(
                copy.deepcopy(optimized_data_)
            )
            return Response(scrapped_data_in_text_format)
        else:
            return Response(serializer.errors, status=400)


class GPTView(views.APIView):
    # authentication_classes = [JWTAuthentication]  # Apply JWT authentication
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GPTSerializer(data=request.data)
        if serializer.is_valid():
            my_profile_data = serializer.validated_data["my_profile_data"]
            other_profile_data = serializer.validated_data["other_profile_data"]
            gpt_api_response = call_gpt_api(
                {
                    "my_profile_data": my_profile_data,
                    "other_profile_data": other_profile_data,
                    "session_id": 123,
                }
            )
            return Response(gpt_api_response)


def home(request):
    if is_access_token_valid(request):
        return render(request, "Scrapping_API/index.html")
    return redirect("login")


def dashboard(request):
    return render(request, "Scrapping_API/dashboard.html")


def pdf(request):
    return render(request, "Scrapping_API/pdf.html")


def login(request):
    if is_access_token_valid(request):
        return redirect("home")
    return render(request, "Scrapping_API/login.html")


def signup(request):
    return render(request, "Scrapping_API/signup.html")


def forgot(request):
    return render(request, "Scrapping_API/forgot.html")


class PDFTextExtractionView(APIView):
    authentication_classes = [JWTAuthentication]  # Apply JWT authentication
    permission_classes = [IsAuthenticated]  # Require authenticated access
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        file = request.FILES.get("pdf_file")
        if not file:
            return Response({"error": "No file uploaded."}, status=400)

        try:
            output = BytesIO()
            extract_text_to_fp(file, output)
            text = output.getvalue().decode("utf-8")
            output.close()

            return Response({"text": text}, status=200)
        except Exception:
            return Response({"error": "Invalid PDF file."}, status=400)


class SignupAPIView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            username = (
                serializer.validated_data["first_name"]
                + serializer.validated_data["last_name"]
            )
            password = serializer.validated_data["password"]
            email = serializer.validated_data["email"]

            if not username or not password:
                return Response(
                    {"error": "Username and password are required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                user = User.objects.create_user(
                    username=username, password=password, email=email
                )
                # Mark the user as active (verified) upon signup
                user.is_active = True
                user.save()

                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                return Response(
                    {"access_token": access_token, "refresh_token": refresh_token},
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    @csrf_exempt
    def post(self, request):
        username_or_email = request.data.get("username")
        password = request.data.get("password")

        if not username_or_email or not password:
            return Response(
                {"error": "Username/Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if the provided username_or_email is a valid email address
        is_email = "@" in username_or_email

        # Try to find the user by email
        if is_email:
            User = get_user_model()
            try:
                user = User.objects.get(email=username_or_email)
            except User.DoesNotExist:
                user = None
        else:
            # Try to find the user by username
            user = authenticate(username=username_or_email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response(
                {"access_token": access_token, "refresh_token": refresh_token},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid username/email or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class RefreshAPIView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh_token")

        if not refresh_token:
            return Response(
                {"error": "Refresh token not provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            return Response({"access_token": access_token}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class ForgotPasswordAPIView(APIView):
    # @csrf_exempt
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            username_or_email = serializer.validated_data["email_or_username"]
            try:
                # Check if the provided value is an email
                if "@" in username_or_email:
                    user = User.objects.get(email=username_or_email)
                else:
                    # If not an email, assume it's a username and retrieve the email from the User model
                    user = User.objects.get(username=username_or_email)

                otp_code = str(random.randint(100000, 999999))
                print(otp_code)

                otp, created = OTP.objects.get_or_create(user=user)
                otp.otp = otp_code
                otp.save()

                # You can send the OTP code to the user's email here (see Step 3)

                return Response(
                    {
                        "message": "OTP has been generated and saved successfully.",
                        "otp": otp.otp,
                    },
                    status=status.HTTP_200_OK,
                )
            except User.DoesNotExist:
                return Response(
                    {"error": "User with this email does not exist."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SetNewPasswordAPIView(APIView):
    # @csrf_exempt
    def post(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            username_or_email = serializer.validated_data["email_or_username"]
            otp_code = request.data.get("otp")
            new_password = request.data.get("new_password")

            try:
                # Check if the provided value is an email
                if "@" in username_or_email:
                    user = User.objects.get(email=username_or_email)
                else:
                    # If not an email, assume it's a username and retrieve the email from the User model
                    user = User.objects.get(username=username_or_email)
                otp = OTP.objects.get(user=user, otp=otp_code)

                # Set the new password for the user
                user.set_password(new_password)
                user.save()

                # Delete the OTP record as it has been used
                otp.delete()

                return Response(
                    {"message": "Password has been reset successfully."},
                    status=status.HTTP_200_OK,
                )
            except User.DoesNotExist:
                return Response(
                    {"error": "User with this email does not exist."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except OTP.DoesNotExist:
                return Response(
                    {"error": "Invalid OTP code."}, status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
