import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QListWidget, QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox, QSpinBox, QFormLayout, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from collections import defaultdict
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from stirrups import different_spacing, same_spacing
import math

class TopSteelInput(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()
        self.beam_num_edit = QLineEdit()
        self.extended_checkbox = QCheckBox("Is this bar extended into other beams?")
        self.end_support_checkbox = QCheckBox("Is end support present?")
        self.num_supports_spin = QSpinBox()
        self.num_supports_spin.setMinimum(1)
        self.num_supports_spin.setMaximum(2)
        self.num_supports_spin.setValue(1)
        self.clear_span_edit = QLineEdit()
        self.es_width1_edit = QLineEdit()
        self.es_width2_edit = QLineEdit()
        self.beam_depth1_edit = QLineEdit()
        self.beam_depth2_edit = QLineEdit()
        self.num_bars_spin = QSpinBox()
        self.num_bars_spin.setMinimum(1)
        self.num_bars_spin.setMaximum(20)
        self.bar_diam_edits = []
        self.bar_qty_spins = []
        self.bar_diam_layout = QVBoxLayout()
        self.bar_diam_widget = QWidget()
        self.bar_diam_widget.setLayout(self.bar_diam_layout)

        form.addRow("Beam Number:", self.beam_num_edit)
        form.addRow(self.extended_checkbox)
        form.addRow(self.end_support_checkbox)
        form.addRow("Number of End Supports:", self.num_supports_spin)
        form.addRow("Clear Span (mm):", self.clear_span_edit)
        form.addRow("End Support Width 1 (mm):", self.es_width1_edit)
        form.addRow("End Support Width 2 (mm):", self.es_width2_edit)
        form.addRow("Beam Depth of End Support 1 (mm):", self.beam_depth1_edit)
        form.addRow("Beam Depth of End Support 2 (mm):", self.beam_depth2_edit)
        form.addRow("Number of Bar Diameters:", self.num_bars_spin)
        layout.addLayout(form)
        layout.addWidget(QLabel("Bar Diameters (mm) and Quantities:"))
        layout.addWidget(self.bar_diam_widget)
        layout.addStretch()
        self.setLayout(layout)

        self.num_bars_spin.valueChanged.connect(self.update_bar_diam_inputs)
        self.extended_checkbox.stateChanged.connect(self.update_extended_fields)
        self.end_support_checkbox.stateChanged.connect(self.update_end_support_fields)
        self.num_supports_spin.valueChanged.connect(self.update_end_support_fields)
        self.update_bar_diam_inputs()
        self.update_extended_fields()
        self.update_end_support_fields()

    def update_bar_diam_inputs(self):
        for i in reversed(range(self.bar_diam_layout.count())):
            widget = self.bar_diam_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.bar_diam_edits = []
        self.bar_qty_spins = []
        for i in range(self.num_bars_spin.value()):
            row = QHBoxLayout()
            edit = QLineEdit()
            edit.setPlaceholderText(f"Diameter for bar {i+1}")
            qty = QSpinBox()
            qty.setMinimum(1)
            qty.setMaximum(1000)
            qty.setValue(1)
            row.addWidget(edit)
            row.addWidget(QLabel("Qty:"))
            row.addWidget(qty)
            container = QWidget()
            container.setLayout(row)
            self.bar_diam_layout.addWidget(container)
            self.bar_diam_edits.append(edit)
            self.bar_qty_spins.append(qty)

    def update_extended_fields(self):
        if self.extended_checkbox.isChecked():
            self.end_support_checkbox.hide()
            self.num_supports_spin.hide()
            self.es_width1_edit.show()
            self.es_width2_edit.show()
            self.beam_depth1_edit.show()
            self.beam_depth2_edit.show()
        else:
            self.end_support_checkbox.show()
            self.update_end_support_fields()

    def update_end_support_fields(self):
        if not self.extended_checkbox.isChecked():
            if self.end_support_checkbox.isChecked():
                self.num_supports_spin.show()
                self.es_width1_edit.show()
                self.beam_depth1_edit.show()
                if self.num_supports_spin.value() == 2:
                    self.es_width2_edit.show()
                    self.beam_depth2_edit.show()
                else:
                    self.es_width2_edit.hide()
                    self.beam_depth2_edit.hide()
            else:
                self.num_supports_spin.hide()
                self.es_width1_edit.hide()
                self.es_width2_edit.hide()
                self.beam_depth1_edit.hide()
                self.beam_depth2_edit.hide()

    def get_inputs(self):
        try:
            beam_num = self.beam_num_edit.text().strip()
            extended = self.extended_checkbox.isChecked()
            end_support = self.end_support_checkbox.isChecked()
            num_supports = self.num_supports_spin.value()
            clear_span = float(self.clear_span_edit.text())
            es_width1 = float(self.es_width1_edit.text()) if self.es_width1_edit.isVisible() and self.es_width1_edit.text().strip() else 0
            es_width2 = float(self.es_width2_edit.text()) if self.es_width2_edit.isVisible() and self.es_width2_edit.text().strip() else 0
            beam_depth1 = float(self.beam_depth1_edit.text() if self.beam_depth1_edit.isVisible() and self.es_width1_edit.text().strip else 0)
            beam_depth2 = float(self.beam_depth2_edit.text() if self.beam_depth2_edit.isVisible() and self.es_width2_edit.text().strip else 0)
            diam_qty = []
            for edit, qty in zip(self.bar_diam_edits, self.bar_qty_spins):
                if edit.text().strip():
                    diam_qty.append((float(edit.text()), qty.value()))
            return beam_num, extended, end_support, num_supports, clear_span, es_width1, es_width2,beam_depth1, beam_depth2, diam_qty
        except Exception as e:
            return None

class BottomSteelInput(QWidget):
    """
    Input form for Bottom Steel calculation (flow2/flow1).
    Allows user to select number of end supports (1 or 2),
    and dynamically shows the appropriate fields.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()
        self.beam_num_edit = QLineEdit()
        self.extended_checkbox = QCheckBox("Is this bar extended into other beams?")
        self.end_support_checkbox = QCheckBox("Is end support present?")
        self.num_supports_spin = QSpinBox()
        self.num_supports_spin.setMinimum(1)
        self.num_supports_spin.setMaximum(2)
        self.num_supports_spin.setValue(1)
        self.clear_span_edit = QLineEdit()
        self.es_width1_edit = QLineEdit()
        self.es_width2_edit = QLineEdit()
        self.beam_depth1_edit = QLineEdit()
        self.beam_depth2_edit = QLineEdit()
        self.beam_depth2_edit = QLineEdit()
        self.num_bars_spin = QSpinBox()
        self.num_bars_spin.setMinimum(1)
        self.num_bars_spin.setMaximum(20)
        self.bar_diam_edits = []
        self.bar_qty_spins = []
        self.bar_diam_layout = QVBoxLayout()
        self.bar_diam_widget = QWidget()
        self.bar_diam_widget.setLayout(self.bar_diam_layout)

        form.addRow("Beam Number:", self.beam_num_edit)
        form.addRow(self.extended_checkbox)
        form.addRow(self.end_support_checkbox)
        form.addRow("Number of End Supports:", self.num_supports_spin)
        form.addRow("Clear Span (mm):", self.clear_span_edit)
        form.addRow("End Support Width 1 (mm):", self.es_width1_edit)
        form.addRow("End Support Width 2 (mm):", self.es_width2_edit)
        form.addRow("Beam Depth of End Support 1 (mm):", self.beam_depth1_edit)
        form.addRow("Beam Depth of End Support 2 (mm):", self.beam_depth2_edit)
        form.addRow("Number of Bar Diameters:", self.num_bars_spin)
        layout.addLayout(form)
        layout.addWidget(QLabel("Bar Diameters (mm) and Quantities:"))
        layout.addWidget(self.bar_diam_widget)
        layout.addStretch()
        self.setLayout(layout)

        self.num_bars_spin.valueChanged.connect(self.update_bar_diam_inputs)
        self.extended_checkbox.stateChanged.connect(self.update_extended_fields)
        self.end_support_checkbox.stateChanged.connect(self.update_end_support_fields)
        self.num_supports_spin.valueChanged.connect(self.update_end_support_fields)
        self.update_bar_diam_inputs()
        self.update_extended_fields()
        self.update_end_support_fields()

    def update_bar_diam_inputs(self):
        for i in reversed(range(self.bar_diam_layout.count())):
            widget = self.bar_diam_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.bar_diam_edits = []
        self.bar_qty_spins = []
        for i in range(self.num_bars_spin.value()):
            row = QHBoxLayout()
            edit = QLineEdit()
            edit.setPlaceholderText(f"Diameter for bar {i+1}")
            qty = QSpinBox()
            qty.setMinimum(1)
            qty.setMaximum(1000)
            qty.setValue(1)
            row.addWidget(edit)
            row.addWidget(QLabel("Qty:"))
            row.addWidget(qty)
            container = QWidget()
            container.setLayout(row)
            self.bar_diam_layout.addWidget(container)
            self.bar_diam_edits.append(edit)
            self.bar_qty_spins.append(qty)

    def update_extended_fields(self):
        if self.extended_checkbox.isChecked():
            self.end_support_checkbox.hide()
            self.num_supports_spin.hide()
            self.es_width1_edit.show()
            self.es_width2_edit.show()
            self.beam_depth1_edit.show()
            self.beam_depth2_edit.show()
        else:
            self.end_support_checkbox.show()
            self.update_end_support_fields()

    def update_end_support_fields(self):
        if not self.extended_checkbox.isChecked():
            if self.end_support_checkbox.isChecked():
                self.num_supports_spin.show()
                self.es_width1_edit.show()
                self.beam_depth1_edit.show()
                if self.num_supports_spin.value() == 2:
                    self.es_width2_edit.show()
                    self.beam_depth2_edit.show()
                else:
                    self.es_width2_edit.hide()
                    self.beam_depth2_edit.hide()
            else:
                self.num_supports_spin.hide()
                self.es_width1_edit.hide()
                self.es_width2_edit.hide()
                self.beam_depth1_edit.hide()
                self.beam_depth2_edit.hide()

    def get_inputs(self):
        try:
            beam_num = self.beam_num_edit.text().strip()
            extended = self.extended_checkbox.isChecked()
            end_support = self.end_support_checkbox.isChecked()
            num_supports = self.num_supports_spin.value()
            clear_span = float(self.clear_span_edit.text())
            es_width1 = float(self.es_width1_edit.text()) if self.es_width1_edit.isVisible() and self.es_width1_edit.text().strip() else 0
            es_width2 = float(self.es_width2_edit.text()) if self.es_width2_edit.isVisible() and self.es_width2_edit.text().strip() else 0
            beam_depth1 = float(self.beam_depth1_edit.text() if self.beam_depth1_edit.isVisible() and self.es_width1_edit.text().strip else 0)
            beam_depth2 = float(self.beam_depth2_edit.text() if self.beam_depth2_edit.isVisible() and self.es_width2_edit.text().strip else 0)
            diam_qty = []
            for edit, qty in zip(self.bar_diam_edits, self.bar_qty_spins):
                if edit.text().strip():
                    diam_qty.append((float(edit.text()), qty.value()))
            return beam_num, extended, end_support, num_supports, clear_span, es_width1, es_width2,beam_depth1, beam_depth2, diam_qty
        except Exception as e:
            return None

class StirrupsInput(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()
        # Stirrup type
        self.type_spin = QSpinBox()
        self.type_spin.setMinimum(1)
        self.type_spin.setMaximum(3)
        self.type_spin.setValue(1)
        # 1: Two legged, 2: Four legged, 3: Six legged
        self.type_spin.setPrefix("")
        # Beam number
        self.beam_num_edit = QLineEdit()
        # Clear span
        self.clear_span_edit = QLineEdit()
        # Beam width
        self.beam_width_edit = QLineEdit()
        # Beam depth
        self.beam_depth_edit = QLineEdit()
        # Spacing type
        self.spacing_type_spin = QSpinBox()
        self.spacing_type_spin.setMinimum(1)
        self.spacing_type_spin.setMaximum(2)
        self.spacing_type_spin.setValue(1)
        # 1: Uniform, 2: Different (L/4, L/2)
        # Spacing fields
        self.spacing_edit = QLineEdit()
        self.l4_spacing_edit = QLineEdit()
        self.l2_spacing_edit = QLineEdit()
        self.num_bars_spin = QSpinBox()
        self.num_bars_spin.setMinimum(1)
        self.num_bars_spin.setMaximum(20)
        self.bar_diam_edits = []
        self.bar_qty_spins = []
        self.bar_diam_layout = QVBoxLayout()
        self.bar_diam_widget = QWidget()
        self.bar_diam_widget.setLayout(self.bar_diam_layout)

        form.addRow("Stirrup Type (1: Two, 2: Four, 3: Six legged):", self.type_spin)
        form.addRow("Beam Number:", self.beam_num_edit)
        form.addRow("Clear Span (mm):", self.clear_span_edit)
        form.addRow("Beam Width (mm):", self.beam_width_edit)
        form.addRow("Beam Depth (mm):", self.beam_depth_edit)
        form.addRow("Spacing Type (1: Uniform, 2: Different):", self.spacing_type_spin)
        form.addRow("Uniform Spacing (mm):", self.spacing_edit)
        form.addRow("L/4 Spacing (mm):", self.l4_spacing_edit)
        form.addRow("L/2 Spacing (mm):", self.l2_spacing_edit)
        form.addRow("Number of Bar Diameters:", self.num_bars_spin)
        layout.addLayout(form)
        layout.addWidget(QLabel("Bar Diameters (mm) and Quantities:"))
        layout.addWidget(self.bar_diam_widget)
        layout.addStretch()
        self.setLayout(layout)
        self.spacing_type_spin.valueChanged.connect(self.update_spacing_fields)
        self.num_bars_spin.valueChanged.connect(self.update_bar_diam_inputs)
        self.update_spacing_fields()
        self.update_bar_diam_inputs()

    def update_spacing_fields(self):
        if self.spacing_type_spin.value() == 1:
            self.spacing_edit.show()
            self.l4_spacing_edit.hide()
            self.l2_spacing_edit.hide()
        else:
            self.spacing_edit.hide()
            self.l4_spacing_edit.show()
            self.l2_spacing_edit.show()

    def update_bar_diam_inputs(self):
        for i in reversed(range(self.bar_diam_layout.count())):
            widget = self.bar_diam_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.bar_diam_edits = []
        self.bar_qty_spins = []
        for i in range(self.num_bars_spin.value()):
            row = QHBoxLayout()
            edit = QLineEdit()
            edit.setPlaceholderText(f"Diameter for bar {i+1}")
            qty = QSpinBox()
            qty.setMinimum(1)
            qty.setMaximum(1000)
            qty.setValue(1)
            row.addWidget(edit)
            row.addWidget(QLabel("Qty:"))
            row.addWidget(qty)
            container = QWidget()
            container.setLayout(row)
            self.bar_diam_layout.addWidget(container)
            self.bar_diam_edits.append(edit)
            self.bar_qty_spins.append(qty)

    def get_inputs(self):
        try:
            type_stirrup = str(self.type_spin.value())
            beam_num = self.beam_num_edit.text().strip()
            clear_span = float(self.clear_span_edit.text())
            beam_width = float(self.beam_width_edit.text())
            beam_depth = float(self.beam_depth_edit.text())
            spacing_type = self.spacing_type_spin.value()
            diam_qty = []
            for edit, qty in zip(self.bar_diam_edits, self.bar_qty_spins):
                if edit.text().strip():
                    diam_qty.append((float(edit.text()), qty.value()))
            if spacing_type == 1:
                spacing = float(self.spacing_edit.text())
                return dict(type_stirrup=type_stirrup, beam_num=beam_num, clear_span=clear_span, beam_width=beam_width, beam_depth=beam_depth, diam_qty=diam_qty, spacing_type='uniform', spacing=spacing)
            else:
                l4_spacing = float(self.l4_spacing_edit.text())
                l2_spacing = float(self.l2_spacing_edit.text())
                return dict(type_stirrup=type_stirrup, beam_num=beam_num, clear_span=clear_span, beam_width=beam_width, beam_depth=beam_depth, diam_qty=diam_qty, spacing_type='diff', l4_spacing=l4_spacing, l2_spacing=l2_spacing)
        except Exception:
            return None

class SlabInput(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()
        self.slab_type_spin = QSpinBox()
        self.slab_type_spin.setMinimum(1)
        self.slab_type_spin.setMaximum(2)
        self.slab_type_spin.setValue(1)
        self.slab_type_spin.setDisabled(True)
        self.x_edit = QLineEdit()
        self.y_edit = QLineEdit()
        self.a_edit = QLineEdit()
        self.b_edit = QLineEdit()
        self.beam_width1_edit = QLineEdit()
        self.beam_width2_edit = QLineEdit()
        self.spacing_mainBar_edit = QLineEdit()
        self.spacing_distBar_edit = QLineEdit()
        self.num_bars_spin = QSpinBox()
        self.num_bars_spin.setMinimum(1)
        self.num_bars_spin.setMaximum(20)
        self.bar_diam_edits = []
        self.bar_qty_spins = []
        self.bar_diam_layout = QVBoxLayout()
        self.bar_diam_widget = QWidget()
        self.bar_diam_widget.setLayout(self.bar_diam_layout)

        form.addRow("Slab Type (1: One-way):", self.slab_type_spin)
        form.addRow("Breadth x (mm):", self.x_edit)
        form.addRow("Length y (mm):", self.y_edit)
        form.addRow("Adjacent span a (mm):", self.a_edit)
        form.addRow("Adjacent span b (mm):", self.b_edit)
        form.addRow("Beam Width 1 (mm):", self.beam_width1_edit)
        form.addRow("Beam Width 2 (mm):", self.beam_width2_edit)
        form.addRow("Spacing Main Bars (mm):", self.spacing_mainBar_edit)
        form.addRow("Spacing Dist Bars (mm):", self.spacing_distBar_edit)
        form.addRow("Number of Bar Diameters:", self.num_bars_spin)
        layout.addLayout(form)
        layout.addWidget(QLabel("Bar Diameters (mm) and Quantities:"))
        layout.addWidget(self.bar_diam_widget)
        layout.addStretch()
        self.setLayout(layout)
        self.num_bars_spin.valueChanged.connect(self.update_bar_diam_inputs)
        self.update_bar_diam_inputs()

    def update_bar_diam_inputs(self):
        for i in reversed(range(self.bar_diam_layout.count())):
            widget = self.bar_diam_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.bar_diam_edits = []
        self.bar_qty_spins = []
        for i in range(self.num_bars_spin.value()):
            row = QHBoxLayout()
            edit = QLineEdit()
            edit.setPlaceholderText(f"Diameter for bar {i+1}")
            qty = QSpinBox()
            qty.setMinimum(1)
            qty.setMaximum(1000)
            qty.setValue(1)
            row.addWidget(edit)
            row.addWidget(QLabel("Qty:"))
            row.addWidget(qty)
            container = QWidget()
            container.setLayout(row)
            self.bar_diam_layout.addWidget(container)
            self.bar_diam_edits.append(edit)
            self.bar_qty_spins.append(qty)

    def get_inputs(self):
        try:
            x = float(self.x_edit.text())
            y = float(self.y_edit.text())
            a = float(self.a_edit.text())
            b = float(self.b_edit.text())
            beam_width1 = float(self.beam_width1_edit.text())
            beam_width2 = float(self.beam_width2_edit.text())
            spacing_mainBar = float(self.spacing_mainBar_edit.text())
            spacing_distBar = float(self.spacing_distBar_edit.text())
            diam_qty = []
            for edit, qty in zip(self.bar_diam_edits, self.bar_qty_spins):
                if edit.text().strip():
                    diam_qty.append((float(edit.text()), qty.value()))
            return dict(x=x, y=y, a=a, b=b, beam_width1=beam_width1, beam_width2=beam_width2, spacing_mainBar=spacing_mainBar, spacing_distBar=spacing_distBar, diam_qty=diam_qty)
        except Exception:
            return None

class CantileverInput(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()
        self.extended_checkbox = QCheckBox("Does it extend up to dead-end?")
        self.full_span_edit = QLineEdit()
        self.inner_span_edit = QLineEdit()
        self.canti_span_edit = QLineEdit()
        self.beam_num_edit = QLineEdit()
        self.num_bars_spin = QSpinBox()
        self.num_bars_spin.setMinimum(1)
        self.num_bars_spin.setMaximum(20)
        self.bar_diam_edits = []
        self.bar_qty_spins = []
        self.bar_diam_layout = QVBoxLayout()
        self.bar_diam_widget = QWidget()
        self.bar_diam_widget.setLayout(self.bar_diam_layout)
        form.addRow(self.extended_checkbox)
        form.addRow("Full Span (mm):", self.full_span_edit)
        form.addRow("Inner Span (mm):", self.inner_span_edit)
        form.addRow("Cantilever Span (mm):", self.canti_span_edit)
        form.addRow("Beam Number:", self.beam_num_edit)
        form.addRow("Number of Bar Diameters:", self.num_bars_spin)
        layout.addLayout(form)
        layout.addWidget(QLabel("Bar Diameters (mm) and Quantities:"))
        layout.addWidget(self.bar_diam_widget)
        layout.addStretch()
        self.setLayout(layout)
        self.num_bars_spin.valueChanged.connect(self.update_bar_diam_inputs)
        self.extended_checkbox.stateChanged.connect(self.update_extended_fields)
        self.update_bar_diam_inputs()
        self.update_extended_fields()

    def update_bar_diam_inputs(self):
        for i in reversed(range(self.bar_diam_layout.count())):
            widget = self.bar_diam_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.bar_diam_edits = []
        self.bar_qty_spins = []
        for i in range(self.num_bars_spin.value()):
            row = QHBoxLayout()
            edit = QLineEdit()
            edit.setPlaceholderText(f"Diameter for bar {i+1}")
            qty = QSpinBox()
            qty.setMinimum(1)
            qty.setMaximum(1000)
            qty.setValue(1)
            row.addWidget(edit)
            row.addWidget(QLabel("Qty:"))
            row.addWidget(qty)
            container = QWidget()
            container.setLayout(row)
            self.bar_diam_layout.addWidget(container)
            self.bar_diam_edits.append(edit)
            self.bar_qty_spins.append(qty)

    def update_extended_fields(self):
        if self.extended_checkbox.isChecked():
            self.full_span_edit.show()
            self.inner_span_edit.hide()
            self.canti_span_edit.hide()
        else:
            self.full_span_edit.hide()
            self.inner_span_edit.show()
            self.canti_span_edit.show()

    def get_inputs(self):
        try:
            extended = self.extended_checkbox.isChecked()
            full_span = float(self.full_span_edit.text()) if self.full_span_edit.text().strip() else 0
            inner_span = float(self.inner_span_edit.text()) if self.inner_span_edit.text().strip() else 0
            canti_span = float(self.canti_span_edit.text()) if self.canti_span_edit.text().strip() else 0
            beam_num = self.beam_num_edit.text().strip()
            diam_qty = []
            for edit, qty in zip(self.bar_diam_edits, self.bar_qty_spins):
                if edit.text().strip():
                    diam_qty.append((float(edit.text()), qty.value()))
            return extended, full_span, inner_span, canti_span, beam_num, diam_qty
        except Exception:
            return None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cutting Length Calculator (GUI)")
        self.resize(900, 600)
        self.results = []  # Store results as list of dicts
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Sidebar/Menu
        self.menu_list = QListWidget()
        self.menu_list.addItems([
            "Top Steel", "Bottom Steel", "Cantilever Top Steel", "Stirrups", "Slab"
        ])
        self.menu_list.setFixedWidth(180)
        self.menu_list.setCurrentRow(0)
        self.menu_list.currentRowChanged.connect(self.switch_input_area)
        main_layout.addWidget(self.menu_list)

        # Central area: dynamic input + results
        center_layout = QVBoxLayout()
        main_layout.addLayout(center_layout)

        # Dynamic input area
        self.input_stack = QStackedWidget()
        self.top_steel_input = TopSteelInput()
        self.bottom_steel_input = BottomSteelInput()
        self.input_stack.addWidget(self.top_steel_input)
        self.input_stack.addWidget(self.bottom_steel_input)
        # Placeholders for other flows
        self.stirrups_input = StirrupsInput()
        self.slab_input = SlabInput()
        self.cantilever_input = CantileverInput()
        self.input_stack.addWidget(self.stirrups_input)
        self.input_stack.addWidget(self.slab_input)
        self.input_stack.insertWidget(2, self.cantilever_input)
        center_layout.addWidget(self.input_stack)

        # Results Table
        self.results_table = QTableWidget(0, 7)
        """
        self.results_table.setHorizontalHeaderLabels([
            "Beam Type", "Beam No.", "Bend len 1", "Bend len 2", "Quantity", "Cutting-length (per bar)", "Weight"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        """
        center_layout.addWidget(QLabel("Results so far:"))
        center_layout.addWidget(self.results_table)

        # PDF filename input and buttons
        bottom_layout = QHBoxLayout()
        center_layout.addLayout(bottom_layout)
        bottom_layout.addWidget(QLabel("PDF Filename:"))
        self.pdf_filename_edit = QLineEdit("cutting_length_results.pdf")
        bottom_layout.addWidget(self.pdf_filename_edit)
        self.add_result_btn = QPushButton("Add/Save Result")
        self.generate_pdf_btn = QPushButton("Generate PDF")
        self.save_exit_btn = QPushButton("Save & Exit")
        bottom_layout.addWidget(self.add_result_btn)
        bottom_layout.addWidget(self.generate_pdf_btn)
        bottom_layout.addWidget(self.save_exit_btn)

        # Connect button signals
        self.add_result_btn.clicked.connect(self.add_result)
        self.generate_pdf_btn.clicked.connect(self.generate_pdf)
        self.save_exit_btn.clicked.connect(self.save_and_exit)

    def switch_input_area(self, index):
        self.input_stack.setCurrentIndex(index)



    def add_result_to_table(self, _):
        """
        Refresh the results table, grouped by type first, then by diameter.
        """
        def get_beam_number(res):
            """Helper function to get beam number from result dict with various key names"""
            return str(res.get("beam no.", "") or res.get("beam_num", "") or res.get("beam num", "") or "")
        
        self.results_table.setRowCount(0)
        
        # Group results by type first
        type_groups = defaultdict(list)
        for res in self.results:
            if res.get("type", "").endswith("legged"):
                type_groups["Stirrups"].append(res)
            elif res.get("type") == "Top Steel":
                type_groups["Top Steel"].append(res)
            elif res.get("type") == "Bottom Steel":
                type_groups["Bottom Steel"].append(res)
            elif res.get("type") == "Cantilever":
                type_groups["Cantilever"].append(res)
            elif res.get("type") == "One-way":
                type_groups["Slab"].append(res)
        
        # Set default headers (will be updated per section)
        default_headers = ["Beam Type", "Beam No.", "Bend len 1", "Bend len 2", "Quantity", "CL(per bar)", "Weight"]
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels(default_headers)
        
        # Process each type group
        for type_name in sorted(type_groups.keys()):
            results_of_type = type_groups[type_name]
            
            # Add main type header
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            type_header = QTableWidgetItem(f"═══════════ {type_name.upper()} ═══════════")
            type_header.setFlags(type_header.flags() & ~Qt.ItemFlag.ItemIsEditable)
            #type_header.setBackground(QColor(70, 130, 180))  # Steel blue
            #type_header.setForeground(QColor(255, 255, 255))  # White text
            self.results_table.setItem(row, 0, type_header)
            self.results_table.setSpan(row, 0, 1, self.results_table.columnCount())
            
            # Add headers row for this type
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            
            if type_name == "Stirrups":
                headers = ["Type", "Beam No.", "Spacing Type", "No. of Stirrups", "Cutting Length", "Total Weight", "Diameter"]
            elif type_name in ["Top Steel", "Bottom Steel"]:
                headers = ["Type", "Beam No.", "Bend len 1", "Bend len 2", "Quantity", "Length per bar", "Weight"]
            elif type_name == "Cantilever":
                headers = ["Type", "Beam No.", "-", "-", "Quantity", "Length per bar", "Weight"]
            elif type_name == "Slab":
                headers = ["Type", "Diameter", "-", "-", "Quantity", "Main bars", "Total Weight"]
            
            # Set headers for this section
            for col, header in enumerate(headers):
                header_item = QTableWidgetItem(header)
                header_item.setFlags(header_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                #header_item.setBackground(QColor(200, 200, 200))  # Light gray
                self.results_table.setItem(row, col, header_item)
            
            # Group by diameter within this type
            diameter_groups = defaultdict(list)
            for res in results_of_type:
                if 'd' in res:
                    diameter_groups[res["d"]].append(res)
                elif 'diameter' in res:
                    diameter_groups[res["diameter"]].append(res)
                else:
                    diameter_groups["N/A"].append(res)
            
            # Process each diameter group
            for diameter in sorted(diameter_groups.keys(), key=lambda x: float(x) if str(x).replace('.','').isdigit() else 0):
                # Add diameter subheader
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                diameter_header = QTableWidgetItem(f"    ○ Bar Diameter: {diameter} mm")
                diameter_header.setFlags(diameter_header.flags() & ~Qt.ItemFlag.ItemIsEditable)
                #diameter_header.setBackground(QColor(240, 240, 240))  # Very light gray
                self.results_table.setItem(row, 0, diameter_header)
                self.results_table.setSpan(row, 0, 1, self.results_table.columnCount())
                
                # Add data rows for this diameter
                for res in diameter_groups[diameter]:
                    row = self.results_table.rowCount()
                    self.results_table.insertRow(row)
                    
                    if type_name == "Stirrups":
                        if res.get("spacing type") == "uniform":
                            self.results_table.setItem(row, 0, QTableWidgetItem(str(res.get("type", ""))))
                            self.results_table.setItem(row, 1, QTableWidgetItem(get_beam_number(res)))
                            self.results_table.setItem(row, 2, QTableWidgetItem("Uniform"))
                            self.results_table.setItem(row, 3, QTableWidgetItem(str(res.get("num_stirrups", ""))))
                            self.results_table.setItem(row, 4, QTableWidgetItem(str(res.get("cutting_len", ""))))
                            self.results_table.setItem(row, 5, QTableWidgetItem(str(res.get("total_weight", ""))))
                            self.results_table.setItem(row, 6, QTableWidgetItem(str(res.get("d", ""))))
                        else:  # different spacing
                            self.results_table.setItem(row, 0, QTableWidgetItem(str(res.get("type", ""))))
                            self.results_table.setItem(row, 1, QTableWidgetItem(get_beam_number(res)))
                            self.results_table.setItem(row, 2, QTableWidgetItem("L/4 & L/2"))
                            self.results_table.setItem(row, 3, QTableWidgetItem(f"L/4: {res.get('num_l/4_stirrups', '')}, L/2: {res.get('num_l/2_stirrups', '')}"))
                            self.results_table.setItem(row, 4, QTableWidgetItem(str(res.get("cutting_len", ""))))
                            self.results_table.setItem(row, 5, QTableWidgetItem(str(res.get("total_weight", ""))))
                            self.results_table.setItem(row, 6, QTableWidgetItem(str(res.get("d", ""))))
                    
                    elif type_name in ["Top Steel", "Bottom Steel"]:
                        self.results_table.setItem(row, 0, QTableWidgetItem(str(res.get("type", ""))))
                        self.results_table.setItem(row, 1, QTableWidgetItem(get_beam_number(res)))
                        self.results_table.setItem(row, 2, QTableWidgetItem(str(res.get("bend length1", ""))))
                        self.results_table.setItem(row, 3, QTableWidgetItem(str(res.get("bend length2", ""))))
                        self.results_table.setItem(row, 4, QTableWidgetItem(str(res.get("quantity", ""))))
                        self.results_table.setItem(row, 5, QTableWidgetItem(str(res.get("length per bar", ""))))
                        self.results_table.setItem(row, 6, QTableWidgetItem(str(res.get("weight", ""))))
                    
                    elif type_name == "Cantilever":
                        self.results_table.setItem(row, 0, QTableWidgetItem(str(res.get("type", ""))))
                        self.results_table.setItem(row, 1, QTableWidgetItem(get_beam_number(res)))
                        self.results_table.setItem(row, 2, QTableWidgetItem("-"))
                        self.results_table.setItem(row, 3, QTableWidgetItem("-"))
                        self.results_table.setItem(row, 4, QTableWidgetItem(str(res.get("quantity", ""))))
                        self.results_table.setItem(row, 5, QTableWidgetItem(str(res.get("length per bar", ""))))
                        self.results_table.setItem(row, 6, QTableWidgetItem(str(res.get("weight", ""))))
                    
                    elif type_name == "Slab":
                        self.results_table.setItem(row, 0, QTableWidgetItem(str(res.get("type", ""))))
                        self.results_table.setItem(row, 1, QTableWidgetItem(str(res.get("diameter", ""))))
                        self.results_table.setItem(row, 2, QTableWidgetItem("-"))
                        self.results_table.setItem(row, 3, QTableWidgetItem("-"))
                        self.results_table.setItem(row, 4, QTableWidgetItem(str(res.get("quantity", ""))))
                        self.results_table.setItem(row, 5, QTableWidgetItem(str(res.get("main bars", ""))))
                        self.results_table.setItem(row, 6, QTableWidgetItem(str(res.get("total weight", ""))))
            
            # Add spacing between type sections
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            spacer_item = QTableWidgetItem("")
            spacer_item.setFlags(spacer_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.results_table.setItem(row, 0, spacer_item)
            self.results_table.setSpan(row, 0, 1, self.results_table.columnCount())

    def add_result(self):
        # Top Steel
        if self.menu_list.currentRow() == 0:
            inputs = self.top_steel_input.get_inputs()
            if not inputs:
                QMessageBox.warning(self, "Input Error", "Please fill all fields with valid numbers.")
                return
            beam_num, extended, end_support, num_supports, clear_span, es_width1, es_width2,beam_depth1, beam_depth2, diam_qty = inputs
            from cuttingLen import flow1, flow2, bend_length
            for d, qty in diam_qty:
                if extended:
                    bl1 = bend_length(d, es_width1, beam_depth1)
                    bl2 = bend_length(d, es_width2, beam_depth2)
                    length = flow1(d, clear_span, es_width1, es_width2, bl1, bl2)
                else:
                    if end_support:
                        if num_supports == 2:
                            bl1 = bend_length(d, es_width1, beam_depth1)
                            bl2 = bend_length(d, es_width2, beam_depth2)
                            length = flow1(d, clear_span, es_width1, es_width2, bl1, bl2)
                        else:
                            bl1 = bend_length(d, es_width1, beam_depth1)
                            bl2 = 0
                            length = flow2(d, clear_span, es_width1, 0, bl1)
                    else:
                        bl1 = bend_length(d, es_width1, beam_depth1)
                        bl2 = bend_length(d, es_width2, beam_depth2)
                        length = flow1(d, clear_span, es_width1, es_width2, bl1, bl2)
                weight = ((d*d)/162)* qty * (length)/1000
                result = {
                    "type": "Top Steel",
                    "beam no.": beam_num,
                    "bend length1": bl1,
                    "bend length2": bl2,
                    "quantity": qty,
                    "length per bar": length,
                    "d": d,
                    "weight": weight
                }
                self.results.append(result)
            self.add_result_to_table(None)
            QMessageBox.information(self, "Success", "Result(s) added.")
        # Bottom Steel
        elif self.menu_list.currentRow() == 1:
            inputs = self.bottom_steel_input.get_inputs()
            if not inputs:
                QMessageBox.warning(self, "Input Error", "Please fill all fields with valid numbers.")
                return
            beam_num, extended, end_support, num_supports, clear_span, es_width1, es_width2,beam_depth1, beam_depth2, diam_qty = inputs
            from cuttingLen import flow1, flow2, bend_length
            for d, qty in diam_qty:
                if extended:
                    bl1 = bend_length(d, es_width1, beam_depth1)
                    bl2 = bend_length(d, es_width2, beam_depth2)
                    length = flow1(d, clear_span, es_width1, es_width2, bl1, bl2)
                else:
                    if end_support:
                        if num_supports == 2:
                            bl1 = bend_length(d, es_width1, beam_depth1)
                            bl2 = bend_length(d, es_width2, beam_depth2)
                            length = flow1(d, clear_span, es_width1, es_width2, bl1, bl2)
                        else:
                            bl1 = bend_length(d, es_width1, beam_depth1)
                            bl2 = 0
                            length = flow2(d, clear_span, es_width1, 0, bl1)
                    else:
                        bl1 = bend_length(d, es_width1, beam_depth1)
                        bl2 = bend_length(d, es_width2, beam_depth2)
                        length = flow1(d, clear_span, es_width1, es_width2, bl1, bl2)
                weight = ((d*d)/162)* qty * (length)/1000
                result = {
                    "type": "Bottom Steel",
                    "beam no.": beam_num,
                    "bend length1": bl1,
                    "bend length2": bl2,
                    "quantity": qty,
                    "length per bar": length,
                    "d": d,
                    "weight": weight
                }
                self.results.append(result)
            self.add_result_to_table(None)
            QMessageBox.information(self, "Success", "Result(s) added.")
        # Cantilever Top Steel
        elif self.menu_list.currentRow() == 2:
            inputs = self.cantilever_input.get_inputs()
            if not inputs:
                QMessageBox.warning(self, "Input Error", "Please fill all fields with valid numbers.")
                return
            extended, full_span, inner_span, canti_span, beam_num, diam_qty = inputs
            for d, qty in diam_qty:
                if extended:
                    length = full_span + 300
                else:
                    from cuttingLen import flow4
                    length = flow4(inner_span, canti_span)
                weight = ((d*d)/162) * (length)/1000 * qty 
                result = {
                    "type": "Cantilever",
                    "beam no.": beam_num,
                    "d": d,
                    "quantity": qty,
                    "length per bar": length,
                    "weight": weight
                }
                self.results.append(result)
            self.add_result_to_table(None)
            QMessageBox.information(self, "Success", "Cantilever result(s) added.")
        # Stirrups
        elif self.menu_list.currentRow() == 3:
            inputs = self.stirrups_input.get_inputs()
            if not inputs:
                QMessageBox.warning(self, "Input Error", "Please fill all fields with valid numbers.")
                return
            
            type_stirrup = inputs['type_stirrup']
            beam_num = inputs['beam_num']
            clear_span = float(inputs['clear_span'])
            beam_width = float(inputs['beam_width'])
            beam_depth = float(inputs['beam_depth'])
            diam_qty = inputs['diam_qty']
            
            stirrups_data = []
            
            for d, qty in diam_qty:
                if type_stirrup == "1":
                    a = beam_width 
                    b = beam_depth 
                    cutting_len = 2*a + 2*b + 20*d - 6*d - 80
                    weight_bar = ((d*d)/162)*cutting_len
                    
                    if inputs['spacing_type'] == 'uniform':
                        spacing = float(inputs['spacing'])
                        same_spacing(clear_span, spacing, weight_bar, stirrups_data, type_stirrup, beam_num, cutting_len, d)
                    else:
                        l4_spacing = float(inputs['l4_spacing'])
                        l2_spacing = float(inputs['l2_spacing'])
                        different_spacing(l4_spacing, clear_span, l2_spacing, weight_bar, stirrups_data, type_stirrup, d, beam_num, cutting_len)
                
                elif type_stirrup == "2":
                    a = beam_depth 
                    b = beam_width 
                    cutting_len = math.floor(4*a + 2*b + 2*(b/3) + 16*d - 80)
                    weight_bar = math.floor((d*d/162)*cutting_len)
                    
                    if inputs['spacing_type'] == 'uniform':
                        spacing = float(inputs['spacing'])
                        same_spacing(clear_span, spacing, weight_bar, stirrups_data, type_stirrup, beam_num, cutting_len, d)
                    else:
                        l4_spacing = float(inputs['l4_spacing'])
                        l2_spacing = float(inputs['l2_spacing'])
                        different_spacing(l4_spacing, clear_span, l2_spacing, weight_bar, stirrups_data, type_stirrup, d, beam_num, cutting_len)
                
                elif type_stirrup == "3":
                    a = beam_depth 
                    b = beam_width 
                    cutting_len = math.floor(6*a + 2*b + 4*b/5 + 24*d - 80)
                    weight_bar = math.floor((d*d/162)*cutting_len)
                    
                    if inputs['spacing_type'] == 'uniform':
                        spacing = float(inputs['spacing'])
                        same_spacing(clear_span, spacing, weight_bar, stirrups_data, type_stirrup, beam_num, cutting_len, d)
                    else:
                        l4_spacing = float(inputs['l4_spacing'])
                        l2_spacing = float(inputs['l2_spacing'])
                        different_spacing(l4_spacing, clear_span, l2_spacing, weight_bar, stirrups_data, type_stirrup, d, beam_num, cutting_len)
            
            # Add all stirrup results to main results
            self.results.extend(stirrups_data)
            self.add_result_to_table(None)
            QMessageBox.information(self, "Success", "Stirrups result added.")
        # Slab
        elif self.menu_list.currentRow() == 4:
            inputs = self.slab_input.get_inputs()
            if not inputs:
                QMessageBox.warning(self, "Input Error", "Please fill all fields with valid numbers.")
                return
            from math import floor
            x = inputs['x']
            y = inputs['y']
            a = inputs['a']
            b = inputs['b']
            beam_width1 = inputs['beam_width1']
            beam_width2 = inputs['beam_width2']
            spacing_mainBar = inputs['spacing_mainBar']
            spacing_distBar = inputs['spacing_distBar']
            diam_qty = inputs['diam_qty']
            for d, qty in diam_qty:
                num_main_bars = floor((y / spacing_mainBar) + 1) * qty
                num_dist_bars = floor((x / spacing_distBar) + 1) * qty
                l1 = ((x + beam_width1 + beam_width2 + a / 4)/1000)
                l2 = ((x + beam_width1 + beam_width2 + b / 4)/1000)
                weight1 = floor((num_main_bars / 2) * l1 * (d*d)/162 )
                weight2 = floor((num_main_bars - num_main_bars / 2) * l2 *(d*d)/162 )
                total_weight = weight1 + weight2
                result = {
                    "type": "One-way",
                    "diameter": d,
                    "main bars": num_main_bars,
                    "dist bars": num_dist_bars,
                    "cutting len1": l1,
                    "cutting len2": l2,
                    "total weight": total_weight,
                    "quantity": qty
                }
                self.results.append(result)
            self.add_result_to_table(None)
            QMessageBox.information(self, "Success", "Slab result added.")
        else:
            QMessageBox.information(self, "Info", "This flow is not implemented yet.")

    def generate_pdf(self):
        # Get filename and ensure pdfs directory exists
        filename = self.pdf_filename_edit.text().strip()
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
        pdf_dir = os.path.join(os.getcwd(), 'pdfs')
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, filename)

        # Prepare CSV filename and directory
        csv_filename = filename.replace('.pdf', '.csv')
        csv_path = os.path.join(pdf_dir, csv_filename)

        # Prepare data for PDF table and CSV
        headers = ["Beam Type", "Beam No.", "Bend len 1", "Bend len 2", "Quantity", "Cutting-length (per bar)", "Weight(kg/m)"]
        data = [headers]
        grouped = defaultdict(list)
        for res in self.results:
            if 'd' in res:
                grouped[res["d"]].append(res)
            elif 'diameter' in res:
                grouped[res["diameter"].__str__()].append(res)
            else:
                grouped[res["type"]].append(res)
        for key in sorted(grouped.keys(), key=lambda x: str(x)):
            # Add a header row for each group
            data.append([f"Bar Diameter: {key} mm", '', '', '', '', '', ''])
            for res in grouped[key]:
                # For Cantilever
                if res.get("type") == "Cantilever":
                    row = [
                        str(res.get("type", "")),
                        str(res.get("beam no.", "")),
                        "-", "-",
                        str(res.get("quantity", "")),
                        str(res.get("length per bar", "")),
                        str(res.get("weight", "")),
                    ]
                # For stirrups
                elif res.get("spacing type") == "uniform":
                    row = [
                        str(res.get("type", "")),
                        str(res.get("beam no.", "")),
                        "-", "-",
                        str(res.get("quantity", "")),
                        str(res.get("num_stirrups", "")),
                        str(res.get("total_weight", "")),
                    ]
                # For Top Steel
                elif res.get("type") == "Top Steel":
                    row = [
                        str(res.get("type", "")),
                        str(res.get("beam no.", "")),
                        str(res.get("bend length1", "")),
                        str(res.get("bend length2", "")),
                        str(res.get("quantity", "")),
                        str(res.get("length per bar", "")),
                        str(res.get("weight", "")),
                    ]
                # For Bottom Steel
                elif res.get("type") == "Bottom Steel":
                    row = [
                        str(res.get("type", "")),
                        str(res.get("beam no.", "")),
                        str(res.get("bend length1", "")),
                        str(res.get("bend length2", "")),
                        str(res.get("quantity", "")),
                        str(res.get("length per bar", "")),
                        str(res.get("weight", "")),
                    ]
                # For Slab
                elif res.get("type") == "One-way":
                    row = [
                        str(res.get("type", "")),
                        str(res.get("diameter", "")),
                        "-", "-",
                        str(res.get("quantity", "")),
                        str(res.get("main bars", "")),
                        str(res.get("total weight", "")),
                    ]
                else:
                    row = [str(res.get(h, "")) for h in headers]
                data.append(row)
        # Generate PDF
        try:
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            elements.append(Paragraph("Cutting Length Results", styles['Title']))
            elements.append(Spacer(1, 12))
            table = Table(data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.black),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(table)
            doc.build(elements)
            pdf_success = True
            pdf_error = None
        except Exception as e:
            pdf_success = False
            pdf_error = str(e)
        # Generate CSV
        try:
            import csv
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(data)
            csv_success = True
            csv_error = None
        except Exception as e:
            csv_success = False
            csv_error = str(e)
        # Show appropriate message based on results
        if pdf_success and csv_success:
            QMessageBox.information(self, "Success", f"PDF saved to {pdf_path}\nCSV saved to {csv_path}")
        elif pdf_success and not csv_success:
            QMessageBox.warning(self, "Partial Success", f"PDF saved to {pdf_path}\nCSV failed: {csv_error}")
        elif not pdf_success and csv_success:
            QMessageBox.warning(self, "Partial Success", f"CSV saved to {csv_path}\nPDF failed: {pdf_error}")
        else:
            QMessageBox.critical(self, "Error", f"Both exports failed:\nPDF: {pdf_error}\nCSV: {csv_error}")
    def save_and_exit(self):
        QMessageBox.information(self, "Info", "Save & Exit functionality to be implemented.")
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 