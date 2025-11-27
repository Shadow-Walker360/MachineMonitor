from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

def create_card(title, on_click_func, threshold=None):
    """
    Creates a dashboard card.

    threshold: optional dict like {'value': 85, 'type': 'cpu', 'color': 'red'}
    """
    card = QWidget()
    card.setFixedSize(200, 120)
    layout = QVBoxLayout()
    
    label = QLabel(title)
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet("font-size: 16px; font-weight: bold;")
    
    value_label = QLabel("N/A")
    value_label.setAlignment(Qt.AlignCenter)
    value_label.setStyleSheet("font-size: 14px;")

    button = QPushButton("View")
    button.clicked.connect(on_click_func)
    
    layout.addWidget(label)
    layout.addWidget(value_label)
    layout.addWidget(button)
    card.setLayout(layout)

    # Style
    card.setStyleSheet("background-color: #f0f0f0; border-radius: 10px; padding: 10px;")
    
    # Return both card and value_label to update dynamically
    return card, value_label
