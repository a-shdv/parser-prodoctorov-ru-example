class Doctor:
    name: str
    profession: str
    experience: str
    url: str

    def __int__(self, name: str, profession: str, experience: str, url: str):
        self._name = name
        self._profession = profession
        self._experience = experience
        self._url = url

    def set_name(self, name):
        self._name = name

    def set_profession(self, profession):
        self._profession = profession

    def set_experience(self, experience):
        self._experience = experience

    def set_url(self, url):
        self._url = url

    def get_url(self):
        return self._url

    def __str__(self):
        return self._name.strip() + " " + self._profession.strip() + " " + self._experience.strip() + " "
