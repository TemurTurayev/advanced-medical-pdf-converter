import click
import time
from pathlib import Path
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskID
from src.tread.monitoring import TREADMonitor

console = Console()

def create_stats_table(stats: dict) -> Table:
    """Create rich table with current statistics"""
    table = Table(show_header=True, header_style="bold magenta")
    
    table.add_column("Metric", style="blue")
    table.add_column("Value", justify="right")
    
    if not stats:
        table.add_row("No data available", "--")
        return table
        
    table.add_row(
        "Pages Processed",
        str(stats['pages_processed'])
    )
    table.add_row(
        "Memory Usage",
        f"{stats['memory_usage_mb']:.2f}MB"
    )
    table.add_row(
        "CPU Usage",
        f"{stats['cpu_usage_percent']:.1f}%"
    )
    table.add_row(
        "Processing Speed",
        f"{stats['pages_per_second']:.2f} pages/s"
    )
    table.add_row(
        "OCR Accuracy",
        f"{stats['ocr_accuracy']:.2%}"
    )
    
    return table

def create_warning_panel(stats: dict) -> Panel:
    """Create panel with performance warnings"""
    warnings = []
    
    if stats.get('memory_usage_mb', 0) > 1000:
        warnings.append("⚠️ High memory usage")
    if stats.get('pages_per_second', 0) < 0.5:
        warnings.append("⚠️ Slow processing speed")
    if stats.get('ocr_accuracy', 1) < 0.9:
        warnings.append("⚠️ Low OCR accuracy")
        
    if not warnings:
        warnings = ["✅ All systems normal"]
        
    return Panel(
        "\n".join(warnings),
        title="Status",
        border_style="yellow"
    )

@click.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--refresh-rate', default=1.0, help='Stats refresh rate in seconds')
@click.option('--save-metrics/--no-save-metrics', default=True,
              help='Save metrics to file')
def monitor(file_path: str, refresh_rate: float, save_metrics: bool):
    """Monitor PDF processing performance."""
    monitor = TREADMonitor()
    monitor.start_file_processing(file_path)
    
    with Live(console=console, refresh_per_second=4) as live:
        try:
            while True:
                stats = monitor.get_current_stats()
                
                # Create display elements
                table = create_stats_table(stats)
                warnings = create_warning_panel(stats)
                
                # Update display
                live.update(
                    Panel(
                        Table(
                            table,
                            warnings,
                            show_header=False,
                            show_edge=False,
                            padding=1
                        ),
                        title="TREAD Performance Monitor",
                        border_style="blue"
                    )
                )
                
                time.sleep(refresh_rate)
                
        except KeyboardInterrupt:
            console.print("\n\nMonitoring stopped.")
            if save_metrics:
                monitor.save_metrics()
                console.print("Metrics saved to log directory.")

if __name__ == '__main__':
    monitor()