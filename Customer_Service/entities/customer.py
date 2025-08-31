from typing import List, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class Address(BaseModel):
    """
    Represents the address of a customer.
    """
    street: str
    city: str
    state: str
    zip: str
    model_config = ConfigDict(from_attributes=True)

class Product(BaseModel):
    """
    Represents a product in a customer's purchase history.
    """
    product_id: str
    name: str
    quantity: int
    model_config = ConfigDict(from_attributes=True)

class Purchase(BaseModel):
    """
    Represents a customer's purchase.
    """
    date: str
    items: List[Product]
    total_amount: float
    model_config = ConfigDict(from_attributes=True)

class CommunicationPreferences(BaseModel):
    """
    Represents a customer's communication preferences.
    """
    email: bool = True
    sms: bool =True
    push_notifications: bool = True
    model_config = ConfigDict(from_attributes=True)

class GardenProfile(BaseModel):
    """
    Represents a customer's garden profile.
    """
    type: str
    size: str
    sun_exposure: str
    soil_type: str
    interests: List[str]
    model_config = ConfigDict(from_attributes=True)

class Customer(BaseModel):
    """
    Represents a customer.
    """

    account_number: str
    customer_id: str
    customer_first_name: str
    customer_last_name: str
    email: str
    phone_number: str
    customer_start_date: str
    years_as_customer: int
    billing_address: Address
    purchase_history: List[Purchase]
    loyalty_points: int
    preferred_store: str
    communication_preferences: CommunicationPreferences
    garden_profile: GardenProfile
    scheduled_appointments: Dict = Field(default_factory=dict)
    model_config = ConfigDict(from_attributes=True)

    def to_json(self) -> str:
        """
        Converts the customer objectto a JSON string.

        :return:
            A JSON string representing the customer object
        """

        return self.model_dump_json(indent=4)

    @staticmethod
    def get_customer(current_customer_id: str) -> Optional['Customer']:
        """
        Generates and returns a sample customer with mock data for the given customer ID.
        
        :param current_customer_id: The ID of the customer to retrieve
        :return:
            A Customer object with sample data if found, None otherwise
        """
        # Return None for unknown customer IDs (simulate database lookup)
        if current_customer_id not in ["CUST001", "CUST002", "CUST003"]:
            return None
            
        sample_address = Address(
            street="123 Garden Lane",
            city="Springfield",
            state="IL",
            zip="62701"
        )
        
        sample_products = [
            Product(product_id="P001", name="Tomato Seeds", quantity=2),
            Product(product_id="P002", name="Garden Hose", quantity=1),
            Product(product_id="P003", name="Fertilizer", quantity=3)
        ]
        
        sample_purchase_1 = Purchase(
                    date="2023-03-05",
                    items=[
                        Product(
                            product_id="fert-111",
                            name="All-Purpose Fertilizer",
                            quantity=1,
                        ),
                        Product(
                            product_id="trowel-222",
                            name="Gardening Trowel",
                            quantity=1,
                        ),
                    ],
                    total_amount=35.98,
                )

        sample_purchase_2 = Purchase(
                    date="2023-07-12",
                    items=[
                        Product(
                            product_id="seeds-333",
                            name="Tomato Seeds (Variety Pack)",
                            quantity=2,
                        ),
                        Product(
                            product_id="pots-444",
                            name="Terracotta Pots (6-inch)",
                            quantity=4,
                        ),
                    ],
                    total_amount=42.5,
                )
        sample_purchase_3 = Purchase(
                    date="2024-01-20",
                    items=[
                        Product(
                            product_id="gloves-555",
                            name="Gardening Gloves (Leather)",
                            quantity=1,
                        ),
                        Product(
                            product_id="pruner-666",
                            name="Pruning Shears",
                            quantity=1,
                        ),
                    ],
                    total_amount=55.25,
                )
        
        sample_comm_prefs = CommunicationPreferences(
            email=True,
            sms=False,
            push_notifications=True
        )
        
        sample_garden_profile = GardenProfile(
            type="Vegetable Garden",
            size="Medium",
            sun_exposure="Full Sun",
            soil_type="Loamy",
            interests=["Organic Gardening", "Composting", "Herb Growing"]
        )
        
        return Customer(
            account_number="ACC12345",
            customer_id=current_customer_id,
            customer_first_name="John",
            customer_last_name="Smith",
            email="john.smith@email.com",
            phone_number="555-0123",
            customer_start_date="2020-05-01",
            years_as_customer=4,
            billing_address=sample_address,
            purchase_history=[sample_purchase_1, sample_purchase_2, sample_purchase_3],
            loyalty_points=250,
            preferred_store="Springfield Garden Center",
            communication_preferences=sample_comm_prefs,
            garden_profile=sample_garden_profile,
            scheduled_appointments={}
        )