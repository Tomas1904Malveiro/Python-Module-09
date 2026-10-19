from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ValidationError, model_validator


class Rank(str, Enum):
    cadet = "cadet"
    officer = "officer"
    lieutenant = "lieutenant"
    captain = "captain"
    commander = "commander"


class CrewMember(BaseModel):
    member_id: str = Field(..., min_length=3, max_length=10)
    name: str = Field(..., min_length=2, max_length=50)
    rank: Rank
    age: int = Field(..., ge=18, le=80)
    specialization: str = Field(..., min_length=3, max_length=30)
    years_experience: int = Field(..., ge=0, le=50)
    is_active: bool = Field(default=True)


class SpaceMission(BaseModel):
    mission_id: str = Field(..., min_length=5, max_length=15)
    mission_name: str = Field(..., min_length=3, max_length=100)
    destination: str = Field(..., min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(..., ge=1, le=3650)
    crew: list[CrewMember] = Field(..., min_length=1, max_length=12)
    mission_status: str = Field(default="planned")
    budget_millions: float = Field(..., ge=1.0, le=10000.0)

    @model_validator(mode="after")
    def validate_mission(self) -> "SpaceMission":
        if not self.mission_id.startswith("M"):
            raise ValueError("Mission ID must start with M")

        have_cap_or_com = False
        for member in self.crew:
            if member.rank == Rank.commander or member.rank == Rank.captain:
                have_cap_or_com = True

        if not have_cap_or_com:
            raise ValueError("Must have at least one Commander or Captain")

        if self.duration_days > 365:
            experienceds = 0
            for member in self.crew:
                if member.years_experience >= 5:
                    experienceds += 1

            if not experienceds >= len(self.crew) / 2:
                raise ValueError(
                                "Long missions (> 365 days) "
                                "need 50% experienced crew (5+ years)"
                                )

        for member in self.crew:
            if not member.is_active:
                raise ValueError("All crew members must be active")

        return self


def main() -> None:
    space_mission = SpaceMission(
            mission_id="M2024_MARS",
            mission_name="Mars Colony Establishment",
            destination="Mars",
            launch_date=datetime(2024, 1, 15, 10, 30),
            duration_days=900,
            crew=[
                CrewMember(
                        member_id="id1",
                        name="Sarah Connor",
                        rank=Rank.commander,
                        age=30,
                        specialization="Mission Command",
                        years_experience=10,
                        ),
                CrewMember(
                        member_id="id2",
                        name="John Smith",
                        rank=Rank.lieutenant,
                        age=30,
                        specialization="Navigation",
                        years_experience=5,
                        ),
                CrewMember(
                        member_id="id3",
                        name="Alice Johnson",
                        rank=Rank.officer,
                        age=30,
                        specialization="Engineering",
                        years_experience=3,
                        )
                ],
            mission_status="planned",
            budget_millions=2500.0
        )

    print("Space Mission Crew Validation")
    print("=========================================")
    print("Valid mission created:")
    print(f"Mission: {space_mission.mission_name}")
    print(f"ID: {space_mission.mission_id}")
    print(f"Destination: {space_mission.destination}")
    print(f"Duration: {space_mission.duration_days} days")
    print(f"Budget: ${space_mission.budget_millions}M")
    print(f"Crew size: {len(space_mission.crew)}")
    print("Crew members:")

    for member in space_mission.crew:
        print(f"- {member.name} ({member.rank.value})"
              f" - {member.specialization}")

    print()
    print("=========================================")
    print("Expected validation error:")

    try:
        space_mission = SpaceMission(
                mission_id="M2024_MARS",
                mission_name="Mars Colony Establishment",
                destination="Mars",
                launch_date=datetime(2024, 1, 15, 10, 30),
                duration_days=900,
                crew=[
                    CrewMember(
                            member_id="id1",
                            name="John Smith",
                            rank=Rank.lieutenant,
                            age=30,
                            specialization="Navigation",
                            years_experience=3,
                            ),
                    CrewMember(
                            member_id="id2",
                            name="Alice Johnson",
                            rank=Rank.officer,
                            age=30,
                            specialization="Engineering",
                            years_experience=3,
                            )
                    ],
                mission_status="planned",
                budget_millions=2500.0
                )
    except ValidationError as e:
        for error in e.errors():
            print(error["msg"].removeprefix("Value error, "))


if __name__ == "__main__":
    main()
