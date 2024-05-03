import time

import requests
import openpyxl

from bs4 import BeautifulSoup
from openpyxl.styles import Font
from ordered_set import OrderedSet

from clinic import Clinic
from doctor import Doctor

clinics_url = 'https://prodoctorov.ru/moskva/lpu/?page=1'
max_clinics_per_page = 20


def main():
    max_number_of_pages = check_max_number_of_pages(clinics_url.replace("?page=1", "?page=0"))

    response = requests.get(clinics_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        clinics_set = OrderedSet()

        current_page: int = 1
        while current_page <= max_number_of_pages:
            if soup.find("div", class_="appointments_page b-container") is not None:
                clinics_container = soup.find("div", class_="appointments_page b-container")

                if clinics_container.find_all("div", class_="b-card") is not None:
                    clinics_cards = clinics_container.find_all("div", class_="b-card")

                    for clinic_card in clinics_cards:
                        clinic = Clinic()
                        if clinic_card.find("a", class_="b-link b-link_underline_hover b-link_color_primary-blue d-inline").find(
                            "span") is not None:
                            clinic_name: str = clinic_card.find("a",
                                                                class_="b-link b-link_underline_hover b-link_color_primary-blue d-inline").find(
                                "span").get_text()

                            if clinic_card.find("a", class_="b-link b-link_underline_hover b-link_color_primary-blue d-inline") is not None:

                                clinic_url: str = ("https://prodoctorov.ru"
                                                   + clinic_card.find("a",
                                                                      class_="b-link b-link_underline_hover b-link_color_primary-blue d-inline")
                                                   .get("href")) + "vrachi/#tab-content"

                                if soup.find("div", "b-text-unit b-text-unit_vertical_middle") is not None:
                                    clinic_city = soup.find("div", "b-text-unit b-text-unit_vertical_middle").get_text().strip()
                                else:
                                    clinic_city = "-"
                                clinic.set_name(clinic_name)
                                clinic.set_city(clinic_city)
                                clinic.set_url(clinic_url)

                                response = requests.get(clinic_url)
                                soup = BeautifulSoup(response.content, "html.parser")
                                doctors_container = soup.findAll("div", class_="b-doctor-card")

                                for doctor in doctors_container:
                                    doc_to_add = Doctor()

                                    doc_name: str
                                    doc_prof: str
                                    doc_exp: str
                                    doc_url: str

                                    if doctor.find("span", class_="b-doctor-card__name-surname") is not None:
                                        doc_name = doctor.find("span", class_="b-doctor-card__name-surname").get_text()
                                    else:
                                        doc_name = "-"

                                    if doctor.find("div", class_="b-doctor-card__spec") is not None:
                                        doc_prof = doctor.find("div", class_="b-doctor-card__spec").get_text()
                                    else:
                                        doc_prof = "-"

                                    if doctor.find("div", class_="b-doctor-card__experience-years") is not None:
                                        doc_exp = doctor.find("div", class_="b-doctor-card__experience-years").get_text()
                                    else:
                                        doc_exp = "-"

                                    if doctor.find("a", class_="b-doctor-card__name-link") is not None:
                                        doc_url = "https://prodoctorov.ru" + doctor.find("a", class_="b-doctor-card__name-link").get("href")
                                    else:
                                        doc_url = "-"

                                    init_doctor(doc_to_add, doc_name, doc_prof, doc_exp, doc_url)
                                    clinic.get_doctors.add(doc_to_add)

                                clinics_set.add(clinic)
                                print(current_page)
                # print("=========================================")
                # # print(clinic_url)
                # # print(len(doctors_set))
                # for i, e in enumerate(clinics_set):
                #     print(e.get_doctors)
                #     for val in e.get_doctors:
                #         print(val)
                # print("=========================================")

            current_page += 1
            response = requests.get(clinics_url.replace("?page=1", f"?page={current_page}"))
            soup = BeautifulSoup(response.content, "html.parser")

        write_to_excel_file(clinics_set)

        # print(len(clinics_set))
        # for i, e in enumerate(clinics_set):
        #     print(i, e)


def check_max_number_of_pages(url) -> int:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    soup.find("span", "b-pagination-vuetify-imitation__item b-pagination-vuetify-imitation__item_current")
    return int(soup.find("span",
                         "b-pagination-vuetify-imitation__item b-pagination-vuetify-imitation__item_current").get_text().strip())


def init_doctor(doctor: Doctor, name: str, profession: str, experience: str, url: str) -> Doctor:
    doctor.set_name(name)
    doctor.set_profession(profession)
    doctor.set_experience(experience)
    doctor.set_url(url)
    return doctor


def write_to_excel_file(clinics_set: OrderedSet):
    # Create a new Excel workbook
    workbook = openpyxl.Workbook()

    # Select the active worksheet
    sheet = workbook.active

    # Write data to the Excel file
    sheet['A1'] = 'Город'
    sheet['B1'] = 'Клиника'
    sheet['C1'] = 'Врач'
    sheet['D1'] = 'Специализация'
    sheet['E1'] = 'Стаж'
    sheet['F1'] = 'Ссылка на клинику'
    sheet['G1'] = 'Ссылка на врача'

    # Set bold font for cells A1 to G1
    bold_font = Font(bold=True)
    for col in range(1, 8):  # Columns A to G
        sheet.cell(row=1, column=col).font = bold_font

    # Set column widths
    column_widths = [20, 30, 20, 30, 15, 40, 40]  # Adjust as needed
    for i, width in enumerate(column_widths, start=1):
        sheet.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width

    row = 2
    while row < len(clinics_set):

        for clinic in clinics_set:
            for doc in clinic.get_doctors:
                sheet['A' + str(row)] = clinic.get_city  # Город
                sheet['B' + str(row)] = clinic.get_name.strip()  # Клиника
                sheet['C' + str(row)] = doc.get_name()  # Врач
                sheet['D' + str(row)] = doc.get_profession()  # Специализация
                sheet['E' + str(row)] = doc.get_experience()  # Стаж
                sheet['F' + str(row)] = str(clinic.get_url).strip()  # Ссылка на клинику
                sheet['G' + str(row)] = str(doc.get_url()).strip()  # Ссылка на врача

                row += 1
        # for doc in clinics_set.__getitem__(row).get_doctors:
        #     # clinics_set.__getitem__(1).get_doctors
        #     sheet['A' + str(row)] = "-"  # Город
        #     sheet['B' + str(row)] = clinics_set.__getitem__(j).get_name.strip()  # Клиника
        #     sheet['C' + str(row)] = doc.get_name()  # Врач
        #     sheet['D' + str(row)] = doc.get_profession()  # Специализация
        #     sheet['E' + str(row)] = doc.get_experience()  # Стаж
        #     # sheet['F' + str(rowNo)] = clinics_set.__getitem__(rowNo).get_url.strip()  # Ссылка на клинику
        #     # sheet['G' + str(rowNo)] = doc.get_url  # Ссылка на врача

    # Save the workbook
    workbook.save('/Users/a-shdv/Desktop/example.xlsx')


if __name__ == '__main__':
    main()
