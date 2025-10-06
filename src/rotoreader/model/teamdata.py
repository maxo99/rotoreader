from sqlalchemy import Column, String
from sqlmodel import Field, SQLModel


class TeamData(SQLModel, table=True):
    """
    SQLModel representing NFL team data from nfl_data_py.import_team_desc()
    """

    # Primary key
    team_abbr: str = Field(sa_column=Column(String, primary_key=True, nullable=False))

    # Basic team information
    team_name: str = Field(description="Full team name (e.g., 'Arizona Cardinals')")
    team_id: str = Field(description="nfl_data_py team identifier")
    team_nick: str = Field(description="Team nickname (e.g., 'Cardinals')")
    team_conf: str = Field(description="Conference (AFC/NFC)")
    team_division: str = Field(description="Division (e.g., 'NFC West')")

    # Team colors
    team_color: str = Field(description="Primary team color (hex code)")
    team_color2: str | None = Field(
        default=None, description="Secondary team color (hex code)"
    )
    team_color3: str | None = Field(
        default=None, description="Tertiary team color (hex code)"
    )
    team_color4: str | None = Field(
        default=None, description="Quaternary team color (hex code)"
    )

    # Logo and image URLs
    team_logo_wikipedia: str | None = Field(
        default=None, description="Wikipedia logo URL"
    )
    team_logo_espn: str | None = Field(default=None, description="ESPN logo URL")
    team_wordmark: str | None = Field(default=None, description="Team wordmark URL")
    team_conference_logo: str | None = Field(
        default=None, description="Conference logo URL"
    )
    team_league_logo: str | None = Field(
        default=None, description="NFL league logo URL"
    )
    team_logo_squared: str | None = Field(
        default=None, description="Squared team logo URL"
    )

    @classmethod
    def from_nfl_data(cls, df_row) -> "TeamData":
        """
        Create a TeamData instance from a row of nfl_data_py.import_team_desc() DataFrame

        Args:
            df_row: A pandas Series representing a single row from the NFL team data

        Returns:
            TeamData instance
        """
        return cls(
            team_abbr=df_row["team_abbr"],
            team_name=df_row["team_name"],
            team_id=df_row["team_id"],
            team_nick=df_row["team_nick"],
            team_conf=df_row["team_conf"],
            team_division=df_row["team_division"],
            team_color=df_row["team_color"],
            team_color2=df_row.get("team_color2"),
            team_color3=df_row.get("team_color3"),
            team_color4=df_row.get("team_color4"),
            team_logo_wikipedia=df_row.get("team_logo_wikipedia"),
            team_logo_espn=df_row.get("team_logo_espn"),
            team_wordmark=df_row.get("team_wordmark"),
            team_conference_logo=df_row.get("team_conference_logo"),
            team_league_logo=df_row.get("team_league_logo"),
            team_logo_squared=df_row.get("team_logo_squared"),
        )

    @property
    def location(self) -> str:
        return " ".join(self.team_name.split()[:-1])

    @property
    def searchTags(self) -> list[str]:
        return [self.team_abbr, self.location, self.team_nick]
