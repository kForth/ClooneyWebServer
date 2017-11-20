import json
from datetime import datetime

from models import ScoutingSheetConfig


class SheetDatabaseInteractor:
    def __init__(self, db, app):
        self._db = db
        self.default_fields = json.load(open(app.root_path + "/db/field_settings.json"))

    def get_sheets(self):
        return [ScoutingSheetConfig.from_json(e) for e in self._db.db['sheets']['sheets']]

    def get_sheet_by_id(self, id):
        sheets = [e for e in self.get_sheets() if e.id == id]
        return sheets[0] if sheets else None

    def set_sheet(self, sheet):
        existing = self.get_sheet_by_id(sheet.id)
        if existing:
            self._db.db['sheets']['sheets'].remove(existing.to_dict())
        else:
            sheet.date_created = datetime.now().strftime("%Y-%m-%d %H:%M")
        sheet.date_modified = datetime.now().strftime("%Y-%m-%d %H:%M")
        self._db.db['sheets']['sheets'].append(sheet.to_dict())
        self._db.commit()

    def get_next_sheet_id(self):
        self._db.db['sheets']['max_id'] += 1
        self._db.commit()
        return self._db.db['sheets']['max_id']
