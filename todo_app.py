import sys
import os
from PySide6 import QtWidgets, QtCore, QtGui, QtCharts
import datetime
import json

class YearlyView(QtWidgets.QWidget):
    def __init__(self, tasks):
        super().__init__()
        self.tasks = tasks
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        # Monthly overview
        self.overview_table = QtWidgets.QTableWidget(3, 12)
        self.overview_table.setHorizontalHeaderLabels([datetime.date(2024, m, 1).strftime('%b') for m in range(1, 13)])
        self.overview_table.setVerticalHeaderLabels(["Ideal", "Maintenance", "Missed"])
        self.overview_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.overview_table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        layout.addWidget(self.overview_table)

        # Progress chart
        self.chart_view = QtCharts.QChartView()
        self.chart_view.setRenderHint(QtGui.QPainter.Antialiasing)
        layout.addWidget(self.chart_view)

        self.update_view()

    def update_view(self):
        self.update_overview_table()
        self.update_chart()

    def update_overview_table(self):
        year = datetime.date.today().year
        for month in range(12):
            ideal_count = 0
            maintenance_count = 0
            total_days = 0
            
            start_date = datetime.date(year, month + 1, 1)
            end_date = (start_date.replace(month=start_date.month % 12 + 1, day=1) - datetime.timedelta(days=1))
            
            for day in range((end_date - start_date).days + 1):
                date = start_date + datetime.timedelta(days=day)
                qt_date = QtCore.QDate(date.year, date.month, date.day)
                if qt_date in self.tasks:
                    total_days += 1
                    if any(self.tasks[qt_date].get(("Ideal", sub), []) for sub in ["Health", "Wealth", "Happiness"]):
                        ideal_count += 1
                    elif any(self.tasks[qt_date].get(("Maintenance", sub), []) for sub in ["Health", "Wealth", "Happiness"]):
                        maintenance_count += 1
            
            missed_count = total_days - ideal_count - maintenance_count
            
            self.overview_table.setItem(0, month, QtWidgets.QTableWidgetItem(str(ideal_count)))
            self.overview_table.setItem(1, month, QtWidgets.QTableWidgetItem(str(maintenance_count)))
            self.overview_table.setItem(2, month, QtWidgets.QTableWidgetItem(str(missed_count)))

    def update_chart(self):
        series = QtCharts.QBarSeries()
        ideal_set = QtCharts.QBarSet("Ideal")
        maintenance_set = QtCharts.QBarSet("Maintenance")

        for month in range(12):
            ideal_count = int(self.overview_table.item(0, month).text())
            maintenance_count = int(self.overview_table.item(1, month).text())
            ideal_set.append(ideal_count)
            maintenance_set.append(maintenance_count)

        series.append(ideal_set)
        series.append(maintenance_set)

        chart = QtCharts.QChart()
        chart.addSeries(series)
        chart.setTitle("Monthly Progress")
        chart.setAnimationOptions(QtCharts.QChart.SeriesAnimations)

        months = [datetime.date(2024, m, 1).strftime('%b') for m in range(1, 13)]
        axis_x = QtCharts.QBarCategoryAxis()
        axis_x.append(months)
        chart.addAxis(axis_x, QtCore.Qt.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QtCharts.QValueAxis()
        chart.addAxis(axis_y, QtCore.Qt.AlignLeft)
        series.attachAxis(axis_y)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(QtCore.Qt.AlignBottom)

        self.chart_view.setChart(chart)

class TodoApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("atomic")
        self.setGeometry(100, 100, 1000, 600)
        self.tasks = {}
        self.current_view = "month"
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        self.main_layout = QtWidgets.QHBoxLayout(central_widget)
        
        # Calendar
        self.calendar = QtWidgets.QCalendarWidget()
        self.calendar.setVerticalHeaderFormat(QtWidgets.QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.calendar.selectionChanged.connect(self.update_tasks)
        self.main_layout.addWidget(self.calendar)
        
        # Task layout
        self.task_widget = QtWidgets.QWidget()
        self.task_layout = QtWidgets.QVBoxLayout(self.task_widget)
        self.task_widgets = {}
        
        for main_section in ["Ideal", "Maintenance"]:
            group_box = QtWidgets.QGroupBox(main_section)
            group_layout = QtWidgets.QVBoxLayout()
            
            for sub_section in ["Health", "Wealth", "Happiness"]:
                sub_layout = QtWidgets.QVBoxLayout()
                label = QtWidgets.QLabel(sub_section)
                text_input = QtWidgets.QLineEdit()
                text_input.returnPressed.connect(self.add_task)
                task_list = QtWidgets.QListWidget()
                
                sub_layout.addWidget(label)
                sub_layout.addWidget(text_input)
                sub_layout.addWidget(task_list)
                
                group_layout.addLayout(sub_layout)
                self.task_widgets[(main_section, sub_section)] = (text_input, task_list)
            
            group_box.setLayout(group_layout)
            self.task_layout.addWidget(group_box)
        
        self.main_layout.addWidget(self.task_widget)
        
        # Yearly view (initially hidden)
        self.yearly_view = YearlyView(self.tasks)
        self.yearly_view.hide()
        self.main_layout.addWidget(self.yearly_view)
        
        # Menu
        menu_bar = self.menuBar()
        view_menu = menu_bar.addMenu("View")
        
        monthly_action = QtGui.QAction("Monthly", self)
        monthly_action.triggered.connect(self.switch_to_monthly)
        view_menu.addAction(monthly_action)
        
        yearly_action = QtGui.QAction("Yearly", self)
        yearly_action.triggered.connect(self.switch_to_yearly)
        view_menu.addAction(yearly_action)

    def switch_to_monthly(self):
        self.current_view = "month"
        self.calendar.show()
        self.task_widget.show()
        self.yearly_view.hide()

    def switch_to_yearly(self):
        self.current_view = "year"
        self.calendar.hide()
        self.task_widget.hide()
        self.yearly_view.update_view()
        self.yearly_view.show()

    def update_tasks(self):
            selected_date = self.calendar.selectedDate()
            for (main_section, sub_section), (text_input, task_list) in self.task_widgets.items():
                task_list.clear()
                if selected_date in self.tasks:
                    for task, completed in self.tasks[selected_date].get((main_section, sub_section), []):
                        item = QtWidgets.QListWidgetItem(task)
                        item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                        item.setCheckState(QtCore.Qt.CheckState.Checked if completed else QtCore.Qt.CheckState.Unchecked)
                        task_list.addItem(item)
                task_list.itemChanged.connect(self.task_state_changed)

    def add_task(self):
        sender = self.sender()
        for (main_section, sub_section), (text_input, task_list) in self.task_widgets.items():
            if sender == text_input:
                task = text_input.text().strip()
                if task:
                    selected_date = self.calendar.selectedDate()
                    if selected_date not in self.tasks:
                        self.tasks[selected_date] = {}
                    if (main_section, sub_section) not in self.tasks[selected_date]:
                        self.tasks[selected_date][(main_section, sub_section)] = []
                    self.tasks[selected_date][(main_section, sub_section)].append((task, False))
                    text_input.clear()
                    self.update_tasks()
                    self.update_calendar_colors()
                break

    def task_state_changed(self, item):
        selected_date = self.calendar.selectedDate()
        task_text = item.text()
        is_completed = item.checkState() == QtCore.Qt.CheckState.Checked

        for (main_section, sub_section), tasks in self.tasks[selected_date].items():
            for i, (task, _) in enumerate(tasks):
                if task == task_text:
                    self.tasks[selected_date][(main_section, sub_section)][i] = (task, is_completed)
                    if is_completed:
                        # Uncheck tasks in the other main section
                        other_main_section = "Maintenance" if main_section == "Ideal" else "Ideal"
                        for other_sub_section in ["Health", "Wealth", "Happiness"]:
                            if (other_main_section, other_sub_section) in self.tasks[selected_date]:
                                for j, (other_task, _) in enumerate(self.tasks[selected_date][(other_main_section, other_sub_section)]):
                                    self.tasks[selected_date][(other_main_section, other_sub_section)][j] = (other_task, False)
                    break

        self.update_tasks()
        self.update_calendar_colors()

    def update_calendar_colors(self):
        github_colors = [
            QtGui.QColor(235, 237, 240),  # 0 contributions
            QtGui.QColor(155, 233, 168),  # 1-3 contributions
            QtGui.QColor(64, 196, 99),    # 4-6 contributions
            QtGui.QColor(48, 161, 78),    # 7-9 contributions
            QtGui.QColor(33, 110, 57)     # 10+ contributions
        ]

        for date, sections in self.tasks.items():
            total_tasks = sum(len(tasks) for tasks in sections.values())
            completed_tasks = sum(sum(1 for _, completed in tasks if completed) for tasks in sections.values())
            
            if total_tasks == 0:
                color_index = 0
            else:
                completion_ratio = completed_tasks / total_tasks
                color_index = min(int(completion_ratio * 5), 4)
            
            text_format = QtGui.QTextCharFormat()
            text_format.setBackground(github_colors[color_index])
            self.calendar.setDateTextFormat(QtCore.QDate(date), text_format)


    def save_data(self):
        with open('todo_data.json', 'w') as f:
            json.dump({date.toString(QtCore.Qt.ISODate): tasks for date, tasks in self.tasks.items()}, f)

    def load_data(self):
        try:
            with open('todo_data.json', 'r') as f:
                data = json.load(f)
                self.tasks = {QtCore.QDate.fromString(date, QtCore.Qt.ISODate): tasks for date, tasks in data.items()}
            self.update_calendar_colors()
        except FileNotFoundError:
            pass

    def closeEvent(self, event):
        self.save_data()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = TodoApp()
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    icon_path = os.path.join(base_path, "atom.ico")
    window.setWindowIcon(QtGui.QIcon(icon_path))
    window.show()
    sys.exit(app.exec())