"""Record sheet for tracking game data."""

from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class WeeklyRecord:
    """Record for a single week's data."""
    week: int
    inventory: int
    backlog: int
    order_placed: int
    cost: float
    
    def __str__(self) -> str:
        """String representation of the weekly record."""
        return (f"Week {self.week}: Inventory={self.inventory}, "
                f"Backlog={self.backlog}, Order={self.order_placed}, "
                f"Cost=${self.cost:.2f}")


class RecordSheet:
    """Record sheet for tracking weekly game data."""
    
    INVENTORY_COST_PER_CASE = 0.50
    BACKLOG_COST_PER_CASE = 1.00
    
    def __init__(self, team_name: str, position: str):
        """
        Initialize a record sheet.
        
        Args:
            team_name: Name of the team/brewery
            position: Position name (Retailer, Wholesaler, Distributor, Factory)
        """
        self.team_name = team_name
        self.position = position
        self.records: List[WeeklyRecord] = []
    
    def record_week(self, week: int, inventory: int, backlog: int, 
                    order_placed: int) -> WeeklyRecord:
        """
        Record data for a week.
        
        Args:
            week: Week number
            inventory: Current inventory (0 if backlogged)
            backlog: Current backlog (0 if inventory positive)
            order_placed: Order placed this week
            
        Returns:
            The weekly record created
        """
        cost = self.calculate_weekly_cost(inventory, backlog)
        record = WeeklyRecord(
            week=week,
            inventory=inventory,
            backlog=backlog,
            order_placed=order_placed,
            cost=cost
        )
        self.records.append(record)
        return record
    
    def calculate_weekly_cost(self, inventory: int, backlog: int) -> float:
        """
        Calculate the cost for a week.
        
        Args:
            inventory: Current inventory
            backlog: Current backlog
            
        Returns:
            Weekly cost in dollars
        """
        inventory_cost = inventory * self.INVENTORY_COST_PER_CASE
        backlog_cost = backlog * self.BACKLOG_COST_PER_CASE
        return inventory_cost + backlog_cost
    
    def get_total_cost(self) -> float:
        """Get the total cost across all recorded weeks."""
        return sum(record.cost for record in self.records)
    
    def get_total_inventory(self) -> int:
        """Get the total inventory across all recorded weeks."""
        return sum(record.inventory for record in self.records)
    
    def get_total_backlog(self) -> int:
        """Get the total backlog across all recorded weeks."""
        return sum(record.backlog for record in self.records)
    
    def get_week_data(self, week: int) -> Optional[WeeklyRecord]:
        """Get data for a specific week."""
        for record in self.records:
            if record.week == week:
                return record
        return None
    
    def get_orders_history(self) -> List[int]:
        """Get the history of orders placed."""
        return [record.order_placed for record in self.records]
    
    def get_effective_inventory_history(self) -> List[int]:
        """
        Get the effective inventory history (negative for backlog).
        
        Returns:
            List of effective inventory values (positive for inventory, 
            negative for backlog)
        """
        return [record.inventory - record.backlog for record in self.records]
    
    def print_summary(self) -> None:
        """Print a summary of the record sheet."""
        print(f"\n{self.team_name} - {self.position}")
        print("=" * 50)
        print(f"{'Week':>4} {'Inventory':>10} {'Backlog':>10} "
              f"{'Order':>10} {'Cost':>10}")
        print("-" * 50)
        
        for record in self.records:
            print(f"{record.week:>4} {record.inventory:>10} "
                  f"{record.backlog:>10} {record.order_placed:>10} "
                  f"${record.cost:>9.2f}")
        
        print("-" * 50)
        print(f"Total Cost: ${self.get_total_cost():.2f}")
        print(f"Total Inventory: {self.get_total_inventory()} cases")
        print(f"Total Backlog: {self.get_total_backlog()} cases")