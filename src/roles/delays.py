"""Delay pipeline classes for the Beer Game simulation."""

from typing import List, Optional


class DelayPipeline:
    """Base class for delay pipelines in the Beer Game."""
    
    def __init__(self, length: int = 2, initial_value: int = 4):
        """
        Initialize a delay pipeline.
        
        Args:
            length: Number of weeks in the delay (default 2)
            initial_value: Initial value in each slot (default 4 cases)
        """
        self.length = length
        self.slots: List[int] = [initial_value] * length
    
    def advance(self) -> int:
        """
        Advance the pipeline by one week and return the output.
        
        Returns:
            The value that exits the pipeline
        """
        if not self.slots:
            return 0
        
        output = self.slots.pop(0)
        self.slots.append(0)
        return output
    
    def add_input(self, value: int) -> None:
        """Add a new value to the beginning of the pipeline."""
        if self.slots:
            self.slots[-1] = value
    
    def get_total(self) -> int:
        """Get the total value currently in the pipeline."""
        return sum(self.slots)
    
    def get_slots(self) -> List[int]:
        """Get the current state of all slots."""
        return self.slots.copy()


class ShippingDelay(DelayPipeline):
    """Shipping delay pipeline for beer delivery."""
    
    def __init__(self):
        """Initialize shipping delay with 2 weeks and 4 cases per slot."""
        super().__init__(length=2, initial_value=4)


class OrderDelay(DelayPipeline):
    """Order delay pipeline for order transmission."""
    
    def __init__(self):
        """Initialize order delay with 2 weeks and 4 orders per slot."""
        super().__init__(length=2, initial_value=4)


class ProductionDelay(DelayPipeline):
    """Production delay pipeline for factory production."""
    
    def __init__(self):
        """Initialize production delay with 2 weeks and 4 cases per slot."""
        super().__init__(length=2, initial_value=4)