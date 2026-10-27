#!/usr/bin/env python3
"""
CSI Timesheet Generator - Standalone GUI Application
Generates 2-week timesheets for all employees as a combined PDF.
Created by Pranish
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import Calendar
from datetime import datetime, timedelta
import os
import subprocess
import sys
import json

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet

# =============================================================================
# DEFAULT EMPLOYEE DATA - Used when employees.json doesn't exist
# =============================================================================
DEFAULT_EMPLOYEES = [
    ("Archway/Social Media", "Brianna", "Rached"),
    ("CCEC", "Sarah", "Glisson"),
    ("CCEC", "Savannah", "Davis"),
    ("CCEC", "Kyree", "Robinson-Banks"),
    ("CCEC", "Emily", "Beck"),
    ("CCEC", "Jackie", "Reed"),
    ("CCEC", "Joellie", "Acebo"),
    ("Laptop Upcycle", "Justin", "Burgess"),
    ("Laptop Upcycle", "Aleksandra", "Tomaszkowicz"),
    ("Commuter Affairs", "Luannee", "Hernandez"),
    ("Commuter Affairs", "Kya", "McDonald"),
    ("Financial Assistant", "Siddhant", "Gurung"),
    ("Financial Assistant", "Pranish", "Khanal"),
    ("Financial Assistant", "Jennica", "Bugtong"),
    ("Front Desk", "Carly", "Chiu"),
    ("Front Desk", "Lida", "Kelyman"),
    ("Front Desk", "Giana", "Comisi"),
    ("Front Desk", "Ash", "Curtis"),
    ("OFSL", "Chanel", "Taylor"),
    ("OFSL", "Ilianna", "DeJesus"),
    ("J. Lee's", "Jestina", "Brown"),
    ("J. Lee's", "Charbel", "Maroun"),
    ("J. Lee's", "Theodore", "Walton"),
    ("J. Lee's", "Sandra", "Yeboah"),
    ("J. Lee's", "Gabby", "Hodsden"),
    ("J. Lee's", "Shannon", "Lee Gomez"),
    ("J. Lee's", "Prashant", "Shah"),
    ("J. Lee's", "Ronaldson", "Couyoute"),
    ("J. Lee's", "Magdalena", "Nikolova"),
    ("J. Lee's", "Liza", "Kireev"),
    ("OVP", "Jailyn", "Agard"),
    ("OVP", "Abby", "Casimir"),
    ("OVP", "Gracyn", "Nutt"),
    ("OVP", "Victoria", "Perri"),
    ("Roadrunner Center", "Allison", "Tanasy"),
    ("Roadrunner Center", "Collin", "Suojanen"),
    ("Women's Center", "Ariana", "Jimenez Rivera"),
    ("Women's Center", "Ty", "Boehler"),
    ("Women's Center", "Sofia", "Piccinich"),
    ("Women's Center", "Cookie", "Wahba"),
    ("Women's Center", "Maria", "Manniello"),
    ("Women's Center", "Brooke", "Newland"),
]


def get_data_dir():
    """Get the directory where data files are stored."""
    if getattr(sys, 'frozen', False):
        # Bundled app - use Application Support (writable)
        app_support = os.path.expanduser('~/Library/Application Support/CSI Timesheet Generator')
        if not os.path.exists(app_support):
            os.makedirs(app_support)
        return app_support
    return os.path.dirname(os.path.abspath(__file__))


def get_employees_file():
    """Get the path to the employees JSON file."""
    return os.path.join(get_data_dir(), "employees.json")


def load_employees():
    """Load employees from JSON file, or create it with defaults if it doesn't exist."""
    employees_file = get_employees_file()

    if os.path.exists(employees_file):
        try:
            with open(employees_file, 'r') as f:
                data = json.load(f)
                return [tuple(emp) for emp in data]
        except (json.JSONDecodeError, IOError) as e:
            # File exists but is corrupted - warn user and use defaults
            print(f"Warning: Could not load employees.json ({e}). Using defaults.")
            from tkinter import messagebox
            try:
                messagebox.showwarning(
                    "Data File Error",
                    f"Could not load employees.json:\n{e}\n\nUsing default employee list."
                )
            except:
                pass  # GUI may not be initialized yet

    save_employees(DEFAULT_EMPLOYEES)
    return list(DEFAULT_EMPLOYEES)


def save_employees(employees):
    """Save employees to JSON file."""
    employees_file = get_employees_file()
    try:
        with open(employees_file, 'w') as f:
            json.dump(employees, f, indent=2)
        return True
    except (IOError, OSError) as e:
        from tkinter import messagebox
        try:
            messagebox.showerror(
                "Save Error",
                f"Could not save employees.json:\n{e}"
            )
        except:
            print(f"Error: Could not save employees.json: {e}")
        return False


def draw_centered_text(canvas_obj, text, x, y, cell_width, cell_height, font="Helvetica", font_size=7):
    """Draw text centered both horizontally and vertically in a cell."""
    canvas_obj.setFont(font, font_size)
    text_width = canvas_obj.stringWidth(text, font, font_size)
    text_x = x + (cell_width - text_width) / 2
    text_y = y - cell_height/2 - font_size * 0.35
    canvas_obj.drawString(text_x, text_y, text)


def draw_left_aligned_vcenter_text(canvas_obj, text, x, y, cell_width, cell_height, font="Helvetica", font_size=10, padding=3):
    """Draw text left-aligned horizontally but centered vertically in a cell."""
    canvas_obj.setFont(font, font_size)
    text_x = x + padding  # Left aligned with padding
    text_y = y - cell_height/2 - font_size * 0.35  # Vertically centered
    canvas_obj.drawString(text_x, text_y, text)


def draw_timesheet(c, employee_name, work_area, start_date):
    """Draw a single timesheet page using canvas for precise control."""

    width, height = LETTER  # 612 x 792 points

    # Margins
    left_margin = 0.5 * inch
    right_margin = width - 0.5 * inch
    top_margin = height - 0.4 * inch

    # Calculate dates
    week1_dates = [start_date + timedelta(days=i) for i in range(7)]
    week2_dates = [start_date + timedelta(days=i) for i in range(7, 14)]
    week1_ending = week1_dates[6]  # Friday
    week2_ending = week2_dates[6]  # Friday

    y = top_margin

    # =========================================================================
    # HEADER SECTION (No Master Sheet/CSI row - starts with employee name)
    # =========================================================================
    header_height = 0.25 * inch
    name_box_width = 5.0 * inch
    area_box_width = right_margin - left_margin - name_box_width

    # Row 1: Employee Name value | Work Area value (left-aligned, vertically centered)
    c.setLineWidth(1)
    c.rect(left_margin, y - header_height, name_box_width, header_height)
    draw_left_aligned_vcenter_text(c, employee_name, left_margin, y, name_box_width, header_height, "Helvetica", 10)

    c.rect(left_margin + name_box_width, y - header_height, area_box_width, header_height)
    draw_left_aligned_vcenter_text(c, work_area, left_margin + name_box_width, y, area_box_width, header_height, "Helvetica", 10)

    y -= header_height

    # Row 2: Labels
    label_height = 14
    c.setFont("Helvetica", 7)
    c.rect(left_margin, y - label_height, name_box_width, label_height)
    c.drawString(left_margin + 3, y - 10, "NAME (LAST, FIRST, M.I.)")
    c.rect(left_margin + name_box_width, y - label_height, area_box_width, label_height)
    c.drawString(left_margin + name_box_width + 3, y - 10, "WORK AREA")

    y -= label_height + 0.18 * inch

    # =========================================================================
    # WEEK 1
    # =========================================================================
    y = draw_week_section(c, y, left_margin, right_margin, week1_dates, week1_ending)

    # =========================================================================
    # SEPARATOR - More spacing above and below the line
    # =========================================================================
    y -= 0.25 * inch  # Space above line
    c.setLineWidth(1.5)
    c.line(left_margin, y, right_margin, y)
    y -= 0.25 * inch  # Space below line

    # =========================================================================
    # WEEK 2
    # =========================================================================
    y = draw_week_section(c, y, left_margin, right_margin, week2_dates, week2_ending)

    # =========================================================================
    # TOTAL FOR TWO WEEKS - aligned with Total Worked column
    # =========================================================================
    y -= 0.3 * inch
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(left_margin + 2.0 * inch, y, "TOTAL FOR TWO WEEKS")

    # Total box - same width and aligned with Total Worked column
    right_col_width = 0.95 * inch
    right_table_x = right_margin - right_col_width
    box_height = 0.18 * inch * 2  # Same as double row height
    c.setLineWidth(0.5)
    c.rect(right_table_x, y - box_height/2 - 2, right_col_width, box_height)

    y -= 0.4 * inch

    # =========================================================================
    # SPECIAL NOTES AND CERTIFICATION
    # =========================================================================
    c.setFont("Helvetica-Bold", 9)
    c.drawString(left_margin, y, "SPECIAL NOTES:")
    y -= 0.18 * inch

    c.setFont("Helvetica", 8)
    c.drawString(left_margin + 0.1 * inch, y, "EMPLOYEE CERTIFICATION:")
    y -= 0.13 * inch
    c.drawString(left_margin + 0.1 * inch, y, "I certify that the above information is accurate")
    y -= 0.13 * inch
    c.drawString(left_margin + 0.1 * inch, y, "and complete.")

    y -= 0.3 * inch

    # Signature lines
    line_y = y
    c.setLineWidth(0.5)
    c.line(left_margin, line_y, left_margin + 0.9 * inch, line_y)
    c.line(left_margin + 1.2 * inch, line_y, left_margin + 3.3 * inch, line_y)
    c.line(left_margin + 3.6 * inch, line_y, left_margin + 4.5 * inch, line_y)
    c.line(left_margin + 4.8 * inch, line_y, right_margin, line_y)

    y -= 0.15 * inch
    c.setFont("Helvetica", 7)
    c.drawCentredString(left_margin + 2.25 * inch, y, "EMPLOYEE SIGNATURE")


def draw_week_section(c, y, left_margin, right_margin, week_dates, week_ending):
    """Draw a single week section of the timesheet."""

    # Week ending header
    c.setFont("Helvetica-Bold", 9)
    c.drawString(left_margin + 0.8 * inch, y, "WEEK ENDING")
    day = week_ending.day
    date_str = f"{day}-{week_ending.strftime('%b-%y')}"
    c.drawString(left_margin + 2.5 * inch, y, date_str)
    c.setLineWidth(0.5)
    c.line(left_margin + 2.45 * inch, y - 2, left_margin + 3.5 * inch, y - 2)

    y -= 0.48 * inch  # Space after WEEK ENDING

    # Column headers text
    c.setFont("Helvetica", 7)
    c.drawString(left_margin, y + 0.22 * inch, "Complete IN INK")
    c.drawCentredString(left_margin + 2.7 * inch, y + 0.22 * inch, "Use 2nd column")
    c.drawCentredString(left_margin + 2.7 * inch, y + 0.11 * inch, "only for two shifts")
    c.drawCentredString(left_margin + 2.7 * inch, y, "on same day")
    c.setFont("Helvetica-Bold", 7)
    c.drawString(right_margin - 0.85 * inch, y, "Total Worked")

    y -= 0.24 * inch  # Space after column headers

    # Table setup
    left_col_widths = [1.0 * inch, 0.35 * inch, 0.7 * inch, 0.7 * inch]
    right_col_width = 0.95 * inch
    right_table_x = right_margin - right_col_width
    
    row_height = 0.18 * inch
    double_row_height = row_height * 2

    c.setLineWidth(0.5)

    # DAY OF WEEK header row
    x = left_margin
    
    c.rect(x, y - row_height, left_col_widths[0], row_height)
    draw_centered_text(c, "DAY OF WEEK", x, y, left_col_widths[0], row_height, "Helvetica-Bold", 7)
    x += left_col_widths[0]

    c.rect(x, y - row_height, left_col_widths[1], row_height)
    x += left_col_widths[1]

    c.rect(x, y - row_height, left_col_widths[2], row_height)
    x += left_col_widths[2]

    c.rect(x, y - row_height, left_col_widths[3], row_height)

    # Right table header
    c.rect(right_table_x, y - row_height, right_col_width, row_height)

    y -= row_height

    # Day rows
    day_names = ['SATURDAY', 'SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY']

    for day_idx, (day_name, date) in enumerate(zip(day_names, week_dates)):
        # Draw the Total Worked cell FIRST (spans both IN and OUT rows)
        c.rect(right_table_x, y - double_row_height, right_col_width, double_row_height)
        
        # IN row (left table)
        x = left_margin
        c.rect(x, y - row_height, left_col_widths[0], row_height)
        draw_centered_text(c, day_name, x, y, left_col_widths[0], row_height, "Helvetica-Bold", 7)
        x += left_col_widths[0]

        c.rect(x, y - row_height, left_col_widths[1], row_height)
        draw_centered_text(c, "IN", x, y, left_col_widths[1], row_height, "Helvetica", 7)
        x += left_col_widths[1]

        c.rect(x, y - row_height, left_col_widths[2], row_height)
        x += left_col_widths[2]

        c.rect(x, y - row_height, left_col_widths[3], row_height)

        y -= row_height

        # OUT row (left table)
        x = left_margin
        c.rect(x, y - row_height, left_col_widths[0], row_height)
        date_str = f"{date.month}/{date.day}/{date.year}"
        draw_centered_text(c, date_str, x, y, left_col_widths[0], row_height, "Helvetica", 7)
        x += left_col_widths[0]

        c.rect(x, y - row_height, left_col_widths[1], row_height)
        draw_centered_text(c, "OUT", x, y, left_col_widths[1], row_height, "Helvetica", 7)
        x += left_col_widths[1]

        c.rect(x, y - row_height, left_col_widths[2], row_height)
        x += left_col_widths[2]

        c.rect(x, y - row_height, left_col_widths[3], row_height)

        y -= row_height

    # TOTAL FOR WEEK row - NO borders on left table, only text and right box
    x = left_margin
    x += left_col_widths[0]
    x += left_col_widths[1]

    # Draw "TOTAL FOR WEEK" text centered in the merged area
    total_width = left_col_widths[2] + left_col_widths[3]
    draw_centered_text(c, "TOTAL FOR WEEK", x, y, total_width, row_height, "Helvetica-Bold", 7)

    # Right table - Total for week box (keep the border)
    c.rect(right_table_x, y - row_height, right_col_width, row_height)

    y -= row_height

    return y


def generate_all_timesheets(employees, start_date, output_path, progress_callback=None):
    """Generate timesheets for all employees and save to a single PDF."""

    c = canvas.Canvas(output_path, pagesize=LETTER)
    total = len(employees)

    for i, (work_area, first_name, last_name) in enumerate(employees):
        employee_name = f"{last_name}, {first_name}"

        if progress_callback:
            progress_callback(i + 1, total, employee_name)

        draw_timesheet(c, employee_name, work_area, start_date)

        if i < total - 1:
            c.showPage()

    c.save()
    return output_path


# =============================================================================
# COLOR PALETTE - Modern + Brutalist + Y2K
# =============================================================================
COLORS = {
    'bg': '#1F2937',
    'surface': '#111827',
    'accent': '#14B8A6',
    'accent_hover': '#0D9488',
    'accent_active': '#0F766E',
    'text': '#F3F4F6',
    'text_secondary': '#9CA3AF',
    'border': '#374151',
    'error': '#EF4444',
    'warning': '#F59E0B',
}


class TimesheetGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSI Timesheet Generator")
        self.root.geometry("580x720")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS['bg'])

        # Load employees from file
        self.employees = load_employees()

        # Default save location
        self.save_path = get_data_dir()

        # Configure styles
        self.setup_styles()

        # Create main container using grid for efficient frame switching
        self.container = tk.Frame(self.root, bg=COLORS['bg'])
        self.container.pack(fill=tk.BOTH, expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Create frames for different screens - stack them using grid
        self.main_frame = tk.Frame(self.container, bg=COLORS['bg'])
        self.edit_frame = tk.Frame(self.container, bg=COLORS['bg'])

        # Place both frames in same grid cell (stacked)
        self.main_frame.grid(row=0, column=0, sticky='nsew')
        self.edit_frame.grid(row=0, column=0, sticky='nsew')

        # Setup both screens
        self.setup_main_screen()
        self.setup_edit_screen()

        # Show main screen initially
        self.show_main_screen()

    def setup_styles(self):
        """Configure ttk styles for dark theme."""
        style = ttk.Style()

        # Use 'clam' theme as base for better customization
        style.theme_use('clam')

        # Treeview styling
        style.configure('Dark.Treeview',
            background=COLORS['surface'],
            foreground=COLORS['text'],
            fieldbackground=COLORS['surface'],
            borderwidth=0,
            font=('SF Pro Display', 12)
        )
        style.configure('Dark.Treeview.Heading',
            background=COLORS['surface'],
            foreground=COLORS['accent'],
            borderwidth=0,
            font=('SF Pro Display', 11, 'bold')
        )
        style.map('Dark.Treeview',
            background=[('selected', COLORS['accent'])],
            foreground=[('selected', COLORS['surface'])]
        )

        # Scrollbar styling
        style.configure('Dark.Vertical.TScrollbar',
            background=COLORS['surface'],
            troughcolor=COLORS['bg'],
            borderwidth=0,
            arrowcolor=COLORS['text_secondary']
        )

        # Progress bar styling
        style.configure('Dark.Horizontal.TProgressbar',
            background=COLORS['accent'],
            troughcolor=COLORS['surface'],
            borderwidth=0,
            lightcolor=COLORS['accent'],
            darkcolor=COLORS['accent']
        )

    def show_main_screen(self):
        """Show the main generator screen."""
        self.main_frame.tkraise()
        self.update_status()
        self.update_employee_count_card()

    def show_edit_screen(self):
        """Show the edit employees screen."""
        self.edit_frame.tkraise()
        self.populate_employee_list()

    def create_card(self, parent, label_text, value_text, width=200):
        """Create a styled card widget."""
        card = tk.Frame(parent, bg=COLORS['surface'], highlightbackground=COLORS['border'],
                       highlightthickness=2, width=width)
        card.pack_propagate(False)

        inner = tk.Frame(card, bg=COLORS['surface'])
        inner.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

        label = tk.Label(inner, text=label_text.upper(), bg=COLORS['surface'],
                        fg=COLORS['accent'], font=('SF Pro Display', 11, 'bold'))
        label.pack(anchor='w')

        value = tk.Label(inner, text=value_text, bg=COLORS['surface'],
                        fg=COLORS['text'], font=('SF Pro Display', 26, 'bold'))
        value.pack(anchor='w', pady=(8, 0))

        return card, value

    def create_button(self, parent, text, command, primary=True, width=None):
        """Create a styled button."""
        if primary:
            btn = tk.Button(parent, text=text.upper(), command=command,
                           bg=COLORS['accent'], fg=COLORS['surface'],
                           font=('SF Pro Display', 13, 'bold'),
                           relief='flat', cursor='hand2',
                           activebackground=COLORS['accent_hover'],
                           activeforeground=COLORS['surface'],
                           padx=35, pady=14)
        else:
            btn = tk.Button(parent, text=text.upper(), command=command,
                           bg=COLORS['bg'], fg=COLORS['accent'],
                           font=('SF Pro Display', 12, 'bold'),
                           relief='flat', cursor='hand2',
                           highlightbackground=COLORS['accent'],
                           highlightthickness=2,
                           activebackground=COLORS['surface'],
                           activeforeground=COLORS['accent'],
                           padx=30, pady=12)

        if width:
            btn.config(width=width)

        # Hover effects
        def on_enter(e):
            if primary:
                btn.config(bg=COLORS['accent_hover'])
            else:
                btn.config(bg=COLORS['border'])

        def on_leave(e):
            if primary:
                btn.config(bg=COLORS['accent'])
            else:
                btn.config(bg=COLORS['bg'])

        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)

        return btn

    def setup_main_screen(self):
        """Setup the main timesheet generator screen."""
        main_frame = self.main_frame

        # Title bar with accent border
        title_bar = tk.Frame(main_frame, bg=COLORS['surface'], height=50)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)

        title_label = tk.Label(title_bar, text="CSI TIMESHEET GENERATOR",
                              bg=COLORS['surface'], fg=COLORS['accent'],
                              font=('SF Pro Display', 16, 'bold'))
        title_label.pack(expand=True, pady=12)

        # Accent border under title
        accent_border = tk.Frame(main_frame, bg=COLORS['accent'], height=2)
        accent_border.pack(fill=tk.X)

        # Content area
        content = tk.Frame(main_frame, bg=COLORS['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=24, pady=20)

        # Cards row - centered
        cards_row = tk.Frame(content, bg=COLORS['bg'])
        cards_row.pack(pady=(0, 20))

        # Employees card
        emp_card, self.emp_count_label = self.create_card(cards_row, "Employees", str(len(self.employees)), width=180)
        emp_card.pack(side=tk.LEFT, padx=(0, 4))
        emp_card.config(height=100)

        # Start date card
        date_card_frame = tk.Frame(cards_row, bg=COLORS['surface'], highlightbackground=COLORS['border'],
                                   highlightthickness=2, width=180, height=100)
        date_card_frame.pack(side=tk.LEFT, padx=(4, 0))
        date_card_frame.pack_propagate(False)

        date_inner = tk.Frame(date_card_frame, bg=COLORS['surface'])
        date_inner.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

        date_label = tk.Label(date_inner, text="START DATE", bg=COLORS['surface'],
                             fg=COLORS['accent'], font=('SF Pro Display', 11, 'bold'))
        date_label.pack(anchor='w')

        self.date_display = tk.Label(date_inner, text="Select below", bg=COLORS['surface'],
                                     fg=COLORS['text'], font=('SF Pro Display', 16, 'bold'))
        self.date_display.pack(anchor='w', pady=(8, 0))

        # Calendar section
        cal_section = tk.Frame(content, bg=COLORS['surface'], highlightbackground=COLORS['border'],
                              highlightthickness=2)
        cal_section.pack(fill=tk.X, pady=(0, 16))

        cal_header = tk.Label(cal_section, text="SELECT STARTING SATURDAY", bg=COLORS['surface'],
                             fg=COLORS['accent'], font=('SF Pro Display', 11, 'bold'))
        cal_header.pack(anchor='w', padx=18, pady=(15, 10))

        # Calendar widget with dark theme - larger font for better readability
        self.calendar = Calendar(
            cal_section,
            selectmode='day',
            date_pattern='yyyy-mm-dd',
            font=('SF Pro Display', 14),
            showweeknumbers=False,
            background=COLORS['surface'],
            foreground=COLORS['text'],
            headersbackground=COLORS['surface'],
            headersforeground=COLORS['accent'],
            selectbackground=COLORS['accent'],
            selectforeground=COLORS['surface'],
            normalbackground=COLORS['surface'],
            normalforeground=COLORS['text'],
            weekendbackground=COLORS['surface'],
            weekendforeground=COLORS['text_secondary'],
            bordercolor=COLORS['border'],
            borderwidth=0,
            othermonthbackground=COLORS['bg'],
            othermonthforeground=COLORS['text_secondary'],
            othermonthwebackground=COLORS['bg'],
            othermonthweforeground=COLORS['text_secondary']
        )
        self.calendar.pack(pady=(0, 15))
        self.calendar.bind("<<CalendarSelected>>", self.on_date_select)

        # Output folder section
        folder_section = tk.Frame(content, bg=COLORS['surface'], highlightbackground=COLORS['border'],
                                 highlightthickness=2)
        folder_section.pack(fill=tk.X, pady=(0, 16))

        folder_inner = tk.Frame(folder_section, bg=COLORS['surface'])
        folder_inner.pack(fill=tk.X, padx=18, pady=15)

        folder_label = tk.Label(folder_inner, text="OUTPUT FOLDER", bg=COLORS['surface'],
                               fg=COLORS['accent'], font=('SF Pro Display', 11, 'bold'))
        folder_label.pack(anchor='w')

        folder_row = tk.Frame(folder_inner, bg=COLORS['surface'])
        folder_row.pack(fill=tk.X, pady=(8, 0))

        self.path_var = tk.StringVar(value=self.save_path)
        path_entry = tk.Entry(folder_row, textvariable=self.path_var, state='readonly',
                             bg=COLORS['bg'], fg='#000000', font=('SF Pro Display', 12),
                             relief='flat', highlightbackground=COLORS['border'],
                             highlightthickness=1, insertbackground=COLORS['text'])
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))

        browse_btn = tk.Button(folder_row, text="BROWSE", command=self.browse_folder,
                              bg=COLORS['border'], fg='#000000',
                              font=('SF Pro Display', 11, 'bold'), relief='flat',
                              cursor='hand2', padx=15, pady=6)
        browse_btn.pack(side=tk.RIGHT)

        # Buttons row
        btn_row = tk.Frame(content, bg=COLORS['bg'])
        btn_row.pack(fill=tk.X, pady=(0, 16))

        edit_btn = self.create_button(btn_row, "Edit Employees", self.show_edit_screen, primary=False)
        edit_btn.pack(side=tk.LEFT)

        self.generate_btn = self.create_button(btn_row, "Generate Timesheets", self.generate, primary=True)
        self.generate_btn.pack(side=tk.RIGHT)

        # Progress section
        progress_frame = tk.Frame(content, bg=COLORS['bg'])
        progress_frame.pack(fill=tk.X, pady=(0, 10))

        progress_label = tk.Label(progress_frame, text="PROGRESS", bg=COLORS['bg'],
                                 fg=COLORS['text_secondary'], font=('SF Pro Display', 11, 'bold'))
        progress_label.pack(anchor='w', pady=(0, 8))

        self.progress = ttk.Progressbar(progress_frame, mode='determinate', length=530,
                                        style='Dark.Horizontal.TProgressbar')
        self.progress.pack(fill=tk.X)

        # Status bar at bottom
        status_bar = tk.Frame(main_frame, bg=COLORS['surface'], height=35)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        status_bar.pack_propagate(False)

        # Top border for status bar
        status_border = tk.Frame(main_frame, bg=COLORS['border'], height=1)
        status_border.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(status_bar, textvariable=self.status_var, bg=COLORS['surface'],
                               fg=COLORS['text_secondary'], font=('SF Pro Display', 11))
        status_label.pack(side=tk.LEFT, padx=15, pady=8)

        version_label = tk.Label(status_bar, text="v1.0 — Pranish", bg=COLORS['surface'],
                                fg=COLORS['text_secondary'], font=('SF Pro Display', 11))
        version_label.pack(side=tk.RIGHT, padx=15, pady=8)

    def on_date_select(self, event=None):
        """Update date display when calendar selection changes."""
        selected = self.calendar.get_date()
        date_obj = datetime.strptime(selected, '%Y-%m-%d')
        self.date_display.config(text=date_obj.strftime('%m/%d/%Y'))

    def update_employee_count_card(self):
        """Update the employee count display."""
        self.emp_count_label.config(text=str(len(self.employees)))

    def setup_edit_screen(self):
        """Setup the edit employees screen."""
        edit_frame = self.edit_frame

        # Title bar
        title_bar = tk.Frame(edit_frame, bg=COLORS['surface'], height=50)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)

        back_btn = tk.Button(title_bar, text="<", command=self.show_main_screen,
                            bg=COLORS['surface'], fg=COLORS['accent'],
                            font=('SF Pro Display', 16, 'bold'), relief='flat',
                            cursor='hand2')
        back_btn.pack(side=tk.LEFT, padx=15, pady=8)

        title_label = tk.Label(title_bar, text="EDIT EMPLOYEES",
                              bg=COLORS['surface'], fg=COLORS['accent'],
                              font=('SF Pro Display', 16, 'bold'))
        title_label.pack(expand=True, pady=12)

        # Accent border
        accent_border = tk.Frame(edit_frame, bg=COLORS['accent'], height=2)
        accent_border.pack(fill=tk.X)

        # Content
        content = tk.Frame(edit_frame, bg=COLORS['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=24, pady=20)

        # Employee list section
        list_section = tk.Frame(content, bg=COLORS['surface'], highlightbackground=COLORS['border'],
                               highlightthickness=2)
        list_section.pack(fill=tk.BOTH, expand=True, pady=(0, 16))

        list_header = tk.Frame(list_section, bg=COLORS['surface'])
        list_header.pack(fill=tk.X, padx=18, pady=(15, 10))

        list_label = tk.Label(list_header, text="EMPLOYEE LIST", bg=COLORS['surface'],
                             fg=COLORS['accent'], font=('SF Pro Display', 11, 'bold'))
        list_label.pack(side=tk.LEFT)

        self.count_var = tk.StringVar()
        count_label = tk.Label(list_header, textvariable=self.count_var, bg=COLORS['surface'],
                              fg=COLORS['text_secondary'], font=('SF Pro Display', 11))
        count_label.pack(side=tk.RIGHT)

        # Treeview
        tree_frame = tk.Frame(list_section, bg=COLORS['surface'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 15))

        columns = ('name', 'work_area')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12,
                                style='Dark.Treeview')
        self.tree.heading('name', text='NAME', anchor='w')
        self.tree.heading('work_area', text='WORK AREA', anchor='w')
        self.tree.column('name', width=220, anchor='w')
        self.tree.column('work_area', width=200, anchor='w')

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview,
                                 style='Dark.Vertical.TScrollbar')
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Entry section
        entry_section = tk.Frame(content, bg=COLORS['surface'], highlightbackground=COLORS['border'],
                                highlightthickness=2)
        entry_section.pack(fill=tk.X, pady=(0, 16))

        entry_inner = tk.Frame(entry_section, bg=COLORS['surface'])
        entry_inner.pack(fill=tk.X, padx=18, pady=15)

        entry_label = tk.Label(entry_inner, text="EMPLOYEE DETAILS", bg=COLORS['surface'],
                              fg=COLORS['accent'], font=('SF Pro Display', 11, 'bold'))
        entry_label.pack(anchor='w', pady=(0, 10))

        # Input fields
        fields_frame = tk.Frame(entry_inner, bg=COLORS['surface'])
        fields_frame.pack(fill=tk.X)

        # Work Area
        wa_frame = tk.Frame(fields_frame, bg=COLORS['surface'])
        wa_frame.pack(fill=tk.X, pady=(0, 8))

        wa_label = tk.Label(wa_frame, text="Work Area", bg=COLORS['surface'],
                           fg=COLORS['text_secondary'], font=('SF Pro Display', 11))
        wa_label.pack(anchor='w')

        self.work_area_var = tk.StringVar()
        wa_entry = tk.Entry(wa_frame, textvariable=self.work_area_var,
                           bg=COLORS['bg'], fg=COLORS['text'], font=('SF Pro Display', 12),
                           relief='flat', highlightbackground=COLORS['border'],
                           highlightthickness=2, insertbackground=COLORS['text'])
        wa_entry.pack(fill=tk.X, ipady=8, pady=(4, 0))

        # Names row
        names_row = tk.Frame(fields_frame, bg=COLORS['surface'])
        names_row.pack(fill=tk.X, pady=(0, 8))

        # First Name
        fn_frame = tk.Frame(names_row, bg=COLORS['surface'])
        fn_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        fn_label = tk.Label(fn_frame, text="First Name", bg=COLORS['surface'],
                           fg=COLORS['text_secondary'], font=('SF Pro Display', 11))
        fn_label.pack(anchor='w')

        self.first_name_var = tk.StringVar()
        fn_entry = tk.Entry(fn_frame, textvariable=self.first_name_var,
                           bg=COLORS['bg'], fg=COLORS['text'], font=('SF Pro Display', 12),
                           relief='flat', highlightbackground=COLORS['border'],
                           highlightthickness=2, insertbackground=COLORS['text'])
        fn_entry.pack(fill=tk.X, ipady=8, pady=(4, 0))

        # Last Name
        ln_frame = tk.Frame(names_row, bg=COLORS['surface'])
        ln_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))

        ln_label = tk.Label(ln_frame, text="Last Name", bg=COLORS['surface'],
                           fg=COLORS['text_secondary'], font=('SF Pro Display', 11))
        ln_label.pack(anchor='w')

        self.last_name_var = tk.StringVar()
        ln_entry = tk.Entry(ln_frame, textvariable=self.last_name_var,
                           bg=COLORS['bg'], fg=COLORS['text'], font=('SF Pro Display', 12),
                           relief='flat', highlightbackground=COLORS['border'],
                           highlightthickness=2, insertbackground=COLORS['text'])
        ln_entry.pack(fill=tk.X, ipady=8, pady=(4, 0))

        # Action buttons
        btn_row = tk.Frame(content, bg=COLORS['bg'])
        btn_row.pack(fill=tk.X)

        add_btn = tk.Button(btn_row, text="+ ADD", command=self.add_employee,
                           bg=COLORS['accent'], fg=COLORS['surface'],
                           font=('SF Pro Display', 11, 'bold'), relief='flat',
                           cursor='hand2', padx=20, pady=8)
        add_btn.pack(side=tk.LEFT, padx=(0, 8))

        update_btn = tk.Button(btn_row, text="UPDATE", command=self.update_employee,
                              bg=COLORS['border'], fg='#000000',
                              font=('SF Pro Display', 11, 'bold'), relief='flat',
                              cursor='hand2', padx=20, pady=8)
        update_btn.pack(side=tk.LEFT, padx=(0, 8))

        delete_btn = tk.Button(btn_row, text="DELETE", command=self.delete_employee,
                              bg=COLORS['border'], fg=COLORS['error'],
                              font=('SF Pro Display', 11, 'bold'), relief='flat',
                              cursor='hand2', padx=20, pady=8)
        delete_btn.pack(side=tk.LEFT)

        save_btn = tk.Button(btn_row, text="SAVE CHANGES", command=self.save_employee_changes,
                            bg=COLORS['accent'], fg=COLORS['surface'],
                            font=('SF Pro Display', 11, 'bold'), relief='flat',
                            cursor='hand2', padx=20, pady=8)
        save_btn.pack(side=tk.RIGHT)

        # Status bar
        status_bar = tk.Frame(edit_frame, bg=COLORS['surface'], height=35)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        status_bar.pack_propagate(False)

        status_border = tk.Frame(edit_frame, bg=COLORS['border'], height=1)
        status_border.pack(fill=tk.X, side=tk.BOTTOM)

        self.edit_status_var = tk.StringVar(value="Select an employee to edit")
        edit_status = tk.Label(status_bar, textvariable=self.edit_status_var, bg=COLORS['surface'],
                              fg=COLORS['text_secondary'], font=('SF Pro Display', 11))
        edit_status.pack(side=tk.LEFT, padx=15, pady=8)

        # Bind selection
        self.tree.bind('<<TreeviewSelect>>', self.on_employee_select)

    def populate_employee_list(self):
        """Populate the treeview with employees."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for emp in self.employees:
            # emp is (work_area, first_name, last_name)
            name = f"{emp[2]}, {emp[1]}"  # Last, First
            self.tree.insert('', tk.END, values=(name, emp[0]))

        self.count_var.set(f"{len(self.employees)} total")

    def on_employee_select(self, event):
        """Fill entry fields when an item is selected."""
        selected = self.tree.selection()
        if selected:
            idx = self.tree.index(selected[0])
            emp = self.employees[idx]
            self.work_area_var.set(emp[0])
            self.first_name_var.set(emp[1])
            self.last_name_var.set(emp[2])
            self.edit_status_var.set(f"Editing: {emp[1]} {emp[2]}")

    def add_employee(self):
        """Add a new employee."""
        work_area = self.work_area_var.get().strip()
        first_name = self.first_name_var.get().strip()
        last_name = self.last_name_var.get().strip()

        if not all([work_area, first_name, last_name]):
            messagebox.showwarning("Missing Data", "Please fill in all fields.")
            return

        emp = (work_area, first_name, last_name)
        self.employees.append(emp)
        name = f"{last_name}, {first_name}"
        self.tree.insert('', tk.END, values=(name, work_area))
        self.clear_entries()
        self.count_var.set(f"{len(self.employees)} total")
        self.edit_status_var.set(f"Added: {first_name} {last_name}")

    def update_employee(self):
        """Update the selected employee."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an employee to update.")
            return

        work_area = self.work_area_var.get().strip()
        first_name = self.first_name_var.get().strip()
        last_name = self.last_name_var.get().strip()

        if not all([work_area, first_name, last_name]):
            messagebox.showwarning("Missing Data", "Please fill in all fields.")
            return

        idx = self.tree.index(selected[0])
        emp = (work_area, first_name, last_name)
        self.employees[idx] = emp
        name = f"{last_name}, {first_name}"
        self.tree.item(selected[0], values=(name, work_area))
        self.edit_status_var.set(f"Updated: {first_name} {last_name}")

    def delete_employee(self):
        """Delete the selected employee."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an employee to delete.")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this employee?"):
            idx = self.tree.index(selected[0])
            emp = self.employees[idx]
            del self.employees[idx]
            self.tree.delete(selected[0])
            self.clear_entries()
            self.count_var.set(f"{len(self.employees)} total")
            self.edit_status_var.set(f"Deleted: {emp[1]} {emp[2]}")

    def clear_entries(self):
        """Clear the entry fields."""
        self.work_area_var.set('')
        self.first_name_var.set('')
        self.last_name_var.set('')
        self.edit_status_var.set("Select an employee to edit")

    def save_employee_changes(self):
        """Save employee changes to file."""
        if save_employees(self.employees):
            self.edit_status_var.set(f"Saved {len(self.employees)} employees")
            messagebox.showinfo("Saved", f"Employee list saved!\n{len(self.employees)} employees.")

    def update_status(self):
        """Update the status label."""
        self.status_var.set("Ready")

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.save_path, title="Select Save Location")
        if folder:
            self.save_path = folder
            self.path_var.set(folder)

    def update_progress(self, current, total, name):
        percent = (current / total) * 100
        self.progress['value'] = percent
        self.status_var.set(f"Processing {current}/{total}: {name}")
        self.root.update_idletasks()

    def generate(self):
        if not self.employees:
            messagebox.showerror("No Employees", "Please add employees before generating timesheets.")
            return

        # Get selected date
        selected_date_str = self.calendar.get_date()
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d')

        # Validate it's a Saturday
        if selected_date.weekday() != 5:  # 5 = Saturday
            messagebox.showerror(
                "Invalid Date",
                "Please select a Saturday as the start date.\n\n"
                f"You selected: {selected_date.strftime('%A, %B %d, %Y')}"
            )
            return

        # Calculate end date
        end_date = selected_date + timedelta(days=13)

        # Generate filename
        filename = f"Timesheets_{selected_date.strftime('%Y-%m-%d')}_to_{end_date.strftime('%Y-%m-%d')}.pdf"
        output_path = os.path.join(self.save_path, filename)

        # Disable button during generation
        self.generate_btn.config(state='disabled')
        self.progress['value'] = 0

        try:
            generate_all_timesheets(self.employees, selected_date, output_path, self.update_progress)

            self.status_var.set(f"Complete! Saved to: {filename}")
            self.progress['value'] = 100

            messagebox.showinfo(
                "Success",
                f"Timesheets generated successfully!\n\n"
                f"File: {filename}\n"
                f"Location: {self.save_path}"
            )

            # Open the folder
            try:
                if sys.platform == 'darwin':
                    subprocess.run(['open', self.save_path], check=True)
                elif sys.platform == 'win32':
                    subprocess.run(['explorer', self.save_path], check=True)
                else:
                    subprocess.run(['xdg-open', self.save_path], check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass  # Folder was created successfully, just couldn't open it

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate timesheets:\n\n{str(e)}")
            self.status_var.set("Error occurred")
        finally:
            self.generate_btn.config(state='normal')


def main():
    root = tk.Tk()
    app = TimesheetGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()