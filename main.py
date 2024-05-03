import requests
from bs4 import BeautifulSoup
from ordered_set import OrderedSet

from clinic import Clinic

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
                clinic_name: str = clinic_card.find("a", class_="b-link b-link_underline_hover b-link_color_primary-blue d-inline").find("span").get_text()
                clinic.set_name(clinic_name)
                clinics_set.add(clinic)

                # for i, clinics in enumerate(clinics_set):
                    # doctor_link = clinic_card.find("a", class_="b-link b-link_underline_hover b-link_color_primary-blue d-inline")

                    # if doctor_link:
                    # doctor_link_href = requests.get(url + doctor_link + "vrachi/#tab-content")
                    # pass
                    # print(doctor_link_href)


            current_page += 1
            response = requests.get(clinics_url.replace("?page=1", f"?page={current_page}"))
            soup = BeautifulSoup(response.content, "html.parser")

        # print(len(clinics_set))
        for i, e in enumerate(clinics_set):
            print(i, e)


if __name__ == '__main__':
    main()
