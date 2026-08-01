import random
import uuid

from app.services.auth_service import pwd_context
from faker import Faker
from sqlalchemy.orm import Session

from app.models.social import Profile

LOCALE_DISTRIBUTION = {
    "tr_TR": {"country": "Türkiye", "timezone": "Europe/Istanbul", "weight": 80},
    "en_US": {"country": "ABD", "timezone": "America/New_York", "weight": 45},
    "ja_JP": {"country": "Japonya", "timezone": "Asia/Tokyo", "weight": 35},
    "fr_FR": {"country": "Fransa", "timezone": "Europe/Paris", "weight": 30},
    "ko_KR": {"country": "Güney Kore", "timezone": "Asia/Seoul", "weight": 25},
    "it_IT": {"country": "İtalya", "timezone": "Europe/Rome", "weight": 20},
    "en_GB": {"country": "İngiltere", "timezone": "Europe/London", "weight": 15},
}

USER_ROLES = [
    {"role": "influencer", "weight": 5},
    {"role": "active", "weight": 25},
    {"role": "casual", "weight": 45},
    {"role": "new", "weight": 15},
    {"role": "silent", "weight": 10},
]

def generate_users(db: Session, total_users: int = 250):
    print(f"[Seed] {total_users} sentetik kullanıcı üretiliyor...")
    
    # Calculate exact numbers based on weights
    total_locale_weight = sum(l["weight"] for l in LOCALE_DISTRIBUTION.values())
    total_role_weight = sum(r["weight"] for r in USER_ROLES)
    
    locales = list(LOCALE_DISTRIBUTION.keys())
    locale_weights = [l["weight"]/total_locale_weight for l in LOCALE_DISTRIBUTION.values()]
    
    roles = [r["role"] for r in USER_ROLES]
    role_weights = [r["weight"]/total_role_weight for r in USER_ROLES]
    
    fakers = {loc: Faker(loc) for loc in locales}
    
    users = []
    
    # Shared password hash to speed up generation
    common_password_hash = pwd_context.hash("Password123!")
    
    for _ in range(total_users):
        locale = random.choices(locales, weights=locale_weights, k=1)[0]
        role = random.choices(roles, weights=role_weights, k=1)[0]
        
        fake = fakers[locale]
        
        gender = random.choice(["M", "F"])
        if gender == "M":
            display_name = fake.name_male()
        else:
            display_name = fake.name_female()
            
        username = fake.user_name() + str(random.randint(100, 999))
        email = fake.ascii_free_email()
        
        # Profile Data
        country_name = LOCALE_DISTRIBUTION[locale]["country"]
        timezone = LOCALE_DISTRIBUTION[locale]["timezone"]
        
        bio_templates = [
            f"Fashion lover from {country_name}.",
            "OOTD everyday! ✨",
            "Minimalist wardrobe enthusiast.",
            "Always exploring new styles.",
            fake.sentence()
        ]
        
        profile = Profile(
            id=uuid.uuid4(),
            email=email,
            password_hash=common_password_hash,
            username=username,
            display_name=display_name,
            avatar_url=f"https://ui-avatars.com/api/?name={display_name.replace(' ', '+')}&background=random",
            bio=random.choice(bio_templates),
            location=f"{fake.city()}, {country_name}",
            timezone=timezone,
            height=str(random.randint(150, 195)),
            weight=str(random.randint(45, 95)),
        )
        # Store role temporarily inside the object (not a column) to use in later scripts
        profile._seed_role = role
        users.append(profile)
        
    db.bulk_save_objects(users, return_defaults=True)
    db.commit()
    
    # Refresh is not available for bulk_save, but we can query them later if needed
    print(f"[Seed] {total_users} kullanıcı başarıyla eklendi.")
    return users
