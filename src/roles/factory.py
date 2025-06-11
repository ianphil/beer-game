"""Factory role implementation for the Beer Game."""

from .base_role import BaseRole
from .delays import ProductionDelay


class Factory(BaseRole):
    """
    Factory role in the Beer Game.
    
    The factory:
    - Receives orders from the Distributor (after delay)
    - Ships to the Distributor
    - Sets production levels (no upstream supplier)
    - Has production delay instead of ordering delay
    - Has unlimited production capacity
    """
    
    def __init__(self, team_name: str):
        """
        Initialize the Factory.
        
        Args:
            team_name: Name of the team/brewery
        """
        super().__init__(team_name, "Factory")
        
        # Replace outgoing order delay with production delay
        self.production_delay = ProductionDelay()
        self.outgoing_order_delay = None  # Factory doesn't order upstream
        
        # Track orders from distributor and production
        self.distributor_order_received = 0
        self.last_production_request = 4  # Initial equilibrium
    
    def step_1_receive_inventory(self) -> int:
        """
        Step 1: Receive beer from production delay (not shipping).
        
        Returns:
            Amount of beer produced
        """
        # Factory receives from production, not shipping
        produced = self.production_delay.advance()
        self.inventory += produced
        
        # Also advance incoming shipping (though not used)
        self.incoming_shipping_delay.advance()
        
        return produced
    
    def step_4_advance_order_slips(self) -> None:
        """
        Step 4: Convert production request to production.
        
        For factory, this means moving last week's production request
        into the production delay pipeline.
        """
        # Factory doesn't have outgoing orders, just production
        pass
    
    def step_5_place_order(self) -> int:
        """
        Step 5: Set production level (not place order).
        
        This is the decision point. In a real game, this would be
        determined by the human player or an AI strategy.
        
        Returns:
            Production amount to request
        """
        # Simple strategy: produce what was ordered by distributor
        # In a real game, this would be the player's decision
        return self.current_incoming_order
    
    def execute_week(self, incoming_order: int, production_decision: int) -> None:
        """
        Execute all steps for one week (factory version).
        
        Args:
            incoming_order: Orders received from distributor
            production_decision: Production level to set
        """
        self.current_week += 1
        
        # Execute factory-specific steps
        self.step_1_receive_inventory()  # From production delay
        self.step_2_fill_orders(incoming_order)
        self.step_3_record(production_decision)
        self.step_4_advance_order_slips()  # No-op for factory
        
        # Add new production request to delay pipeline
        self.production_delay.add_input(production_decision)
        self.last_production_request = production_decision
        self.last_order_placed = production_decision  # For consistency
    
    def receive_order_from_distributor(self, order: int) -> None:
        """
        Receive an order from the distributor (after mailing delay).
        
        Args:
            order: Order amount from distributor
        """
        self.distributor_order_received = order
    
    def ship_to_distributor(self, amount: int) -> None:
        """
        Ship beer to the distributor's shipping delay pipeline.
        
        Args:
            amount: Amount to ship
        """
        # In the full game, this would add to distributor's shipping delay
        pass
    
    def get_production_in_pipeline(self) -> int:
        """Get total production currently in the pipeline."""
        return self.production_delay.get_total()
    
    def get_production_slots(self) -> list[int]:
        """Get the current state of production pipeline slots."""
        return self.production_delay.get_slots()
    
    def print_status(self) -> None:
        """Print current status including production info."""
        # Skip parent's print_status to customize
        print(f"\n{self.position} - Week {self.current_week}")
        print(f"Inventory: {self.inventory} cases")
        print(f"Backlog: {self.backlog} cases")
        print(f"Current week cost: ${self.get_current_cost():.2f}")
        print(f"Total cost: ${self.get_total_cost():.2f}")
        print(f"Orders to fill: {self.get_orders_to_fill()} cases")
        print(f"Last production request: {self.last_production_request} cases")
        print(f"Production in pipeline: {self.get_production_in_pipeline()} cases")
        print(f"Order from distributor: {self.distributor_order_received} cases")
        print("Note: Factory has unlimited production capacity!")