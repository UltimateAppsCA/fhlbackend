# SQLAlchemy models for Fantasy League Hockey
from sqlalchemy import Column, Integer, String, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    teams = relationship('FantasyTeam', back_populates='owner')

class League(Base):
    __tablename__ = 'leagues'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    commissioner_id = Column(Integer, ForeignKey('users.id'))
    settings = Column(JSON, default={})
    teams = relationship('FantasyTeam', back_populates='league')

class FantasyTeam(Base):
    __tablename__ = 'fantasy_teams'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    league_id = Column(Integer, ForeignKey('leagues.id'))
    owner = relationship('User', back_populates='teams')
    league = relationship('League', back_populates='teams')
    roster = relationship('RosterSpot', back_populates='team')

class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    position = Column(String, nullable=False)
    nhl_team = Column(String, nullable=False)
    stats = Column(JSON, default={})
    roster_spots = relationship('RosterSpot', back_populates='player')

class RosterSpot(Base):
    __tablename__ = 'roster_spots'
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey('fantasy_teams.id'))
    player_id = Column(Integer, ForeignKey('players.id'))
    team = relationship('FantasyTeam', back_populates='roster')
    player = relationship('Player', back_populates='roster_spots')
