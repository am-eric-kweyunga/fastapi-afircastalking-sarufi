from pydantic import BaseModel, constr, Field, validator
from typing import ClassVar, Union, Optional
import re


class PlateValidator(BaseModel):
    """Base class for plate validation with common functionality"""

    plate: str
    pattern: ClassVar[str]
    description: ClassVar[str]

    @validator("plate")
    def normalize_plate(cls, v):
        """Normalize plate number by converting to uppercase and replacing spaces with hyphens"""
        return v.upper().replace(" ", "-")

    @validator("plate")
    def validate_format(cls, v):
        if not hasattr(cls, "pattern"):
            raise ValueError("Pattern not defined for plate validator")
        if not re.match(cls.pattern, v.replace("-", " ")):
            return ValueError(
                f"Invalid format for {cls.__name__}. Expected format: {cls.description}"
            )
        return v


class PrivateVehiclePlate(PlateValidator):
    pattern: ClassVar[str] = r"^[A-Z]{3} \d{4}$"
    description: ClassVar[str] = "ABC-1234 (e.g., TBA-1234)"


class CommercialVehiclePlate(PlateValidator):
    pattern: ClassVar[str] = r"^T \d{3} [A-Z]{3}$"
    description: ClassVar[str] = "T-123-ABC (e.g., T-456-XYZ)"


class GovernmentVehiclePlate(PlateValidator):
    pattern: ClassVar[str] = r"^SU \d{4}$"
    description: ClassVar[str] = "SU-1234 (e.g., SU-5678)"


class DiplomaticVehiclePlate(PlateValidator):
    pattern: ClassVar[str] = r"^(CD|CMD) \d{4}$"
    description: ClassVar[str] = "CD-1234 or CMD-1234 (e.g., CD-5678)"


class ParastatalVehiclePlate(PlateValidator):
    pattern: ClassVar[str] = r"^STK \d{4}$"
    description: ClassVar[str] = "STK-1234 (e.g., STK-5678)"


class PoliceVehiclePlate(PlateValidator):
    pattern: ClassVar[str] = r"^PT \d{4}$"
    description: ClassVar[str] = "PT-1234 (e.g., PT-7890)"


class MilitaryVehiclePlate(PlateValidator):
    pattern: ClassVar[str] = r"^MT \d{4}$"
    description: ClassVar[str] = "MT-1234 (e.g., MT-3456)"


class MotorcyclePlate(PlateValidator):
    pattern: ClassVar[str] = r"^MC \d{3} [A-Z]{3}$"
    description: ClassVar[str] = "MC-123-ABC (e.g., MC-456-XYZ)"


class TemporaryPlate(PlateValidator):
    pattern: ClassVar[str] = r"^T\d{4}$|^T \d{3} [A-Z]{3}$"
    description: ClassVar[str] = "T1234 or T-123-ABC (e.g., T4567, T-123-ABC)"


class PersonalizedPlate(PlateValidator):
    pattern: ClassVar[str] = r"^[A-Z0-9]{1,8}$"
    description: ClassVar[str] = "CUSTOM NAME/NUMBER (e.g., KWYUNG1)"


class NGOPlate(PlateValidator):
    pattern: ClassVar[str] = r"^U \d{3} [A-Z]{3}$"
    description: ClassVar[str] = "U-123-ABC (e.g., U-789-XYZ)"


class TransitOrExportPlate(PlateValidator):
    pattern: ClassVar[str] = r"^T \d{4} EX$"
    description: ClassVar[str] = "T-1234-EX (e.g., T-5678-EX)"


class DiplomaticTemporaryPlate(PlateValidator):
    pattern: ClassVar[str] = r"^CDT \d{4}$"
    description: ClassVar[str] = "CDT-1234 (e.g., CDT-4321)"


class DealerPlate(PlateValidator):
    pattern: ClassVar[str] = r"^D \d{4} [A-Z]{3}$"
    description: ClassVar[str] = "D-1234-ABC (e.g., D-6789-XYZ)"


class PlateNumberValidator:
    """Main class for validating and formatting Tanzanian plate numbers"""

    PLATE_TYPES = {
        "private": PrivateVehiclePlate,
        "commercial": CommercialVehiclePlate,
        "government": GovernmentVehiclePlate,
        "diplomatic": DiplomaticVehiclePlate,
        "parastatal": ParastatalVehiclePlate,
        "police": PoliceVehiclePlate,
        "military": MilitaryVehiclePlate,
        "motorcycle": MotorcyclePlate,
        "temporary": TemporaryPlate,
        "personalized": PersonalizedPlate,
        "ngo": NGOPlate,
        "transit": TransitOrExportPlate,
        "diplomatic_temp": DiplomaticTemporaryPlate,
        "dealer": DealerPlate,
    }

    @classmethod
    def validate_plate(
        cls, plate_number: str
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Validate a plate number and return its normalized form

        Returns:
        tuple: (is_valid, normalized_plate, plate_type)
        """
        # Remove any existing hyphens and convert to uppercase
        plate_number = plate_number.upper().replace("-", " ").strip()

        for plate_type, validator_class in cls.PLATE_TYPES.items():
            try:
                validated_plate = validator_class(plate=plate_number)
                return True, validated_plate.plate, plate_type
            except ValueError:
                continue

        return False, None, None

    @classmethod
    def get_plate_format(cls, plate_type: str) -> Optional[str]:
        """Get the expected format for a specific plate type"""
        validator_class = cls.PLATE_TYPES.get(plate_type)
        if validator_class:
            return validator_class.description
        return None

    @classmethod
    def get_all_formats(cls) -> dict:
        """Get all supported plate formats with their descriptions"""
        return {
            plate_type: validator_class.description
            for plate_type, validator_class in cls.PLATE_TYPES.items()
        }
