"""
HealthDashboardGenerator - HTML dashboard generator with Chart.js visualizations.

Generates an interactive HTML dashboard showing:
- Success rates by hotel
- Confidence distribution
- Execution times
- Error/warning summaries

Created as part of FASE-10-HEALTH-DASHBOARD.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from .health_metrics_collector import ExecutionMetrics


class HealthDashboardGenerator:
    """
    Generates HTML dashboards with Chart.js visualizations for health metrics.
    
    Usage:
        generator = HealthDashboardGenerator()
        
        # Generate HTML dashboard
        html = generator.generate_html(metrics_list)
        
        # Generate JSON summary
        summary = generator.generate_json_summary(metrics_list)
        
        # Save to file
        generator.save_dashboard(metrics_list, "output/health_dashboard.html")
    """
    
    def __init__(self):
        """Initialize the dashboard generator."""
        self._chart_colors = {
            "success": "#10b981",
            "warning": "#f59e0b", 
            "error": "#ef4444",
            "primary": "#3b82f6",
            "secondary": "#8b5cf6",
            "neutral": "#6b7280",
        }
    
    def generate_html(self, metrics: List[ExecutionMetrics]) -> str:
        """
        Generate an HTML dashboard with Chart.js visualizations.
        
        Args:
            metrics: List of ExecutionMetrics to visualize
            
        Returns:
            HTML string for the dashboard
        """
        if not metrics:
            return self._generate_empty_dashboard()
        
        summary = self.generate_json_summary(metrics)
        
        # Prepare chart data
        hotel_labels = json.dumps([m.hotel_name for m in metrics])
        success_rates = json.dumps([m.success_rate * 100 for m in metrics])
        confidences = json.dumps([m.avg_confidence * 100 for m in metrics])
        execution_times = json.dumps([m.execution_time for m in metrics])
        
        # Confidence distribution buckets
        conf_dist = self._calculate_confidence_distribution(metrics)
        conf_dist_labels = json.dumps(list(conf_dist.keys()))
        conf_dist_values = json.dumps(list(conf_dist.values()))
        
        # Error count per hotel
        error_counts = json.dumps([len(m.errors) for m in metrics])
        warning_counts = json.dumps([len(m.warnings) for m in metrics])
        
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IA Hoteles - System Health Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
            min-height: 100vh;
            color: #f1f5f9;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 2rem;
        }}
        
        header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }}
        
        header p {{
            color: #94a3b8;
            font-size: 1.1rem;
        }}
        
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .card {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 1rem;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
        }}
        
        .card-icon {{
            width: 48px;
            height: 48px;
            border-radius: 0.75rem;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }}
        
        .card-icon.blue {{ background: rgba(59, 130, 246, 0.2); }}
        .card-icon.green {{ background: rgba(16, 185, 129, 0.2); }}
        .card-icon.purple {{ background: rgba(139, 92, 246, 0.2); }}
        .card-icon.orange {{ background: rgba(245, 158, 11, 0.2); }}
        
        .card-value {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }}
        
        .card-label {{
            color: #94a3b8;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .chart-container {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 1rem;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
        }}
        
        .chart-title {{
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #f1f5f9;
        }}
        
        .chart-wrapper {{
            position: relative;
            height: 300px;
        }}
        
        .hotels-table {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 1rem;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
            margin-top: 2rem;
        }}
        
        .hotels-table h2 {{
            font-size: 1.25rem;
            margin-bottom: 1rem;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th, td {{
            text-align: left;
            padding: 0.75rem 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        th {{
            color: #94a3b8;
            font-weight: 600;
            font-size: 0.85rem;
            text-transform: uppercase;
        }}
        
        td {{
            font-size: 0.95rem;
        }}
        
        tr:last-child td {{
            border-bottom: none;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        
        .status-badge.success {{
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
        }}
        
        .status-badge.warning {{
            background: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
        }}
        
        .status-badge.error {{
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 2rem;
            color: #64748b;
            font-size: 0.85rem;
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 1rem;
            }}
            
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
            
            .summary-cards {{
                grid-template-columns: repeat(2, 1fr);
            }}
            
            .card-value {{
                font-size: 1.75rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>System Health Dashboard</h1>
            <p>IA Hoteles Agent - NEVER_BLOCK v4.6.0 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>
        
        <div class="summary-cards">
            <div class="card">
                <div class="card-icon blue">🏨</div>
                <div class="card-value">{summary['total_executions']}</div>
                <div class="card-label">Hotels Analyzed</div>
            </div>
            <div class="card">
                <div class="card-icon green">✓</div>
                <div class="card-value">{summary['overall_success_rate']:.1f}%</div>
                <div class="card-label">Success Rate</div>
            </div>
            <div class="card">
                <div class="card-icon purple">📊</div>
                <div class="card-value">{summary['avg_confidence']:.0f}%</div>
                <div class="card-label">Avg Confidence</div>
            </div>
            <div class="card">
                <div class="card-icon orange">⏱</div>
                <div class="card-value">{summary['avg_execution_time']:.1f}s</div>
                <div class="card-label">Avg Exec Time</div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-container">
                <h3 class="chart-title">Success Rate by Hotel</h3>
                <div class="chart-wrapper">
                    <canvas id="successChart"></canvas>
                </div>
            </div>
            <div class="chart-container">
                <h3 class="chart-title">Confidence Distribution</h3>
                <div class="chart-wrapper">
                    <canvas id="confidenceChart"></canvas>
                </div>
            </div>
            <div class="chart-container">
                <h3 class="chart-title">Execution Time (seconds)</h3>
                <div class="chart-wrapper">
                    <canvas id="timeChart"></canvas>
                </div>
            </div>
            <div class="chart-container">
                <h3 class="chart-title">Errors & Warnings</h3>
                <div class="chart-wrapper">
                    <canvas id="errorsChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="hotels-table">
            <h2>Hotel Execution Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Hotel</th>
                        <th>Assets Generated</th>
                        <th>Assets Failed</th>
                        <th>Success Rate</th>
                        <th>Avg Confidence</th>
                        <th>Exec Time</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {self._generate_table_rows(metrics)}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            Generated by IA Hoteles Agent | NEVER_BLOCK v4.6.0
        </div>
    </div>
    
    <script>
        // Chart.js configuration
        Chart.defaults.color = '#94a3b8';
        Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
        
        // Success Rate Chart
        new Chart(document.getElementById('successChart'), {{
            type: 'bar',
            data: {{
                labels: {hotel_labels},
                datasets: [{{
                    label: 'Success Rate (%)',
                    data: {success_rates},
                    backgroundColor: 'rgba(16, 185, 129, 0.7)',
                    borderColor: '#10b981',
                    borderWidth: 1,
                    borderRadius: 4,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{
                            callback: value => value + '%'
                        }}
                    }}
                }}
            }}
        }});
        
        // Confidence Distribution Chart (Doughnut)
        new Chart(document.getElementById('confidenceChart'), {{
            type: 'doughnut',
            data: {{
                labels: {conf_dist_labels},
                datasets: [{{
                    data: {conf_dist_values},
                    backgroundColor: [
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(59, 130, 246, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(239, 68, 68, 0.8)'
                    ],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }},
                cutout: '60%'
            }}
        }});
        
        // Execution Time Chart
        new Chart(document.getElementById('timeChart'), {{
            type: 'bar',
            data: {{
                labels: {hotel_labels},
                datasets: [{{
                    label: 'Execution Time (s)',
                    data: {execution_times},
                    backgroundColor: 'rgba(139, 92, 246, 0.7)',
                    borderColor: '#8b5cf6',
                    borderWidth: 1,
                    borderRadius: 4,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            callback: value => value + 's'
                        }}
                    }}
                }}
            }}
        }});
        
        // Errors & Warnings Chart
        new Chart(document.getElementById('errorsChart'), {{
            type: 'bar',
            data: {{
                labels: {hotel_labels},
                datasets: [
                    {{
                        label: 'Errors',
                        data: {error_counts},
                        backgroundColor: 'rgba(239, 68, 68, 0.7)',
                        borderColor: '#ef4444',
                        borderWidth: 1,
                        borderRadius: 4,
                    }},
                    {{
                        label: 'Warnings',
                        data: {warning_counts},
                        backgroundColor: 'rgba(245, 158, 11, 0.7)',
                        borderColor: '#f59e0b',
                        borderWidth: 1,
                        borderRadius: 4,
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            stepSize: 1
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
        
        return html
    
    def _generate_table_rows(self, metrics: List[ExecutionMetrics]) -> str:
        """Generate HTML table rows for metrics."""
        rows = []
        for m in metrics:
            if m.success_rate >= 0.8:
                status_class = "success"
                status_text = "Healthy"
            elif m.success_rate >= 0.5:
                status_class = "warning"
                status_text = "Degraded"
            else:
                status_class = "error"
                status_text = "Critical"
            
            rows.append(f"""
                <tr>
                    <td>{m.hotel_name}</td>
                    <td>{m.assets_generated}</td>
                    <td>{m.assets_failed}</td>
                    <td>{m.success_rate * 100:.1f}%</td>
                    <td>{m.avg_confidence * 100:.1f}%</td>
                    <td>{m.execution_time:.2f}s</td>
                    <td><span class="status-badge {status_class}">{status_text}</span></td>
                </tr>
            """)
        return "".join(rows)
    
    def _generate_empty_dashboard(self) -> str:
        """Generate a dashboard showing no data available."""
        return """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IA Hoteles - System Health Dashboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #f1f5f9;
        }
        .container {
            text-align: center;
            padding: 2rem;
        }
        h1 {
            font-size: 2rem;
            margin-bottom: 1rem;
        }
        p {
            color: #94a3b8;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>No Data Available</h1>
        <p>Execute some hotel analyses to see health metrics here.</p>
    </div>
</body>
</html>"""
    
    def _calculate_confidence_distribution(self, metrics: List[ExecutionMetrics]) -> Dict[str, int]:
        """
        Calculate confidence score distribution buckets.
        
        Returns:
            Dictionary with bucket labels and counts
        """
        buckets = {
            "0.9+": 0,
            "0.7-0.9": 0,
            "0.5-0.7": 0,
            "<0.5": 0,
        }
        
        for m in metrics:
            conf = m.avg_confidence
            if conf >= 0.9:
                buckets["0.9+"] += 1
            elif conf >= 0.7:
                buckets["0.7-0.9"] += 1
            elif conf >= 0.5:
                buckets["0.5-0.7"] += 1
            else:
                buckets["<0.5"] += 1
        
        return buckets
    
    def generate_json_summary(self, metrics: List[ExecutionMetrics]) -> Dict[str, Any]:
        """
        Generate a JSON-serializable summary of metrics.
        
        Args:
            metrics: List of ExecutionMetrics to summarize
            
        Returns:
            Dictionary with summary statistics
        """
        if not metrics:
            return {
                "total_executions": 0,
                "total_assets_generated": 0,
                "total_assets_failed": 0,
                "overall_success_rate": 0.0,
                "avg_confidence": 0.0,
                "avg_execution_time": 0.0,
                "total_execution_time": 0.0,
                "unique_hotels": 0,
                "confidence_distribution": {"0.9+": 0, "0.7-0.9": 0, "0.5-0.7": 0, "<0.5": 0},
                "total_errors": 0,
                "total_warnings": 0,
            }
        
        total_gen = sum(m.assets_generated for m in metrics)
        total_fail = sum(m.assets_failed for m in metrics)
        total = total_gen + total_fail
        
        all_confs = [m.avg_confidence for m in metrics if m.avg_confidence > 0]
        all_times = [m.execution_time for m in metrics]
        total_errors = sum(len(m.errors) for m in metrics)
        total_warnings = sum(len(m.warnings) for m in metrics)
        
        return {
            "total_executions": len(metrics),
            "total_assets_generated": total_gen,
            "total_assets_failed": total_fail,
            "overall_success_rate": round((total_gen / total * 100) if total > 0 else 0.0, 1),
            "avg_confidence": round((sum(all_confs) / len(all_confs) * 100) if all_confs else 0.0, 1),
            "avg_execution_time": round(sum(all_times) / len(all_times) if all_times else 0.0, 2),
            "total_execution_time": round(sum(all_times), 2),
            "unique_hotels": len(set(m.hotel_id for m in metrics)),
            "confidence_distribution": self._calculate_confidence_distribution(metrics),
            "total_errors": total_errors,
            "total_warnings": total_warnings,
        }
    
    def save_dashboard(
        self,
        metrics: List[ExecutionMetrics],
        output_path: str,
        include_json: bool = True
    ) -> Dict[str, str]:
        """
        Save the dashboard to an HTML file and optionally a JSON summary.
        
        Args:
            metrics: List of ExecutionMetrics to visualize
            output_path: Path for the HTML dashboard
            include_json: Whether to also save a JSON summary file
            
        Returns:
            Dictionary with paths of saved files
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save HTML
        html = self.generate_html(metrics)
        output_path.write_text(html, encoding='utf-8')
        
        result = {"html": str(output_path)}
        
        # Optionally save JSON summary
        if include_json:
            json_path = output_path.parent / "health_dashboard_summary.json"
            summary = self.generate_json_summary(metrics)
            # Also include individual metrics
            summary["executions"] = [m.to_dict() for m in metrics]
            
            json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
            result["json"] = str(json_path)
        
        return result
