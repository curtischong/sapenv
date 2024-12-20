from pet import Pet


class Team:
    def __init__(self, pets: list[Pet]):
        self.pets = pets

    def __eq__(self, other: "Team"):
        return self.pets == other.pets
