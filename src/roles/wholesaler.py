"""Wholesaler role implementation for the Beer Game."""

from .base_role import BaseRole


class Wholesaler(BaseRole):
    """
    Wholesaler role in the Beer Game.
    
    The wholesaler:
    - Receives orders from the Retailer (after delay)
    - Ships to the Retailer
    - Orders from the Distributor
    - Does NOT know actual customer demand
    """
    
    def __init__(self, team_name: str):
        """
        Initialize the Wholesaler.
        
        Args:
            team_name: Name of the team/brewery
        """
        super().__init__(team_name, "Wholesaler")
        
        # Track orders from retailer
        self.retailer_order_received = 0
    
    def step_5_place_order(self) -> int:
        """
        Step 5: Decide how much to order from distributor.
        
        This is the decision point. In a real game, this would be
        determined by the human player or an AI strategy.
        
        Returns:
            Order amount to place to distributor
        """
        # Simple strategy: order what was received from retailer
        # In a real game, this would be the player's decision
        return self.current_incoming_order
    
    def receive_order_from_retailer(self, order: int) -> None:
        """
        Receive an order from the retailer (after mailing delay).
        
        Args:
            order: Order amount from retailer
        """
        self.retailer_order_received = order
    
    def ship_to_retailer(self, amount: int) -> None:
        """
        Ship beer to the retailer's shipping delay pipeline.
        
        Args:
            amount: Amount to ship
        """
        # In the full game, this would add to retailer's shipping delay
        pass
    
    def get_order_to_upstream(self) -> int:
        """
        Get the order that will be sent upstream (to distributor).
        
        Returns:
            Order amount from the delay pipeline
        """
        # Get the order that's exiting the delay to go to distributor
        slots = self.outgoing_order_delay.get_slots()
        return slots[0] if slots else 0
    
    def print_status(self) -> None:
        """Print current status including retailer order info."""
        super().print_status()
        print(f"Order from retailer: {self.retailer_order_received} cases")
        print("Note: You don't know actual customer demand!")