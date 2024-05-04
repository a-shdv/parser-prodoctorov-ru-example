import asyncio
import random
import time

import aiohttp
import openpyxl
import requests
from bs4 import BeautifulSoup

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


async def fetch_page(url):
    async with aiohttp.ClientSession() as session:
        headers = {'User-Agent': random.choice(user_agents)}
        async with session.get(url, headers=headers, ssl=False) as response:
            return await response.text()


async def scrape_clinic(clinic_url):
    async with aiohttp.ClientSession() as session:
        headers = {'User-Agent': random.choice(user_agents)}
        async with session.get(clinic_url, headers=headers) as response:
            html_text = await response.text()
            soup = BeautifulSoup(html_text, 'html.parser')
            clinic = Clinic()
            clinic_name_span = soup.find("a", class_="b-link b-link_underline_hover b-link_color_primary-blue d-inline")
            if clinic_name_span:
                clinic_name = clinic_name_span.find("span").get_text()
                clinic_url = "https://prodoctorov.ru" + clinic_name_span.get("href") + "vrachi/#tab-content"
                clinic_city = soup.find("div", class_="b-text-unit b-text-unit_vertical_middle")
                clinic_city = clinic_city.get_text().strip() if clinic_city else "-"
                clinic.set_name(clinic_name)
                clinic.set_city(clinic_city)
                clinic.set_url(clinic_url)

                doctors_container = soup.find_all("div", class_="b-doctor-card")

                for doctor in doctors_container:
                    doc_to_add = Doctor()
                    doc_name = doctor.find("span", class_="b-doctor-card__name-surname").get_text() if doctor.find(
                        "span", class_="b-doctor-card__name-surname") else "-"
                    doc_prof = doctor.find("div", class_="b-doctor-card__spec").get_text() if doctor.find("div",
                                                                                                          class_="b-doctor-card__spec") else "-"
                    doc_exp = doctor.find("div", class_="b-doctor-card__experience-years").get_text() if doctor.find(
                        "div", class_="b-doctor-card__experience-years") else "-"
                    doc_url = "https://prodoctorov.ru" + doctor.find("a", class_="b-doctor-card__name-link").get(
                        "href") if doctor.find("a", class_="b-doctor-card__name-link") else "-"
                    init_doctor(doc_to_add, doc_name, doc_prof, doc_exp, doc_url)
                    clinic.get_doctors.add(doc_to_add)

                return clinic


async def main():
    clinics_url = 'https://prodoctorov.ru/moskva/lpu/?page=1'
    max_number_of_pages = check_max_number_of_pages(clinics_url.replace("?page=1", "?page=0"))
    tasks = []
    for page_number in range(1, max_number_of_pages + 1):
        clinics_url = f'https://prodoctorov.ru/moskva/lpu/?page={page_number}'
        html_text = await fetch_page(clinics_url)
        soup = BeautifulSoup(html_text, 'html.parser')
        clinics_container = soup.find("div", class_="appointments_page b-container")
        if clinics_container:
            clinics_cards = clinics_container.find_all("div", class_="b-card")
            for clinic_card in clinics_cards:
                clinic_name_span = clinic_card.find("a",
                                                    class_="b-link b-link_underline_hover b-link_color_primary-blue d-inline")
                if clinic_name_span:
                    clinic_url = "https://prodoctorov.ru" + clinic_name_span.get("href") + "vrachi/#tab-content"
                    tasks.append(scrape_clinic(clinic_url))
    clinics_set = await asyncio.gather(*tasks)

    # Write the scraped data to an Excel file
    write_to_excel(clinics_set)


def init_doctor(doctor: Doctor, name: str, profession: str, experience: str, url: str) -> Doctor:
    doctor.set_name(name)
    doctor.set_profession(profession)
    doctor.set_experience(experience)
    doctor.set_url(url)
    return doctor


def check_max_number_of_pages(url) -> int:
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.content, "html.parser")
    return int(soup.find("span",
                         class_="b-pagination-vuetify-imitation__item b-pagination-vuetify-imitation__item_current").get_text().strip())


def write_to_excel(clinics_set):
    # Create a new Excel workbook
    workbook = openpyxl.Workbook()

    # Create a worksheet for clinics
    clinics_worksheet = workbook.active
    clinics_worksheet.title = "Clinics"
    clinics_worksheet.append(["Clinic Name", "City", "URL"])

    # Create a worksheet for doctors
    doctors_worksheet = workbook.create_sheet(title="Doctors")
    doctors_worksheet.append(["Clinic Name", "Doctor Name", "Profession", "Experience", "URL"])

    # Function to write clinic data to Excel
    def write_clinic_to_excel(clinic):
        clinics_worksheet.append([clinic.name, clinic.city, clinic.url])

    # Function to write doctor data to Excel
    def write_doctor_to_excel(clinic_name, doctor):
        doctors_worksheet.append([clinic_name, doctor.name, doctor.profession, doctor.experience, doctor.url])

    # Write data to Excel
    for clinic in clinics_set:
        write_clinic_to_excel(clinic)
        for doctor in clinic.get_doctors:
            write_doctor_to_excel(clinic.name, doctor)

    # Save the Excel workbook
    workbook.save("/Users/a-shdv/Desktop/scraped_data.xlsx")


if __name__ == '__main__':
    start_time = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
    print(f"Scraped data written to 'scraped_data.xlsx' in {time.time() - start_time} seconds")
