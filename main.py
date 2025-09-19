from typing import Union
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from database import SessionLocal, Base, Branding, Features, BulletPoints, Social, Register, Realisation
from sqlalchemy import Column, Integer, String, ForeignKey
from pydantic import BaseModel , EmailStr
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from fastapi.responses import FileResponse
from src import crud, models, schemas
from src.security import create_access_token, verify_password, get_current_user, get_current_active_admin
from src.config import settings
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from src.models import User
from fastapi import FastAPI
from datetime import datetime, timedelta
from jose import jwt
from src.config import settings  # ton fichier pydantic_settings




import os
import uuid

app = FastAPI()
router = APIRouter()

UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class user_renspons(BaseModel):
    id: int
    name: str
    email: str
    adresse: str
    role: str
    hashed_password: str


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    adresse: str
    role: str = "user"
    hashed_password: str

class user_renspons(BaseModel):
    id: int
    name: Optional[str] = None
    adresse: Optional[str] = None
    email: EmailStr
    role: str
    hashed_password: str

    class Config:
        from_attributes = True


app = FastAPI()

@app.get("/token-test")
def token_test():
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": "testuser", "exp": expire}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

   
@app.get("/users/")
async def get_user(skip: int = 0, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(10).all()
    return users



@router.post("/login", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Connecte un utilisateur et retourne un jeton d'accès.
    """
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

    
@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Crée un nouvel utilisateur.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)



@router.get("/users/connect", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    Récupère l'utilisateur actuellement connecté.
    """
    return current_user

@router.post("/logout")
def logout():
    """
    Déconnecte l'utilisateur (côté client).
    """
    return {"message": "Successfully logged out"}


@app.get("/users_single{user_id}/", response_model= user_renspons)
async def details_user(user_id: int , db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return user


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    adresse: Optional[str] = None
    role: Optional[str] = None
    hashed_password: Optional[str] = None


@app.put("/users/{user_id}", response_model=user_renspons)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_admin)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="user not found")
    db_user.name = user.name if user.name is not None else db_user.name
    db_user.email = user.email if user.email is not None else db_user.email
    db_user.adresse = user.adresse if user.adresse is not None else db_user.adresse
    db_user.role = user.role if user.role is not None else db_user.role
    db.commit()
    db.refresh(db_user)
    return db_user




@app.delete("/users/delete/{user_id}", response_model= user_renspons)
async def user_delete(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_admin)):
    db_user = db.query(User).filter(User.id == user_id).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail="user not found")
    db.delete(db_user)
    db.commit()
    return db_user

# --- Pydantic Schemas ---
class BrandingSchema(BaseModel):
    id: int | None = None
    name: str
    image: str
    class Config:
        from_attributes = True

class FeaturesSchema(BaseModel):
    id: int | None = None
    alt: str
    image: str
    title: str
    text: str
    class Config:
        from_attributes = True

class BulletPointsSchema(BaseModel):
    id: int | None = None
    alt: str
    image: str
    title: str
    text: str
    class Config:
        from_attributes = True

class SocialSchema(BaseModel):
    id: int | None = None
    ico: str
    alt: str
    link: str
    class Config:
        from_attributes = True



# --- Schéma RegisterSchema (remis avant les routes)
class RegisterSchema(BaseModel):
    id: int | None = None
    user_id: int
    info: str | None = None  # Champ optionnel
    email: str
    telephone: int
    adresse: str
    class Config:
        from_attributes = True

# --- Schéma Pydantic Realisation ---
class RealisationSchema(BaseModel):
    id: int | None = None
    titre: str
    description: str
    image: str
    lien: str | None = None
    class Config:
        from_attributes = True


# --- Branding Routes ---
@router.post("/branding/", response_model=BrandingSchema)
def create_branding(name: str = Form(...), image: UploadFile = File(...), db: Session = Depends(get_db)):
    ext = os.path.splitext(image.filename)[1]
    unique_filename = f"{uuid.uuid4()}{ext}"
    image_path = os.path.join(UPLOADS_DIR, unique_filename)
    with open(image_path, "wb") as f:
        f.write(image.file.read())
    branding = Branding(name=name, image=unique_filename)
    db.add(branding)
    db.commit()
    db.refresh(branding)
    return branding

@router.get("/branding/image/{filename}")
def get_branding_image(filename: str):
    image_path = os.path.join(UPLOADS_DIR, filename)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path)

@router.get("/branding/", response_model=list[BrandingSchema])
def get_brandings(db: Session = Depends(get_db)):
    return db.query(Branding).all()

@router.patch("/branding/{branding_id}", response_model=BrandingSchema)
def update_branding(branding_id: int, name: str = Form(None), image: UploadFile = File(None), db: Session = Depends(get_db)):
    branding = db.query(Branding).filter(Branding.id == branding_id).first()
    if not branding:
        raise HTTPException(status_code=404, detail="Branding not found")
    if name:
        branding.name = name
    if image:
        image_path = os.path.join(UPLOADS_DIR, image.filename)
        with open(image_path, "wb") as f:
            f.write(image.file.read())
        branding.image = image.filename
    db.commit()
    db.refresh(branding)
    return branding

# --- Branding Single & Delete ---
@router.get("/branding/{branding_id}", response_model=BrandingSchema)
def get_branding(branding_id: int, db: Session = Depends(get_db)):
    branding = db.query(Branding).filter(Branding.id == branding_id).first()
    if not branding:
        raise HTTPException(status_code=404, detail="Branding not found")
    return branding

@router.delete("/branding/{branding_id}", response_model=BrandingSchema)
def delete_branding(branding_id: int, db: Session = Depends(get_db)):
    branding = db.query(Branding).filter(Branding.id == branding_id).first()
    if not branding:
        raise HTTPException(status_code=404, detail="Branding not found")
    db.delete(branding)
    db.commit()
    return branding

# --- Features Routes ---
@router.post("/features/", response_model=FeaturesSchema)
def create_feature(alt: str = Form(...), image: UploadFile = File(...), title: str = Form(...), text: str = Form(...), db: Session = Depends(get_db)):
    image_path = os.path.join(UPLOADS_DIR, image.filename)
    with open(image_path, "wb") as f:
        f.write(image.file.read())
    feature = Features(alt=alt, image=image.filename, title=title, text=text)
    db.add(feature)
    db.commit()
    db.refresh(feature)
    return feature

@router.get("/features/", response_model=list[FeaturesSchema])
def get_features(db: Session = Depends(get_db)):
    return db.query(Features).all()


@router.get("/features/{features_id}", response_model=FeaturesSchema)
def get_features(features_id: int, db: Session = Depends(get_db)):
    features = db.query(Features).filter(Features.id == features_id).first()
    if not features:
        raise HTTPException(status_code=404, detail="features not found")
    return features

@router.get("/features/image/{filename}")
def get_features_image(filename: str):
    image_path = os.path.join(UPLOADS_DIR, filename)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path)

@router.delete("/features/{features_id}", response_model=FeaturesSchema)
def delete_feature(features_id: int, db: Session = Depends(get_db)):
    feature = db.query(Features).filter(Features.id == features_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    db.delete(feature)
    db.commit()
    return feature

@router.patch("/features/{feature_id}", response_model=FeaturesSchema)
def update_feature(feature_id: int, alt: str = Form(None), image: UploadFile = File(None), title: str = Form(None), text: str = Form(None), db: Session = Depends(get_db)):
    feature = db.query(Features).filter(Features.id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    if alt:
        feature.alt = alt
    if image:
        image_path = os.path.join(UPLOADS_DIR, image.filename)
        with open(image_path, "wb") as f:
            f.write(image.file.read())
        feature.image = image.filename
    if title:
        feature.title = title
    if text:
        feature.text = text
    db.commit()
    db.refresh(feature)
    return feature

# --- BulletPoints Routes ---
@router.post("/bulletpoints/", response_model=BulletPointsSchema)
def create_bulletpoint(alt: str = Form(...), image: UploadFile = File(...), title: str = Form(...), text: str = Form(...), db: Session = Depends(get_db)):
    image_path = os.path.join(UPLOADS_DIR, image.filename)
    with open(image_path, "wb") as f:
        f.write(image.file.read())
    bullet = BulletPoints(alt=alt, image=image.filename, title=title, text=text)
    db.add(bullet)
    db.commit()
    db.refresh(bullet)
    return bullet

@router.get("/bulletpoints/", response_model=list[BulletPointsSchema])
def get_bulletpoints(db: Session = Depends(get_db)):
    return db.query(BulletPoints).all()

@router.get("/bulletpoints/{bullet_id}", response_model=BulletPointsSchema)
def get_single_bulletpoint(bullet_id: int, db: Session = Depends(get_db)):
    bullet = db.query(BulletPoints).filter(BulletPoints.id == bullet_id).first()
    if not bullet:
        raise HTTPException(status_code=404, detail="BulletPoint not found")
    return bullet

@router.get("/bulletpoints/image/{filename}")
def get_bulletpoint_image(filename: str, db: Session = Depends(get_db)):
    image_path = os.path.join(UPLOADS_DIR, filename)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path)


@router.patch("/bulletpoints/{bullet_id}", response_model=BulletPointsSchema)
def update_bulletpoint(bullet_id: int, alt: str = Form(None), image: UploadFile = File(None), title: str = Form(None), text: str = Form(None), db: Session = Depends(get_db)):
    bullet = db.query(BulletPoints).filter(BulletPoints.id == bullet_id).first()
    if not bullet:
        raise HTTPException(status_code=404, detail="BulletPoint not found")
    if alt:
        bullet.alt = alt
    if image:
        image_path = os.path.join(UPLOADS_DIR, image.filename)
        with open(image_path, "wb") as f:
            f.write(image.file.read())
        bullet.image = image.filename
    if title:
        bullet.title = title
    if text:
        bullet.text = text
    db.commit()
    db.refresh(bullet)
    return bullet

@router.delete("/bullet/{bullet_id}", response_model=BulletPointsSchema)
def delete_bullet(bullet_id: int, db: Session = Depends(get_db)):
    bullet = db.query(BulletPoints).filter(BulletPoints.id == bullet_id).first()
    if not bullet:
        raise HTTPException(status_code=404, detail="Branding not found")
    db.delete(bullet)
    db.commit()
    return bullet

# --- Social Routes ---
@router.post("/social/", response_model=SocialSchema)
def create_social(item: SocialSchema, db: Session = Depends(get_db)):
    social = Social(ico=item.ico, alt=item.alt, link=item.link)
    db.add(social)
    db.commit()
    db.refresh(social)
    return social

@router.get("/social/", response_model=list[SocialSchema])
def get_socials(db: Session = Depends(get_db)):
    return db.query(Social).all()

@router.patch("/social/{social_id}", response_model=SocialSchema)
def update_social(social_id: int, item: SocialSchema, db: Session = Depends(get_db)):
    social = db.query(Social).filter(Social.id == social_id).first()
    if not social:
        raise HTTPException(status_code=404, detail="Social not found")
    social.ico = item.ico or social.ico
    social.alt = item.alt or social.alt
    social.link = item.link or social.link
    db.commit()
    db.refresh(social)
    return social

# --- Social Single & Delete ---
@router.get("/social/{social_id}", response_model=SocialSchema)
def get_social(social_id: int, db: Session = Depends(get_db)):
    social = db.query(Social).filter(Social.id == social_id).first()
    if not social:
        raise HTTPException(status_code=404, detail="Social not found")
    return social

@router.delete("/social/{social_id}", response_model=SocialSchema)
def delete_social(social_id: int, db: Session = Depends(get_db)):
    social = db.query(Social).filter(Social.id == social_id).first()
    if not social:
        raise HTTPException(status_code=404, detail="Social not found")
    db.delete(social)
    db.commit()
    return social


# --- Register Routes ---
@router.post("/register/", response_model=RegisterSchema)
def create_register(
    user_id: int = Form(...),
    info: str = Form(None),
    email: str = Form(...),
    telephone: int = Form(...),
    adresse: str = Form(...),
    db: Session = Depends(get_db)
):
    register = Register(
        user_id=user_id,
        info=info,
        email=email,
        telephone=telephone,
        adresse=adresse
    )
    db.add(register)
    db.commit()
    db.refresh(register)
    return register

@router.patch("/register/{register_id}", response_model=RegisterSchema)
def update_register(
    register_id: int,
    info: str = Form(None),
    email: str = Form(...),
    telephone: int = Form(...),
    adresse: str = Form(...),
    db: Session = Depends(get_db)
):
    register = db.query(Register).filter(Register.id == register_id).first()
    if not register:
        raise HTTPException(status_code=404, detail="Register not found")
    register.info = info
    register.email = email
    register.telephone = telephone
    register.adresse = adresse
    db.commit()
    db.refresh(register)
    return register

@router.get("/register/", response_model=list[RegisterSchema])
def get_registers(db: Session = Depends(get_db)):
    return db.query(Register).all()

@router.get("/register/{register_id}", response_model=RegisterSchema)
def get_register(register_id: int, db: Session = Depends(get_db)):
    register = db.query(Register).filter(Register.id == register_id).first()
    if not register:
        raise HTTPException(status_code=404, detail="Register not found")
    return register

@router.delete("/register/{register_id}", response_model=RegisterSchema)
def delete_register(register_id: int, db: Session = Depends(get_db)):
    register = db.query(Register).filter(Register.id == register_id).first()
    if not register:
        raise HTTPException(status_code=404, detail="Register not found")
    db.delete(register)
    db.commit()
    return register


# --- Routes Realisation ---
@router.post("/realisations/", response_model=RealisationSchema)
def create_realisation(
    titre: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(...),
    lien: str = Form(None),
    db: Session = Depends(get_db)
):
    ext = os.path.splitext(image.filename)[1]
    unique_filename = f"{uuid.uuid4()}{ext}"
    image_path = os.path.join(UPLOADS_DIR, unique_filename)
    with open(image_path, "wb") as f:
        f.write(image.file.read())
    realisation = Realisation(
        titre=titre,
        description=description,
        image=unique_filename,
        lien=lien
    )
    db.add(realisation)
    db.commit()
    db.refresh(realisation)
    return realisation

@router.get("/realisations/", response_model=list[RealisationSchema])
def get_realisations(db: Session = Depends(get_db)):
    return db.query(Realisation).all()

@router.get("/realisations/{realisation_id}", response_model=RealisationSchema)
def get_realisation(realisation_id: int, db: Session = Depends(get_db)):
    realisation = db.query(Realisation).filter(Realisation.id == realisation_id).first()
    if not realisation:
        raise HTTPException(status_code=404, detail="Realisation not found")
    return realisation

@router.get("/realisations/image/{filename}")
def get_realisations_image(filename: str):
    image_path = os.path.join(UPLOADS_DIR, filename)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path)

@router.patch("/realisations/{realisation_id}", response_model=RealisationSchema)
def update_realisation(realisation_id: int, titre: str = Form(None), description: str = Form(None), image: str = Form(None), lien: str = Form(None), db: Session = Depends(get_db)):
    realisation = db.query(Realisation).filter(Realisation.id == realisation_id).first()
    if not realisation:
        raise HTTPException(status_code=404, detail="Realisation not found")
    if titre:
        realisation.titre = titre
    if description:
        realisation.description = description
    if image:
        realisation.image = image
    if lien:
        realisation.lien = lien
    db.commit()
    db.refresh(realisation)
    return realisation

@router.delete("/realisations/{realisation_id}", response_model=RealisationSchema)
def delete_realisation(realisation_id: int, db: Session = Depends(get_db)):
    realisation = db.query(Realisation).filter(Realisation.id == realisation_id).first()
    if not realisation:
        raise HTTPException(status_code=404, detail="Realisation not found")
    db.delete(realisation)
    db.commit()
    return realisation

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez vos domaines
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)