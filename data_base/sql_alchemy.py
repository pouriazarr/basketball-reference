import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

# define base
Base = declarative_base()

# define ORM models with relations
class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    Player = Column(String)
    Pos = Column(String)
    Ht = Column(String)
    Wt = Column(Integer)
    Birth_Date = Column(String)
    Birth = Column(String)
    College = Column(String)
    # relation to player_seasons
    seasons = relationship("PlayerSeason", back_populates="player")

class PlayerSeason(Base):
    __tablename__ = 'player_seasons'
    player_id = Column(Integer, ForeignKey('players.id'), primary_key=True, nullable=False)
    season_id = Column(Integer, ForeignKey('seasons.id'), primary_key=True, nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    G = Column(Integer)
    GS = Column(Integer)
    MP = Column(Float)
    FG = Column(Float)
    FGA = Column(Float)
    FG_percentage = Column(Float)
    ThreeP = Column(Float)
    ThreePA = Column(Float)
    ThreeP_percentage = Column(Float)
    TwoP = Column(Float)
    TwoPA = Column(Float)
    TwoP_percentage = Column(Float)
    eFG_percentage = Column(Float)
    FT = Column(Float)
    FTA = Column(Float)
    FT_percentage = Column(Float)
    ORB = Column(Float)
    DRB = Column(Float)
    TRB = Column(Float)
    AST = Column(Float)
    STL = Column(Float)
    BLK = Column(Float)
    TOV = Column(Float)
    PF = Column(Float)
    PTS = Column(Float)
    Salary = Column(String)
    Exp = Column(Integer)
    # relations
    player = relationship("Player", back_populates="seasons")
    team = relationship("Team")
    season = relationship("Season")

class Award(Base):
    __tablename__ = 'awards'
    id = Column(Integer, primary_key=True)
    award_name = Column(String)
    award_type = Column(String)
    recipient_type = Column(String)
    # relation to awards_season
    award_seasons = relationship("AwardSeason", back_populates="award")

class AwardSeason(Base):
    __tablename__ = 'awards_season'
    season_id = Column(Integer, ForeignKey('seasons.id'), primary_key=True, nullable=False)
    award_id = Column(Integer, ForeignKey('awards.id'), primary_key=True, nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), primary_key=True, nullable=False)
    name = Column(String)
    team = Column(String)
    # relations
    season = relationship("Season", back_populates="awards")
    award = relationship("Award", back_populates="award_seasons")

class Season(Base):
    __tablename__ = 'seasons'
    id = Column(Integer, primary_key=True)
    season_label = Column(String)
    year_start = Column(Integer)
    year_end = Column(Integer)
    League_Champion = Column(String)
    Most_Valuable_Player = Column(String)
    Rookie_of_the_Year = Column(String)
    PPG_Leader = Column(String)
    RPG_Leader = Column(String)
    APG_Leader = Column(String)
    WS_Leader = Column(String)
    # relations
    awards = relationship("AwardSeason", back_populates="season")
    team_seasons = relationship("TeamSeason", back_populates="season")

class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    team_code = Column(String)
    location = Column(String)
    team_name = Column(String)
    seasons_played = Column(Integer)
    win = Column(Integer)
    loss = Column(Integer)
    win_percentage = Column(Float)
    playoff_appearances = Column(Integer)
    championships = Column(Integer)
    arena = Column(String)
    conference = Column(String)
    division = Column(String)
    # relation to team_seasons
    team_seasons = relationship("TeamSeason", back_populates="team")

class TeamSeason(Base):
    __tablename__ = 'team_seasons'
    team_id = Column(Integer, ForeignKey('teams.id'), primary_key=True, nullable=False)
    season_id = Column(Integer, ForeignKey('seasons.id'), primary_key=True, nullable=False)
    conference = Column(String)
    rank = Column(Integer)
    coach = Column(String)
    PTS_G = Column(Float)
    OppPTS_G = Column(Float)
    SRS = Column(Float)
    Pace = Column(Float)
    ORtg = Column(Float)
    DRtg = Column(Float)
    NetRtg = Column(Float)
    championship_odds = Column(String)
    attendace_total = Column(Integer)
    wins = Column(Integer)
    losses = Column(Integer)
    # relations
    team = relationship("Team", back_populates="team_seasons")
    season = relationship("Season", back_populates="team_seasons")

# create sqllite engine
engine = create_engine('sqlite:///nba_database.db', echo=False)

# create tables in database
Base.metadata.create_all(engine)

# list of CSV files and their table names
csv_files = [
    ('Players.csv', 'players'),
    ('Player_Seasons_updated.csv', 'player_seasons'),
    ('teams.csv', 'teams'),
    ('team_seasons.csv', 'team_seasons'),
    ('awards_season.csv', 'awards_season'),
    ('awards.csv', 'awards'),
    ('seasons.csv', 'seasons'),
]

# loading csv files into database
for csv_file, table_name in csv_files:
    df = pd.read_csv('../csv_files/' + csv_file)
    df.to_sql(table_name, engine, if_exists='replace', index=False)

print('nba_database has been created.')