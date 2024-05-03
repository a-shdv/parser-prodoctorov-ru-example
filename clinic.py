class Clinic:
    name: str
    doctors: list

    def __init__(self, name: str = "", doctors=None):
        if doctors is None:
            doctors = []
        self._name = name
        self._doctors = doctors

    @property
    def get_name(self) -> str:
        return self._name

    def set_name(self, _name):
        self._name = _name

    @property
    def get_doctors(self) -> list:
        return self.doctors

    def __str__(self):
        return self._name.strip()

