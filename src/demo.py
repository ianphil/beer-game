"""Demo script to show the Beer Game role classes in action."""

from roles import Retailer, Wholesaler, Distributor, Factory


def main():
    """Run a simple demo of the Beer Game roles."""
    print("=" * 60)
    print("BEER GAME ROLE CLASSES DEMO")
    print("=" * 60)
    
    # Create a team
    team_name = "Blue Moon Brewery"
    
    # Create all four roles
    retailer = Retailer(team_name)
    wholesaler = Wholesaler(team_name)
    distributor = Distributor(team_name)
    factory = Factory(team_name)
    
    print(f"\nTeam '{team_name}' created with all 4 positions")
    print("\nInitial state (Week 0):")
    print("-" * 40)
    
    # Show initial state
    for role in [retailer, wholesaler, distributor, factory]:
        print(f"\n{role.position}:")
        print(f"  Inventory: {role.inventory} cases")
        print(f"  Backlog: {role.backlog} cases")
        print(f"  Shipping delay: {role.incoming_shipping_delay.get_slots()}")
        if role.position != "Factory":
            print(f"  Order delay: {role.outgoing_order_delay.get_slots()}")
        else:
            print(f"  Production delay: {role.production_delay.get_slots()}")
    
    print("\n" + "=" * 60)
    print("SIMULATING WEEK 1")
    print("=" * 60)
    
    # Simulate week 1 with equilibrium orders (4 cases)
    print("\nStep 1: All positions order 4 cases (equilibrium)")
    
    # Execute week 1 for retailer
    retailer.execute_week(order_decision=4)
    print(f"\nRetailer after week 1:")
    print(f"  Customer ordered: {retailer.current_customer_order} cases")
    print(f"  Inventory: {retailer.inventory} cases")
    print(f"  Cost this week: ${retailer.get_current_cost():.2f}")
    
    # For other positions, simulate receiving 4 cases from downstream
    wholesaler.execute_week(incoming_order=4, order_decision=4)
    distributor.execute_week(incoming_order=4, order_decision=4)
    factory.execute_week(incoming_order=4, production_decision=4)
    
    print("\n" + "=" * 60)
    print("WEEK 5 - DEMAND DOUBLES!")
    print("=" * 60)
    
    # Jump to week 5 to show the demand change
    for _ in range(4):  # Weeks 2-5
        retailer.execute_week(order_decision=8)  # Retailer reacts to higher demand
        wholesaler.execute_week(incoming_order=4, order_decision=4)
        distributor.execute_week(incoming_order=4, order_decision=4)
        factory.execute_week(incoming_order=4, production_decision=4)
    
    print(f"\nWeek 5 - Customer demand jumps to 8 cases!")
    print(f"\nRetailer status:")
    retailer.print_status()
    
    print("\n" + "=" * 60)
    print("RECORD SHEETS AFTER 5 WEEKS")
    print("=" * 60)
    
    # Show record sheets
    for role in [retailer, wholesaler, distributor, factory]:
        role.record_sheet.print_summary()
    
    print("\n" + "=" * 60)
    print("KEY INSIGHTS")
    print("=" * 60)
    print("\n1. Each role maintains inventory and tracks costs")
    print("2. Delays in shipping and ordering create the bullwhip effect")
    print("3. Only the retailer knows actual customer demand")
    print("4. Backlog costs twice as much as inventory ($1.00 vs $0.50)")
    print("5. The factory has production delays instead of ordering upstream")


if __name__ == "__main__":
    main()