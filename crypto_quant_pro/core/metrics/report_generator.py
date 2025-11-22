"""
Report generator for trading performance and risk analysis.

Generates comprehensive reports with performance metrics,
risk analysis, and visualizations.
"""

from decimal import Decimal
import logging
from pathlib import Path
from typing import Any, Optional

from .performance_calculator import PerformanceCalculator, PerformanceMetrics
from .risk_metrics import PortfolioRiskMetrics, RiskMetricsCalculator

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generate comprehensive trading performance reports.

    Creates detailed reports with performance metrics,
    risk analysis, and trade statistics.
    """

    def __init__(
        self,
        risk_free_rate: Decimal = Decimal("0.02"),
        output_format: str = "text",
    ):
        """
        Initialize report generator.

        Args:
            risk_free_rate: Annual risk-free rate
            output_format: Output format ('text', 'html', 'json')
        """
        self.risk_free_rate = risk_free_rate
        self.output_format = output_format
        self.performance_calculator = PerformanceCalculator(risk_free_rate)
        self.risk_calculator = RiskMetricsCalculator()

    def generate_performance_report(
        self,
        equity_curve: list[Decimal],
        trades: Optional[list[dict[str, Any]]] = None,
        timestamps: Optional[list] = None,
        title: str = "Performance Report",
    ) -> str:
        """
        Generate performance report.

        Args:
            equity_curve: List of portfolio values
            trades: Optional list of trades
            timestamps: Optional list of timestamps
            title: Report title

        Returns:
            Formatted report string
        """
        metrics = self.performance_calculator.calculate(equity_curve, trades, timestamps)

        if self.output_format == "text":
            return self._format_text_report(metrics, title)
        elif self.output_format == "html":
            return self._format_html_report(metrics, title)
        elif self.output_format == "json":
            return self._format_json_report(metrics, title)
        else:
            raise ValueError(f"Unsupported format: {self.output_format}")

    def generate_risk_report(
        self,
        portfolio_returns: Any,
        market_returns: Optional[Any] = None,
        positions: Optional[dict[str, Any]] = None,
        title: str = "Risk Report",
    ) -> str:
        """
        Generate risk analysis report.

        Args:
            portfolio_returns: Series of portfolio returns
            market_returns: Optional market benchmark returns
            positions: Optional dictionary of positions
            title: Report title

        Returns:
            Formatted report string
        """
        import pandas as pd

        if not isinstance(portfolio_returns, pd.Series):
            portfolio_returns = pd.Series(portfolio_returns)

        risk_metrics = self.risk_calculator.calculate_portfolio_risk(
            portfolio_returns, market_returns, positions
        )

        if self.output_format == "text":
            return self._format_risk_text_report(risk_metrics, title)
        elif self.output_format == "html":
            return self._format_risk_html_report(risk_metrics, title)
        elif self.output_format == "json":
            return self._format_risk_json_report(risk_metrics, title)
        else:
            raise ValueError(f"Unsupported format: {self.output_format}")

    def generate_comprehensive_report(
        self,
        equity_curve: list[Decimal],
        portfolio_returns: Any,
        trades: Optional[list[dict[str, Any]]] = None,
        timestamps: Optional[list] = None,
        market_returns: Optional[Any] = None,
        positions: Optional[dict[str, Any]] = None,
        title: str = "Comprehensive Trading Report",
    ) -> str:
        """
        Generate comprehensive report with performance and risk.

        Args:
            equity_curve: List of portfolio values
            portfolio_returns: Series of portfolio returns
            trades: Optional list of trades
            timestamps: Optional list of timestamps
            market_returns: Optional market benchmark returns
            positions: Optional dictionary of positions
            title: Report title

        Returns:
            Formatted comprehensive report
        """
        perf_metrics = self.performance_calculator.calculate(equity_curve, trades, timestamps)

        import pandas as pd

        if not isinstance(portfolio_returns, pd.Series):
            portfolio_returns = pd.Series(portfolio_returns)

        risk_metrics = self.risk_calculator.calculate_portfolio_risk(
            portfolio_returns, market_returns, positions
        )

        if self.output_format == "text":
            return self._format_comprehensive_text_report(perf_metrics, risk_metrics, title)
        elif self.output_format == "html":
            return self._format_comprehensive_html_report(perf_metrics, risk_metrics, title)
        else:
            return self.generate_performance_report(equity_curve, trades, timestamps, title)

    def save_report(self, report: str, filepath: Path, encoding: str = "utf-8") -> None:
        """
        Save report to file.

        Args:
            report: Report content
            filepath: Path to save file
            encoding: File encoding
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", encoding=encoding) as f:
            f.write(report)

        logger.info(f"Saved report to {filepath}")

    def _format_text_report(self, metrics: PerformanceMetrics, title: str) -> str:
        """Format performance report as text."""
        lines = [
            "=" * 60,
            title,
            "=" * 60,
            "",
            "RETURNS",
            "-" * 60,
            f"Total Return:        {metrics.total_return:.2%}",
            f"Annualized Return:   {metrics.annualized_return:.2%}",
            f"Volatility:          {metrics.volatility:.2%}",
            "",
            "RISK-ADJUSTED METRICS",
            "-" * 60,
            f"Sharpe Ratio:        {metrics.sharpe_ratio:.2f}",
            f"Sortino Ratio:       {metrics.sortino_ratio:.2f}",
            f"Calmar Ratio:        {metrics.calmar_ratio:.2f}",
            "",
            "DRAWDOWN",
            "-" * 60,
            f"Max Drawdown:        {metrics.max_drawdown:.2%}",
            f"Max DD Duration:     {metrics.max_drawdown_duration} days",
            "",
            "TRADE STATISTICS",
            "-" * 60,
            f"Total Trades:        {metrics.total_trades}",
            f"Winning Trades:      {metrics.winning_trades}",
            f"Losing Trades:       {metrics.losing_trades}",
            f"Win Rate:            {metrics.win_rate:.2%}",
            f"Profit Factor:       {metrics.profit_factor:.2f}",
            f"Average Win:         {metrics.average_win:.2f}",
            f"Average Loss:        {metrics.average_loss:.2f}",
            "",
            "=" * 60,
        ]

        return "\n".join(lines)

    def _format_html_report(self, metrics: PerformanceMetrics, title: str) -> str:
        """Format performance report as HTML."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <h2>Returns</h2>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Total Return</td><td>{metrics.total_return:.2%}</td></tr>
                <tr><td>Annualized Return</td><td>{metrics.annualized_return:.2%}</td></tr>
                <tr><td>Volatility</td><td>{metrics.volatility:.2%}</td></tr>
            </table>
            <h2>Risk-Adjusted Metrics</h2>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Sharpe Ratio</td><td>{metrics.sharpe_ratio:.2f}</td></tr>
                <tr><td>Sortino Ratio</td><td>{metrics.sortino_ratio:.2f}</td></tr>
                <tr><td>Calmar Ratio</td><td>{metrics.calmar_ratio:.2f}</td></tr>
            </table>
            <h2>Trade Statistics</h2>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Total Trades</td><td>{metrics.total_trades}</td></tr>
                <tr><td>Win Rate</td><td>{metrics.win_rate:.2%}</td></tr>
                <tr><td>Profit Factor</td><td>{metrics.profit_factor:.2f}</td></tr>
            </table>
        </body>
        </html>
        """
        return html

    def _format_json_report(self, metrics: PerformanceMetrics, title: str) -> str:
        """Format performance report as JSON."""
        import json

        data = {
            "title": title,
            "returns": {
                "total_return": float(metrics.total_return),
                "annualized_return": float(metrics.annualized_return),
                "volatility": float(metrics.volatility),
            },
            "risk_adjusted": {
                "sharpe_ratio": float(metrics.sharpe_ratio),
                "sortino_ratio": float(metrics.sortino_ratio),
                "calmar_ratio": float(metrics.calmar_ratio),
            },
            "drawdown": {
                "max_drawdown": float(metrics.max_drawdown),
                "max_drawdown_duration": metrics.max_drawdown_duration,
            },
            "trades": {
                "total_trades": metrics.total_trades,
                "winning_trades": metrics.winning_trades,
                "losing_trades": metrics.losing_trades,
                "win_rate": float(metrics.win_rate),
                "profit_factor": float(metrics.profit_factor),
            },
        }

        return json.dumps(data, indent=2)

    def _format_risk_text_report(self, metrics: PortfolioRiskMetrics, title: str) -> str:
        """Format risk report as text."""
        lines = [
            "=" * 60,
            title,
            "=" * 60,
            "",
            "VALUE AT RISK (VaR)",
            "-" * 60,
            f"VaR (95%):           {metrics.var_95:.2%}",
            f"VaR (99%):           {metrics.var_99:.2%}",
            "",
            "CONDITIONAL VaR (CVaR)",
            "-" * 60,
            f"CVaR (95%):          {metrics.cvar_95:.2%}",
            f"CVaR (99%):          {metrics.cvar_99:.2%}",
            "",
            "VOLATILITY & BETA",
            "-" * 60,
            f"Portfolio Volatility: {metrics.portfolio_volatility:.2%}",
            f"Beta:                 {metrics.beta:.2f}",
            "",
            "=" * 60,
        ]

        return "\n".join(lines)

    def _format_risk_html_report(self, metrics: PortfolioRiskMetrics, title: str) -> str:
        """Format risk report as HTML."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f44336; color: white; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <h2>Risk Metrics</h2>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>VaR (95%)</td><td>{metrics.var_95:.2%}</td></tr>
                <tr><td>VaR (99%)</td><td>{metrics.var_99:.2%}</td></tr>
                <tr><td>CVaR (95%)</td><td>{metrics.cvar_95:.2%}</td></tr>
                <tr><td>CVaR (99%)</td><td>{metrics.cvar_99:.2%}</td></tr>
                <tr><td>Portfolio Volatility</td><td>{metrics.portfolio_volatility:.2%}</td></tr>
                <tr><td>Beta</td><td>{metrics.beta:.2f}</td></tr>
            </table>
        </body>
        </html>
        """
        return html

    def _format_risk_json_report(self, metrics: PortfolioRiskMetrics, title: str) -> str:
        """Format risk report as JSON."""
        import json

        data = {
            "title": title,
            "var": {
                "var_95": float(metrics.var_95),
                "var_99": float(metrics.var_99),
            },
            "cvar": {
                "cvar_95": float(metrics.cvar_95),
                "cvar_99": float(metrics.cvar_99),
            },
            "volatility": float(metrics.portfolio_volatility),
            "beta": float(metrics.beta),
        }

        return json.dumps(data, indent=2)

    def _format_comprehensive_text_report(
        self,
        perf_metrics: PerformanceMetrics,
        risk_metrics: PortfolioRiskMetrics,
        title: str,
    ) -> str:
        """Format comprehensive report as text."""
        perf_section = self._format_text_report(perf_metrics, "Performance")
        risk_section = self._format_risk_text_report(risk_metrics, "Risk Analysis")

        return f"{perf_section}\n\n{risk_section}"

    def _format_comprehensive_html_report(
        self,
        perf_metrics: PerformanceMetrics,
        risk_metrics: PortfolioRiskMetrics,
        title: str,
    ) -> str:
        """Format comprehensive report as HTML."""
        perf_html = self._format_html_report(perf_metrics, "Performance")
        risk_html = self._format_risk_html_report(risk_metrics, "Risk Analysis")

        # Combine HTML reports
        combined = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            {perf_html}
            {risk_html}
        </body>
        </html>
        """
        return combined
