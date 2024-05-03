import requests
from bs4 import BeautifulSoup
from ordered_set import OrderedSet

from clinic import Clinic
from doctor import Doctor

clinics_url = 'https://prodoctorov.ru/moskva/lpu/?page=1'
max_clinics_per_page = 20


def main():
    response = requests.get(clinics_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        clinics_set = OrderedSet()

        current_page: int = 1
        while current_page <= 5:

            clinics_container = soup.find("div", class_="appointments_page b-container")
            clinics_cards = clinics_container.find_all("div", class_="b-card")

            for clinic_card in clinics_cards:
                # город фио специализация название клиники
                clinic = Clinic()
                clinic_name: str = clinic_card.find("a",
                                                    class_="b-link b-link_underline_hover b-link_color_primary-blue d-inline").find(
                    "span").get_text()
                clinic_url: str = ("https://prodoctorov.ru"
                                   + clinic_card.find("a",
                                                      class_="b-link b-link_underline_hover b-link_color_primary-blue d-inline")
                                   .get("href")) + "vrachi/#tab-content"
                clinic.set_name(clinic_name)
                clinic.set_url(clinic_url)
                clinics_set.add(clinic)

                response = requests.get(clinic_url)
                soup = BeautifulSoup(response.content, "html.parser")
                doctors_container = soup.findAll("div", class_="b-doctor-card")

                doctors_set = OrderedSet()
                for doctor in doctors_container:
                    # name: doctor.find("span", class_="b-doctor-card__name-surname").get_text()
                    # profession: doctor.find("div", class_="b-doctor-card__spec").get_text()
                    # exp: doctor.find("div", class_="b-doctor-card__experience-years").get_text()
                    # link: doctor.find("a", class_="b-doctor-card__name-link").get("href")
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
                        doc_url = doctor.find("a", class_="b-doctor-card__name-link")
                    else:
                        doc_url = "-"

                    init_doctor(doc_to_add, doc_name, doc_prof, doc_exp, doc_url)
                    doctors_set.add(doc_to_add)

                print("=========================================")
                print(clinic_url)
                print(len(doctors_set))
                for i, e in enumerate(doctors_set):
                    print(e)
                print("=========================================")

            current_page += 1
            response = requests.get(clinics_url.replace("?page=1", f"?page={current_page}"))
            soup = BeautifulSoup(response.content, "html.parser")

        # print(len(clinics_set))
        # for i, e in enumerate(clinics_set):
        #     print(i, e)


def init_doctor(doctor: Doctor, name: str, profession: str, experience: str, url: str) -> Doctor:
    doctor.set_name(name)
    doctor.set_profession(profession)
    doctor.set_experience(experience)
    doctor.set_url(url)
    return doctor


if __name__ == '__main__':
    main()
