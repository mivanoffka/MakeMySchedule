from PySide6.QtCore import Qt
from PySide6.QtWidgets import QItemDelegate, QComboBox


class RelatedComboBoxDelegate(QItemDelegate):
    def __init__(self, session, related_description, parent=None):
        super().__init__(parent)
        self.session = session
        self.related_description = related_description

    def createEditor(self, parent, option, index):
        """Создаем QComboBox для редактирования"""
        combo_box = QComboBox(parent)
        # Получаем список объектов из связанной таблицы
        related_objects = self.session.query(self.related_description.orm_type).all()

        # Добавляем в ComboBox строковые представления объектов
        for obj in related_objects:
            combo_box.addItem(self.related_description.represent(obj), obj)

        return combo_box

    def setEditorData(self, editor, index):
        """Устанавливаем текущее значение QComboBox при редактировании"""
        current_text = index.data(Qt.ItemDataRole.DisplayRole)
        combo_box = editor
        current_index = combo_box.findText(current_text)
        if current_index >= 0:
            combo_box.setCurrentIndex(current_index)

    def setModelData(self, editor, model, index):
        """Передаем выбранное значение обратно в модель"""
        combo_box = editor
        selected_object = combo_box.currentData()  # Это будет объект ORM, связанный с выбранной строкой
        if selected_object is not None:
            model.setData(index, selected_object, Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        """Обновляем размеры редактора."""
        editor.setGeometry(option.rect)