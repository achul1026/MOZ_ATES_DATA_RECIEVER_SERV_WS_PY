from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MozCameraEnfOrg(Base):
    __tablename__ = 'MOZ_CAMERA_ENF_ORG'

    idx = Column(Integer, primary_key=True)
    code = Column(String(100))
    enforce_lane = Column(Integer)
    avg_speed = Column(Integer)
    enforce_speed = Column(Integer)
    signal_system = Column(Integer)
    signal_info = Column(Integer)
    enforce_mode = Column(Integer)
    time = Column(Integer)
    addr = Column(String(255))
    enforce_time = Column(DateTime)
    car_plate = Column(String(100))
    enforce_code = Column(Integer)
    speed_limit = Column(Integer)
    cr_dt = Column(DateTime)

class MozCameraEnfOrgFile(Base):
    __tablename__ = 'MOZ_CAMERA_ENF_ORG_FILE'

    idx = Column(Integer, primary_key=True)
    org_idx = Column(Integer, nullable=False)
    seq = Column(Integer, nullable=False)
    file_path = Column(String(255), nullable=False)
