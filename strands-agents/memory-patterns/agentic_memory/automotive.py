import random
import json
from typing import List, Dict, Tuple, Optional
from typing_extensions import TypedDict
from datetime import datetime
import os


class RepairCostEstimate(TypedDict):
    item: str
    labor_cost: float
    parts_cost: float
    total_cost: float


class AutomotiveKnowledgeToolkit:
    def __init__(self, vehicle_data_path: str = "vechicle_model.json"):
        self.vehicle_data_path = vehicle_data_path
        self.fallback_vehicle_catalog = {
            "Toyota": ["Camry", "Corolla", "RAV4"],
            "Honda": ["Civic", "Accord", "CR-V"],
            "Ford": ["F-150", "Escape", "Explorer"],
            "Chevrolet": ["Malibu", "Equinox", "Silverado"],
            "BMW": ["X3", "3 Series", "5 Series"],
            "Tesla": ["Model 3", "Model Y", "Model S"],
            "Nissan": ["Altima", "Sentra", "Rogue"],
            "Hyundai": ["Elantra", "Tucson", "Santa Fe"],
            "Jeep": ["Wrangler", "Cherokee", "Compass"],
            "Audi": ["A4", "Q5", "A6"]
        }
        self.fallback_years = list(range(2015, 2023))  # 2015–2022
    def estimate_repair_costs(self, repair_items: List[str]) -> List[RepairCostEstimate]:
        estimates: List[RepairCostEstimate] = []

        for item in repair_items:
            labor_cost = round(random.uniform(50, 200), 2)
            parts_cost = round(random.uniform(30, 300), 2)
            total_cost = labor_cost + parts_cost
            estimates.append({
                "item": item,
                "labor_cost": labor_cost,
                "parts_cost": parts_cost,
                "total_cost": total_cost
            })

        return estimates

    def get_vehicle_info(self, vin: str) -> Tuple[str, str, int]:
        try:
            if os.path.exists(self.vehicle_data_path):
                with open(self.vehicle_data_path, "r") as f:
                    data = json.load(f)
                record = data.get(vin)
                if record and all(k in record for k in ("make", "model", "year")):
                    return record["make"], record["model"], record["year"]
        except Exception:
            pass  # fallback if anything fails

        fallback_make = random.choice(list(self.fallback_vehicle_catalog.keys()))
        fallback_model = random.choice(self.fallback_vehicle_catalog[fallback_make])
        fallback_year = random.choice(self.fallback_years)

        return fallback_make, fallback_model, fallback_year 
