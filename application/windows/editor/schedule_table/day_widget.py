from PySide6.QtWidgets import QComboBox
from PySide6.QtCore import Qt

from ..primary_table import PrimaryTableWidget


class ScheduleDayWidget(PrimaryTableWidget):
    def __init__(self, day_id: int, *args, **kwargs):
        PrimaryTableWidget.__init__(self, *args, **kwargs)

        day_combo_box: QComboBox = self.filter_widgets_list[1] 
        day_combo_box.setCurrentIndex(day_id)
        self.set_layout_visible(self.filters_layout)
        self.table_view.sortByColumn(2, Qt.SortOrder.AscendingOrder)

    def set_group(self, group_name: str):
        group_combo_box: QComboBox = self.filter_widgets_list[0] 
        group_combo_box.setCurrentText(group_name)
        self.filter()
        self.table_view.sortByColumn(2, Qt.SortOrder.AscendingOrder)
    
    def set_layout_visible(self, layout, visible = False):
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget():
                item.widget().setVisible(visible)
            elif item.layout():
                self.set_layout_visible(item.layout(), visible)  # Рекурсивно скрываем вложенные лэйауты
