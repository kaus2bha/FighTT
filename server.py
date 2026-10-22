import os
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

# 1. DATABASE SETUP
DATABASE_URL = "sqlite:///./retro_fighter.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. DATABASE MODELS (Tables)
class PlayerModel(Base):
    __tablename__ = "players"
    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )
    username = Column(String, unique=True, index=True)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    equipped_weapon_id = Column(Integer, ForeignKey("weapons.id"), default=1)

class WeaponModel(Base):
    __tablename__ = "weapons"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    damage = Column(Integer)
    weight = Column(Integer)  # Affects attack speed in frontend

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Seed default weapons into the database if empty
def seed_weapons():
    db = SessionLocal()
    if db.query(WeaponModel).count() == 0:
        default_weapons = [
            WeaponModel(id=1, name="Rusty Sword", damage=10, weight=5),
            WeaponModel(id=2, name="Heavy Battleaxe", damage=25, weight=12),
            WeaponModel(id=3, name="Shadow Dagger", damage=7, weight=2),
        ]
        db.add_all(default_weapons)
        db.commit()
    db.close()

seed_weapons()

# 3. FASTAPI INITIALIZATION
app = FastAPI(title="Retro Weapon Fighter Backend")

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. PYDANTIC SCHEMAS (Data Validation)
class PlayerCreate(BaseModel):
    username: str

class MatchResult(BaseModel):
    winner_username: str
    loser_username: str

# 5. API ENDPOINTS

@app.post("/register")
def register_player(player: PlayerCreate, db: Session = Depends(get_db)):
    """Creates a new player account."""
    existing_player = db.query(PlayerModel).filter(PlayerModel.username == player.username).first()
    if existing_player:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    new_player = PlayerModel(username=player.username)
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    return {"message": "Player registered successfully", "username": new_player.username}

@app.get("/player/{username}")
def get_player_stats(username: str, db: Session = Depends(get_db)):
    """Fetches a player's stats and their weapon data."""
    player = db.query(PlayerModel).filter(PlayerModel.username == username).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    weapon = db.query(WeaponModel).filter(WeaponModel.id == player.equipped_weapon_id).first()
    
    return {
        "username": player.username,
        "wins": player.wins,
        "losses": player.losses,
        "weapon": {
            "name": weapon.name,
            "damage": weapon.damage,
            "weight": weapon.weight
        }
    }

@app.post("/match/report")
def report_match_result(result: MatchResult, db: Session = Depends(get_db)):
    """Updates wins/losses after a game ends."""
    winner = db.query(PlayerModel).filter(PlayerModel.username == result.winner_username).first()
    loser = db.query(PlayerModel).filter(PlayerModel.username == result.loser_username).first()
    
    if not winner or not loser:
        raise HTTPException(status_code=404, detail="One or both players not found")
    
    winner.wins += 1
    loser.losses += 1
    db.commit()
    
    return {"status": "Success", "winner_total_wins": winner.wins, "loser_total_losses": loser.losses}

@app.get("/weapons")
def get_all_weapons(db: Session = Depends(get_db)):
    """Returns the list of all available game weapons."""
    return db.query(WeaponModel).all()
