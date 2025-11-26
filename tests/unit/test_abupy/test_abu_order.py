from abupy.TradeBu.ABuOrder import AbuOrder


class TestAbuOrder:
    def test_initialization(self):
        """Test AbuOrder initialization defaults"""
        order = AbuOrder()
        assert order.order_deal is False
        assert order.buy_symbol is None
        assert order.buy_price is None
        assert order.sell_type == "keep"
        assert order.keep_days == 0

    def test_str_representation(self):
        """Test string representation of AbuOrder"""
        order = AbuOrder()
        order.buy_symbol = "usAAPL"
        order.buy_price = 150.0
        order.buy_cnt = 100.0
        order.buy_date = 20230101

        str_repr = str(order)
        assert "buy Symbol = usAAPL" in str_repr
        assert "buy Prices = 150.0" in str_repr
