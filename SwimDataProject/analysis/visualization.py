"""
Visualization module for swimming data.

This module provides functions for creating visualizations of swimming data.
"""
import os
import sys
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import io
import base64

# Add the parent directory to the path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from analysis.swimmer_analysis import calculate_progression, compare_with_standards


# Configure logging
logger = logging.getLogger(__name__)

# Set default style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_style("darkgrid")
sns.set_palette("deep")


def create_progression_chart(swimmer_id, event_id, db_session):
    """
    Create a progression chart for a swimmer in a specific event.
    
    Args:
        swimmer_id (int): Swimmer ID
        event_id (int): Event ID
        db_session: Database session
        
    Returns:
        str: Base64 encoded PNG image
    """
    try:
        # Get progression data
        progression_data = calculate_progression(swimmer_id, event_id, db_session)
        
        if not progression_data or not progression_data.get("has_data"):
            logger.warning(f"No progression data for swimmer {swimmer_id} in event {event_id}")
            # Create a simple error chart
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, "No data available", ha='center', va='center', fontsize=16)
            plt.axis('off')
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            return base64.b64encode(buf.getvalue()).decode('utf-8')
        
        # Create a DataFrame from times
        times = progression_data["times"]
        if not times:
            logger.warning(f"No times in progression data for swimmer {swimmer_id} in event {event_id}")
            # Create a simple error chart
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, "No times available", ha='center', va='center', fontsize=16)
            plt.axis('off')
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            return base64.b64encode(buf.getvalue()).decode('utf-8')
        
        df = pd.DataFrame(times)
        
        # Convert date strings to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Sort by date
        df = df.sort_values('date')
        
        # Create the plot
        plt.figure(figsize=(10, 6))
        
        # Plot time progression
        plt.plot(df['date'], df['time_seconds'], marker='o', linestyle='-', linewidth=2, markersize=8)
        
        # Add data points
        for i, row in df.iterrows():
            plt.annotate(
                row['time_formatted'],
                (row['date'], row['time_seconds']),
                textcoords="offset points",
                xytext=(0, 10),
                ha='center'
            )
        
        # Add trend line if there are at least 2 points
        if len(df) >= 2:
            z = np.polyfit(df.index, df['time_seconds'], 1)
            p = np.poly1d(z)
            plt.plot(df['date'], p(df.index), linestyle='--', color='r', alpha=0.6)
        
        # Set labels and title
        plt.title(f"{progression_data['swimmer_name']} - {progression_data['event_name']} Progression", fontsize=16)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Time (seconds)', fontsize=12)
        
        # Invert y-axis (lower times are better)
        plt.gca().invert_yaxis()
        
        # Format x-axis dates
        plt.gcf().autofmt_xdate()
        
        # Add grid
        plt.grid(True, alpha=0.3)
        
        # Add improvement annotation
        if progression_data["total_improvement"] > 0:
            improvement_text = (
                f"Total Improvement: {progression_data['total_improvement']} sec "
                f"({progression_data['total_improvement_percent']:.2f}%)\n"
                f"Yearly Improvement: {progression_data['avg_improvement_per_year']} sec/year"
            )
            plt.figtext(0.5, 0.01, improvement_text, ha='center', fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
        
        # Tight layout
        plt.tight_layout()
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        
        return base64.b64encode(buf.getvalue()).decode('utf-8')
    
    except Exception as e:
        logger.error(f"Error creating progression chart: {str(e)}")
        
        # Create an error chart
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, f"Error creating chart: {str(e)}", ha='center', va='center', fontsize=12)
        plt.axis('off')
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode('utf-8')


def create_standards_comparison_chart(swimmer_id, event_id, db_session):
    """
    Create a chart comparing swimmer's time with standards.
    
    Args:
        swimmer_id (int): Swimmer ID
        event_id (int): Event ID
        db_session: Database session
        
    Returns:
        str: Base64 encoded PNG image
    """
    try:
        # Get standards comparison data
        comparison_data = compare_with_standards(swimmer_id, event_id, db_session)
        
        if not comparison_data or not comparison_data.get("has_data"):
            logger.warning(f"No standards data for swimmer {swimmer_id} in event {event_id}")
            # Create a simple error chart
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, "No standards data available", ha='center', va='center', fontsize=16)
            plt.axis('off')
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            return base64.b64encode(buf.getvalue()).decode('utf-8')
        
        # Extract data
        standards = comparison_data["comparisons"]
        if not standards:
            logger.warning(f"No standards found for swimmer {swimmer_id} in event {event_id}")
            # Create a simple error chart
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, "No standards found", ha='center', va='center', fontsize=16)
            plt.axis('off')
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            return base64.b64encode(buf.getvalue()).decode('utf-8')
        
        # Create a DataFrame
        df = pd.DataFrame(standards)
        
        # Sort standards by time
        df = df.sort_values('standard_time_seconds')
        
        # Create the plot
        plt.figure(figsize=(12, 8))
        
        # Create barplot of standards
        bars = plt.barh(df['standard_name'], df['standard_time_seconds'], alpha=0.6)
        
        # Add swimmer's time as a vertical line
        plt.axvline(x=comparison_data["best_time_seconds"], color='r', linestyle='-', linewidth=2, label=f"Current Time: {comparison_data['best_time_formatted']}")
        
        # Add data labels
        for i, bar in enumerate(bars):
            plt.text(
                bar.get_width() + 0.1,
                bar.get_y() + bar.get_height()/2,
                df['standard_time_formatted'].iloc[i],
                va='center'
            )
        
        # Set labels and title
        plt.title(f"{comparison_data['swimmer_name']} - {comparison_data['event_name']} Standards Comparison", fontsize=16)
        plt.xlabel('Time (seconds)', fontsize=12)
        plt.ylabel('Standard', fontsize=12)
        
        # Add legend
        plt.legend()
        
        # Add annotation
        plt.figtext(
            0.5, 0.01,
            f"Swimmer: {comparison_data['swimmer_name']} | "
            f"Age: {comparison_data['age']} | "
            f"Best Time: {comparison_data['best_time_formatted']}",
            ha='center', fontsize=10, bbox=dict(facecolor='white', alpha=0.8)
        )
        
        # Tight layout
        plt.tight_layout()
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        
        return base64.b64encode(buf.getvalue()).decode('utf-8')
    
    except Exception as e:
        logger.error(f"Error creating standards comparison chart: {str(e)}")
        
        # Create an error chart
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, f"Error creating chart: {str(e)}", ha='center', va='center', fontsize=12)
        plt.axis('off')
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode('utf-8')


def create_percentile_chart(swimmer_id, event_id, db_session):
    """
    Create a chart showing swimmer's performance percentile.
    
    Args:
        swimmer_id (int): Swimmer ID
        event_id (int): Event ID
        db_session: Database session
        
    Returns:
        str: Base64 encoded PNG image
    """
    try:
        from analysis.swimmer_analysis import calculate_rankings, get_peer_statistics
        
        # Get rankings data
        rankings_data = calculate_rankings(swimmer_id, event_id, db_session)
        
        if not rankings_data or not rankings_data.get("has_data"):
            logger.warning(f"No rankings data for swimmer {swimmer_id} in event {event_id}")
            # Create a simple error chart
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, "No rankings data available", ha='center', va='center', fontsize=16)
            plt.axis('off')
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            return base64.b64encode(buf.getvalue()).decode('utf-8')
        
        # Extract data
        rankings = rankings_data.get("rankings", [])
        if not rankings:
            logger.warning(f"No rankings found for swimmer {swimmer_id} in event {event_id}")
            # Create a simple error chart
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, "No rankings found", ha='center', va='center', fontsize=16)
            plt.axis('off')
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            return base64.b64encode(buf.getvalue()).decode('utf-8')
        
        # Create a DataFrame
        df = pd.DataFrame(rankings)
        
        # Create the plot
        plt.figure(figsize=(10, 6))
        
        # Create bar plot of percentiles
        bars = plt.bar(df['scope'] + ' (' + df['scope_value'] + ')', df['percentile'], alpha=0.7)
        
        # Add data labels
        for i, bar in enumerate(bars):
            plt.text(
                bar.get_x() + bar.get_width()/2,
                bar.get_height() + 1,
                f"{df['percentile'].iloc[i]}%\nRank: {df['rank'].iloc[i]}/{df['total'].iloc[i]}",
                ha='center', va='bottom'
            )
        
        # Set labels and title
        plt.title(f"{rankings_data['swimmer_name']} - {rankings_data['event_name']} Percentile Rankings", fontsize=16)
        plt.xlabel('Ranking Scope', fontsize=12)
        plt.ylabel('Percentile', fontsize=12)
        
        # Set y-axis limit
        plt.ylim(0, 105)  # Slightly more than 100% to allow space for labels
        
        # Add horizontal lines at important percentiles
        plt.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='50th percentile')
        plt.axhline(y=90, color='green', linestyle='--', alpha=0.5, label='90th percentile')
        plt.axhline(y=95, color='blue', linestyle='--', alpha=0.5, label='95th percentile')
        plt.axhline(y=99, color='purple', linestyle='--', alpha=0.5, label='99th percentile')
        
        # Add legend
        plt.legend()
        
        # Add annotation
        plt.figtext(
            0.5, 0.01,
            f"Swimmer: {rankings_data['swimmer_name']} | "
            f"Age: {rankings_data['age']} | "
            f"Best Time: {rankings_data['best_time_formatted']}",
            ha='center', fontsize=10, bbox=dict(facecolor='white', alpha=0.8)
        )
        
        # Rotate x-axis labels if there are several
        if len(df) > 2:
            plt.xticks(rotation=45, ha='right')
        
        # Tight layout
        plt.tight_layout()
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        
        return base64.b64encode(buf.getvalue()).decode('utf-8')
    
    except Exception as e:
        logger.error(f"Error creating percentile chart: {str(e)}")
        
        # Create an error chart
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, f"Error creating chart: {str(e)}", ha='center', va='center', fontsize=12)
        plt.axis('off')
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode('utf-8')


def create_peer_distribution_chart(event_id, gender, age_min, age_max, state=None, swimmer_time=None, db_session=None):
    """
    Create a chart showing peer time distribution with swimmer's position.
    
    Args:
        event_id (int): Event ID
        gender (str): Gender ('M' or 'F')
        age_min (int): Minimum age for peer group
        age_max (int): Maximum age for peer group
        state (str, optional): State code to filter by (e.g., 'CA')
        swimmer_time (float, optional): Swimmer's time to highlight in the distribution
        db_session: Database session
        
    Returns:
        str: Base64 encoded PNG image
    """
    try:
        from analysis.swimmer_analysis import get_peer_statistics
        
        # Get peer statistics
        stats_data = get_peer_statistics(event_id, gender, age_min, age_max, state, db_session)
        
        if not stats_data or not stats_data.get("has_data"):
            logger.warning(f"No peer statistics for event {event_id}, gender {gender}, ages {age_min}-{age_max}")
            # Create a simple error chart
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, "No peer statistics available", ha='center', va='center', fontsize=16)
            plt.axis('off')
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            return base64.b64encode(buf.getvalue()).decode('utf-8')
        
        # Extract data
        stats = stats_data.get("statistics", {})
        
        # Get event details
        event_name = stats_data.get("event_name", "Unknown Event")
        
        # Create the plot
        plt.figure(figsize=(12, 8))
        
        # Query all times for this peer group
        from database.models import SwimTime, Swimmer
        query = db_session.query(SwimTime.time_seconds).join(Swimmer).filter(
            SwimTime.event_id == event_id,
            Swimmer.gender == gender,
            SwimTime.swimmer_age >= age_min,
            SwimTime.swimmer_age <= age_max
        )
        
        if state:
            query = query.filter(Swimmer.state == state)
        
        times = [t[0] for t in query.all()]
        
        if not times:
            logger.warning(f"No times found for event {event_id}, gender {gender}, ages {age_min}-{age_max}")
            # Create a simple error chart
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, "No times found for this peer group", ha='center', va='center', fontsize=16)
            plt.axis('off')
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            return base64.b64encode(buf.getvalue()).decode('utf-8')
        
        # Create histogram of times
        sns.histplot(times, bins=30, kde=True, alpha=0.6)
        
        # Add percentile lines
        percentiles = [
            (stats.get("percentile_10", None), "10th", "gray"),
            (stats.get("percentile_25", None), "25th", "lightblue"),
            (stats.get("median", None), "50th (Median)", "green"),
            (stats.get("percentile_75", None), "75th", "orange"),
            (stats.get("percentile_90", None), "90th", "red"),
            (stats.get("percentile_95", None), "95th", "purple"),
            (stats.get("percentile_99", None), "99th", "darkred")
        ]
        
        for value, label, color in percentiles:
            if value is not None:
                plt.axvline(x=value, color=color, linestyle='--', alpha=0.7, label=f"{label} Percentile")
        
        # Add swimmer's time if provided
        if swimmer_time is not None:
            plt.axvline(x=swimmer_time, color='blue', linestyle='-', linewidth=2, label="Your Time")
        
        # Set labels and title
        scope_text = f" in {state}" if state else ""
        plt.title(f"{event_name} - {gender} {age_min}-{age_max} Distribution{scope_text}", fontsize=16)
        plt.xlabel('Time (seconds)', fontsize=12)
        plt.ylabel('Number of Swimmers', fontsize=12)
        
        # Add legend
        plt.legend()
        
        # Add statistics annotation
        stats_text = (
            f"Sample Size: {stats.get('count', 'N/A')} | "
            f"Mean: {stats.get('mean', 'N/A'):.2f} sec | "
            f"Median: {stats.get('median', 'N/A'):.2f} sec | "
            f"Std Dev: {stats.get('std', 'N/A'):.2f} sec"
        )
        plt.figtext(0.5, 0.01, stats_text, ha='center', fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
        
        # Tight layout
        plt.tight_layout()
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        
        return base64.b64encode(buf.getvalue()).decode('utf-8')
    
    except Exception as e:
        logger.error(f"Error creating peer distribution chart: {str(e)}")
        
        # Create an error chart
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, f"Error creating chart: {str(e)}", ha='center', va='center', fontsize=12)
        plt.axis('off')
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode('utf-8')


def create_elite_comparison_chart(swimmer_id, event_id, db_session):
    """
    Create a chart comparing swimmer with elite/Olympic times.
    
    Args:
        swimmer_id (int): Swimmer ID
        event_id (int): Event ID
        db_session: Database session
        
    Returns:
        str: Base64 encoded PNG image
    """
    try:
        from analysis.swimmer_analysis import compare_with_elite
        
        # Get elite comparison data
        comparison_data = compare_with_elite(swimmer_id, event_id, db_session)
        
        if not comparison_data or not comparison_data.get("has_data"):
            logger.warning(f"No elite comparison data for swimmer {swimmer_id} in event {event_id}")
            # Create a simple error chart
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, "No elite comparison data available", ha='center', va='center', fontsize=16)
            plt.axis('off')
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            return base64.b64encode(buf.getvalue()).decode('utf-8')
        
        # Extract data
        comparisons = comparison_data.get("comparisons", [])
        if not comparisons:
            logger.warning(f"No elite benchmarks found for swimmer {swimmer_id} in event {event_id}")
            # Create a simple error chart
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, "No elite benchmarks found", ha='center', va='center', fontsize=16)
            plt.axis('off')
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            return base64.b64encode(buf.getvalue()).decode('utf-8')
        
        # Create a DataFrame
        df = pd.DataFrame(comparisons)
        
        # Sort by time
        df = df.sort_values('benchmark_time_seconds')
        
        # Create the plot
        plt.figure(figsize=(12, 8))
        
        # Create horizontal bar chart
        bars = plt.barh(df['benchmark_name'], df['benchmark_time_seconds'], alpha=0.6)
        
        # Add data labels
        for i, bar in enumerate(bars):
            plt.text(
                bar.get_width() + 0.1,
                bar.get_y() + bar.get_height()/2,
                df['benchmark_time_formatted'].iloc[i],
                va='center'
            )
            
            # Add holder name if available
            if 'holder_name' in df.columns and not pd.isna(df['holder_name'].iloc[i]):
                plt.text(
                    bar.get_width() - 0.5,
                    bar.get_y() + bar.get_height()/2,
                    df['holder_name'].iloc[i],
                    va='center', ha='right',
                    color='white', fontweight='bold'
                )
        
        # Add swimmer's time as a vertical line
        plt.axvline(x=comparison_data["best_time_seconds"], color='r', linestyle='-', linewidth=2, label=f"Current Time: {comparison_data['best_time_formatted']}")
        
        # Set labels and title
        plt.title(f"{comparison_data['swimmer_name']} - {comparison_data['event_name']} Elite Comparison", fontsize=16)
        plt.xlabel('Time (seconds)', fontsize=12)
        plt.ylabel('Benchmark', fontsize=12)
        
        # Add legend
        plt.legend()
        
        # Add pathway metrics if available
        pathway_metrics = comparison_data.get("pathway_metrics", {})
        if pathway_metrics:
            metrics_text = []
            
            if 'years_to_trials_cut' in pathway_metrics:
                metrics_text.append(f"Estimated Years to Olympic Trials Cut: {pathway_metrics['years_to_trials_cut']}")
                
            if 'percent_improvement_needed' in pathway_metrics:
                metrics_text.append(f"Improvement Needed: {pathway_metrics['percent_improvement_needed']}%")
                
            if metrics_text:
                plt.figtext(0.5, 0.01, " | ".join(metrics_text), ha='center', fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
        
        # Tight layout
        plt.tight_layout()
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        
        return base64.b64encode(buf.getvalue()).decode('utf-8')
    
    except Exception as e:
        logger.error(f"Error creating elite comparison chart: {str(e)}")
        
        # Create an error chart
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, f"Error creating chart: {str(e)}", ha='center', va='center', fontsize=12)
        plt.axis('off')
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode('utf-8')
