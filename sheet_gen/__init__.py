import json
from glob import glob
from math import ceil

from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from sheet_gen.fields import *

pdfmetrics.registerFont(TTFont("OpenSansEmoji", "resources/OpenSansEmoji.ttf"))

field_types = [Barcode, Boolean, BoxNumber, BulkOptions, Digits, Divider, Header, HorizontalOptions, Image, Markers,
               Numbers, SevenSegment, String]
valid_fields = map(lambda x: x.__name__, field_types)

DEFAULT_CONFIG = {
    "min_sheet_num":           1,
    "max_sheet_num":           100,
    "encode_scanner":          True,
    "event":                   "#2Champs 2017",
    "spacer_page":             True,
    "x_pos":                   0.25,
    "y_spacing":               0.2,
    "box_size":                0.22,
    "box_spacing":             0.12,
    "bool_x_offset":           6,
    "font_size":               0.13,
    "box_font_size":           0.1,
    "marker_size":             0.5,
    "divider_height":          0.016,
    "team_x_offset":           5.6875,
    "seven_segment_width":     0.25,
    "seven_segment_thickness": 0.0625,
    "seven_segment_offset":    0.5,
    "marker_colour":           [255, 0, 0],
    "font_color":              [100, 100, 150],
    "label_offset":            1.25
}


class SheetGenerator:
    def __init__(self, min_sheet, max_sheet):
        self.fields = []
        self.config = dict(DEFAULT_CONFIG)
        self.config['event'] = event
        self.config['min_sheet_num'] = min_sheet
        self.config['max_sheet_num'] = max_sheet
        self.filename = self._get_new_pdf_filename()
        self.fields_filename = self._get_fields_filename()
        self.canvas = canvas.Canvas(self.filename, pagesize=letter)
        self.canvas.setFont("OpenSansEmoji", 1)
        self.headers = []
        self.scan_data = []
        self.first_sheet = True

    def _get_new_pdf_filename(self):
        files = glob('sheets/pdf/*.pdf')
        return 'sheets/pdf/sheet_{}.pdf'.format(len(files))

    def _get_fields_filename(self):
        return 'sheets/fields/{}_fields.json'.format(self.filename.split('/')[-1].split('.')[0])

    def get_filename(self):
        return self.filename

    def _add_field(self, field):
        if field.get_label() is not None:
            self.headers.append(field.get_label())
        self.fields.append(field)

    def _draw_sheet(self, match, pos):
        self.canvas.setFont("OpenSansEmoji", 1)
        if self.first_sheet:
            json.dump({}, open(self.fields_filename, "w+"))

        y_pos = self.config["marker_size"] + 1.125
        Markers().draw(self.canvas, self.config)
        header = Header(match, pos)
        header_height, self.scan_data = header.draw(self.canvas, self.config["x_pos"] + self.config["marker_size"], y_pos, self.config)
        y_pos += header_height

        line_width = 0
        prev_y = 0
        seg_width = (8.5 - self.config["marker_size"] * 2) / 4

        for f_num in range(len(self.fields)):
            x_pos = self.config["x_pos"]

            f = self.fields[f_num]
            f_width = ceil(f.calc_width(self.config) / seg_width)
            if f.prev_line and f_width <= 4 - line_width:
                if line_width == 0:
                    y_pos += prev_y
                x_pos += (self.config["box_size"] + self.config["box_spacing"]) * self.config[
                    "bool_x_offset"] * line_width
                line_width += f_width
            else:
                y_pos += prev_y
                line_width = f_width
            if line_width > 4:
                line_width = 0

            prev_y = f.draw(self.canvas, x_pos + self.config["marker_size"], y_pos, self.config)

            if self.first_sheet:
                data = {
                    "type":    f.get_type(),
                    "options": f.get_info(),
                    "id":      f.get_id()
                }
                if data["options"] is not None:
                    data["x_pos"] = x_pos
                    data["y_pos"] = y_pos
                    data["height"] = prev_y
                    self.scan_data.append(data)

        if self.first_sheet:
            json.dump(self.scan_data, open(self.fields_filename, "w+"))

    def get_scan_data(self):
        return self.scan_data

    def _draw_sheets(self):
        for p in range(0, 6):
            for m in range(self.config["min_sheet_num"], self.config["max_sheet_num"] + 1):
                self._draw_sheet(m, p)
                self.canvas.showPage()
            if self.config["spacer_page"]:
                self.canvas.showPage()
        self.canvas.save()

    def create_from_json(self, fields):
        field_dict = dict(zip(valid_fields, field_types))
        for field in fields:
            if field["type"] in field_dict.keys():
                tmp_field = dict(field)
                del tmp_field['key']
                del tmp_field['name']
                del tmp_field['type']
                expr = field["type"] + "(**tmp_field)"
                f = eval(expr, {"__builtins__": None, 'tmp_field': tmp_field}, field_dict)
                if "id" in field.keys():
                    f.set_id(field["id"])
                self._add_field(f)
        self.first_sheet = True
        self._draw_sheets()
