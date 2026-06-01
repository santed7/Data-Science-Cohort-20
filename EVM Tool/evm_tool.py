"""
Earned Value Management (EVM) Tool
A comprehensive tool for tracking project performance using EVM metrics
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Dict, Optional
from enum import Enum
import json


class TaskStatus(Enum):
    """Task status enumeration"""
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    ON_HOLD = "On Hold"


@dataclass
class Task:
    """Represents a project task with EVM data"""
    id: str
    name: str
    planned_value: float  # Budget at Completion (BAC) for this task
    planned_start: date
    planned_end: date
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None
    percent_complete: float = 0.0
    actual_cost: float = 0.0
    status: TaskStatus = TaskStatus.NOT_STARTED
    
    def __post_init__(self):
        """Validate task data"""
        if self.percent_complete < 0 or self.percent_complete > 100:
            raise ValueError("Percent complete must be between 0 and 100")
        if self.planned_value < 0:
            raise ValueError("Planned value must be non-negative")
        if self.actual_cost < 0:
            raise ValueError("Actual cost must be non-negative")
    
    @property
    def earned_value(self) -> float:
        """Calculate Earned Value (EV) for this task"""
        return self.planned_value * (self.percent_complete / 100.0)
    
    @property
    def is_completed(self) -> bool:
        """Check if task is completed"""
        return self.status == TaskStatus.COMPLETED or self.percent_complete == 100.0
    
    def update_progress(self, percent_complete: float, actual_cost: float):
        """Update task progress"""
        self.percent_complete = max(0, min(100, percent_complete))
        self.actual_cost = actual_cost
        
        if self.percent_complete == 100:
            self.status = TaskStatus.COMPLETED
            if not self.actual_end:
                self.actual_end = date.today()
        elif self.percent_complete > 0:
            self.status = TaskStatus.IN_PROGRESS
            if not self.actual_start:
                self.actual_start = date.today()


@dataclass
class EVMMetrics:
    """Container for EVM calculations and metrics"""
    planned_value: float  # PV
    earned_value: float   # EV
    actual_cost: float    # AC
    budget_at_completion: float  # BAC
    
    @property
    def cost_variance(self) -> float:
        """CV = EV - AC (positive is good)"""
        return self.earned_value - self.actual_cost
    
    @property
    def schedule_variance(self) -> float:
        """SV = EV - PV (positive is good)"""
        return self.earned_value - self.planned_value
    
    @property
    def cost_performance_index(self) -> float:
        """CPI = EV / AC (>1 is good)"""
        if self.actual_cost == 0:
            return 1.0
        return self.earned_value / self.actual_cost
    
    @property
    def schedule_performance_index(self) -> float:
        """SPI = EV / PV (>1 is good)"""
        if self.planned_value == 0:
            return 1.0
        return self.earned_value / self.planned_value
    
    @property
    def estimate_at_completion(self) -> float:
        """EAC = BAC / CPI (estimated total cost)"""
        cpi = self.cost_performance_index
        if cpi == 0:
            return float('inf')
        return self.budget_at_completion / cpi
    
    @property
    def estimate_to_complete(self) -> float:
        """ETC = EAC - AC (estimated remaining cost)"""
        return self.estimate_at_completion - self.actual_cost
    
    @property
    def variance_at_completion(self) -> float:
        """VAC = BAC - EAC (projected over/under budget)"""
        return self.budget_at_completion - self.estimate_at_completion
    
    @property
    def to_complete_performance_index(self) -> float:
        """TCPI = (BAC - EV) / (BAC - AC) (required future performance)"""
        remaining_budget = self.budget_at_completion - self.actual_cost
        if remaining_budget == 0:
            return 1.0
        remaining_work = self.budget_at_completion - self.earned_value
        return remaining_work / remaining_budget
    
    @property
    def percent_complete(self) -> float:
        """Percent complete based on earned value"""
        if self.budget_at_completion == 0:
            return 0.0
        return (self.earned_value / self.budget_at_completion) * 100
    
    @property
    def percent_spent(self) -> float:
        """Percent of budget spent"""
        if self.budget_at_completion == 0:
            return 0.0
        return (self.actual_cost / self.budget_at_completion) * 100
    
    def get_status_summary(self) -> Dict[str, str]:
        """Get human-readable status summary"""
        return {
            "cost_status": "Under Budget" if self.cost_variance > 0 else "Over Budget" if self.cost_variance < 0 else "On Budget",
            "schedule_status": "Ahead of Schedule" if self.schedule_variance > 0 else "Behind Schedule" if self.schedule_variance < 0 else "On Schedule",
            "cost_efficiency": "Good" if self.cost_performance_index >= 1 else "Poor",
            "schedule_efficiency": "Good" if self.schedule_performance_index >= 1 else "Poor"
        }


class Project:
    """Manages a project with multiple tasks and calculates EVM metrics"""
    
    def __init__(self, name: str, budget: float, start_date: date, end_date: date):
        self.name = name
        self.budget = budget
        self.start_date = start_date
        self.end_date = end_date
        self.tasks: List[Task] = []
        self.status_date = date.today()
    
    def add_task(self, task: Task):
        """Add a task to the project"""
        self.tasks.append(task)
    
    def remove_task(self, task_id: str):
        """Remove a task from the project"""
        self.tasks = [t for t in self.tasks if t.id != task_id]
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def calculate_planned_value(self, as_of_date: Optional[date] = None) -> float:
        """
        Calculate Planned Value (PV) - what should have been accomplished
        Based on planned schedule up to the status date
        """
        if as_of_date is None:
            as_of_date = self.status_date
        
        total_pv = 0.0
        for task in self.tasks:
            # Calculate what percentage of the task should be complete by now
            if as_of_date < task.planned_start:
                # Task hasn't started yet
                continue
            elif as_of_date >= task.planned_end:
                # Task should be complete
                total_pv += task.planned_value
            else:
                # Task is in progress - calculate proportional PV
                total_days = (task.planned_end - task.planned_start).days
                if total_days > 0:
                    days_elapsed = (as_of_date - task.planned_start).days
                    planned_percent = (days_elapsed / total_days) * 100
                    total_pv += task.planned_value * (planned_percent / 100)
        
        return total_pv
    
    def calculate_earned_value(self) -> float:
        """Calculate Earned Value (EV) - what has been accomplished"""
        return sum(task.earned_value for task in self.tasks)
    
    def calculate_actual_cost(self) -> float:
        """Calculate Actual Cost (AC) - what has been spent"""
        return sum(task.actual_cost for task in self.tasks)
    
    def get_metrics(self, as_of_date: Optional[date] = None) -> EVMMetrics:
        """Get current EVM metrics for the project"""
        if as_of_date:
            self.status_date = as_of_date
        
        pv = self.calculate_planned_value(self.status_date)
        ev = self.calculate_earned_value()
        ac = self.calculate_actual_cost()
        bac = sum(task.planned_value for task in self.tasks)
        
        return EVMMetrics(
            planned_value=pv,
            earned_value=ev,
            actual_cost=ac,
            budget_at_completion=bac
        )
    
    def get_task_summary(self) -> Dict:
        """Get summary of all tasks"""
        return {
            "total_tasks": len(self.tasks),
            "completed": sum(1 for t in self.tasks if t.is_completed),
            "in_progress": sum(1 for t in self.tasks if t.status == TaskStatus.IN_PROGRESS),
            "not_started": sum(1 for t in self.tasks if t.status == TaskStatus.NOT_STARTED),
            "on_hold": sum(1 for t in self.tasks if t.status == TaskStatus.ON_HOLD)
        }
    
    def generate_report(self, detailed: bool = True) -> str:
        """Generate a comprehensive EVM report"""
        metrics = self.get_metrics()
        task_summary = self.get_task_summary()
        status = metrics.get_status_summary()
        
        report = []
        report.append("=" * 70)
        report.append(f"EARNED VALUE MANAGEMENT REPORT")
        report.append("=" * 70)
        report.append(f"\nProject: {self.name}")
        report.append(f"Status Date: {self.status_date.strftime('%Y-%m-%d')}")
        report.append(f"Project Period: {self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}")
        
        report.append("\n" + "-" * 70)
        report.append("PROJECT SUMMARY")
        report.append("-" * 70)
        report.append(f"Total Tasks: {task_summary['total_tasks']}")
        report.append(f"  - Completed: {task_summary['completed']}")
        report.append(f"  - In Progress: {task_summary['in_progress']}")
        report.append(f"  - Not Started: {task_summary['not_started']}")
        report.append(f"  - On Hold: {task_summary['on_hold']}")
        
        report.append("\n" + "-" * 70)
        report.append("KEY METRICS")
        report.append("-" * 70)
        report.append(f"Budget at Completion (BAC):    ${metrics.budget_at_completion:,.2f}")
        report.append(f"Planned Value (PV):             ${metrics.planned_value:,.2f}")
        report.append(f"Earned Value (EV):              ${metrics.earned_value:,.2f}")
        report.append(f"Actual Cost (AC):               ${metrics.actual_cost:,.2f}")
        report.append(f"\nPercent Complete:               {metrics.percent_complete:.1f}%")
        report.append(f"Percent Spent:                  {metrics.percent_spent:.1f}%")
        
        report.append("\n" + "-" * 70)
        report.append("VARIANCE ANALYSIS")
        report.append("-" * 70)
        report.append(f"Cost Variance (CV):             ${metrics.cost_variance:,.2f} ({status['cost_status']})")
        report.append(f"Schedule Variance (SV):         ${metrics.schedule_variance:,.2f} ({status['schedule_status']})")
        
        report.append("\n" + "-" * 70)
        report.append("PERFORMANCE INDICES")
        report.append("-" * 70)
        report.append(f"Cost Performance Index (CPI):   {metrics.cost_performance_index:.3f} ({status['cost_efficiency']})")
        report.append(f"Schedule Performance Index (SPI): {metrics.schedule_performance_index:.3f} ({status['schedule_efficiency']})")
        report.append(f"To-Complete Perf. Index (TCPI): {metrics.to_complete_performance_index:.3f}")
        
        report.append("\n" + "-" * 70)
        report.append("FORECASTS")
        report.append("-" * 70)
        report.append(f"Estimate at Completion (EAC):   ${metrics.estimate_at_completion:,.2f}")
        report.append(f"Estimate to Complete (ETC):     ${metrics.estimate_to_complete:,.2f}")
        report.append(f"Variance at Completion (VAC):   ${metrics.variance_at_completion:,.2f}")
        
        if detailed and self.tasks:
            report.append("\n" + "-" * 70)
            report.append("TASK DETAILS")
            report.append("-" * 70)
            for task in self.tasks:
                report.append(f"\n{task.name} ({task.id})")
                report.append(f"  Status: {task.status.value}")
                report.append(f"  Progress: {task.percent_complete:.1f}%")
                report.append(f"  Planned Value: ${task.planned_value:,.2f}")
                report.append(f"  Earned Value: ${task.earned_value:,.2f}")
                report.append(f"  Actual Cost: ${task.actual_cost:,.2f}")
                if task.actual_cost > 0:
                    task_cv = task.earned_value - task.actual_cost
                    report.append(f"  Cost Variance: ${task_cv:,.2f}")
        
        report.append("\n" + "=" * 70)
        report.append("\nKEY INTERPRETATIONS:")
        report.append("  CPI > 1.0: Project is under budget")
        report.append("  SPI > 1.0: Project is ahead of schedule")
        report.append("  CV > 0: Under budget | CV < 0: Over budget")
        report.append("  SV > 0: Ahead of schedule | SV < 0: Behind schedule")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def export_to_dict(self) -> Dict:
        """Export project data to dictionary"""
        return {
            "name": self.name,
            "budget": self.budget,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "status_date": self.status_date.isoformat(),
            "tasks": [
                {
                    "id": task.id,
                    "name": task.name,
                    "planned_value": task.planned_value,
                    "planned_start": task.planned_start.isoformat(),
                    "planned_end": task.planned_end.isoformat(),
                    "actual_start": task.actual_start.isoformat() if task.actual_start else None,
                    "actual_end": task.actual_end.isoformat() if task.actual_end else None,
                    "percent_complete": task.percent_complete,
                    "actual_cost": task.actual_cost,
                    "status": task.status.value
                }
                for task in self.tasks
            ]
        }
    
    def save_to_file(self, filename: str):
        """Save project to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.export_to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filename: str) -> 'Project':
        """Load project from JSON file"""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        project = cls(
            name=data["name"],
            budget=data["budget"],
            start_date=date.fromisoformat(data["start_date"]),
            end_date=date.fromisoformat(data["end_date"])
        )
        project.status_date = date.fromisoformat(data["status_date"])
        
        for task_data in data["tasks"]:
            task = Task(
                id=task_data["id"],
                name=task_data["name"],
                planned_value=task_data["planned_value"],
                planned_start=date.fromisoformat(task_data["planned_start"]),
                planned_end=date.fromisoformat(task_data["planned_end"]),
                actual_start=date.fromisoformat(task_data["actual_start"]) if task_data["actual_start"] else None,
                actual_end=date.fromisoformat(task_data["actual_end"]) if task_data["actual_end"] else None,
                percent_complete=task_data["percent_complete"],
                actual_cost=task_data["actual_cost"],
                status=TaskStatus(task_data["status"])
            )
            project.add_task(task)
        
        return project


def main():
    """Example usage of the EVM tool"""
    # Create a sample project
    project = Project(
        name="Website Redesign Project",
        budget=100000,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 6, 30)
    )
    
    # Add tasks
    tasks_data = [
        ("T001", "Requirements Gathering", 10000, date(2026, 1, 1), date(2026, 1, 31), 100, 9500),
        ("T002", "Design Mockups", 15000, date(2026, 2, 1), date(2026, 2, 28), 100, 16000),
        ("T003", "Frontend Development", 30000, date(2026, 3, 1), date(2026, 4, 30), 60, 20000),
        ("T004", "Backend Development", 25000, date(2026, 3, 1), date(2026, 4, 30), 50, 15000),
        ("T005", "Testing & QA", 12000, date(2026, 5, 1), date(2026, 5, 31), 0, 0),
        ("T006", "Deployment", 8000, date(2026, 6, 1), date(2026, 6, 30), 0, 0),
    ]
    
    for task_id, name, pv, start, end, complete, cost in tasks_data:
        task = Task(
            id=task_id,
            name=name,
            planned_value=pv,
            planned_start=start,
            planned_end=end
        )
        task.update_progress(complete, cost)
        project.add_task(task)
    
    # Set status date to mid-project
    project.status_date = date(2026, 4, 1)
    
    # Generate and print report
    print(project.generate_report())
    
    # Save project to file
    project.save_to_file("/home/claude/project_data.json")
    print("\n\nProject data saved to project_data.json")
    
    # Example: Get metrics programmatically
    metrics = project.get_metrics()
    print(f"\n\nQuick Status Check:")
    print(f"Project is {metrics.percent_complete:.1f}% complete")
    print(f"CPI: {metrics.cost_performance_index:.3f} (Cost efficiency)")
    print(f"SPI: {metrics.schedule_performance_index:.3f} (Schedule efficiency)")


if __name__ == "__main__":
    main()
