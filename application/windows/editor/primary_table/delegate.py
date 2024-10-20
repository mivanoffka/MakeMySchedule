from PySide6.QtGui import Qt
from PySide6.QtWidgets import QStyledItemDelegate, QComboBox


class ForeignKeyDelegate(QStyledItemDelegate):
    def __init__(self, parent, session, foreign_key_column):
        super().__init__(parent)
        self.session = session
        self.foreign_key_column = foreign_key_column

    def createEditor(self, parent, option, index):
        combo_box = QComboBox(parent)
        items = self.session.query(self.foreign_key_column.orm_type).all()
        for item in items:
            combo_box.addItem(self.foreign_key_column.represent(item), item)
        return combo_box

    def setEditorData(self, editor, index):
        value = index.data(Qt.ItemDataRole.EditRole)
        editor.setCurrentText(value)

    def setModelData(self, editor, model, index):
        value = editor.currentData()
        model.setData(index, value, Qt.ItemDataRole.EditRole)
