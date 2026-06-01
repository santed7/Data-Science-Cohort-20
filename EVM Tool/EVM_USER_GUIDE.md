# Earned Value Management (EVM) Tool - User Guide

## Overview

This Python-based EVM tool helps project managers track project performance using industry-standard Earned Value Management metrics. It can be used for any type of project across any industry.

## Key Features

- **Task Management**: Add, update, and track multiple tasks
- **Automatic EVM Calculations**: All standard EVM metrics computed automatically
- **Performance Analysis**: Cost and schedule performance tracking
- **Forecasting**: Predict project completion costs and timelines
- **Reporting**: Generate detailed or summary reports
- **Data Persistence**: Save and load projects from JSON files

## EVM Metrics Explained

### Primary Metrics
- **PV (Planned Value)**: What you planned to accomplish by now (budgeted cost of scheduled work)
- **EV (Earned Value)**: What you actually accomplished (budgeted cost of completed work)
- **AC (Actual Cost)**: What you actually spent
- **BAC (Budget at Completion)**: Total project budget

### Variance Metrics
- **CV (Cost Variance)**: EV - AC
  - Positive = Under budget ✓
  - Negative = Over budget ✗
  
- **SV (Schedule Variance)**: EV - PV
  - Positive = Ahead of schedule ✓
  - Negative = Behind schedule ✗

### Performance Indices
- **CPI (Cost Performance Index)**: EV / AC
  - > 1.0 = Under budget ✓
  - < 1.0 = Over budget ✗
  
- **SPI (Schedule Performance Index)**: EV / PV
  - > 1.0 = Ahead of schedule ✓
  - < 1.0 = Behind schedule ✗

### Forecasting Metrics
- **EAC (Estimate at Completion)**: BAC / CPI (projected total cost)
- **ETC (Estimate to Complete)**: EAC - AC (cost to finish)
- **VAC (Variance at Completion)**: BAC - EAC (projected over/under budget)
- **TCPI (To-Complete Performance Index)**: Required future efficiency to meet budget

## Quick Start Guide

### 1. Import the Module

```python
from evm_tool import Project, Task, TaskStatus
from datetime import date
```

### 2. Create a Project

```python
project = Project(
    name="My Project",
    budget=100000,
    start_date=date(2026, 1, 1),
    end_date=date(2026, 12, 31)
)
```

### 3. Add Tasks

```python
task = Task(
    id="T001",
    name="Design Phase",
    planned_value=20000,
    planned_start=date(2026, 1, 1),
    planned_end=date(2026, 3, 31)
)
project.add_task(task)
```

### 4. Update Progress

```python
task.update_progress(percent_complete=75, actual_cost=18000)
```

### 5. Generate Reports

```python
print(project.generate_report())
```

## Complete Example

See `evm_example.py` for a complete working example with multiple tasks.

## API Reference

### Project Class

#### Constructor
```python
Project(name: str, budget: float, start_date: date, end_date: date)
```

#### Methods
- `add_task(task: Task)` - Add a task to the project
- `remove_task(task_id: str)` - Remove a task by ID
- `get_task(task_id: str)` - Retrieve a task by ID
- `get_metrics(as_of_date: Optional[date])` - Calculate current EVM metrics
- `generate_report(detailed: bool)` - Generate text report
- `save_to_file(filename: str)` - Save project to JSON
- `load_from_file(filename: str)` - Load project from JSON

### Task Class

#### Constructor
```python
Task(
    id: str,
    name: str,
    planned_value: float,
    planned_start: date,
    planned_end: date,
    actual_start: Optional[date] = None,
    actual_end: Optional[date] = None,
    percent_complete: float = 0.0,
    actual_cost: float = 0.0,
    status: TaskStatus = TaskStatus.NOT_STARTED
)
```

#### Methods
- `update_progress(percent_complete: float, actual_cost: float)` - Update task status

#### Properties
- `earned_value` - Calculated EV for the task
- `is_completed` - Boolean indicating completion status

### EVMMetrics Class

Contains all calculated metrics as properties:
- `cost_variance`, `schedule_variance`
- `cost_performance_index`, `schedule_performance_index`
- `estimate_at_completion`, `estimate_to_complete`
- `variance_at_completion`, `to_complete_performance_index`
- `percent_complete`, `percent_spent`

## Best Practices

1. **Regular Updates**: Update task progress and costs regularly (weekly recommended)
2. **Realistic Estimates**: Use accurate planned values based on historical data
3. **Status Date**: Keep the status date current for accurate PV calculations
4. **Task Granularity**: Break work into tasks of 1-4 weeks duration
5. **Track Actuals**: Record actual costs promptly and accurately

## Common Use Cases

### Construction Projects
- Track material costs, labor hours, and subcontractor expenses
- Monitor milestone completion against baseline schedule

### Software Development
- Track sprint completion and development costs
- Measure velocity against planned story points

### Marketing Campaigns
- Monitor campaign deliverable completion
- Track agency fees and media spend

### Research Projects
- Track experiment completion and research phases
- Monitor grant spending against approved budget

## Troubleshooting

### CPI or SPI showing as 1.0 when it shouldn't
- Check that actual_cost > 0 and planned_value > 0
- Ensure percent_complete is being updated

### PV showing as 0
- Verify status_date is within project date range
- Check that tasks have planned_start dates before status_date

### Tasks not appearing in report
- Confirm tasks are added to project using add_task()
- Check that task IDs are unique

## File Format

Projects saved as JSON with this structure:
```json
{
  "name": "Project Name",
  "budget": 100000,
  "start_date": "2026-01-01",
  "end_date": "2026-12-31",
  "status_date": "2026-04-01",
  "tasks": [
    {
      "id": "T001",
      "name": "Task Name",
      "planned_value": 10000,
      "planned_start": "2026-01-01",
      "planned_end": "2026-01-31",
      "percent_complete": 100,
      "actual_cost": 9500,
      "status": "Completed"
    }
  ]
}
```

## License

This tool is provided as-is for project management purposes.
