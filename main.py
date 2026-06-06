import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QDialog, QTableWidget,
    QTableWidgetItem, QHeaderView, QScrollArea, QMessageBox, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QFont, QLinearGradient, QBrush, QPen
import db
import atm

db.connect()

# ══════════════════════════════════════════════════════════════
#  DESIGN TOKENS  — Premium light banking palette
# ══════════════════════════════════════════════════════════════
BG          = "#F0F2F7"   # Cool light gray page bg
SURFACE     = "#FFFFFF"   # Pure white surfaces
CARD        = "#FFFFFF"
BORDER      = "#E2E6EE"
BORDER_MED  = "#C9D0DE"

# Brand blues
NAVY        = "#0B2545"   # Deep navy — headings / logo
BLUE        = "#1558C0"   # Primary action
BLUE_H      = "#1048A8"   # Hover
BLUE_LIGHT  = "#EBF0FB"   # Tint bg for tiles

# Accents
TEAL        = "#0D7377"   # Secondary accent
GOLD        = "#B8881A"   # Premium gold detail

# Text
T1          = "#0D1B2E"   # Primary — near black
T2          = "#4A5568"   # Secondary
T3          = "#8C9BB0"   # Muted / hints

# Semantic
SUCCESS     = "#0A7C4E"
SUCCESS_BG  = "#E6F5EE"
SUCCESS_BD  = "#A3D9BE"
DANGER      = "#C0392B"
DANGER_BG   = "#FDECEC"
DANGER_BD   = "#F1ABAB"

WHITE = "#FFFFFF"

def qc(h): return QColor(h)

def shadow(widget, blur=18, opacity=0.10, color="#001133", dx=0, dy=4):
    fx = QGraphicsDropShadowEffect()
    fx.setBlurRadius(blur)
    fx.setOffset(dx, dy)
    c = QColor(color)
    c.setAlphaF(opacity)
    fx.setColor(c)
    widget.setGraphicsEffect(fx)
    return fx


# ══════════════════════════════════════════════════════════════
#  BASE WINDOW
# ══════════════════════════════════════════════════════════════
class BaseWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"QMainWindow {{ background:{BG}; }}")


# ══════════════════════════════════════════════════════════════
#  INPUT FIELD
# ══════════════════════════════════════════════════════════════
class InputField(QLineEdit):
    def __init__(self, placeholder="", password=False, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setFixedHeight(46)
        if password:
            self.setEchoMode(QLineEdit.EchoMode.Password)
        self.setStyleSheet(f"""
            QLineEdit {{
                background: {SURFACE};
                border: 1.5px solid {BORDER_MED};
                border-radius: 8px;
                padding: 0 14px 0 16px;
                font-size: 14px;
                color: {T1};
            }}
            QLineEdit:hover {{
                border-color: #9AAAC0;
            }}
            QLineEdit:focus {{
                border: 2px solid {BLUE};
                background: #FAFCFF;
            }}
        """)


# ══════════════════════════════════════════════════════════════
#  BUTTONS
# ══════════════════════════════════════════════════════════════
class PrimaryBtn(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(46)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background: {BLUE};
                color: {WHITE};
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            QPushButton:hover  {{ background: {BLUE_H}; }}
            QPushButton:pressed {{ background: #0D3A8A; }}
            QPushButton:disabled {{
                background: {BORDER};
                color: {T3};
            }}
        """)


class GhostBtn(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(46)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background: {SURFACE};
                color: {T2};
                border: 1.5px solid {BORDER_MED};
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {BLUE_LIGHT};
                color: {BLUE};
                border-color: {BLUE};
            }}
        """)


class DangerOutlineBtn(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(90, 34)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background: {DANGER_BG};
                color: {DANGER};
                border: 1px solid {DANGER_BD};
                border-radius: 7px;
                font-size: 12px;
                font-weight: bold;
                letter-spacing: 0.3px;
            }}
            QPushButton:hover {{
                background: #FDDCDC;
                border-color: {DANGER};
            }}
        """)


# ══════════════════════════════════════════════════════════════
#  MICRO COMPONENTS
# ══════════════════════════════════════════════════════════════
class ErrLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(0)
        self.setStyleSheet(f"color:{DANGER}; font-size:11px; padding:3px 2px 0; background:transparent;")

    def show_err(self, msg):
        self.setText("⚠  " + msg)
        self.setFixedHeight(20)

    def clear(self):
        self.setText("")
        self.setFixedHeight(0)


class Divider(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(1)
        self.setStyleSheet(f"background:{BORDER}; border:none;")


class TagLabel(QLabel):
    """Pill-style section tag"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            color: {T3};
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 2px;
            background: transparent;
            padding: 0;
        """)


# ══════════════════════════════════════════════════════════════
#  CARD FRAME
# ══════════════════════════════════════════════════════════════
class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {CARD};
                border: 1px solid {BORDER};
                border-radius: 14px;
            }}
        """)
        shadow(self, blur=20, opacity=0.06, dy=6)


# ══════════════════════════════════════════════════════════════
#  TOAST
# ══════════════════════════════════════════════════════════════
class Toast(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(0)
        self._lbl = QLabel(self)
        self._lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.addWidget(self._lbl)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(lambda: self.setFixedHeight(0))

    def show_msg(self, msg, ok=True):
        if ok:
            bg = SUCCESS_BG; bd = SUCCESS_BD; col = SUCCESS
        else:
            bg = DANGER_BG; bd = DANGER_BD; col = DANGER
        self.setStyleSheet(f"QFrame {{ background:{bg}; border-bottom:2px solid {bd}; }}")
        self._lbl.setStyleSheet(f"font-size:12px; font-weight:bold; color:{col}; background:transparent;")
        self._lbl.setText(msg)
        self.setFixedHeight(38)
        self._timer.start(3500)


# ══════════════════════════════════════════════════════════════
#  ACTION TILE
# ══════════════════════════════════════════════════════════════
class Tile(QWidget):
    def __init__(self, icon, label, callback, parent=None):
        super().__init__(parent)
        self.setFixedSize(148, 84)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cb = callback
        self._hover = False

        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(6)
        lay.setContentsMargins(8, 8, 8, 8)

        ic = QLabel(icon)
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ic.setStyleSheet("font-size: 22px; background: transparent;")

        lb = QLabel(label)
        lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lb.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {T2}; background: transparent; letter-spacing: 0.4px;")

        lay.addWidget(ic)
        lay.addWidget(lb)

    def enterEvent(self, e):
        self._hover = True
        self.update()

    def leaveEvent(self, e):
        self._hover = False
        self.update()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._cb()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        r = self.rect().adjusted(1, 1, -1, -1)
        path.addRoundedRect(float(r.x()), float(r.y()), float(r.width()), float(r.height()), 12, 12)
        if self._hover:
            p.fillPath(path, qc(BLUE_LIGHT))
            pen = QPen(qc(BLUE), 1.5)
        else:
            p.fillPath(path, qc(SURFACE))
            pen = QPen(qc(BORDER), 1.0)
        p.setPen(pen)
        p.drawPath(path)
        super().paintEvent(e)


# ══════════════════════════════════════════════════════════════
#  LOGIN WINDOW
# ══════════════════════════════════════════════════════════════
class Login(BaseWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ATM — Secure Login")
        self.setFixedSize(460, 580)
        self._build()

    def _build(self):
        root = QWidget()
        root.setStyleSheet(f"background: {BG};")
        self.setCentralWidget(root)
        vl = QVBoxLayout(root)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(0)

        # ── Top bar ───────────────────────────────────────
        bar = QWidget()
        bar.setFixedHeight(64)
        bar.setStyleSheet(f"""
            background: {SURFACE};
            border-bottom: 1px solid {BORDER};
        """)
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(28, 0, 28, 0)

        logo_row = QHBoxLayout()
        logo_row.setSpacing(0)

        mark = QLabel()
        mark.setFixedSize(32, 32)
        mark.setStyleSheet(f"""
            background: {NAVY};
            border-radius: 8px;
            color: white;
            font-size: 15px;
            font-weight: bold;
            qproperty-alignment: AlignCenter;
        """)
        mark.setText("M")
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)

        brand = QLabel("  ATM")
        brand.setStyleSheet(f"color: {NAVY}; font-size: 16px; font-weight: bold; letter-spacing: 0.5px; background: transparent;")

        logo_row.addWidget(mark)
        logo_row.addWidget(brand)
        bl.addLayout(logo_row)
        bl.addStretch()

        shield = QLabel("🔒  256-bit SSL")
        shield.setStyleSheet(f"color: {T3}; font-size: 11px; background: transparent;")
        bl.addWidget(shield)
        vl.addWidget(bar)

        # ── Body ──────────────────────────────────────────
        body = QWidget()
        body.setStyleSheet(f"background: {BG};")
        bl2 = QVBoxLayout(body)
        bl2.setContentsMargins(40, 36, 40, 36)
        bl2.setSpacing(0)

        card = Card()
        cl = QVBoxLayout(card)
        cl.setContentsMargins(36, 36, 36, 36)
        cl.setSpacing(0)

        # Card header
        h1 = QLabel("Welcome back")
        h1.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {NAVY}; background: transparent;")
        # h2 = QLabel("Sign in to continue to your account")
        # h2.setStyleSheet(f"font-size: 13px; color: {T2}; margin-top: 15px; margin-bottom: 30px; background: transparent;")
        cl.addWidget(h1)
        # cl.addWidget(h2)

        # Account number
        lbl1 = QLabel("ACCOUNT NUMBER")
        lbl1.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {T3}; letter-spacing: 1.5px; margin-bottom: 7px; background: transparent;")
        cl.addWidget(lbl1)
        self.acc = InputField("e.g.  1234567890")
        cl.addWidget(self.acc)
        self.acc_err = ErrLabel()
        cl.addWidget(self.acc_err)

        sp = QWidget(); sp.setFixedHeight(18)
        cl.addWidget(sp)

        # PIN
        lbl2 = QLabel("PIN")
        lbl2.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {T3}; letter-spacing: 1.5px; margin-bottom: 7px; background: transparent;")
        cl.addWidget(lbl2)
        self.pin = InputField("4–6 digit PIN", password=True)
        cl.addWidget(self.pin)
        self.pin_err = ErrLabel()
        cl.addWidget(self.pin_err)

        sp2 = QWidget(); sp2.setFixedHeight(28)
        cl.addWidget(sp2)

        self.btn = PrimaryBtn("SIGN IN")
        cl.addWidget(self.btn)

        sp3 = QWidget(); sp3.setFixedHeight(20)
        cl.addWidget(sp3)

        divrow = QHBoxLayout()
        divrow.addStretch()
        foot = QLabel("Protected by ATM Security  ·  Support: 0800-ATM")
        foot.setStyleSheet(f"font-size: 10px; color: {T3}; background: transparent;")
        foot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(foot)

        bl2.addWidget(card)
        vl.addWidget(body)

        # signals
        self.btn.clicked.connect(self._login)
        self.acc.returnPressed.connect(lambda: self.pin.setFocus())
        self.pin.returnPressed.connect(self._login)
        self.acc.textChanged.connect(self.acc_err.clear)
        self.pin.textChanged.connect(self.pin_err.clear)

    def _login(self):
        acc = self.acc.text().strip()
        pin = self.pin.text().strip()
        ok  = True
        self.acc_err.clear(); self.pin_err.clear()

        if   not acc:             self.acc_err.show_err("Account number is required");        ok=False
        elif not acc.isdigit():   self.acc_err.show_err("Digits only — no spaces or letters"); ok=False
        elif not 4<=len(acc)<=20: self.acc_err.show_err("Must be 4–20 digits");               ok=False

        if   not pin:             self.pin_err.show_err("PIN is required");                   ok=False
        elif not pin.isdigit():   self.pin_err.show_err("Digits only");                       ok=False
        elif not 4<=len(pin)<=6:  self.pin_err.show_err("PIN must be 4–6 digits");            ok=False

        if not ok: return

        self.btn.setEnabled(False)
        self.btn.setText("Verifying…")
        QTimer.singleShot(420, lambda: self._do_login(acc, pin))

    def _do_login(self, acc, pin):
        self.btn.setEnabled(True)
        self.btn.setText("SIGN IN")
        result = atm.login(acc, pin)
        if result == "LOCKED":
            self.pin_err.show_err("Account locked — visit your nearest branch")
        elif result == "INVALID":
            self.pin_err.show_err("Incorrect account number or PIN")
            self.pin.clear()
        else:
            self.dash = Dashboard(result)
            self.dash.show()
            self.close()


# ══════════════════════════════════════════════════════════════
#  BALANCE CARD WIDGET  (gradient painted)
# ══════════════════════════════════════════════════════════════
class BalanceCard(QFrame):
    def __init__(self, acc_no, parent=None):
        super().__init__(parent)
        self.acc_no = acc_no
        self.setFixedHeight(128)
        self.setStyleSheet("QFrame { border-radius: 16px; border: none; }")
        shadow(self, blur=28, opacity=0.18, color="#0B2545", dy=8)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 0, 28, 0)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tag = QLabel("AVAILABLE BALANCE")
        tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tag.setStyleSheet("color: rgba(255,255,255,0.60); font-size: 10px; font-weight: bold; letter-spacing: 2px; background: transparent;")

        bal = atm.get_balance(acc_no)
        self.bal_lbl = QLabel(f"Rs. {bal:,}" if isinstance(bal, (int, float)) else f"Rs. {bal}")
        self.bal_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bal_lbl.setStyleSheet("color: #FFFFFF; font-size: 32px; font-weight: bold; background: transparent; letter-spacing: -0.5px;")

        lay.addSpacing(4)
        lay.addWidget(tag)
        lay.addSpacing(8)
        lay.addWidget(self.bal_lbl)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0.0, qc("#0B2545"))
        grad.setColorAt(0.5, qc("#1558C0"))
        grad.setColorAt(1.0, qc("#0D7377"))
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 16, 16)
        p.fillPath(path, QBrush(grad))
        # subtle pattern overlay
        p.setOpacity(0.06)
        pen = QPen(QColor("#FFFFFF"), 1)
        p.setPen(pen)
        for x in range(-20, self.width() + 20, 32):
            p.drawLine(x, 0, x + self.height(), self.height())
        p.setOpacity(1.0)
        super().paintEvent(e)

    def refresh(self):
        bal = atm.get_balance(self.acc_no)
        self.bal_lbl.setText(f"Rs. {bal:,}" if isinstance(bal, (int, float)) else f"Rs. {bal}")


# ══════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════
class Dashboard(BaseWindow):
    def __init__(self, user):
        super().__init__()
        self.user   = user
        self.acc_no = user[1]
        self.setWindowTitle("ATM — Dashboard")
        self.setFixedSize(560, 560)
        self._build()

    def _build(self):
        root = QWidget()
        root.setStyleSheet(f"background: {BG};")
        self.setCentralWidget(root)
        vl = QVBoxLayout(root)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(0)

        # Toast
        self.toast = Toast()
        vl.addWidget(self.toast)

        # ── Top bar ────────────────────────────────────────
        bar = QWidget()
        bar.setFixedHeight(64)
        bar.setStyleSheet(f"background: {SURFACE}; border-bottom: 1px solid {BORDER};")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(28, 0, 28, 0)

        mark = QLabel()
        mark.setFixedSize(32, 32)
        mark.setText("M")
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mark.setStyleSheet(f"background: {NAVY}; border-radius: 8px; color: white; font-size: 15px; font-weight: bold;")

        brand = QLabel("  ATM")
        brand.setStyleSheet(f"color: {NAVY}; font-size: 16px; font-weight: bold; background: transparent;")

        bl.addWidget(mark)
        bl.addWidget(brand)
        bl.addStretch()



        # # User avatar pill
        # # name_text = str(self.user[0]) if self.user[0] else "User"
        # # initials  = "".join(w[0].upper() for w in name_text.split()[:2]) if name_text else "U"
        # # av = QLabel(initials)
        # av.setFixedSize(34, 34)
        # av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # av.setStyleSheet(f"""
        #     background: {BLUE_LIGHT};
        #     color: {BLUE};
        #     border-radius: 17px;
        #     font-size: 12px;
        #     font-weight: bold;
        # """)
        # nm = QLabel(name_text)
        # nm.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {T1}; background: transparent; margin-right: 14px;")

        # bl.addWidget(av)
        # bl.addSpacing(8)
        # bl.addWidget(nm)

        so = DangerOutlineBtn("Sign Out")
        so.clicked.connect(self._logout)
        bl.addWidget(so)
        vl.addWidget(bar)

        # ── Scroll area ────────────────────────────────────
        sc = QScrollArea()
        sc.setWidgetResizable(True)
        sc.setFrameShape(QFrame.Shape.NoFrame)
        sc.setStyleSheet(f"""
            QScrollArea {{ background: {BG}; border: none; }}
            QScrollBar:vertical {{ background: {BG}; width: 5px; border-radius: 3px; }}
            QScrollBar::handle:vertical {{ background: {BORDER_MED}; border-radius: 3px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)

        inner = QWidget()
        inner.setStyleSheet(f"background: {BG};")
        il = QVBoxLayout(inner)
        il.setContentsMargins(28, 24, 28, 28)
        il.setSpacing(20)

        # Balance card
        self.bal_card = BalanceCard(self.acc_no)
        il.addWidget(self.bal_card)

        # Quick actions header
        actions_header = QHBoxLayout()
        actions_header.addWidget(TagLabel("QUICK ACTIONS"))
        actions_header.addStretch()
        il.addLayout(actions_header)

        # Tiles grid — 3 columns × 2 rows
        tiles_widget = QWidget()
        tiles_widget.setStyleSheet("background: transparent;")
        tl = QHBoxLayout(tiles_widget)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.setSpacing(10)

        actions = [
            ("💰", "Deposit",   self._deposit),
            ("💸", "Withdraw",  self._withdraw),
            ("🔁", "Transfer",  self._transfer),
            ("📊", "Balance",   self._balance),
            ("🧾", "Statement", self._statement),
            ("⚙️",  "Settings",  self._settings),
        ]

        col1 = QVBoxLayout(); col1.setSpacing(10)
        col2 = QVBoxLayout(); col2.setSpacing(10)
        col3 = QVBoxLayout(); col3.setSpacing(10)

        for i, (ic, lb, cb) in enumerate(actions):
            t = Tile(ic, lb, cb)
            [col1, col2, col3][i % 3].addWidget(t)

        tl.addLayout(col1)
        tl.addLayout(col2)
        tl.addLayout(col3)
        il.addWidget(tiles_widget)

        il.addStretch()

        # Footer
        ft = QLabel("🔒  All transactions are encrypted and secured by ATM  ·  0800-ATM")
        ft.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ft.setStyleSheet(f"font-size: 10px; color: {T3}; padding: 6px; background: transparent;")
        il.addWidget(ft)

        sc.setWidget(inner)
        vl.addWidget(sc)

    # ── Actions ───────────────────────────────────────────────
    def _balance(self):
        bal = atm.get_balance(self.acc_no)
        InfoDlg("Current Balance", f"Rs. {bal:,}" if isinstance(bal, (int, float)) else f"Rs. {bal}", self).exec()

    def _deposit(self):
        d = AmountDlg("Deposit Funds", "Deposit", self)
        if d.exec() == QDialog.DialogCode.Accepted:
            amt = d.value()
            atm.deposit(self.acc_no, amt)
            self.bal_card.refresh()
            self.toast.show_msg(f"✓  Rs. {amt:,} deposited successfully")

    def _withdraw(self):
        d = AmountDlg("Withdraw Funds", "Withdraw", self)
        if d.exec() == QDialog.DialogCode.Accepted:
            amt = d.value()
            res = atm.withdraw(self.acc_no, amt)
            if "insufficient" in str(res).lower() or "error" in str(res).lower():
                self.toast.show_msg(f"✗  {res}", ok=False)
            else:
                self.bal_card.refresh()
                self.toast.show_msg(f"✓  Rs. {amt:,} withdrawn successfully")

    def _transfer(self):
        d = TransferDlg(self.acc_no, self)
        if d.exec() == QDialog.DialogCode.Accepted:
            recv, amt = d.values()
            res = atm.transfer(self.acc_no, recv, amt)
            if "success" in str(res).lower():
                self.bal_card.refresh()
                self.toast.show_msg(f"✓  Rs. {amt:,} transferred to {recv}")
            else:
                self.toast.show_msg(f"✗  {res}", ok=False)

    def _statement(self):
        StatementDlg(atm.mini_statement(self.acc_no), self).exec()

    def _settings(self):
        self.toast.show_msg("⚙️  Settings — coming soon")

    def _logout(self):
        if QMessageBox.question(
            self, "Sign Out", "Are you sure you want to sign out?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            self.close()
            self._lw = Login()
            self._lw.show()


# ══════════════════════════════════════════════════════════════
#  DIALOG STYLES
# ══════════════════════════════════════════════════════════════
DS = f"QDialog {{ background: {BG}; }} QLabel {{ background: transparent; }}"


class InfoDlg(QDialog):
    def __init__(self, title, value, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(340, 220)
        self.setStyleSheet(DS)
        l = QVBoxLayout(self)
        l.setContentsMargins(32, 32, 32, 32)
        l.setSpacing(0)
        t = QLabel(title)
        t.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {NAVY}; margin-bottom: 10px;")
        v = QLabel(value)
        v.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {BLUE}; margin-bottom: 24px;")
        l.addWidget(t); l.addWidget(v); l.addStretch()
        b = PrimaryBtn("Close"); b.clicked.connect(self.accept)
        l.addWidget(b)


class AmountDlg(QDialog):
    def __init__(self, title, action, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(380, 260)
        self.setStyleSheet(DS)
        l = QVBoxLayout(self)
        l.setContentsMargins(32, 30, 32, 30)
        l.setSpacing(0)
        t = QLabel(title)
        t.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {NAVY};")
        s = QLabel("Enter the amount below")
        s.setStyleSheet(f"font-size: 12px; color: {T2}; margin-top: 4px; margin-bottom: 22px;")
        l.addWidget(t); l.addWidget(s)
        lb = QLabel("AMOUNT (RS.)")
        lb.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {T3}; letter-spacing: 1.5px; margin-bottom: 7px;")
        l.addWidget(lb)
        self._i = InputField("e.g. 5,000")
        l.addWidget(self._i)
        self._e = ErrLabel(); l.addWidget(self._e)
        l.addStretch()
        row = QHBoxLayout()
        c = GhostBtn("Cancel"); c.clicked.connect(self.reject)
        ok = PrimaryBtn(action); ok.clicked.connect(self._validate)
        row.addWidget(c); row.addSpacing(10); row.addWidget(ok)
        l.addLayout(row)
        self._i.returnPressed.connect(self._validate)
        self._i.textChanged.connect(self._e.clear)

    def _validate(self):
        t = self._i.text().strip()
        if not t:               self._e.show_err("Amount is required"); return
        try: v = float(t)
        except: self._e.show_err("Enter a valid number"); return
        if v <= 0:              self._e.show_err("Must be greater than zero"); return
        if v > 1_000_000:       self._e.show_err("Exceeds limit — max Rs. 10,00,000"); return
        if v != int(v):         self._e.show_err("Whole numbers only (no decimals)"); return
        self.accept()

    def value(self): return int(float(self._i.text().strip()))


class TransferDlg(QDialog):
    def __init__(self, sender, parent=None):
        super().__init__(parent)
        self.sender = sender
        self.setWindowTitle("Transfer Funds")
        self.setFixedSize(400, 345)
        self.setStyleSheet(DS)
        l = QVBoxLayout(self)
        l.setContentsMargins(32, 30, 32, 30)
        l.setSpacing(0)
        t = QLabel("Transfer Funds")
        t.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {NAVY};")
        s = QLabel("Send money to another account")
        s.setStyleSheet(f"font-size: 12px; color: {T2}; margin-top: 4px; margin-bottom: 22px;")
        l.addWidget(t); l.addWidget(s)

        lb1 = QLabel("RECEIVER ACCOUNT NUMBER")
        lb1.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {T3}; letter-spacing: 1.5px; margin-bottom: 7px;")
        l.addWidget(lb1)
        self._r = InputField("e.g. 1234567890")
        l.addWidget(self._r)
        self._re = ErrLabel(); l.addWidget(self._re)

        sp = QWidget(); sp.setFixedHeight(14); l.addWidget(sp)

        lb2 = QLabel("AMOUNT (RS.)")
        lb2.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {T3}; letter-spacing: 1.5px; margin-bottom: 7px;")
        l.addWidget(lb2)
        self._a = InputField("e.g. 1,000")
        l.addWidget(self._a)
        self._ae = ErrLabel(); l.addWidget(self._ae)
        l.addStretch()

        row = QHBoxLayout()
        c = GhostBtn("Cancel"); c.clicked.connect(self.reject)
        ok = PrimaryBtn("Transfer →"); ok.clicked.connect(self._validate)
        row.addWidget(c); row.addSpacing(10); row.addWidget(ok)
        l.addLayout(row)
        self._r.textChanged.connect(self._re.clear)
        self._a.textChanged.connect(self._ae.clear)

    def _validate(self):
        rec = self._r.text().strip(); amt = self._a.text().strip(); ok = True
        self._re.clear(); self._ae.clear()
        if not rec:              self._re.show_err("Receiver account required"); ok = False
        elif not rec.isdigit():  self._re.show_err("Digits only");               ok = False
        elif rec == self.sender: self._re.show_err("Cannot transfer to own account"); ok = False
        elif len(rec) < 4:       self._re.show_err("Invalid account number");    ok = False
        if not amt:              self._ae.show_err("Amount required"); ok = False
        else:
            try:
                v = float(amt)
                if v <= 0:        self._ae.show_err("Must be greater than zero"); ok = False
                elif v > 500_000: self._ae.show_err("Limit: Rs. 5,00,000 per transfer"); ok = False
                elif v != int(v): self._ae.show_err("Whole numbers only"); ok = False
            except:
                self._ae.show_err("Enter a valid number"); ok = False
        if ok: self.accept()

    def values(self):
        return self._r.text().strip(), int(float(self._a.text().strip()))


class StatementDlg(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Account Statement")
        self.setFixedSize(520, 440)
        self.setStyleSheet(DS)
        l = QVBoxLayout(self)
        l.setContentsMargins(28, 28, 28, 28)
        l.setSpacing(0)

        hrow = QHBoxLayout()
        t = QLabel("Account Statement")
        t.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {NAVY};")
        hrow.addWidget(t); hrow.addStretch()
        l.addLayout(hrow)
        sp = QWidget(); sp.setFixedHeight(16); l.addWidget(sp)

        if not data:
            em = QLabel("No transactions found.")
            em.setAlignment(Qt.AlignmentFlag.AlignCenter)
            em.setStyleSheet(f"color: {T3}; font-size: 14px; padding: 40px;")
            l.addWidget(em)
        else:
            tbl = QTableWidget(len(data), 3)
            tbl.setHorizontalHeaderLabels(["Date / Time", "Amount (Rs.)", "Type"])
            tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            tbl.verticalHeader().setVisible(False)
            tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            tbl.setShowGrid(False)
            tbl.setAlternatingRowColors(True)
            tbl.setStyleSheet(f"""
                QTableWidget {{
                    background: {SURFACE};
                    alternate-background-color: #F7F9FC;
                    border: 1px solid {BORDER};
                    border-radius: 10px;
                    color: {T1};
                    font-size: 13px;
                    outline: none;
                }}
                QTableWidget::item {{
                    padding: 10px 14px;
                    border-bottom: 1px solid {BORDER};
                    color: {T1};
                }}
                QTableWidget::item:selected {{
                    background: {BLUE_LIGHT};
                    color: {BLUE};
                }}
                QHeaderView::section {{
                    background: #F0F2F7;
                    color: {T3};
                    font-size: 10px;
                    font-weight: bold;
                    letter-spacing: 1.2px;
                    padding: 10px 14px;
                    border: none;
                    border-bottom: 1px solid {BORDER};
                }}
                QScrollBar:vertical {{ background: {BG}; width: 5px; border-radius: 3px; }}
                QScrollBar::handle:vertical {{ background: {BORDER_MED}; border-radius: 3px; }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
            """)
            for i, tx in enumerate(data):
                tx_type = str(tx[2]).lower()
                is_cr   = "deposit" in tx_type or "credit" in tx_type
                color   = SUCCESS if is_cr else DANGER
                d  = QTableWidgetItem(str(tx[0]))
                a  = QTableWidgetItem(f"{tx[1]:,}" if isinstance(tx[1], (int, float)) else str(tx[1]))
                tp = QTableWidgetItem(("↑ " if is_cr else "↓ ") + str(tx[2]).title())
                a.setForeground(qc(color))
                tp.setForeground(qc(color))
                for col, item in enumerate([d, a, tp]):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                    tbl.setItem(i, col, item)
            l.addWidget(tbl)

        l.addStretch()
        sp2 = QWidget(); sp2.setFixedHeight(14); l.addWidget(sp2)
        c = PrimaryBtn("Close")
        c.clicked.connect(self.accept)
        l.addWidget(c)


# ══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════
app = QApplication(sys.argv)
app.setStyle("Fusion")
app.setFont(QFont("Segoe UI", 10))

from PyQt6.QtGui import QPalette
pal = QPalette()
pal.setColor(QPalette.ColorRole.Window,          qc(BG))
pal.setColor(QPalette.ColorRole.WindowText,      qc(T1))
pal.setColor(QPalette.ColorRole.Base,            qc(SURFACE))
pal.setColor(QPalette.ColorRole.AlternateBase,   qc("#F7F9FC"))
pal.setColor(QPalette.ColorRole.Text,            qc(T1))
pal.setColor(QPalette.ColorRole.Button,          qc(SURFACE))
pal.setColor(QPalette.ColorRole.ButtonText,      qc(T1))
pal.setColor(QPalette.ColorRole.Highlight,       qc(BLUE))
pal.setColor(QPalette.ColorRole.HighlightedText, qc(WHITE))
pal.setColor(QPalette.ColorRole.ToolTipBase,     qc(SURFACE))
pal.setColor(QPalette.ColorRole.ToolTipText,     qc(T1))
pal.setColor(QPalette.ColorRole.PlaceholderText, qc(T3))
app.setPalette(pal)

win = Login()
win.show()
sys.exit(app.exec())