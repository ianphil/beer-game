"""Full Beer Game demonstration showing the bullwhip effect."""

from roles import Retailer, Wholesaler, Distributor, Factory
from typing import List, Dict, Tuple


class BeerGameSimulation:
    """Simulates the complete Beer Game with all four positions connected."""
    
    def __init__(self, team_name: str = "Blue Moon Brewery"):
        """Initialize the simulation with all four roles."""
        self.team_name = team_name
        self.retailer = Retailer(team_name)
        self.wholesaler = Wholesaler(team_name)
        self.distributor = Distributor(team_name)
        self.factory = Factory(team_name)
        
        self.current_week = 0
        self.roles = [self.retailer, self.wholesaler, self.distributor, self.factory]
        
        # Track order history for analysis
        self.order_history: Dict[str, List[int]] = {
            "Customer": [],
            "Retailer": [],
            "Wholesaler": [],
            "Distributor": [],
            "Factory": []
        }
    
    def simulate_week(self):
        """Simulate one complete week of the game."""
        self.current_week += 1
        
        # Step 1: Get orders that are arriving this week (from delays)
        retailer_order_arriving = self.retailer.outgoing_order_delay.slots[0] if self.retailer.outgoing_order_delay.slots else 0
        wholesaler_order_arriving = self.wholesaler.outgoing_order_delay.slots[0] if self.wholesaler.outgoing_order_delay.slots else 0
        distributor_order_arriving = self.distributor.outgoing_order_delay.slots[0] if self.distributor.outgoing_order_delay.slots else 0
        
        # Step 2: Get beer shipments arriving (from delays)
        retailer_beer_arriving = self.retailer.incoming_shipping_delay.slots[0] if self.retailer.incoming_shipping_delay.slots else 0
        wholesaler_beer_arriving = self.wholesaler.incoming_shipping_delay.slots[0] if self.wholesaler.incoming_shipping_delay.slots else 0
        distributor_beer_arriving = self.distributor.incoming_shipping_delay.slots[0] if self.distributor.incoming_shipping_delay.slots else 0
        factory_beer_arriving = self.factory.production_delay.slots[0] if self.factory.production_delay.slots else 0
        
        # Step 3: Each position makes their ordering decision based on current state
        # Simple strategy: order based on incoming orders + adjustment for inventory/backlog
        retailer_decision = self.make_order_decision(self.retailer, self.retailer.get_customer_order(self.current_week))
        wholesaler_decision = self.make_order_decision(self.wholesaler, retailer_order_arriving)
        distributor_decision = self.make_order_decision(self.distributor, wholesaler_order_arriving)
        factory_decision = self.make_order_decision(self.factory, distributor_order_arriving)
        
        # Step 4: Execute the week for each position and capture shipments
        # Retailer ships to customers (not captured)
        self.retailer.execute_week(order_decision=retailer_decision)
        
        # Others ship to downstream partners  
        wholesaler_shipped = self.wholesaler.execute_week(incoming_order=retailer_order_arriving, order_decision=wholesaler_decision)
        distributor_shipped = self.distributor.execute_week(incoming_order=wholesaler_order_arriving, order_decision=distributor_decision)
        factory_shipped = self.factory.execute_week(incoming_order=distributor_order_arriving, production_decision=factory_decision)
        
        # Step 5: Add shipments to downstream shipping delays
        if wholesaler_shipped > 0:
            self.retailer.incoming_shipping_delay.add_input(wholesaler_shipped)
        if distributor_shipped > 0:
            self.wholesaler.incoming_shipping_delay.add_input(distributor_shipped)
        if factory_shipped > 0:
            self.distributor.incoming_shipping_delay.add_input(factory_shipped)
        
        # Track orders for analysis
        self.order_history["Customer"].append(self.retailer.get_customer_order(self.current_week))
        self.order_history["Retailer"].append(retailer_decision)
        self.order_history["Wholesaler"].append(wholesaler_decision)
        self.order_history["Distributor"].append(distributor_decision)
        self.order_history["Factory"].append(factory_decision)
    
    def make_order_decision(self, role, incoming_order: int) -> int:
        """
        Make ordering decision based on current state.
        
        Simple strategy that demonstrates the bullwhip effect:
        - Base order on incoming demand
        - Adjust up if backlogged
        - Adjust up if inventory is low
        """
        base_order = incoming_order
        
        # If backlogged, order extra to catch up
        if role.backlog > 0:
            base_order += role.backlog // 2
        
        # If inventory is low, order extra as safety stock
        if role.inventory < 4:
            base_order += 4
        
        return max(0, base_order)
    
    def print_week_status(self):
        """Print the current status of all positions."""
        print(f"\n{'='*80}")
        print(f"WEEK {self.current_week}")
        print(f"{'='*80}")
        
        customer_order = self.retailer.get_customer_order(self.current_week)
        print(f"\nCustomer Order: {customer_order} cases")
        print(f"{'-'*80}")
        
        print(f"{'Position':<12} {'Inventory':>10} {'Backlog':>10} {'Cost':>10} {'Order Placed':>15}")
        print(f"{'-'*80}")
        
        for role in self.roles:
            last_order = role.record_sheet.records[-1].order_placed if role.record_sheet.records else 0
            print(f"{role.position:<12} {role.inventory:>10} {role.backlog:>10} "
                  f"${role.get_current_cost():>9.2f} {last_order:>15}")
    
    def print_order_amplification(self):
        """Show how orders amplify through the supply chain."""
        print(f"\n{'='*80}")
        print("ORDER AMPLIFICATION ANALYSIS")
        print(f"{'='*80}")
        
        print(f"\n{'Position':<12} {'Min Order':>10} {'Max Order':>10} {'Avg Order':>10} {'Amplification':>15}")
        print(f"{'-'*80}")
        
        customer_avg = sum(self.order_history["Customer"]) / len(self.order_history["Customer"]) if self.order_history["Customer"] else 0
        
        for position in ["Customer", "Retailer", "Wholesaler", "Distributor", "Factory"]:
            orders = self.order_history[position]
            if orders:
                min_order = min(orders)
                max_order = max(orders)
                avg_order = sum(orders) / len(orders)
                amplification = (max_order - min_order) / 4.0  # Relative to demand change of 4
                
                print(f"{position:<12} {min_order:>10} {max_order:>10} {avg_order:>10.1f} {amplification:>15.1f}x")
    
    def print_cost_summary(self):
        """Print cost summary for all positions."""
        print(f"\n{'='*80}")
        print("COST SUMMARY")
        print(f"{'='*80}")
        
        total_cost = 0
        for role in self.roles:
            cost = role.get_total_cost()
            total_cost += cost
            print(f"{role.position:<12}: ${cost:>10.2f}")
        
        print(f"{'-'*40}")
        print(f"{'TOTAL':<12}: ${total_cost:>10.2f}")
    
    def plot_inventory_trends(self):
        """Create ASCII plot of inventory trends."""
        print(f"\n{'='*80}")
        print("INVENTORY/BACKLOG TRENDS (Effective Inventory)")
        print(f"{'='*80}")
        
        # Create simple ASCII plot
        height = 20
        width = 50
        
        for role in self.roles:
            print(f"\n{role.position}:")
            data = role.record_sheet.get_effective_inventory_history()
            
            if not data:
                continue
                
            # Scale data to fit
            min_val = min(data)
            max_val = max(data)
            range_val = max_val - min_val if max_val != min_val else 1
            
            # Print scale
            print(f"  {max_val:>4} |")
            
            # Plot data
            for row in range(height):
                line = f"  {'':>4} |"
                threshold = max_val - (row * range_val / height)
                
                for week, value in enumerate(data):
                    if len(line) - 7 < width and value >= threshold - (range_val / height / 2):
                        line += "*"
                    else:
                        line += " " if len(line) - 7 < width else ""
                
                if row == height // 2:
                    print(f"  {int((max_val + min_val) / 2):>4} |" + line[7:])
                elif row == height - 1:
                    print(f"  {min_val:>4} |" + line[7:])
                else:
                    print(line)
            
            print(f"  {'':>4} +" + "-" * min(len(data), width))
            print(f"  {'':>4}  0" + " " * (min(len(data), width) - 2) + f"{len(data)}")
            print(f"  {'':>4}  Weeks")


def main():
    """Run the full Beer Game simulation."""
    print("=" * 80)
    print("FULL BEER GAME SIMULATION - DEMONSTRATING THE BULLWHIP EFFECT")
    print("=" * 80)
    
    # Create simulation
    sim = BeerGameSimulation("Blue Moon Brewery")
    
    print("\nGame Setup:")
    print("- Customer demand: 4 cases/week for weeks 1-4, then 8 cases/week")
    print("- All positions start with 12 cases inventory")
    print("- 2-week delays for shipping and orders")
    print("- Costs: $0.50/case inventory, $1.00/case backlog")
    
    # Run simulation for 36 weeks
    print("\nRunning simulation for 36 weeks...")
    
    # Show status at key weeks
    key_weeks = [1, 5, 10, 15, 20, 25, 30, 36]
    
    for week in range(1, 37):
        sim.simulate_week()
        
        if week in key_weeks:
            sim.print_week_status()
    
    # Show analysis
    sim.print_order_amplification()
    sim.print_cost_summary()
    sim.plot_inventory_trends()
    
    # Print key insights
    print(f"\n{'='*80}")
    print("KEY INSIGHTS - THE BULLWHIP EFFECT")
    print(f"{'='*80}")
    
    print("\n1. DEMAND AMPLIFICATION:")
    print("   - Customer demand only changed from 4 to 8 cases (100% increase)")
    print("   - But upstream orders fluctuated much more dramatically")
    
    print("\n2. PHASE LAG:")
    print("   - Each position reacts to changes with a delay")
    print("   - The factory is the last to feel the demand change")
    print("   - And the last to recover from overproduction")
    
    print("\n3. OSCILLATION:")
    print("   - The system oscillates between shortage and surplus")
    print("   - These oscillations get larger as you move upstream")
    
    print("\n4. COST IMPACT:")
    print("   - Total supply chain costs are much higher than necessary")
    print("   - Most costs come from alternating inventory and backlog")
    
    print("\n5. INFORMATION HIDING:")
    print("   - Only the retailer knows true customer demand")
    print("   - Each position only sees orders from their immediate customer")
    print("   - This lack of information sharing amplifies the problem")


if __name__ == "__main__":
    main()