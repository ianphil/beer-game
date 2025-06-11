"""Base role class for the Beer Game simulation."""

from abc import ABC, abstractmethod
from typing import Tuple
from .delays import ShippingDelay, OrderDelay
from .record_sheet import RecordSheet


class BaseRole(ABC):
    """Base class for all roles in the Beer Game."""
    
    INITIAL_INVENTORY = 12
    
    def __init__(self, team_name: str, position: str):
        """
        Initialize a base role.
        
        Args:
            team_name: Name of the team/brewery
            position: Position name (Retailer, Wholesaler, Distributor, Factory)
        """
        self.team_name = team_name
        self.position = position
        self.current_week = 0
        
        # Game state
        self.inventory = self.INITIAL_INVENTORY
        self.backlog = 0
        self.last_order_placed = 4  # Initial equilibrium order
        
        # Delays
        self.incoming_shipping_delay = ShippingDelay()
        self.outgoing_order_delay = OrderDelay()
        
        # Record keeping
        self.record_sheet = RecordSheet(team_name, position)
        
        # Track incoming orders
        self.current_incoming_order = 0
    
    def step_1_receive_inventory(self) -> int:
        """
        Step 1: Receive inventory from shipping delay.
        
        Returns:
            Amount of inventory received
        """
        received = self.incoming_shipping_delay.advance()
        self.inventory += received
        return received
    
    def step_2_fill_orders(self, incoming_order: int) -> Tuple[int, int]:
        """
        Step 2: Look at incoming orders and fill them.
        
        Args:
            incoming_order: New orders received this week
            
        Returns:
            Tuple of (filled_orders, remaining_backlog)
        """
        self.current_incoming_order = incoming_order
        
        # Calculate total orders to fill
        total_to_fill = incoming_order + self.backlog
        
        # Fill as many orders as possible
        if self.inventory >= total_to_fill:
            # Can fill all orders
            filled = total_to_fill
            self.inventory -= filled
            self.backlog = 0
        else:
            # Can only partially fill
            filled = self.inventory
            self.backlog = total_to_fill - filled
            self.inventory = 0
        
        return filled, self.backlog
    
    def step_3_record(self, order_placed: int) -> None:
        """
        Step 3: Record inventory/backlog and costs.
        
        Args:
            order_placed: The order that will be placed this week
        """
        self.record_sheet.record_week(
            week=self.current_week,
            inventory=self.inventory,
            backlog=self.backlog,
            order_placed=order_placed
        )
    
    def step_4_advance_order_slips(self) -> int:
        """
        Step 4: Advance the order slips through delay.
        
        Returns:
            Order that exits the delay pipeline
        """
        return self.outgoing_order_delay.advance()
    
    @abstractmethod
    def step_5_place_order(self) -> int:
        """
        Step 5: Place order (decision point).
        
        This is the only decision point in the game.
        Must be implemented by each specific role.
        
        Returns:
            Order amount to place
        """
        pass
    
    def execute_week(self, incoming_order: int, order_decision: int) -> int:
        """
        Execute all steps for one week.
        
        Args:
            incoming_order: Orders received this week
            order_decision: Order to place this week
            
        Returns:
            Amount shipped this week
        """
        self.current_week += 1
        
        # Execute all 5 steps
        self.step_1_receive_inventory()
        filled, _ = self.step_2_fill_orders(incoming_order)
        self.step_3_record(order_decision)
        self.step_4_advance_order_slips()
        
        # Add new order to delay pipeline
        self.outgoing_order_delay.add_input(order_decision)
        self.last_order_placed = order_decision
        
        return filled
    
    def get_current_cost(self) -> float:
        """Get the cost for the current week."""
        return self.record_sheet.calculate_weekly_cost(
            self.inventory, self.backlog
        )
    
    def get_total_cost(self) -> float:
        """Get the total accumulated cost."""
        return self.record_sheet.get_total_cost()
    
    def get_effective_inventory(self) -> int:
        """
        Get effective inventory (positive for inventory, negative for backlog).
        """
        return self.inventory - self.backlog
    
    def get_orders_to_fill(self) -> int:
        """Get the total orders that need to be filled."""
        return self.current_incoming_order + self.backlog
    
    def print_status(self) -> None:
        """Print current status."""
        print(f"\n{self.position} - Week {self.current_week}")
        print(f"Inventory: {self.inventory} cases")
        print(f"Backlog: {self.backlog} cases")
        print(f"Current week cost: ${self.get_current_cost():.2f}")
        print(f"Total cost: ${self.get_total_cost():.2f}")
        print(f"Orders to fill: {self.get_orders_to_fill()} cases")
        print(f"Last order placed: {self.last_order_placed} cases")