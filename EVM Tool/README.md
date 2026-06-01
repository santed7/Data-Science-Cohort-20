# Earned Value Management (EVM) Tool

A comprehensive Python-based Earned Value Management system for tracking project performance across any industry or project type.

## 📋 Overview

This tool provides a complete implementation of EVM methodology, helping project managers:
- Track project costs and schedule performance
- Calculate all standard EVM metrics automatically
- Forecast project completion costs and timelines
- Generate professional reports
- Save and load project data

## 🚀 Quick Start

### Option 1: Run the Example
```bash
python evm_tool.py
```

### Option 2: Use the Interactive CLI
```bash
python evm_cli.py
```

### Option 3: View Multiple Examples
```bash
python evm_examples.py
```

## 📁 Files Included

- **evm_tool.py** - Core EVM classes and functionality
- **evm_cli.py** - Interactive command-line interface
- **evm_examples.py** - Multiple real-world examples
- **EVM_USER_GUIDE.md** - Comprehensive documentation
- **README.md** - This file

## 💡 Key Features

### Automatic Calculations
- **Planned Value (PV)** - Budgeted cost of scheduled work
- **Earned Value (EV)** - Budgeted cost of completed work
- **Actual Cost (AC)** - Actual cost incurred
- **Cost Variance (CV)** - Budget performance indicator
- **Schedule Variance (SV)** - Schedule performance indicator
- **CPI & SPI** - Performance efficiency indices
- **EAC, ETC, VAC** - Completion forecasts

### Project Management
- Add and manage multiple tasks
- Track progress and costs
- Set custom status dates
- Generate detailed reports
- Export/import JSON data

## 📊 Example Usage

```python
from evm_tool import Project, Task
from datetime import date

# Create a project
project = Project(
    name="Website Redesign",
    budget=100000,
    start_date=date(2026, 1, 1),
    end_date=date(2026, 6, 30)
)

# Add a task
task = Task(
    id="T001",
    name="Design Phase",
    planned_value=20000,
    planned_start=date(2026, 1, 1),
    planned_end=date(2026, 2, 28)
)
project.add_task(task)

# Update progress
task.update_progress(percent_complete=75, actual_cost=18000)

# View metrics
metrics = project.get_metrics()
print(f"CPI: {metrics.cost_performance_index:.3f}")
print(f"SPI: {metrics.schedule_performance_index:.3f}")

# Generate report
print(project.generate_report())

# Save project
project.save_to_file("my_project.json")
```

## 📈 Industry Examples

The tool includes ready-to-run examples for:

1. **Software Development** - Agile sprint tracking
2. **Construction** - Multi-phase building project
3. **Marketing** - Campaign budget management
4. **Research** - Grant-funded clinical trial
5. **Performance Comparison** - Side-by-side analysis

Run all examples:
```bash
python evm_examples.py
```

## 🎯 Use Cases

### Construction Projects
- Track material costs and labor
- Monitor subcontractor expenses
- Forecast completion dates

### Software Development
- Track sprint velocity
- Monitor development costs
- Measure team efficiency

### Marketing Campaigns
- Track deliverable completion
- Monitor agency fees
- Measure ROI progress

### Research Projects
- Track grant spending
- Monitor milestone completion
- Forecast budget needs

## 📖 EVM Metrics Explained

### Performance Indicators
- **CPI > 1.0** = Under budget ✓
- **CPI < 1.0** = Over budget ✗
- **SPI > 1.0** = Ahead of schedule ✓
- **SPI < 1.0** = Behind schedule ✗

### Variance Analysis
- **CV > 0** = Under budget
- **CV < 0** = Over budget
- **SV > 0** = Ahead of schedule
- **SV < 0** = Behind schedule

### Forecasting
- **EAC** = Projected total cost at completion
- **ETC** = Estimated remaining cost
- **VAC** = Projected over/under budget
- **TCPI** = Required future performance to meet budget

## 🔧 Requirements

- Python 3.7 or higher
- No external dependencies (uses only standard library)

## 📝 CLI Interface

The interactive CLI provides:
1. Create new projects
2. Load existing projects
3. Add tasks
4. Update task progress
5. View quick summaries
6. Generate detailed reports
7. Set status dates
8. Save projects

## 💾 Data Format

Projects are saved as JSON files with this structure:
```json
{
  "name": "Project Name",
  "budget": 100000,
  "start_date": "2026-01-01",
  "end_date": "2026-06-30",
  "tasks": [...]
}
```

## 📚 Documentation

See **EVM_USER_GUIDE.md** for:
- Detailed API reference
- Best practices
- Troubleshooting guide
- Advanced usage examples

## 🎓 Learning Resources

The tool includes:
- Inline code documentation
- Comprehensive examples
- Interpretation guides
- Performance comparisons

## 🔍 Report Features

Reports include:
- Project summary
- Key metrics
- Variance analysis
- Performance indices
- Forecasts
- Task details
- Status interpretations

## ⚡ Performance

- Fast calculations (processes hundreds of tasks instantly)
- Minimal memory footprint
- No database required
- Portable JSON storage

## 🛠️ Customization

The tool is designed to be extensible:
- Add custom metrics
- Modify report formats
- Integrate with other tools
- Export to different formats

## 📊 Sample Output

```
======================================================================
EARNED VALUE MANAGEMENT REPORT
======================================================================

Project: Website Redesign Project
Status Date: 2026-04-01

KEY METRICS
----------------------------------------------------------------------
Budget at Completion (BAC):    $100,000.00
Planned Value (PV):             $53,416.67
Earned Value (EV):              $55,500.00
Actual Cost (AC):               $60,500.00

Percent Complete:               55.5%
Percent Spent:                  60.5%

VARIANCE ANALYSIS
----------------------------------------------------------------------
Cost Variance (CV):             $-5,000.00 (Over Budget)
Schedule Variance (SV):         $2,083.33 (Ahead of Schedule)

PERFORMANCE INDICES
----------------------------------------------------------------------
Cost Performance Index (CPI):   0.917 (Poor)
Schedule Performance Index (SPI): 1.039 (Good)
```

## 🤝 Contributing

This tool is designed to be:
- Easy to understand
- Simple to modify
- Well-documented
- Production-ready

## 📄 License

This tool is provided as-is for project management purposes.

## 🆘 Support

For issues or questions:
1. Check the EVM_USER_GUIDE.md
2. Review the examples in evm_examples.py
3. Examine the inline code documentation

## 🎯 Best Practices

1. Update task progress weekly
2. Record actual costs promptly
3. Use realistic planned values
4. Break work into 1-4 week tasks
5. Keep status date current

## ✨ Features Highlights

- ✅ Complete EVM methodology
- ✅ No external dependencies
- ✅ Interactive CLI
- ✅ Multiple examples
- ✅ JSON export/import
- ✅ Detailed reporting
- ✅ Automatic forecasting
- ✅ Well-documented
- ✅ Production-ready
- ✅ Easy to customize

## 🚦 Getting Started Checklist

- [ ] Review EVM_USER_GUIDE.md
- [ ] Run evm_tool.py to see basic example
- [ ] Run evm_examples.py to explore use cases
- [ ] Try evm_cli.py for interactive mode
- [ ] Create your first project
- [ ] Generate your first report

---

**Ready to track your project performance with confidence!** 🎉
