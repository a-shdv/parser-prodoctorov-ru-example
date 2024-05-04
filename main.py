import time
import random
import requests
import openpyxl

from bs4 import BeautifulSoup
from openpyxl.styles import Font
from ordered_set import OrderedSet

from clinic import Clinic
from doctor import Doctor

# Define a list of user-agent strings
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 10; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
]

# Initialize a session
session = requests.Session()

clinics_url = 'https://prodoctorov.ru/moskva/lpu/?page=1'


def main():
    max_number_of_pages = check_max_number_of_pages(clinics_url.replace("?page=1", "?page=0"))

    current_page: int = 1
    while current_page <= max_number_of_pages:
        response = get_page(clinics_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            clinics_set = OrderedSet()
            clinics_container = soup.find("div", class_="appointments_page b-container")
            if clinics_container:
                clinics_cards = clinics_container.find_all("div", class_="b-card")
                for clinic_card in clinics_cards:
                    clinic = Clinic()
                    clinic_name_span = clinic_card.find("a",
                                                        class_="b-link b-link_underline_hover b-link_color_primary-blue d-inline")
                    if clinic_name_span:
                        clinic_name = clinic_name_span.find("span").get_text()
                        clinic_url = "https://prodoctorov.ru" + clinic_name_span.get("href") + "vrachi/#tab-content"
                        clinic_city = soup.find("div",
                                                "b-text-unit b-text-unit_vertical_middle").get_text().strip() if soup.find(
                            "div", "b-text-unit b-text-unit_vertical_middle") else "-"
                        clinic.set_name(clinic_name)
                        clinic.set_city(clinic_city)
                        clinic.set_url(clinic_url)

                        response = get_page(clinic_url)
                        soup = BeautifulSoup(response.content, "html.parser")
                        doctors_container = soup.findAll("div", class_="b-doctor-card")

                        for doctor in doctors_container:
                            doc_to_add = Doctor()
                            doc_name = doctor.find("span",
                                                   class_="b-doctor-card__name-surname").get_text() if doctor.find(
                                "span", class_="b-doctor-card__name-surname") else "-"
                            doc_prof = doctor.find("div", class_="b-doctor-card__spec").get_text() if doctor.find("div",
                                                                                                                  class_="b-doctor-card__spec") else "-"
                            doc_exp = doctor.find("div",
                                                  class_="b-doctor-card__experience-years").get_text() if doctor.find(
                                "div", class_="b-doctor-card__experience-years") else "-"
                            doc_url = "https://prodoctorov.ru" + doctor.find("a",
                                                                             class_="b-doctor-card__name-link").get(
                                "href") if doctor.find("a", class_="b-doctor-card__name-link") else "-"
                            init_doctor(doc_to_add, doc_name, doc_prof, doc_exp, doc_url)
                            clinic.get_doctors.add(doc_to_add)

                        clinics_set.add(clinic)

                        current_time = time.strftime("%d/%m/%Y %H:%M:%S")
                        formatted_curr_page = str(current_page)

                        print(current_time + " " + formatted_curr_page)
                        time.sleep(random.uniform(2, 5))  # Sleep for random duration between 2 and 5 seconds

        current_page += 1


def get_page(url):
    # Randomly select a user-agent string
    headers = {'User-Agent': random.choice(user_agents)}

    # Make the request with the selected user-agent string
    response = session.get(url, headers=headers)

    return response


def check_max_number_of_pages(url) -> int:
    response = get_page(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return int(soup.find("span",
                         "b-pagination-vuetify-imitation__item b-pagination-vuetify-imitation__item_current").get_text().strip())


def init_doctor(doctor: Doctor, name: str, profession: str, experience: str, url: str) -> Doctor:
    doctor.set_name(name)
    doctor.set_profession(profession)
    doctor.set_experience(experience)
    doctor.set_url(url)
    return doctor


if __name__ == '__main__':
    main()
