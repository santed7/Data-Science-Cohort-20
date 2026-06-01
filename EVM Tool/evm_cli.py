"""
Simple CLI Interface for EVM Tool
Provides an interactive command-line interface for managing projects
"""

from evm_tool import Project, Task, TaskStatus
from datetime import date, datetime
import sys
import os


class EVMCLI:
    def __init__(self):
        self.project = None
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_header(self, text):
        """Print a formatted header"""
        print("\n" + "="*70)
        print(text.center(70))
        print("="*70 + "\n")
    
    def get_date_input(self, prompt):
        """Get a date from user input"""
        while True:
            date_str = input(f"{prompt} (YYYY-MM-DD): ").strip()
            try:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD")
    
    def get_float_input(self, prompt):
        """Get a float from user input"""
        while True:
            try:
                return float(input(f"{prompt}: ").strip())
            except ValueError:
                print("Invalid number. Please enter a valid number.")
    
    def create_new_project(self):
        """Create a new project"""
        self.print_header("CREATE NEW PROJECT")
        
        name = input("Project Name: ").strip()
        budget = self.get_float_input("Total Budget ($)")
        start_date = self.get_date_input("Start Date")
        end_date = self.get_date_input("End Date")
        
        self.project = Project(name, budget, start_date, end_date)
        print(f"\n✓ Project '{name}' created successfully!")
        input("\nPress Enter to continue...")
    
    def add_task(self):
        """Add a task to the project"""
        if not self.project:
            print("\n✗ No project loaded. Please create or load a project first.")
            input("\nPress Enter to continue...")
            return
        
        self.print_header("ADD NEW TASK")
        
        task_id = input("Task ID: ").strip()
        name = input("Task Name: ").strip()
        planned_value = self.get_float_input("Planned Value ($)")
        planned_start = self.get_date_input("Planned Start Date")
        planned_end = self.get_date_input("Planned End Date")
        
        task = Task(task_id, name, planned_value, planned_start, planned_end)
        self.project.add_task(task)
        
        print(f"\n✓ Task '{name}' added successfully!")
        input("\nPress Enter to continue...")
    
    def update_task(self):
        """Update task progress"""
        if not self.project:
            print("\n✗ No project loaded. Please create or load a project first.")
            input("\nPress Enter to continue...")
            return
        
        if not self.project.tasks:
            print("\n✗ No tasks in project. Please add tasks first.")
            input("\nPress Enter to continue...")
            return
        
        self.print_header("UPDATE TASK PROGRESS")
        
        # List tasks
        print("Available Tasks:")
        for i, task in enumerate(self.project.tasks, 1):
            print(f"  {i}. {task.id}: {task.name} ({task.percent_complete:.1f}% complete)")
        
        choice = input("\nSelect task number: ").strip()
        try:
            task_index = int(choice) - 1
            task = self.project.tasks[task_index]
            
            print(f"\nUpdating: {task.name}")
            print(f"Current progress: {task.percent_complete:.1f}%")
            print(f"Current cost: ${task.actual_cost:,.2f}")
            
            percent = self.get_float_input("\nNew percent complete (0-100)")
            cost = self.get_float_input("Actual cost to date ($)")
            
            task.update_progress(percent, cost)
            
            print(f"\n✓ Task updated successfully!")
            print(f"  Status: {task.status.value}")
            print(f"  Earned Value: ${task.earned_value:,.2f}")
            
        except (ValueError, IndexError):
            print("\n✗ Invalid task selection.")
        
        input("\nPress Enter to continue...")
    
    def view_report(self):
        """View project report"""
        if not self.project:
            print("\n✗ No project loaded. Please create or load a project first.")
            input("\nPress Enter to continue...")
            return
        
        self.clear_screen()
        print(self.project.generate_report(detailed=True))
        input("\nPress Enter to continue...")
    
    def view_summary(self):
        """View quick project summary"""
        if not self.project:
            print("\n✗ No project loaded. Please create or load a project first.")
            input("\nPress Enter to continue...")
            return
        
        self.print_header("PROJECT SUMMARY")
        
        metrics = self.project.get_metrics()
        task_summary = self.project.get_task_summary()
        
        print(f"Project: {self.project.name}")
        print(f"Status Date: {self.project.status_date}")
        print(f"\nTasks: {task_summary['total_tasks']} total")
        print(f"  - Completed: {task_summary['completed']}")
        print(f"  - In Progress: {task_summary['in_progress']}")
        print(f"  - Not Started: {task_summary['not_started']}")
        
        print(f"\nProgress: {metrics.percent_complete:.1f}% complete")
        print(f"Budget: ${metrics.actual_cost:,.2f} of ${metrics.budget_at_completion:,.2f} spent")
        
        print(f"\nPerformance:")
        print(f"  Cost Efficiency (CPI): {metrics.cost_performance_index:.3f}", end="")
        print(" ✓" if metrics.cost_performance_index >= 1 else " ✗")
        print(f"  Schedule Efficiency (SPI): {metrics.schedule_performance_index:.3f}", end="")
        print(" ✓" if metrics.schedule_performance_index >= 1 else " ✗")
        
        print(f"\nForecast:")
        print(f"  Estimated Final Cost: ${metrics.estimate_at_completion:,.2f}")
        print(f"  Projected Variance: ${metrics.variance_at_completion:,.2f}")
        
        input("\nPress Enter to continue...")
    
    def save_project(self):
        """Save project to file"""
        if not self.project:
            print("\n✗ No project loaded. Please create or load a project first.")
            input("\nPress Enter to continue...")
            return
        
        self.print_header("SAVE PROJECT")
        
        filename = input("Enter filename (e.g., my_project.json): ").strip()
        if not filename.endswith('.json'):
            filename += '.json'
        
        try:
            self.project.save_to_file(filename)
            print(f"\n✓ Project saved to {filename}")
        except Exception as e:
            print(f"\n✗ Error saving project: {e}")
        
        input("\nPress Enter to continue...")
    
    def load_project(self):
        """Load project from file"""
        self.print_header("LOAD PROJECT")
        
        filename = input("Enter filename: ").strip()
        
        try:
            self.project = Project.load_from_file(filename)
            print(f"\n✓ Project '{self.project.name}' loaded successfully!")
        except FileNotFoundError:
            print(f"\n✗ File '{filename}' not found.")
        except Exception as e:
            print(f"\n✗ Error loading project: {e}")
        
        input("\nPress Enter to continue...")
    
    def set_status_date(self):
        """Set the status date for the project"""
        if not self.project:
            print("\n✗ No project loaded. Please create or load a project first.")
            input("\nPress Enter to continue...")
            return
        
        self.print_header("SET STATUS DATE")
        
        print(f"Current status date: {self.project.status_date}")
        new_date = self.get_date_input("\nNew status date")
        
        self.project.status_date = new_date
        print(f"\n✓ Status date updated to {new_date}")
        input("\nPress Enter to continue...")
    
    def main_menu(self):
        """Display main menu"""
        while True:
            self.clear_screen()
            self.print_header("EARNED VALUE MANAGEMENT TOOL")
            
            if self.project:
                print(f"Current Project: {self.project.name}")
                print(f"Tasks: {len(self.project.tasks)}")
                print(f"Status Date: {self.project.status_date}\n")
            else:
                print("No project loaded\n")
            
            print("1. Create New Project")
            print("2. Load Project from File")
            print("3. Add Task")
            print("4. Update Task Progress")
            print("5. View Quick Summary")
            print("6. View Detailed Report")
            print("7. Set Status Date")
            print("8. Save Project")
            print("9. Exit")
            
            choice = input("\nSelect option (1-9): ").strip()
            
            if choice == '1':
                self.create_new_project()
            elif choice == '2':
                self.load_project()
            elif choice == '3':
                self.add_task()
            elif choice == '4':
                self.update_task()
            elif choice == '5':
                self.view_summary()
            elif choice == '6':
                self.view_report()
            elif choice == '7':
                self.set_status_date()
            elif choice == '8':
                self.save_project()
            elif choice == '9':
                print("\nThank you for using the EVM Tool!")
                sys.exit(0)
            else:
                print("\n✗ Invalid option. Please select 1-9.")
                input("\nPress Enter to continue...")


def main():
    """Main entry point"""
    cli = EVMCLI()
    try:
        cli.main_menu()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)


if __name__ == "__main__":
    main()
