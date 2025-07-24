# Smart Parking Lot Management System with Streamlit UI
import time
import streamlit as st

class Vehicle:
    def __init__(self, license_plate):
        self.license_plate = license_plate
        self.entry_time = time.time()

class Car(Vehicle): pass
class Bike(Vehicle): pass
class Truck(Vehicle): pass

class ParkingSpot:
    def __init__(self, spot_id, spot_type):
        self.spot_id = spot_id
        self.spot_type = spot_type
        self.is_occupied = False
        self.vehicle = None

class ParkingLot:
    def __init__(self):
        self.spots = []
        self.parked_vehicles = {}
        self.vehicle_type_map = {"Car": Car, "Bike": Bike, "Truck": Truck}
        self.total_income = 0.0
        self.fee_rates = {"Car": 2.0, "Bike": 1.5, "Truck": 3.0}  # ₹ per minute

    def add_spot(self, spot):
        self.spots.append(spot)

    def park_vehicle(self, vehicle):
        for spot in self.spots:
            if not spot.is_occupied and vehicle.__class__.__name__ == spot.spot_type:
                spot.is_occupied = True
                spot.vehicle = vehicle
                self.parked_vehicles[vehicle.license_plate] = (spot, time.time())
                return f"Vehicle {vehicle.license_plate} parked at spot {spot.spot_id}."
        return "No available spot for this vehicle type."

    def remove_vehicle(self, license_plate):
        if license_plate not in self.parked_vehicles:
            return "Vehicle not found."

        spot, entry_time = self.parked_vehicles.pop(license_plate)
        spot.is_occupied = False
        spot.vehicle = None
        duration = time.time() - entry_time
        fee = self.calculate_fee(duration, spot.spot_type)
        self.total_income += fee
        return f"Vehicle {license_plate} has left. Parking time: {int(duration)} seconds. Fee: ₹{fee:.2f}"

    def calculate_fee(self, duration, vehicle_type):
        rate = self.fee_rates.get(vehicle_type, 1.0)
        return (duration / 60) * rate

    def get_status(self):
        status_list = []
        current_time = time.time()
        for spot in self.spots:
            status = "Occupied" if spot.is_occupied else "Available"
            duration = (current_time - spot.vehicle.entry_time) if spot.vehicle else 0
            status_list.append({
                "Spot ID": spot.spot_id,
                "Type": spot.spot_type,
                "Status": status,
                "Vehicle": spot.vehicle.license_plate if spot.vehicle else "-",
                "Duration (min)": f"{duration/60:.1f}" if spot.vehicle else "-"
            })
        return status_list

    def get_parking_summary(self):
        summary = {"Car": {"Available": 0, "Occupied": 0},
                   "Bike": {"Available": 0, "Occupied": 0},
                   "Truck": {"Available": 0, "Occupied": 0}}
        for spot in self.spots:
            if spot.is_occupied:
                summary[spot.spot_type]["Occupied"] += 1
            else:
                summary[spot.spot_type]["Available"] += 1
        return summary

# Streamlit App
st.set_page_config(page_title="Smart Parking Lot System", layout="wide")
st.title("🚗 Smart Parking Lot Management System")

if 'lot' not in st.session_state:
    st.session_state.lot = ParkingLot()

lot = st.session_state.lot

# Layout columns
col1, col2 = st.columns(2)

with col1:
    st.header("🅿️ Add Parking Spot")
    spot_id = st.text_input("Spot ID", key="add_spot_id")
    spot_type = st.selectbox("Spot Type", ["Car", "Bike", "Truck"], key="add_spot_type")
    if st.button("Add Spot"):
        if spot_id:
            lot.add_spot(ParkingSpot(spot_id, spot_type))
            st.success(f"Added spot {spot_id} for {spot_type}s.")
        else:
            st.error("Please enter a Spot ID.")

with col2:
    st.header("🚘 Park a Vehicle")
    vehicle_type = st.selectbox("Vehicle Type", ["Car", "Bike", "Truck"], key="vehicle_type")
    license_plate = st.text_input("License Plate", key="license_plate")
    if st.button("Park Vehicle"):
        if license_plate:
            if vehicle_type == 'Car': vehicle = Car(license_plate)
            elif vehicle_type == 'Bike': vehicle = Bike(license_plate)
            elif vehicle_type == 'Truck': vehicle = Truck(license_plate)
            result = lot.park_vehicle(vehicle)
            st.info(result)
        else:
            st.error("Please enter a license plate.")

st.header("🚗 Remove a Vehicle")
remove_plate = st.text_input("Enter License Plate to Remove", key="remove_plate")
if st.button("Remove Vehicle"):
    if remove_plate:
        result = lot.remove_vehicle(remove_plate)
        st.warning(result)
    else:
        st.error("Please enter a license plate.")

st.header("📋 Parking Lot Status")
status = lot.get_status()
st.dataframe(status, use_container_width=True)

st.header("📊 Available vs Occupied Spots by Type")
summary = lot.get_parking_summary()
st.table(summary)

st.header("💰 Total Income")
st.metric(label="Total Earnings (₹)", value=f"₹{lot.total_income:.2f}")
