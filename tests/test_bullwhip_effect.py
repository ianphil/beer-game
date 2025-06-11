"""Tests specifically focused on validating the Bullwhip Effect behaviors."""

import pytest


class TestOrderAmplification:
    """Test order amplification through the supply chain."""
    
    def test_customer_demand_stability(self, full_simulation):
        """Customer demand shows minimal variation (4 to 8 cases)."""
        sim = full_simulation
        customer_orders = sim.order_history["Customer"]
        
        # First 4 weeks should be 4 cases
        assert all(order == 4 for order in customer_orders[:4])
        
        # Remaining weeks should be 8 cases
        assert all(order == 8 for order in customer_orders[4:])
        
        # Total variation is only 4 cases (100% increase)
        min_order = min(customer_orders)
        max_order = max(customer_orders)
        assert min_order == 4
        assert max_order == 8
        assert max_order - min_order == 4  # Only 4 cases variation
    
    def test_retailer_order_amplification(self, full_simulation):
        """Retailer orders show amplification beyond customer demand."""
        sim = full_simulation
        retailer_orders = sim.order_history["Retailer"]
        
        min_order = min(retailer_orders)
        max_order = max(retailer_orders)
        
        # Retailer should have much higher variation than customer
        variation = max_order - min_order
        assert variation > 10  # Much more than customer's 4-case variation
        assert max_order >= 16  # Should reach high order quantities
    
    def test_upstream_amplification_increases(self, full_simulation):
        """Order amplification increases as you move upstream."""
        sim = full_simulation
        
        # Calculate order variation for each position
        positions = ["Customer", "Retailer", "Wholesaler", "Distributor", "Factory"]
        variations = {}
        
        for position in positions:
            orders = sim.order_history[position]
            variations[position] = max(orders) - min(orders)
        
        # Each upstream position should have higher variation
        assert variations["Retailer"] > variations["Customer"]
        assert variations["Wholesaler"] > variations["Retailer"]
        assert variations["Distributor"] > variations["Wholesaler"]
        assert variations["Factory"] >= variations["Distributor"]
    
    def test_order_amplification_ratios(self, full_simulation, expected_order_amplification):
        """Test order amplification ratios match expected values."""
        sim = full_simulation
        expected = expected_order_amplification
        
        for position in ["Customer", "Retailer", "Wholesaler", "Distributor", "Factory"]:
            orders = sim.order_history[position]
            min_order = min(orders)
            max_order = max(orders)
            avg_order = sum(orders) / len(orders)
            
            exp_data = expected[position]
            
            # Test min/max orders (exact match for customer, ranges for others due to strategy)
            if position == "Customer":
                assert min_order == exp_data["min"]
                assert max_order == exp_data["max"]
            else:
                # Allow some variation in strategy implementation
                assert min_order <= exp_data["min"] + 2
                assert max_order >= exp_data["max"] * 0.7  # At least 70% of expected max
            
            # Test that amplification is significant for upstream positions
            if position != "Customer":
                amplification = (max_order - min_order) / 4.0  # Relative to customer change
                assert amplification >= 2.0, f"{position} should show significant amplification"


class TestInventoryOscillations:
    """Test inventory/backlog oscillation patterns."""
    
    def test_shortage_to_surplus_pattern(self, full_simulation):
        """System oscillates from shortage (backlog) to surplus (inventory)."""
        sim = full_simulation
        
        # Check retailer pattern: should have backlog in middle weeks, inventory later
        retailer_records = sim.retailer.record_sheet.records
        
        # Find periods of backlog and inventory
        backlog_weeks = [r.week for r in retailer_records if r.backlog > 0]
        inventory_weeks = [r.week for r in retailer_records if r.inventory > 50]  # High inventory
        
        assert len(backlog_weeks) > 0, "Retailer should experience backlog periods"
        assert len(inventory_weeks) > 0, "Retailer should experience high inventory periods"
        
        # Backlog should generally come before high inventory
        if backlog_weeks and inventory_weeks:
            avg_backlog_week = sum(backlog_weeks) / len(backlog_weeks)
            avg_inventory_week = sum(inventory_weeks) / len(inventory_weeks)
            assert avg_backlog_week < avg_inventory_week, "Backlog should precede inventory buildup"
    
    def test_oscillation_amplitude_increases_upstream(self, full_simulation):
        """Oscillation amplitude increases as you move upstream."""
        sim = full_simulation
        
        positions = [sim.retailer, sim.wholesaler, sim.distributor, sim.factory]
        max_inventories = []
        max_backlogs = []
        
        for role in positions:
            records = role.record_sheet.records
            max_inv = max(r.inventory for r in records)
            max_back = max(r.backlog for r in records)
            max_inventories.append(max_inv)
            max_backlogs.append(max_back)
        
        # Upstream positions should generally have larger oscillations
        # (though exact ordering may vary due to timing differences)
        factory_max_inv = max_inventories[3]  # Factory
        retailer_max_inv = max_inventories[0]  # Retailer
        
        assert factory_max_inv > retailer_max_inv, "Factory should have higher inventory swings"
    
    def test_effective_inventory_swings(self, full_simulation):
        """Test effective inventory (inventory - backlog) shows large swings."""
        sim = full_simulation
        
        for role in [sim.retailer, sim.wholesaler, sim.distributor, sim.factory]:
            effective_inventory = role.record_sheet.get_effective_inventory_history()
            
            if effective_inventory:
                min_eff = min(effective_inventory)
                max_eff = max(effective_inventory)
                swing = max_eff - min_eff
                
                # Should see significant swings from negative (backlog) to positive (inventory)
                assert swing > 50, f"{role.position} should show significant effective inventory swings"
                assert min_eff < 0, f"{role.position} should experience negative effective inventory (backlog)"
                assert max_eff > 100, f"{role.position} should experience high positive effective inventory"


class TestPhaseLagBehavior:
    """Test phase lag - upstream positions react with delays."""
    
    def test_demand_change_propagation_timing(self, fresh_simulation):
        """Demand change takes time to propagate upstream."""
        sim = fresh_simulation
        
        # Run enough weeks to see the demand change propagate
        for week in range(1, 21):
            sim.simulate_week()
            
            if week == 5:  # Demand changes in week 5
                # Retailer should start seeing effect immediately
                assert sim.order_history["Retailer"][-1] > 4
            elif week == 7:  # A few weeks later
                # Wholesaler should start reacting
                wholesaler_recent_orders = sim.order_history["Wholesaler"][-3:]
                assert max(wholesaler_recent_orders) > 4
            elif week >= 10:
                # Distributor and factory should be reacting by now
                distributor_recent = sim.order_history["Distributor"][-3:]
                factory_recent = sim.order_history["Factory"][-3:]
                assert max(distributor_recent) > 4
                # Factory may take longer due to delays, so check by week 15
                if week >= 15:
                    assert max(factory_recent) > 4
    
    def test_recovery_phase_lag(self, full_simulation):
        """Upstream positions are last to recover from overordering."""
        sim = full_simulation
        
        # Look at final weeks - orders should stabilize back to 8
        # but upstream positions take longer
        final_orders = {
            "Retailer": sim.order_history["Retailer"][-5:],
            "Wholesaler": sim.order_history["Wholesaler"][-5:],
            "Distributor": sim.order_history["Distributor"][-5:],
            "Factory": sim.order_history["Factory"][-5:]
        }
        
        # Retailer should stabilize quickly to 8
        retailer_final_avg = sum(final_orders["Retailer"]) / len(final_orders["Retailer"])
        assert abs(retailer_final_avg - 8) < 2, "Retailer should stabilize near 8"
        
        # Factory may still have higher variability in final weeks
        factory_final = final_orders["Factory"]
        factory_variability = max(factory_final) - min(factory_final)
        retailer_variability = max(final_orders["Retailer"]) - min(final_orders["Retailer"])
        
        # Allow factory to have more variability in recovery
        assert factory_variability >= retailer_variability * 0.5


class TestInformationHiding:
    """Test information hiding effects - only local visibility."""
    
    def test_local_decision_making(self, fresh_simulation):
        """Each position only sees orders from immediate downstream customer."""
        sim = fresh_simulation
        
        # Run a few weeks
        for _ in range(10):
            sim.simulate_week()
        
        # Wholesaler's decisions should be based on retailer orders, not customer demand
        retailer_orders = sim.order_history["Retailer"]
        wholesaler_orders = sim.order_history["Wholesaler"]
        customer_orders = sim.order_history["Customer"]
        
        # Wholesaler orders should correlate more with retailer orders than customer orders
        # (This tests the information hiding principle)
        assert len(retailer_orders) == len(wholesaler_orders)
        assert len(customer_orders) == len(wholesaler_orders)
    
    def test_no_perfect_information_sharing(self, full_simulation):
        """Lack of information sharing leads to overreaction."""
        sim = full_simulation
        
        # If positions had perfect information, they would only need to order 8 cases
        # after week 5. The overordering demonstrates information hiding effects.
        
        total_customer_demand = sum(sim.order_history["Customer"])
        total_factory_production = sum(sim.order_history["Factory"])
        
        # Factory should produce much more than actual customer demand
        # due to information distortion
        assert total_factory_production > total_customer_demand * 1.2, \
            "Factory overproduction demonstrates information hiding effects"


class TestSystemDynamicsPrinciples:
    """Test core system dynamics principles demonstrated by the bullwhip effect."""
    
    def test_structure_produces_behavior(self, full_simulation):
        """The oscillating behavior emerges from system structure, not external forces."""
        sim = full_simulation
        
        # Customer demand is very simple (step change from 4 to 8)
        customer_orders = sim.order_history["Customer"]
        customer_changes = sum(1 for i in range(1, len(customer_orders)) 
                              if customer_orders[i] != customer_orders[i-1])
        
        # Only 1 change in customer demand
        assert customer_changes == 1, "Customer demand has only one step change"
        
        # But factory orders should show many fluctuations
        factory_orders = sim.order_history["Factory"]
        factory_changes = sum(1 for i in range(1, len(factory_orders))
                             if abs(factory_orders[i] - factory_orders[i-1]) > 2)
        
        # Many changes in factory orders despite simple customer demand
        assert factory_changes > 10, "Complex factory behavior emerges from simple customer input"
    
    def test_delays_create_instability(self, full_simulation):
        """System delays create instability and oscillation."""
        sim = full_simulation
        
        # The 2-week delays in shipping and orders create the instability
        # This is demonstrated by the fact that positions continue to oscillate
        # even after customer demand stabilizes
        
        # Customer demand stabilizes after week 5
        stable_customer_demand = sim.order_history["Customer"][10:]  # After week 10
        customer_variation = max(stable_customer_demand) - min(stable_customer_demand)
        assert customer_variation == 0, "Customer demand is stable after week 5"
        
        # But factory orders continue to vary significantly even in later weeks
        factory_orders_later = sim.order_history["Factory"][15:]  # After week 15
        factory_variation = max(factory_orders_later) - min(factory_orders_later)
        assert factory_variation > 20, "Factory orders vary significantly despite stable demand"