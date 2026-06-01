"""
Interactive Examples for EVM Tool
Demonstrates various project scenarios and use cases
"""

from evm_tool import Project, Task, TaskStatus
from datetime import date, timedelta


def example_software_project():
    """Example: Software Development Project"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Software Development Project")
    print("="*70)
    
    project = Project(
        name="Mobile App Development",
        budget=250000,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 8, 31)
    )
    
    # Sprint 1 - Completed
    project.add_task(Task(
        id="SPRINT-1",
        name="Sprint 1: User Authentication",
        planned_value=30000,
        planned_start=date(2026, 1, 1),
        planned_end=date(2026, 1, 14)
    ))
    project.get_task("SPRINT-1").update_progress(100, 28000)
    
    # Sprint 2 - Completed
    project.add_task(Task(
        id="SPRINT-2",
        name="Sprint 2: Profile Management",
        planned_value=35000,
        planned_start=date(2026, 1, 15),
        planned_end=date(2026, 1, 28)
    ))
    project.get_task("SPRINT-2").update_progress(100, 37000)
    
    # Sprint 3 - In Progress
    project.add_task(Task(
        id="SPRINT-3",
        name="Sprint 3: Core Features",
        planned_value=45000,
        planned_start=date(2026, 1, 29),
        planned_end=date(2026, 2, 11)
    ))
    project.get_task("SPRINT-3").update_progress(70, 35000)
    
    # Remaining sprints
    for i in range(4, 8):
        project.add_task(Task(
            id=f"SPRINT-{i}",
            name=f"Sprint {i}: Development",
            planned_value=35000,
            planned_start=date(2026, 2, 1) + timedelta(weeks=(i-4)*2),
            planned_end=date(2026, 2, 1) + timedelta(weeks=(i-4)*2 + 2)
        ))
    
    project.status_date = date(2026, 2, 8)
    print(project.generate_report(detailed=True))
    
    return project


def example_construction_project():
    """Example: Construction Project"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Construction Project")
    print("="*70)
    
    project = Project(
        name="Office Building Construction",
        budget=5000000,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31)
    )
    
    # Foundation - Completed, over budget
    foundation = Task(
        id="FOUNDATION",
        name="Foundation & Excavation",
        planned_value=500000,
        planned_start=date(2026, 1, 1),
        planned_end=date(2026, 2, 28)
    )
    foundation.update_progress(100, 550000)
    project.add_task(foundation)
    
    # Structural - In Progress, behind schedule
    structural = Task(
        id="STRUCTURAL",
        name="Structural Framework",
        planned_value=1200000,
        planned_start=date(2026, 3, 1),
        planned_end=date(2026, 5, 31)
    )
    structural.update_progress(45, 600000)
    project.add_task(structural)
    
    # MEP - Not started yet
    project.add_task(Task(
        id="MEP",
        name="Mechanical, Electrical, Plumbing",
        planned_value=1500000,
        planned_start=date(2026, 6, 1),
        planned_end=date(2026, 9, 30)
    ))
    
    # Interior - Not started
    project.add_task(Task(
        id="INTERIOR",
        name="Interior Finishes",
        planned_value=1000000,
        planned_start=date(2026, 10, 1),
        planned_end=date(2026, 11, 30)
    ))
    
    # Landscaping - Not started
    project.add_task(Task(
        id="LANDSCAPE",
        name="Landscaping & Exterior",
        planned_value=800000,
        planned_start=date(2026, 11, 15),
        planned_end=date(2026, 12, 31)
    ))
    
    project.status_date = date(2026, 4, 15)
    print(project.generate_report(detailed=True))
    
    return project


def example_marketing_campaign():
    """Example: Marketing Campaign"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Marketing Campaign")
    print("="*70)
    
    project = Project(
        name="Q1 Product Launch Campaign",
        budget=150000,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 3, 31)
    )
    
    # Research - Completed
    research = Task(
        id="RESEARCH",
        name="Market Research & Strategy",
        planned_value=15000,
        planned_start=date(2026, 1, 1),
        planned_end=date(2026, 1, 15)
    )
    research.update_progress(100, 14500)
    project.add_task(research)
    
    # Content Creation - Completed
    content = Task(
        id="CONTENT",
        name="Content Creation & Design",
        planned_value=35000,
        planned_start=date(2026, 1, 16),
        planned_end=date(2026, 2, 15)
    )
    content.update_progress(100, 38000)
    project.add_task(content)
    
    # Digital Ads - In Progress, ahead of schedule
    digital = Task(
        id="DIGITAL",
        name="Digital Advertising Campaign",
        planned_value=60000,
        planned_start=date(2026, 2, 1),
        planned_end=date(2026, 3, 15)
    )
    digital.update_progress(85, 48000)
    project.add_task(digital)
    
    # PR - In Progress
    pr = Task(
        id="PR",
        name="Public Relations & Events",
        planned_value=25000,
        planned_start=date(2026, 2, 15),
        planned_end=date(2026, 3, 31)
    )
    pr.update_progress(40, 12000)
    project.add_task(pr)
    
    # Analytics - Not Started
    project.add_task(Task(
        id="ANALYTICS",
        name="Campaign Analytics & Reporting",
        planned_value=15000,
        planned_start=date(2026, 3, 15),
        planned_end=date(2026, 3, 31)
    ))
    
    project.status_date = date(2026, 3, 1)
    print(project.generate_report(detailed=True))
    
    return project


def example_research_project():
    """Example: Research Project"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Research Project (Grant-Funded)")
    print("="*70)
    
    project = Project(
        name="Clinical Trial Phase II",
        budget=800000,
        start_date=date(2026, 1, 1),
        end_date=date(2027, 12, 31)
    )
    
    # IRB Approval - Completed
    irb = Task(
        id="IRB",
        name="IRB Approval & Documentation",
        planned_value=50000,
        planned_start=date(2026, 1, 1),
        planned_end=date(2026, 3, 31)
    )
    irb.update_progress(100, 48000)
    project.add_task(irb)
    
    # Patient Recruitment - In Progress
    recruitment = Task(
        id="RECRUIT",
        name="Patient Recruitment",
        planned_value=150000,
        planned_start=date(2026, 4, 1),
        planned_end=date(2026, 9, 30)
    )
    recruitment.update_progress(60, 95000)
    project.add_task(recruitment)
    
    # Data Collection - In Progress
    datacoll = Task(
        id="DATACOLL",
        name="Data Collection & Monitoring",
        planned_value=300000,
        planned_start=date(2026, 7, 1),
        planned_end=date(2027, 6, 30)
    )
    datacoll.update_progress(25, 80000)
    project.add_task(datacoll)
    
    # Analysis - Not Started
    project.add_task(Task(
        id="ANALYSIS",
        name="Statistical Analysis",
        planned_value=150000,
        planned_start=date(2027, 7, 1),
        planned_end=date(2027, 10, 31)
    ))
    
    # Publication - Not Started
    project.add_task(Task(
        id="PUBLISH",
        name="Results Publication",
        planned_value=150000,
        planned_start=date(2027, 11, 1),
        planned_end=date(2027, 12, 31)
    ))
    
    project.status_date = date(2026, 8, 1)
    print(project.generate_report(detailed=True))
    
    return project


def compare_scenarios():
    """Compare different project performance scenarios"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Comparing Project Performance Scenarios")
    print("="*70)
    
    # Scenario 1: Healthy Project
    healthy = Project("Healthy Project", 100000, date(2026, 1, 1), date(2026, 6, 30))
    task1 = Task("T1", "Phase 1", 50000, date(2026, 1, 1), date(2026, 3, 31))
    task1.update_progress(100, 48000)
    healthy.add_task(task1)
    
    task2 = Task("T2", "Phase 2", 50000, date(2026, 4, 1), date(2026, 6, 30))
    task2.update_progress(60, 28000)
    healthy.add_task(task2)
    healthy.status_date = date(2026, 5, 1)
    
    # Scenario 2: Over Budget
    overbudget = Project("Over Budget Project", 100000, date(2026, 1, 1), date(2026, 6, 30))
    task3 = Task("T1", "Phase 1", 50000, date(2026, 1, 1), date(2026, 3, 31))
    task3.update_progress(100, 65000)
    overbudget.add_task(task3)
    
    task4 = Task("T2", "Phase 2", 50000, date(2026, 4, 1), date(2026, 6, 30))
    task4.update_progress(60, 38000)
    overbudget.add_task(task4)
    overbudget.status_date = date(2026, 5, 1)
    
    # Scenario 3: Behind Schedule
    behind = Project("Behind Schedule Project", 100000, date(2026, 1, 1), date(2026, 6, 30))
    task5 = Task("T1", "Phase 1", 50000, date(2026, 1, 1), date(2026, 3, 31))
    task5.update_progress(100, 50000)
    behind.add_task(task5)
    
    task6 = Task("T2", "Phase 2", 50000, date(2026, 4, 1), date(2026, 6, 30))
    task6.update_progress(30, 15000)  # Should be 60% complete by now
    behind.add_task(task6)
    behind.status_date = date(2026, 5, 1)
    
    # Compare metrics
    projects = [
        ("Healthy Project", healthy),
        ("Over Budget Project", overbudget),
        ("Behind Schedule Project", behind)
    ]
    
    print("\nCOMPARATIVE ANALYSIS\n")
    print(f"{'Metric':<30} {'Healthy':<15} {'Over Budget':<15} {'Behind Sched':<15}")
    print("-" * 75)
    
    for name, proj in projects:
        metrics = proj.get_metrics()
    
    metrics_list = [proj.get_metrics() for _, proj in projects]
    
    comparisons = [
        ("CPI (Cost Efficiency)", lambda m: f"{m.cost_performance_index:.3f}"),
        ("SPI (Schedule Efficiency)", lambda m: f"{m.schedule_performance_index:.3f}"),
        ("Cost Variance", lambda m: f"${m.cost_variance:,.0f}"),
        ("Schedule Variance", lambda m: f"${m.schedule_variance:,.0f}"),
        ("% Complete", lambda m: f"{m.percent_complete:.1f}%"),
        ("% Spent", lambda m: f"{m.percent_spent:.1f}%"),
        ("Est. at Completion", lambda m: f"${m.estimate_at_completion:,.0f}"),
        ("Variance at Completion", lambda m: f"${m.variance_at_completion:,.0f}"),
    ]
    
    for metric_name, formatter in comparisons:
        values = [formatter(m) for m in metrics_list]
        print(f"{metric_name:<30} {values[0]:<15} {values[1]:<15} {values[2]:<15}")
    
    print("\n" + "="*70)
    print("KEY INSIGHTS:")
    print("="*70)
    print("\nHealthy Project:")
    print("  - CPI > 1.0: Under budget ✓")
    print("  - SPI ≈ 1.0: On schedule ✓")
    print("  - Positive variances indicate good performance")
    
    print("\nOver Budget Project:")
    print("  - CPI < 1.0: Over budget ✗")
    print("  - EAC > BAC: Project will exceed original budget")
    print("  - Negative cost variance shows overspending")
    
    print("\nBehind Schedule Project:")
    print("  - SPI < 1.0: Behind schedule ✗")
    print("  - Less work completed than planned")
    print("  - Negative schedule variance indicates delays")


def save_and_load_example():
    """Demonstrate saving and loading projects"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Saving and Loading Projects")
    print("="*70)
    
    # Create a project
    project = Project(
        name="Data Migration Project",
        budget=75000,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 4, 30)
    )
    
    task = Task(
        id="MIGRATE",
        name="Database Migration",
        planned_value=75000,
        planned_start=date(2026, 1, 1),
        planned_end=date(2026, 4, 30)
    )
    task.update_progress(50, 40000)
    project.add_task(task)
    
    # Save to file
    filename = "/home/claude/sample_project.json"
    project.save_to_file(filename)
    print(f"\n✓ Project saved to {filename}")
    
    # Load from file
    loaded_project = Project.load_from_file(filename)
    print(f"✓ Project loaded from {filename}")
    
    print("\nLoaded Project Report:")
    print(loaded_project.generate_report(detailed=False))


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("EARNED VALUE MANAGEMENT TOOL - EXAMPLES")
    print("="*70)
    print("\nThis script demonstrates various use cases for the EVM tool")
    print("across different industries and project types.")
    
    # Run examples
    example_software_project()
    input("\nPress Enter to continue to next example...")
    
    example_construction_project()
    input("\nPress Enter to continue to next example...")
    
    example_marketing_campaign()
    input("\nPress Enter to continue to next example...")
    
    example_research_project()
    input("\nPress Enter to continue to next example...")
    
    compare_scenarios()
    input("\nPress Enter to continue to next example...")
    
    save_and_load_example()
    
    print("\n" + "="*70)
    print("Examples completed! Check the generated reports above.")
    print("You can modify these examples or create your own projects.")
    print("="*70)


if __name__ == "__main__":
    main()
