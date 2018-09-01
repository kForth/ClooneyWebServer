import json
import sqlite3

import xlsxwriter
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from tba_py import TBA


class SpreadsheetGenerator:
    def __init__(self, db_path, tba, path_prefix):
        self.db_path = db_path
        self.tba = tba
        self.path_prefix = path_prefix

        self.workbook = None
        self.formats = None
        self.headers = None
        self.event = None
        self.raw_entries = None
        self.teams = None
        self.matches = None

        self.page_names = {
            'raw':                  'raw_data',
            'raw_calculated':       'raw_calculated',
            'raw_analysis':         'raw_analysis',
            'raw_team_list':        'raw_team_list',
            'raw_matches':          'raw_matches',
            'raw_team_schedule':    'raw_team_schedule',
            'pretty_raw':           'Raw Data',
            'pretty_team_list':     'Team List',
            'pretty_analysis':      'Analysis',
            'pretty_matches':       'Schedule',
            'pretty_team_schedule': 'Team Schedule',
            'team_stats':           'Team Stats',
            'match_rundown':        'Match Rundown'
        }

        self.raw_formats = {
            "raw_data_cell":           {
                "bg_color":     "#FFFFFF",
                "font_color":   "#000000",
                "num_format":   2,
                "border":       True,
                "border_color": "#DADADA"
            },
            "pretty_header":           {
                "bg_color":   "#FFFFFF",
                "font_color": "#000000",
                "bold":       True,
                "valign":     "bottom",
                "align":      "center",
                "text_wrap":  "text_wrap",
                "border":     True
            },
            "pretty_team_cell":        {
                "bg_color":     "#FFFFFF",
                "font_color":   "#000000",
                "valign":       "vcenter",
                "align":        "center",
                "text_wrap":    "text_wrap",
                "num_format":   1,
                "left":         True,
                "right":        True,
                "bottom":       True,
                "bottom_color": "#DADADA",
                "bold":         True
            },
            "pretty_data_cell":        {
                "bg_color":     "#FFFFFF",
                "font_color":   "#000000",
                "valign":       "vcenter",
                "align":        "center",
                "text_wrap":    "text_wrap",
                "num_format":   2,
                "left":         True,
                "right":        True,
                "bottom":       True,
                "bottom_color": "#DADADA"
            },
            "pretty_data_cell_int":    {
                "bg_color":     "#FFFFFF",
                "font_color":   "#000000",
                "valign":       "vcenter",
                "align":        "center",
                "text_wrap":    "text_wrap",
                "num_format":   1,
                "left":         True,
                "right":        True,
                "bottom":       True,
                "bottom_color": "#DADADA"
            },
            "pretty_avg_cell":         {
                "bg_color":     "#B2DFDB",
                "font_color":   "#000000",
                "valign":       "vcenter",
                "align":        "center",
                "text_wrap":    "text_wrap",
                "bold":         True,
                "num_format":   2,
                "left":         True,
                "right":        True,
                "bottom":       True,
                "bottom_color": "#DADADA"
            },
            "schedule_data_cell":      {
                "bg_color":     "#FFFFFF",
                "font_color":   "#000000",
                "valign":       "vcenter",
                "align":        "center",
                "text_wrap":    "text_wrap",
                "num_format":   1,
                "left":         True,
                "right":        True,
                "bottom":       True,
                "bottom_color": "#DADADA"
            },
            "schedule_header":         {
                "bg_color":   "#FFFFFF",
                "font_color": "#000000",
                "bold":       True,
                "valign":     "bottom",
                "align":      "center",
                "text_wrap":  "text_wrap",
                "border":     True
            },
            "red_alliance_header":     {
                "bg_color":   "#EF9A9A",
                "font_color": "#000000",
                "bold":       True,
                "valign":     "bottom",
                "align":      "center",
                "text_wrap":  "text_wrap",
                "border":     True
            },
            "red_alliance_data_cell":  {
                "bg_color":     "#FFCDD2",
                "font_color":   "#000000",
                "valign":       "vcenter",
                "align":        "center",
                "num_format":   1,
                "left":         True,
                "right":        True,
                "bottom":       True,
                "bottom_color": "#FFEBEE"
            },
            "blue_alliance_header":    {
                "bg_color":   "#90CAF9",
                "font_color": "#000000",
                "bold":       True,
                "valign":     "bottom",
                "align":      "center",
                "text_wrap":  "text_wrap",
                "border":     True
            },
            "blue_alliance_data_cell": {
                "bg_color":     "#BBDEFB",
                "font_color":   "#000000",
                "valign":       "vcenter",
                "align":        "center",
                "num_format":   1,
                "left":         True,
                "right":        True,
                "bottom":       True,
                "bottom_color": "#E3F2FD"
            },
            "bold":                    {
                "bold": True
            },
            "team_input":              {
                "num_format":   1,
                "bg_color":     "#B2DFDB",
                "border":       True,
                "border_color": "#DADADA"
            },
            "team_input_label":        {
                "bg_color":     "#FFFFFF",
                "border":       True,
                "border_color": "#DADADA"
            }
        }

        self.range_formats = {
            'max_green': {
                'type':      '2_color_scale',
                'min_color': "#FFFFFF",
                'max_color': "#66BB6A"
            },
            'max_red':   {
                'type':      '2_color_scale',
                'min_color': "#FFFFFF",
                'max_color': "#EF5350"
            }
        }

        self.headers = {
            "matches":        [
                {
                    "title":         "Match",
                    "key":           "match_number",
                    "format":        "schedule_data_cell",
                    "header_format": "schedule_header"
                },
                {
                    "title":         "Red 1",
                    "key":           "red_1",
                    "format":        "red_alliance_data_cell",
                    "header_format": "red_alliance_header"
                },
                {
                    "title":         "Red 2",
                    "key":           "red_2",
                    "format":        "red_alliance_data_cell",
                    "header_format": "red_alliance_header"
                },
                {
                    "title":         "Red 3",
                    "key":           "red_3",
                    "format":        "red_alliance_data_cell",
                    "header_format": "red_alliance_header"
                },
                {
                    "title":         "Blue 1",
                    "key":           "blue_1",
                    "format":        "blue_alliance_data_cell",
                    "header_format": "blue_alliance_header"
                },
                {
                    "title":         "Blue 2",
                    "key":           "blue_2",
                    "format":        "blue_alliance_data_cell",
                    "header_format": "blue_alliance_header"
                },
                {
                    "title":         "Blue 3",
                    "key":           "blue_3",
                    "format":        "blue_alliance_data_cell",
                    "header_format": "blue_alliance_header"
                },
                {
                    "title":         "Red Score",
                    "key":           "alliances.red.score",
                    "format":        "red_alliance_data_cell",
                    "header_format": "red_alliance_header"
                },
                {
                    "title":         "Blue Score",
                    "key":           "alliances.blue.score",
                    "format":        "blue_alliance_data_cell",
                    "header_format": "blue_alliance_header"
                },
                {
                    "title":         "Red RP",
                    "key":           "score_breakdown.red.rp",
                    "format":        "red_alliance_data_cell",
                    "header_format": "red_alliance_header"
                },
                {
                    "title":         "Blue RP",
                    "key":           "score_breakdown.blue.rp",
                    "format":        "blue_alliance_data_cell",
                    "header_format": "blue_alliance_header"
                },
                {
                    "title":         "Red Auto Switch Ownership Sec",
                    "key":           "score_breakdown.red.autoSwitchOwnershipSec",
                    "format":        "red_alliance_data_cell",
                    "header_format": "red_alliance_header",
                    "hidden":        True
                },
                {
                    "title":         "Blue Auto Switch Ownership Sec",
                    "key":           "score_breakdown.blue.autoSwitchOwnershipSec",
                    "format":        "blue_alliance_data_cell",
                    "header_format": "blue_alliance_header",
                    "hidden":        True
                },
                {
                    "title":         "Red Auto Scale Ownership Sec",
                    "key":           "score_breakdown.red.autoScaleOwnershipSec",
                    "format":        "red_alliance_data_cell",
                    "header_format": "red_alliance_header",
                    "hidden":        True
                },
                {
                    "title":         "Blue Auto Scale Ownership Sec",
                    "key":           "score_breakdown.blue.autoScaleOwnershipSec",
                    "format":        "blue_alliance_data_cell",
                    "header_format": "blue_alliance_header",
                    "hidden":        True
                },
                {
                    "title":         "Red Auto Run Points",
                    "key":           "score_breakdown.red.autoRunPoints",
                    "format":        "red_alliance_data_cell",
                    "header_format": "red_alliance_header",
                    "hidden":        True
                },
                {
                    "title":         "Blue Auto Run Points",
                    "key":           "score_breakdown.blue.autoRunPoints",
                    "format":        "blue_alliance_data_cell",
                    "header_format": "blue_alliance_header",
                    "hidden":        True
                },
                {
                    "title":         "Red Tele Switch Ownership Sec",
                    "key":           "score_breakdown.red.teleopSwitchOwnershipSec",
                    "format":        "red_alliance_data_cell",
                    "header_format": "red_alliance_header",
                    "hidden":        True
                },
                {
                    "title":         "Blue Tele Switch Ownership Sec",
                    "key":           "score_breakdown.blue.teleopSwitchOwnershipSec",
                    "format":        "blue_alliance_data_cell",
                    "header_format": "blue_alliance_header",
                    "hidden":        True
                },
                {
                    "title":         "Red Tele Scale Ownership Sec",
                    "key":           "score_breakdown.red.teleopScaleOwnershipSec",
                    "format":        "red_alliance_data_cell",
                    "header_format": "red_alliance_header",
                    "hidden":        True
                },
                {
                    "title":         "Blue Tele Scale Ownership Sec",
                    "key":           "score_breakdown.blue.teleopScaleOwnershipSec",
                    "format":        "blue_alliance_data_cell",
                    "header_format": "blue_alliance_header",
                    "hidden":        True
                },
                {
                    "title":         "Red Climb Points",
                    "key":           "score_breakdown.red.endgamePoints",
                    "format":        "red_alliance_data_cell",
                    "header_format": "red_alliance_header",
                    "hidden":        True
                },
                {
                    "title":         "Blue Climb Points",
                    "key":           "score_breakdown.blue.endgamePoints",
                    "format":        "blue_alliance_data_cell",
                    "header_format": "blue_alliance_header",
                    "hidden":        True
                },
                {
                    "title":         "Red Boost",
                    "key":           "score_breakdown.red.vaultBoostPlayed",
                    "format":        "red_alliance_data_cell",
                    "header_format": "red_alliance_header",
                    "hidden":        True
                },
                {
                    "title":         "Blue Boost",
                    "key":           "score_breakdown.blue.vaultBoostPlayed",
                    "format":        "blue_alliance_data_cell",
                    "header_format": "blue_alliance_header",
                    "hidden":        True
                },
                {
                    "title":         "Red Force",
                    "key":           "score_breakdown.red.vaultForcePlayed",
                    "format":        "red_alliance_data_cell",
                    "header_format": "red_alliance_header",
                    "hidden":        True
                },
                {
                    "title":         "Blue Force",
                    "key":           "score_breakdown.blue.vaultForcePlayed",
                    "format":        "blue_alliance_data_cell",
                    "header_format": "blue_alliance_header",
                    "hidden":        True
                },
                {
                    "title":         "Red Levitate",
                    "key":           "score_breakdown.red.vaultLevitatePlayed",
                    "format":        "red_alliance_data_cell",
                    "header_format": "red_alliance_header",
                    "hidden":        True
                },
                {
                    "title":         "Blue Levitate",
                    "key":           "score_breakdown.blue.vaultLevitatePlayed",
                    "format":        "blue_alliance_data_cell",
                    "header_format": "blue_alliance_header",
                    "hidden":        True
                },
                {
                    "title":         "Red Home Switch Cubes",
                    "key":           "red_own_switch_cubes",
                    "value":         "=IFERROR(SUM(FILTER(raw_tele_scored_own_switch, raw_match=INDEX(schedule_match_number, ROW()), raw_pos < 3)))",
                    "format":        "red_alliance_data_cell",
                    "header_format": "red_alliance_header",
                    "hidden":        True
                },
                {
                    "title":         "Blue Away Switch Cubes",
                    "key":           "blue_opp_switch_cubes",
                    "value":         "=IFERROR(SUM(FILTER(raw_tele_scored_opp_switch, raw_match=INDEX(schedule_match_number, ROW()), raw_pos > 2)))",
                    "format":        "blue_alliance_data_cell",
                    "header_format": "blue_alliance_header",
                    "hidden":        True
                },
                {
                    "title":         "Red Away Switch Cubes",
                    "key":           "red_opp_switch_cubes",
                    "value":         "=IFERROR(SUM(FILTER(raw_tele_scored_opp_switch, raw_match=INDEX(schedule_match_number, ROW()), raw_pos < 3)))",
                    "format":        "red_alliance_data_cell",
                    "header_format": "red_alliance_header",
                    "hidden":        True
                },
                {
                    "title":         "Blue Home Switch Cubes",
                    "key":           "blue_own_switch_cubes",
                    "value":         "=IFERROR(SUM(FILTER(raw_tele_scored_own_switch, raw_match=INDEX(schedule_match_number, ROW()), raw_pos > 2)))",
                    "format":        "blue_alliance_data_cell",
                    "header_format": "blue_alliance_header",
                    "hidden":        True
                },
                {
                    "title":         "Red Scale Cubes",
                    "key":           "red_scale_cubes",
                    "value":         "=IFERROR(SUM(FILTER(raw_tele_scored_scale, raw_match=INDEX(schedule_match_number, ROW()), raw_pos < 3)))",
                    "format":        "red_alliance_data_cell",
                    "header_format": "red_alliance_header",
                    "hidden":        True
                },
                {
                    "title":         "Blue Scale Cubes",
                    "key":           "blue_scale_cubes",
                    "value":         "=IFERROR(SUM(FILTER(raw_tele_scored_scale, raw_match=INDEX(schedule_match_number, ROW()), raw_pos > 2)))",
                    "format":        "blue_alliance_data_cell",
                    "header_format": "blue_alliance_header",
                    "hidden":        True
                }
            ],
            "analysis":       [
                {
                    "title":  "Team",
                    "key":    "team_number",
                    "value":  "",
                    "format": "pretty_team_cell"
                },
                {
                    "title": "Num Matches",
                    "key":   "match",
                    "value": "=IF(ISBLANK(analysis_team_number), \"\", COUNTIF(raw_team_number, \"=\"&analysis_team_number))"
                },
                {
                    "title": "Num Times Auto No Move",
                    "key":   "auto_no_move",
                    "scale": "max_red",
                    "func":  "sum"
                },
                {
                    "title": "Num Times Auto Wrong Side",
                    "key":   "auto_wrong_switch",
                    "scale": "max_red",
                    "func":  "sum"
                },
                {
                    "title": "Avg Auto Scored Exchange",
                    "key":   "auto_scored_exchange",
                    "scale": "max_green",
                    "func":  "avg"
                },
                {
                    "title": "Avg Auto Scored Switch",
                    "key":   "auto_scored_switch",
                    "scale": "max_green",
                    "func":  "avg"
                },
                {
                    "title": "Avg Auto Scored Scale",
                    "key":   "auto_scored_scale",
                    "scale": "max_green",
                    "func":  "avg"
                },
                {
                    "title": "Avg Auto Cubes Scored",
                    "key":   "calculated_auto_cubes_scored",
                    "scale": "max_green",
                    "value": "=IF(ISBLANK(analysis_team_number), \"\", SUMIF(raw_team_number, \"=\"&analysis_team_number, raw_calculated_auto_cubes_scored) / analysis_match)"
                },
                {
                    "title": "Avg Scored Exchange",
                    "key":   "tele_scored_exchange",
                    "scale": "max_green",
                    "func":  "avg"
                },
                {
                    "title": "Avg Scored Home Switch",
                    "key":   "tele_scored_own_switch",
                    "scale": "max_green",
                    "func":  "avg"
                },
                {
                    "title": "Avg Scored Away Switch",
                    "key":   "tele_scored_opp_switch",
                    "scale": "max_green",
                    "func":  "avg"
                },
                {
                    "title": "Avg Scored Scale",
                    "key":   "tele_scored_scale",
                    "scale": "max_green",
                    "func":  "avg"
                },
                {
                    "title": "Avg Knocked Off Scale",
                    "key":   "tele_descored_scale",
                    "scale": "max_red",
                    "func":  "avg"
                },
                {
                    "title": "Avg Cubes Dropped",
                    "key":   "tele_dropped_cubes",
                    "scale": "max_red",
                    "func":  "avg"
                },
                {
                    "title": "Avg Cubes Scored",
                    "key":   "calculated_tele_cubes_scored",
                    "scale": "max_green",
                    "value": "=IF(ISBLANK(analysis_team_number), \"\", SUMIF(raw_team_number, \"=\"&analysis_team_number, raw_calculated_tele_cubes_scored) / analysis_match)"
                },
                {
                    "title": "Avg Switch Cubes Scored",
                    "key":   "calculated_switch_cubes_scored",
                    "scale": "max_green",
                    "value": "=IF(ISBLANK(analysis_team_number), \"\", SUMIF(raw_team_number, \"=\"&analysis_team_number, raw_calculated_switch_cubes_scored) / analysis_match)"
                },
                {
                    "title": "Self Lifting",
                    "key":   "tele_climbed_self",
                    "value": "=CONCAT(IF(COUNTIF(FILTER(raw_tele_climbed_self, raw_team_number=INDEX(analysis_team_number, ROW())), \"=S\")>0, CONCAT(\"  [S]\", COUNTIF(FILTER(raw_tele_climbed_self, raw_team_number=INDEX(analysis_team_number, ROW())), \"=S\")), \"\"),IF(COUNTIF(FILTER(raw_tele_climbed_self, raw_team_number =INDEX(analysis_team_number, ROW())), \"=F\")>0, CONCAT(\"  [F]\", COUNTIF(FILTER(raw_tele_climbed_self, raw_team_number=INDEX(analysis_team_number, ROW())), \"=F\")), \"\"))",
                    "width": 10
                },
                {
                    "title": "Climb Setup Times",
                    "key":   "tele_setup_climb_time",
                    "value": "=CONCAT(CONCAT(CONCAT(IF(COUNTIF(FILTER(raw_tele_setup_climb_time, raw_team_number=INDEX(analysis_team_number, ROW())), \"=<5\")>0, CONCAT(\"  [<5]\", COUNTIF(FILTER(raw_tele_setup_climb_time, raw_team_number=INDEX(analysis_team_number, ROW())), \"=<5\")), \"\"), IF(COUNTIF(FILTER(raw_tele_setup_climb_time, raw_team_number=INDEX(analysis_team_number, ROW())), \"=<10\")>0, CONCAT(\"  [<10]\", COUNTIF(FILTER(raw_tele_setup_climb_time, raw_team_number=INDEX(analysis_team_number, ROW())), \"=<10\")), \"\")),CONCAT(IF(COUNTIF(FILTER(raw_tele_setup_climb_time, raw_team_number=INDEX(analysis_team_number, ROW())), \"=<20\")>0, CONCAT(\"  [<20]\", COUNTIF(FILTER(raw_tele_setup_climb_time, raw_team_number=INDEX(analysis_team_number, ROW())), \"=<20\")), \"\"), IF(COUNTIF(FILTER(raw_tele_setup_climb_time, raw_team_number=INDEX(analysis_team_number, ROW())), \"=<30\")>0, CONCAT(\"  [<30]\", COUNTIF(FILTER(raw_tele_setup_climb_time, raw_team_number=INDEX(analysis_team_number, ROW())), \"=<30\")), \"\"))),CONCAT(CONCAT(IF(COUNTIF(FILTER(raw_tele_setup_climb_time, raw_team_number=INDEX(analysis_team_number, ROW())), \"=<40\")>0, CONCAT(\"  [<40]\", COUNTIF(FILTER(raw_tele_setup_climb_time, raw_team_number=INDEX(analysis_team_number, ROW())), \"=<40\")), \"\"), IF(COUNTIF(FILTER(raw_tele_setup_climb_time, raw_team_number=INDEX(analysis_team_number, ROW())), \"=<50\")>0, CONCAT(\"  [<50]\", COUNTIF(FILTER(raw_tele_setup_climb_time, raw_team_number=INDEX(analysis_team_number, ROW())), \"=<50\")), \"\")),CONCAT(IF(COUNTIF(FILTER(raw_tele_setup_climb_time, raw_team_number=INDEX(analysis_team_number, ROW())), \"=<60\")>0, CONCAT(\"  [<60]\", COUNTIF(FILTER(raw_tele_setup_climb_time, raw_team_number=INDEX(analysis_team_number, ROW())), \"<60\")), \"\"), IF(COUNTIF(FILTER(raw_tele_setup_climb_time, raw_team_number=INDEX(analysis_team_number, ROW())), \"=60+\")>0, CONCAT(\"  [60+]\", COUNTIF(FILTER(raw_tele_setup_climb_time, raw_team_number=INDEX(analysis_team_number, ROW())), \"=60+\")), \"\"))))",
                    "width": 16
                },
                {
                    "title": "Avg Partners Lifted",
                    "key":   "tele_partners_lifted",
                    "scale": "max_green",
                    "func":  "avg"
                },
                {
                    "title":  "Avg Partners Attempted",
                    "key":    "tele_partners_attempted",
                    "scale":  "max_green",
                    "func":   "avg",
                    "hidden": True
                },
                {
                    "title": "Num Times Dropped Partner",
                    "key":   "tele_partner_dropped",
                    "scale": "max_red",
                    "func":  "sum"
                },
                {
                    "title":  "Num Times Lifted By Partner",
                    "key":    "tele_lifted_by_partner",
                    "func":   "sum",
                    "hidden": True
                },
                {
                    "title":  "Parked",
                    "key":    "tele_parked",
                    "value":  "=CONCAT(IF(COUNTIF(FILTER(raw_tele_parked, raw_team_number=INDEX(analysis_team_number, ROW())), \"=S\")>0, CONCAT(\"  [S]\", COUNTIF(FILTER(raw_tele_parked, raw_team_number=INDEX(analysis_team_number, ROW())), \"=S\")), \"\"),IF(COUNTIF(FILTER(raw_tele_parked, raw_team_number=INDEX(analysis_team_number, ROW())), \"=F\")>0, CONCAT(\"  [F]\", COUNTIF(FILTER(raw_tele_parked, raw_team_number=INDEX(analysis_team_number, ROW())), \"=F\")), \"\"))",
                    "width":  14,
                    "hidden": True
                },
                {
                    "title": "Defense",
                    "key":   "tele_defense",
                    "value": "=CONCAT(CONCAT(IF(COUNTIF(FILTER(raw_tele_defense, raw_team_number=INDEX(analysis_team_number, ROW())), \"=🔥\")>0, CONCAT(\"  [🔥]\", COUNTIF(FILTER(raw_tele_defense, raw_team_number=INDEX(analysis_team_number, ROW())), \"=🔥\")), \"\"),IF(COUNTIF(FILTER(raw_tele_defense, raw_team_number=INDEX(analysis_team_number, ROW())), \"=👍\")>0, CONCAT(\"  [👍]\", COUNTIF(FILTER(raw_tele_defense, raw_team_number=INDEX(analysis_team_number, ROW())), \"=👍\")), \"\")),CONCAT(IF(COUNTIF(FILTER(raw_defense, raw_team_number=INDEX(analysis_team_number, ROW())), \"=👎\")>0, CONCAT(\"  [👎]\", COUNTIF(FILTER(raw_defense, raw_team_number=INDEX(analysis_team_number, ROW())), \"=👎\")), \"\"),IF(COUNTIF(FILTER(raw_defense, raw_team_number=INDEX(analysis_team_number, ROW())), \"=💩\")>0, CONCAT(\"  [💩]\", COUNTIF(FILTER(raw_defense, raw_team_number=INDEX(analysis_team_number, ROW())), \"=💩\")), \"\")))",
                    "width": 14
                },
                {
                    "title": "Avg % of Match Cubes Scored",
                    "key":   "calculated_percent_match_cubes",
                    "scale": "max_green",
                    "value": "=IF(ISBLANK(analysis_team_number), \"\", SUMIF(raw_team_number, \"=\"&analysis_team_number, raw_calculated_percent_match_cubes) / analysis_match)"
                },
                {
                    "title": "Avg % of Match Scale Cubes Scored",
                    "key":   "calculated_percent_match_scale_cubes",
                    "scale": "max_green",
                    "value": "=IF(ISBLANK(analysis_team_number), \"\", SUMIF(raw_team_number, \"=\"&analysis_team_number, raw_calculated_percent_match_scale_cubes) / analysis_match)"
                },
                {
                    "title": "Avg % of Match Switch Cubes Scored",
                    "key":   "calculated_percent_match_switch_cubes",
                    "scale": "max_green",
                    "value": "=IF(ISBLANK(analysis_team_number), \"\", SUMIF(raw_team_number, \"=\"&analysis_team_number, raw_calculated_percent_match_switch_cubes) / analysis_match)"
                },
                {
                    "title": "Avg % of Alliance Exchange Cubes Scored",
                    "key":   "calculated_percent_alliance_exchange_cubes",
                    "scale": "max_green",
                    "value": "=IF(ISBLANK(analysis_team_number), \"\", SUMIF(raw_team_number, \"=\"&analysis_team_number, raw_calculated_percent_alliance_exchange_cubes) / analysis_match)"
                },
                {
                    "title": "Num Wins",
                    "key":   "calculated_win",
                    "scale": "max_green",
                    "func":  "sum"
                },
                {
                    "title": "Avg Score",
                    "key":   "calculated_alliance_score",
                    "scale": "max_green",
                    "func":  "avg"
                }
            ],
            "team_list":      [
                {
                    "key":           "team_number",
                    "title":         "Team Number",
                    "format":        "schedule_data_cell",
                    "header_format": "schedule_header"
                },
                {
                    "key":           "nickname",
                    "title":         "Name",
                    "width":         30,
                    "format":        "schedule_data_cell",
                    "header_format": "schedule_header"
                },
                {
                    "key":           "num_events",
                    "title":         "Num Events",
                    "format":        "schedule_data_cell",
                    "header_format": "schedule_header"
                },
                {
                    "key":           "prev_events",
                    "title":         "Prev Events",
                    "format":        "schedule_data_cell",
                    "header_format": "schedule_header"
                }
            ],
            "raw_calculated": [
                {
                    "value":  "=INDEX(raw_match, ROW())",
                    "key":    "match",
                    "title":  "M#",
                    "format": "pretty_data_cell_int"
                },
                {
                    "value":  "=INDEX(raw_pos, ROW())",
                    "key":    "pos",
                    "title":  "P#",
                    "format": "pretty_data_cell_int"
                },
                {
                    "value":  "=INDEX(raw_team_number, ROW())",
                    "key":    "team_number",
                    "title":  "Team",
                    "format": "pretty_data_cell_int"
                },
                {
                    "value":  "=INDEX(raw_tele_scored_scale, ROW()) + INDEX(raw_tele_scored_own_switch, ROW()) + INDEX(raw_tele_scored_opp_switch, ROW()) + INDEX(raw_tele_scored_exchange, ROW())",
                    "key":    "tele_cubes_scored",
                    "title":  " Cubes Scored",
                    "format": "pretty_data_cell_int"
                },
                {
                    "value":  "=INDEX(raw_tele_scored_own_switch, ROW()) + INDEX(raw_tele_scored_opp_switch, ROW())",
                    "key":    "switch_cubes_scored",
                    "title":  " Switch Cubes Scored",
                    "format": "pretty_data_cell_int"
                },
                {
                    "value":  "=INDEX(raw_auto_scored_scale, ROW()) + INDEX(raw_auto_scored_switch, ROW()) + INDEX(raw_auto_scored_exchange, ROW())",
                    "key":    "auto_cubes_scored",
                    "title":  "Auto Cubes Scored",
                    "format": "pretty_data_cell_int"
                },
                {
                    "value": "=IFERROR(raw_calculated_tele_cubes_scored / SUM(FILTER(raw_calculated_tele_cubes_scored, raw_calculated_match=INDEX(raw_calculated_match, ROW()))) * 100, 0)",
                    "key":   "percent_match_cubes",
                    "title": "% of Match Cubes"
                },
                {
                    "value": "=IFERROR(raw_tele_scored_scale / SUM(FILTER(raw_tele_scored_scale, raw_match=INDEX(raw_calculated_match, ROW()))) * 100, 0)",
                    "key":   "percent_match_scale_cubes",
                    "title": "% of Match Scale Cubes"
                },
                {
                    "value": "=IFERROR((raw_tele_scored_own_switch + raw_tele_scored_opp_switch) / SUM(FILTER(raw_tele_scored_own_switch, raw_match=INDEX(raw_calculated_match, ROW())), FILTER(raw_tele_scored_opp_switch, raw_match=INDEX(raw_calculated_match, ROW()))) * 100, 0)",
                    "key":   "percent_match_switch_cubes",
                    "title": "% of Match Switch Cubes"
                },
                {
                    "value": "=IFERROR(raw_tele_scored_exchange / SUM(FILTER(raw_tele_scored_exchange, raw_match=INDEX(raw_calculated_match, ROW()), raw_pos < IF(INDEX(raw_calculated_pos, ROW()) > 2, 6, 3), raw_pos > IF(INDEX(raw_calculated_pos, ROW()) > 2, 2, -1))) * 100, 0)",
                    "key":   "percent_alliance_exchange_cubes",
                    "title": "% of Alliance Exchange Cubes"
                },
                {
                    "value":  "=LOOKUP(raw_calculated_match, schedule_match_number, IF(raw_calculated_pos < 3, schedule_alliances.red.score, schedule_alliances.blue.score))",
                    "key":    "alliance_score",
                    "title":  "Alliance Score",
                    "format": "pretty_data_cell_int"
                },
                {
                    "value":  "=IF(raw_calculated_alliance_score > LOOKUP(raw_calculated_match, schedule_match_number, IF(raw_calculated_pos < 3, schedule_alliances.blue.score, schedule_alliances.red.score)), 1, 0)",
                    "key":    "win",
                    "title":  "Win",
                    "format": "pretty_data_cell_int"
                }
            ],
            "raw":            [
                {
                    "key":    "team_number",
                    "title":  "Team",
                    "format": "pretty_data_cell_int"
                },
                {
                    "key":    "match",
                    "title":  "M#",
                    "format": "pretty_data_cell_int"
                },
                {
                    "key":    "pos",
                    "title":  "P#",
                    "format": "pretty_data_cell_int"
                },
                {
                    "key":    "auto_no_move",
                    "title":  "Auto No Move",
                    "format": "pretty_data_cell_int"
                },
                {
                    "key":    "auto_wrong_switch",
                    "title":  "Auto Wrong Side",
                    "format": "pretty_data_cell_int"
                },
                {
                    "key":    "auto_scored_exchange",
                    "title":  "Auto Scored Ex",
                    "format": "pretty_data_cell_int"
                },
                {
                    "key":    "auto_scored_switch",
                    "title":  "Auto Scored Switch",
                    "format": "pretty_data_cell_int"
                },
                {
                    "key":    "auto_scored_scale",
                    "title":  "Auto Scored Scale",
                    "format": "pretty_data_cell_int"
                },
                {
                    "key":    "tele_scored_exchange",
                    "title":  "Scored Exchange",
                    "format": "pretty_data_cell_int"
                },
                {
                    "key":    "tele_scored_own_switch",
                    "title":  "Scored Own Switch",
                    "format": "pretty_data_cell_int"
                },
                {
                    "key":    "tele_scored_opp_switch",
                    "title":  "Scored Opp Switch",
                    "format": "pretty_data_cell_int"
                },
                {
                    "key":    "tele_scored_scale",
                    "title":  "Scored Scale",
                    "format": "pretty_data_cell_int"
                },
                {
                    "key":    "tele_descored_scale",
                    "title":  "Knocked Off Scale",
                    "format": "pretty_data_cell_int"
                },
                {
                    "key":    "tele_dropped_cubes",
                    "title":  "Dropped Cubes",
                    "format": "pretty_data_cell_int"
                },
                {
                    "key":   "tele_climbed_self",
                    "title": "Lifted Self"
                },
                {
                    "key":   "tele_setup_climb_time",
                    "title": "Setup Climb"
                },
                {
                    "key":    "tele_partners_lifted",
                    "title":  "Partners Lifted",
                    "format": "pretty_data_cell_int"
                },
                {
                    "key":    "tele_partners_attempted",
                    "title":  "Partners Attempted",
                    "format": "pretty_data_cell_int",
                    "hidden": True
                },
                {
                    "key":    "tele_partner_dropped",
                    "title":  "Dropped Partner",
                    "format": "pretty_data_cell_int"
                },
                {
                    "key":   "tele_lifted_by_partner",
                    "title": "Lifted By Partner"
                },
                {
                    "key":   "tele_parked",
                    "title": "Parked"
                },
                {
                    "key":   "tele_defense",
                    "title": "Defense"
                }
            ]
        }

    def create_spreadsheet_for_event(self, event_id, filename='Clooney.xlsx'):
        self.workbook = xlsxwriter.Workbook(filename)
        self.formats = dict([(k, self.workbook.add_format(v)) for k, v in self.raw_formats.items()])

        # db = sqlite3.connect(self.db_path)
        db = self.db_path
        self.event = list(db.engine.execute('SELECT * FROM events WHERE id = "{}"'.format(event_id)))[0]
        self.raw_entries = [json.loads(e[-2]) for e in
                            list(db.engine.execute('SELECT * FROM scouting_entries WHERE event = "{}"'.format(event_id)))]
        self.teams = sorted(json.loads(self.event[2]), key=lambda x: int(x['team_number']))
        self.matches = sorted([e for e in self.tba.get_event_matches(event_id) if e['comp_level'] == 'qm'],
                              key=lambda x: x['match_number'])
        for match in self.matches:
            for alli in ['red', 'blue']:
                for i in range(3):
                    match[alli + '_' + str(i + 1)] = int(match['alliances'][alli]['team_keys'][i][3:])

        self.draw_pretty_analysis()
        self.draw_pretty_match_rundown()
        self.draw_pretty_team_stats()
        self.draw_pretty_team_schedule()
        self.draw_pretty_schedule()
        self.draw_pretty_team_list()
        self.draw_pretty_raw_data()

        self.draw_raw_data()
        self.draw_raw_calculated()
        self.draw_raw_analysis()
        self.draw_raw_team_list()
        self.draw_raw_schedule()
        self.draw_raw_team_matches()

        self.workbook.close()
        self.workbook = None
        print("Created Workbook for {}".format(event_id))

    @staticmethod
    def next_col(col, i=1):
        col = list(col)
        while i > 0:
            if col[-1] == 'Z':
                col[-1] = 'A'
                col.append('A')
            else:
                col[-1] = chr(ord(col[-1]) + 1)
            i -= 1
        return "".join(col)

    def name_col(self, name, page, col, num_rows=999, start_row=1):
        self.workbook.define_name(name, "='{0}'!{1}{3}:{1}{2}".format(page, col, num_rows + start_row, start_row))

    def name_range(self, name, page, start_row=None, start_col='A', end_col='Z', end_row=None):
        range_str = "='{0}'!{1}{3}:{2}{4}".format(page, start_col, end_col,
                                                  start_row if start_row is not None else "",
                                                  (end_row if end_row is not None else start_row)
                                                  if start_row is not None else "")
        self.workbook.define_name(name, range_str)

    def draw_raw_data(self):
        page_name = self.page_names['raw']
        headers = self.headers['raw']
        sheet = self.workbook.add_worksheet(page_name)
        sheet.set_tab_color('red')
        sheet.hide()
        col = 'A'
        row = 1
        header_cols = {}
        data_len = len(self.raw_entries)
        for header in headers:
            sheet.write(self.get_cell(col, row), header['title'])
            self.name_col('raw_{}'.format(header['key']), page_name, col, data_len + 1)
            header_cols[header['key']] = col
            col = self.next_col(col)

        for i in range(data_len):
            for header in headers:
                col = header_cols[header['key']]
                val = self.raw_entries[i][header['key']]
                sheet.write(self.get_cell(col, i + 2), val, self.formats['raw_data_cell'])

    def draw_raw_calculated(self):
        page_name = self.page_names['raw_calculated']
        headers = self.headers['raw_calculated']
        sheet = self.workbook.add_worksheet(page_name)
        sheet.set_tab_color('red')
        sheet.hide()
        data_len = len(self.raw_entries)
        col = 'A'
        for header in headers:
            sheet.write(self.get_cell(col, 1), header['title'])
            self.name_col('raw_calculated_{}'.format(header['key']), page_name, col, data_len + 1)
            for i in range(data_len):
                sheet.write(self.get_cell(col, i + 2), header['value'], self.formats['raw_data_cell'])
            col = self.next_col(col)

    def draw_raw_analysis(self):
        page_name = self.page_names['raw_analysis']
        headers = self.headers['analysis']
        sheet = self.workbook.add_worksheet(page_name)
        sheet.set_tab_color('red')
        sheet.hide()
        num_teams = len(self.teams)

        functions = {
            'avg': '=IF(ISBLANK(analysis_team_number), "", SUMIF(raw_team_number, "="&analysis_team_number, {}) / analysis_match)',
            'sum': '=IF(ISBLANK(analysis_team_number), "", SUMIF(raw_team_number, "="&analysis_team_number, {}))'
        }

        col = 'A'
        for header in headers:
            sheet.write(self.get_cell(col, 1), header['title'])
            self.name_col('analysis_{}'.format(header['key']), page_name, col, num_teams + 1)
            for i in range(num_teams):
                if header['key'] == 'team_number':
                    sheet.write(self.get_cell(col, i + 2), self.teams[i]['team_number'], self.formats['raw_data_cell'])
                elif 'func' in header.keys():
                    value = functions[header['func']].format('raw_{}'.format(header['key']))
                    sheet.write(self.get_cell(col, i + 2), value, self.formats['raw_data_cell'])
                else:
                    sheet.write(self.get_cell(col, i + 2), header['value'], self.formats['raw_data_cell'])
            col = self.next_col(col)

    def draw_raw_team_list(self):
        page_name = self.page_names['raw_team_list']
        headers = self.headers['team_list']
        sheet = self.workbook.add_worksheet(page_name)
        sheet.set_tab_color('red')
        sheet.hide()
        data_len = len(self.teams)
        col = 'A'
        for header in headers:
            sheet.write(self.get_cell(col, 1), header['title'])
            self.name_col('team_list_{}'.format(header['key']), page_name, col, data_len + 1)
            if header['key'] == 'team_number':
                self.name_col('team_number_list', page_name, col, data_len, 2)
            for i in range(data_len):
                sheet.write(self.get_cell(col, i + 2), self.teams[i][header['key']], self.formats['raw_data_cell'])
            col = self.next_col(col)

    def draw_raw_team_matches(self):
        page_name = self.page_names['raw_team_schedule']
        sheet = self.workbook.add_worksheet(page_name)
        sheet.set_tab_color('red')
        sheet.hide()
        data_len = len(self.teams)
        col = 'A'
        sheet.write(self.get_cell(col, 1), 'Team Number')
        self.name_col('team_schedule_team_number', page_name, col)
        for i in range(data_len):
            sheet.write(self.get_cell(col, i + 2), self.teams[i]['team_number'], self.formats['raw_data_cell'])
        col = self.next_col(col)

        sheet.write(self.get_cell(col, 1), 'Matches')
        self.name_range('team_schedule_matches', page_name,
                        start_col=col, end_col=self.next_col(col, 20))
        for i in range(data_len):
            for j in range(20):
                sheet.write_array_formula(
                        "{0}:{0}".format(self.get_cell(self.next_col(col, j), i + 2)),
                        "=ArrayFormula(IFERROR(SMALL(IF(schedule_match_teams=$A{0},ROW(schedule_red_1)-1), ROW({1}:{1}))))".format(
                                i + 2, j + 1),
                        self.formats['raw_data_cell']
                )

    def draw_raw_schedule(self):
        page_name = self.page_names['raw_matches']
        headers = self.headers['matches']
        sheet = self.workbook.add_worksheet(page_name)
        sheet.set_tab_color('red')
        sheet.hide()
        data_len = len(self.matches)
        col = 'A'
        red_1_col = col
        blue_3_col = col
        for header in headers:
            sheet.write(self.get_cell(col, 1), header['title'])
            self.name_col('schedule_{}'.format(header['key']), page_name, col, data_len + 1)
            if header['key'] == 'red_1':
                red_1_col = col
            elif header['key'] == 'blue_3':
                blue_3_col = col
            for i in range(data_len):
                if "value" in header.keys() and header["value"]:
                    sheet.write(
                            self.get_cell(col, i + 2),
                            header['value'],
                            self.formats['raw_data_cell']
                    )
                else:
                    sheet.write(
                            self.get_cell(col, i + 2),
                            self._get_data(self.matches[i], header['key']),
                            self.formats['raw_data_cell']
                    )
            col = self.next_col(col)
        self.workbook.define_name(
                'schedule_match_teams',
                "='{0}'!{1}:{2}".format(page_name, red_1_col, blue_3_col)
        )

    def draw_pretty_raw_data(self):
        page_name = self.page_names['pretty_raw']
        raw_headers = self.headers['raw']
        calc_headers = self.headers['raw_calculated']
        sheet = self.workbook.add_worksheet(page_name)
        sheet.set_tab_color('blue')
        col = 'A'
        row = 1
        data_len = len(self.raw_entries)
        for header in raw_headers:
            sheet.write(
                    self.get_cell(col, row),
                    header['title'],
                    self.formats[header['header_format'] if 'header_format' in header.keys() else 'pretty_header']
            )
            for i in range(data_len):
                if col in ['A', 'B', 'C']:
                    sheet.write(
                            self.get_cell(col, i + 2),
                            self.raw_entries[i][header['key']],
                            self.formats[header['format'] if 'format' in header.keys() else 'pretty_data_cell'])
                else:
                    sheet.write(
                            self.get_cell(col, i + 2),
                            '=FILTER(raw_{}, raw_team_number=INDEX(A:A, ROW()), raw_match=INDEX(B:B, ROW()))'.format(
                                    header['key']),
                            self.formats[header['format'] if 'format' in header.keys() else 'pretty_data_cell'])
            col = self.next_col(col)

        for header in calc_headers[3:]:
            sheet.write(
                    self.get_cell(col, row),
                    header['title'],
                    self.formats[header['header_format'] if 'header_format' in header.keys() else 'pretty_header']
            )
            for i in range(data_len):
                sheet.write(
                        self.get_cell(col, i + 2),
                        '=FILTER(raw_calculated_{}, raw_team_number=INDEX(A:A, ROW()), raw_match=INDEX(B:B, ROW()))'.format(
                                header['key']),
                        self.formats[header['format'] if 'format' in header.keys() else 'pretty_data_cell']
                )
            col = self.next_col(col)

    def draw_pretty_team_list(self):
        page_name = self.page_names['pretty_team_list']
        headers = self.headers['team_list']
        sheet = self.workbook.add_worksheet(page_name)
        sheet.set_tab_color('blue')
        sheet.set_default_row(16, True)
        sheet.set_row(0, 35)
        data_len = len(self.teams)
        col = 'A'
        for header in headers:
            sheet.write(
                    self.get_cell(col, 1),
                    header['title'],
                    self.formats[header['header_format']] if 'format' in header.keys()
                    else self.formats['pretty_header']
            )
            options = {}
            if "hidden" in header.keys():
                options['hidden'] = header['hidden']
            sheet.set_column(self.get_col_range(col),
                             width=header['width'] if "width" in header.keys() else 8,
                             options=options)
            for i in range(data_len):
                sheet.write(
                        self.get_cell(col, i + 2),
                        self.teams[i][header['key']],
                        self.formats[header['format']] if 'format' in header.keys()
                        else self.formats['pretty_data_cell']
                )
            col = self.next_col(col)

    def draw_pretty_schedule(self):
        page_name = self.page_names['pretty_matches']
        headers = self.headers['matches']
        sheet = self.workbook.add_worksheet(page_name)
        sheet.set_tab_color('blue')
        sheet.set_default_row(16, True)
        sheet.set_row(0, 35)
        data_len = len(self.matches)
        col = 'A'
        for header in headers:
            sheet.write(
                    self.get_cell(col, 1),
                    header['title'],
                    self.formats[header['header_format']] if 'format' in header.keys() else self.formats[
                        'pretty_header']
            )
            options = {}
            if "hidden" in header.keys():
                options['hidden'] = header['hidden']
            for i in range(data_len):
                if "value" in header.keys() and header["value"]:
                    sheet.write(
                            self.get_cell(col, i + 2),
                            header['value'],
                            self.formats[header['format']] if 'format' in header.keys() else self.formats[
                                'pretty_data_cell']
                    )
                else:
                    sheet.write(
                            self.get_cell(col, i + 2),
                            self._get_data(self.matches[i], header['key']),
                            self.formats[header['format']] if 'format' in header.keys() else self.formats[
                                'pretty_data_cell']
                    )
            sheet.set_column(self.get_col_range(col),
                             width=header['width'] if "width" in header.keys() else 8,
                             options=options)
            if header['title'] == 'Red Score':
                sheet.conditional_format(self.get_col_range(col, 2, data_len), {
                    'type':               'formula',
                    'criteria':           '{0}2>{1}2'.format(col, self.next_col(col)),
                    'format': self.formats['bold']
                })
                sheet.conditional_format(self.get_col_range(self.next_col(col), 2, data_len), {
                    'type':               'formula',
                    'criteria':           '{0}2>{1}2'.format(self.next_col(col), col),
                    'format': self.formats['bold']
                })
            col = self.next_col(col)

    def draw_pretty_analysis(self):
        page_name = self.page_names['pretty_analysis']
        headers = self.headers['analysis']
        sheet = self.workbook.add_worksheet(page_name)
        sheet.set_tab_color('green')
        sheet.set_default_row(16, True)
        sheet.set_row(0, 70)
        data_len = len(self.teams)
        col = 'A'
        team_num_col = col
        for header in headers:
            sheet.write(
                    self.get_cell(col, 1),
                    header['title'],
                    self.formats[header['header_format']] if 'header_format' in header.keys()
                    else self.formats['pretty_header']
            )
            options = {}
            if "hidden" in header.keys():
                options['hidden'] = header['hidden']
            sheet.set_column(self.get_col_range(col), header['width'] if "width" in header.keys() else 8,
                             options=options)
            if header['key'] != 'team_number':
                if "scale" in header.keys():
                    sheet.conditional_format(self.get_col_range(col, 2, data_len), {
                        'type':     'cell',
                        'criteria': '=',
                        'value':    0,
                        'format':   self.formats[header['format']] if 'format' in header.keys()
                                    else self.formats['pretty_data_cell']
                    })
                    sheet.conditional_format(self.get_col_range(col, 2, data_len), self.range_formats[header['scale']])
            for i in range(data_len):
                if header['key'] == 'team_number':
                    sheet.write(
                            self.get_cell(col, i + 2),
                            self.teams[i]['team_number'],
                            self.formats[header['format']] if 'format' in header.keys()
                            else self.formats['pretty_data_cell']
                    )
                    team_num_col = col
                else:
                    formula = '=LOOKUP({0}, analysis_team_number, {1})'.format(
                            self.get_col_range(team_num_col),
                            'analysis_' + header['key']
                    )
                    sheet.write(
                            self.get_cell(col, i + 2),
                            formula,
                            self.formats[header['format']] if 'format' in header.keys()
                            else self.formats['pretty_data_cell']
                    )
            col = self.next_col(col)

    def draw_pretty_team_schedule(self):
        page_name = self.page_names['pretty_team_schedule']
        headers = self.headers['matches']
        sheet = self.workbook.add_worksheet(page_name)
        sheet.set_tab_color('blue')
        sheet.write('B2', 'Team:', self.formats['team_input_label'])
        sheet.write('C2', int(self.teams[0]["team_number"]), self.formats['team_input'])
        sheet.data_validation('C2', {
            'validate': 'list',
            'source':   '=team_number_list'
        })
        sheet.set_default_row(16, True)
        sheet.set_row(3, 35)
        data_len = 20
        col = 'B'
        match_num_col = col
        for header in headers:
            options = {}
            if "hidden" in header.keys():
                options['hidden'] = header['hidden']
            sheet.set_column(self.get_col_range(col),
                             width=header['width'] if "width" in header.keys() else 8,
                             options=options)
            sheet.write(
                    self.get_cell(col, 4),
                    header['title'],
                    self.formats[header['header_format']] if 'format' in header.keys()
                    else self.formats['pretty_header']
            )
            if header['title'] in ['Red 1', 'Red 2', 'Red 3', 'Blue 1', 'Blue 2', 'Blue 3']:
                sheet.conditional_format(self.get_col_range(col, 5, data_len), {
                    'type':               'formula',
                    'criteria':           '{0}5=$C$2'.format(col),
                    'format': self.formats['bold']
                })
            for i in range(data_len):
                if header['title'] == 'Match':
                    match_num_col = col
                    sheet.write(
                            self.get_cell(col, 5),
                            "=TRANSPOSE(FILTER(team_schedule_matches, team_schedule_team_number=$C$2))",
                            self.formats[header['format']] if 'format' in header.keys()
                            else self.formats['pretty_data_cell']
                    )
                    for i in range(1, data_len):
                        sheet.write_blank(
                                self.get_cell(col, 5 + i),
                                "",
                                self.formats[header['format']] if 'format' in header.keys()
                                else self.formats['pretty_data_cell']
                        )
                else:
                    for i in range(data_len):
                        sheet.write(
                                self.get_cell(col, i + 5),
                                '=IFERROR(LOOKUP({0}, schedule_match_number, {1}))'.format(
                                        self.get_col_range(match_num_col),
                                        'schedule_{}'.format(header['key'])
                                ),
                                self.formats[header['format']] if 'format' in header.keys()
                                else self.formats['pretty_data_cell']
                        )
            if header['title'] == 'Red Score':
                sheet.conditional_format(self.get_col_range(col, 5, data_len), {
                    'type':               'formula',
                    'criteria':           '{0}5>{1}5'.format(col, self.next_col(col)),
                    'format': self.formats['bold']
                })
                sheet.conditional_format(self.get_col_range(self.next_col(col), 5, data_len), {
                    'type':               'formula',
                    'criteria':           '{0}5>{1}5'.format(self.next_col(col), col),
                    'format': self.formats['bold']
                })
            col = self.next_col(col)

    def draw_pretty_team_stats(self):
        page_name = self.page_names['team_stats']
        header_dict = {
            'raw': self.headers                             ['raw'],
            'raw_calculated': self.headers['raw_calculated'][3:]
        }
        sheet = self.workbook.add_worksheet(page_name)
        sheet.set_tab_color('green')
        sheet.write('B1', 'Team:', self.formats['team_input_label'])
        sheet.write('C1', int(self.teams[0]["team_number"]), self.formats['team_input'])
        sheet.data_validation('C1', {
            'validate': 'list',
            'source':   '=team_number_list'
        })
        sheet.set_default_row(16, True)
        sheet.set_row(3, 70)
        data_len = 20
        col = 'A'
        for key, headers in header_dict.items():
            for header in headers:
                sheet.write(
                        self.get_cell(col, 4),
                        header['title'],
                        self.formats[header['header_format']] if 'header_format' in header.keys()
                        else self.formats['pretty_header']
                )
                options = {}
                if "hidden" in header.keys():
                    options['hidden'] = header['hidden']
                sheet.set_column(self.get_col_range(col), header['width'] if "width" in header.keys() else 8,
                                 options=options)

                sheet.write(
                        self.get_cell(col, 5),
                        "=IFERROR(LOOKUP($C1, analysis_team_number, analysis_{}{}))"
                            .format('' if key == 'raw' else 'calculated_', header['key']),
                        self.formats['pretty_avg_cell']
                )
                sheet.write(
                        self.get_cell(col, 6),
                        "=IFERROR(FILTER({0}_{1}, {0}_team_number=$C$1))".format(key, header['key']),
                        self.formats[header['format']] if 'format' in header.keys()
                        else self.formats['pretty_data_cell']
                )

                for i in range(1, data_len):
                    sheet.write(
                            self.get_cell(col, 6 + i),
                            "",
                            self.formats[header['format']] if 'format' in header.keys()
                            else self.formats['pretty_data_cell']
                    )

                if "scale" in header.keys():
                    sheet.conditional_format(self.get_col_range(col, 6, data_len), {
                        'type':     'cell',
                        'criteria': '=',
                        'value':    0,
                        'format':   self.formats[header['format']] if 'format' in header.keys()
                                    else self.formats['pretty_data_cell']
                    })
                    sheet.conditional_format(self.get_col_range(col, 6, data_len), self.range_formats[header['scale']])

                col = self.next_col(col)

    def draw_pretty_match_rundown(self):
        page_name = self.page_names['match_rundown']
        raw_header_dict = {
            'raw': self.headers                             ['raw'],
            'raw_calculated': self.headers['raw_calculated'][3:]
        }
        analysis_headers = self.headers['analysis']
        sheet = self.workbook.add_worksheet(page_name)
        sheet.set_tab_color('green')
        sheet.set_default_row(10, True)

        sheet.write('B2', 'Team:', self.formats['team_input_label'])
        sheet.write('C2', int(self.teams[0]["team_number"]), self.formats['team_input'])
        sheet.data_validation('C2', {
            'validate': 'list',
            'source':   '=team_number_list'
        })

        sheet.write('A1', '=FILTER(team_schedule_matches, team_schedule_team_number=C2)')
        sheet.set_row(0, None, None, {'hidden': True})
        sheet.write('D2', 'Match:', self.formats['team_input_label'])
        sheet.write('E2', '', self.formats['team_input'])
        sheet.data_validation('E2', {
            'validate': 'list',
            'source':   'A1:{}1'.format(self.next_col('A', 20))
        })

        col = 'A'
        row = 3
        team_num_col = col
        sheet.set_row(row - 1, 70)
        for header in analysis_headers:
            sheet.write(
                    self.get_cell(col, row),
                    header['title'],
                    self.formats[header['header_format']] if 'header_format' in header.keys()
                    else self.formats['pretty_header']
            )
            sheet.set_column(self.get_col_range(col), 8)
            if header['key'] == 'team_number':
                team_num_col = col
                for pos in range(6):
                    sheet.set_row(row + 1 + pos, 16)
                    sheet.write(
                            self.get_cell(col, row + 1 + pos),
                            "=IFERROR(LOOKUP($E$2, schedule_match_number, schedule_{}_{}))".format(
                                    'red' if pos < 3 else 'blue',
                                    (pos % 3) + 1),
                            self.formats['red_alliance_data_cell' if pos < 3 else 'blue_alliance_data_cell']
                    )
                    sheet.conditional_format(
                            self.get_range(start_col=col, end_col=self.next_col(col, len(analysis_headers)),
                                           start_row=row + 1 + pos), {
                                'type':               'formula',
                                'criteria':           '${0}{1}=$C$2'.format(col, row + 1 + pos),
                                'format': self.formats['bold']
                            })
            else:
                for pos in range(6):
                    sheet.write(
                            self.get_cell(col, row + 1 + pos),
                            "=IFERROR(LOOKUP({}{}, analysis_team_number, analysis_{}))".format(team_num_col,
                                                                                               row + 1 + pos,
                                                                                               header['key']),
                            self.formats['red_alliance_data_cell' if pos < 3 else 'blue_alliance_data_cell']
                    )

            col = self.next_col(col)

        col = 'A'
        row = 11
        team_num_col = col
        sheet.set_row(row - 1, 70)
        for key, raw_headers in raw_header_dict.items():
            for header in raw_headers:
                sheet.write(
                        self.get_cell(col, row),
                        header['title'],
                        self.formats[header['header_format']] if 'header_format' in header.keys() else self.formats[
                            'pretty_header']
                )
                sheet.set_column(self.get_col_range(col), 8)
                if header['key'] == 'team_number':
                    team_num_col = col
                    for pos in range(6):
                        sheet.set_row(row + 1 + pos, 16)
                        sheet.write(
                                self.get_cell(col, row + 1 + pos),
                                "=IFERROR(LOOKUP($E$2, schedule_match_number, schedule_{}_{}))".format(
                                        'red' if pos < 3 else 'blue',
                                        (pos % 3) + 1),
                                self.formats['red_alliance_data_cell' if pos < 3 else 'blue_alliance_data_cell']
                        )
                        sheet.conditional_format(
                                self.get_range(start_col=col, end_col=self.next_col(col, len(raw_headers)),
                                               start_row=row + 1 + pos), {
                                    'type':               'formula',
                                    'criteria':           '${0}{1}=$C$2'.format(col, row + 1 + pos),
                                    'format': self.formats['bold']
                                })
                else:
                    for pos in range(6):
                        sheet.write(
                                self.get_cell(col, row + 1 + pos),
                                "=IFERROR(FILTER({}_{}, raw_match=$E$2, raw_team_number=${}{}))".format(key,
                                                                                                        header['key'],
                                                                                                        team_num_col,
                                                                                                        row + 1 + pos),
                                self.formats['red_alliance_data_cell' if pos < 3 else 'blue_alliance_data_cell']
                        )

                col = self.next_col(col)

    @staticmethod
    def col_to_num(col):
        return (26 * (len(col) - 1)) + (ord(col[-1]) - ord('A'))

    @staticmethod
    def get_range(start_col='A', end_col='Z', start_row=None, end_row=None):
        return "{0}{2}:{1}{3}".format(start_col, end_col, start_row if start_row is not None else "",
                                      (end_row if end_row is not None else start_row) if start_row is not None else "")

    @staticmethod
    def get_col_range(col, start=1, num=None):
        if not num:
            return '{0}:{0}'.format(col)
        return '{0}{1}:{0}{2}'.format(col, start, start + num)

    @staticmethod
    def get_cell(col, row):
        return '{0}{1}'.format(col, row)

    @staticmethod
    def _get_data(data, key):
        keys = key
        if type(key) is str:
            keys = []
            [[keys.append(e) for e in k.split(".")] for k in key.split(",")]
        val = data
        for k in keys:
            try:
                if val is None:
                    return val
                val = val[str(k).strip()]
            except Exception as ex:
                print(k)
                print(val)
                print(val.keys())
                raise ex
        return val

    def upload_to_google_drive(self, filename, upload_filename="Clooney.xlsx"):
        gauth = GoogleAuth(settings_file=self.path_prefix + "/gauth.yaml")
        # Try to load saved client credentials
        gauth.LoadCredentialsFile(self.path_prefix + "/credentials.json")
        if gauth.credentials is None:
            # Authenticate if they're not there
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            # Refresh them if expired
            gauth.Refresh()
        else:
            # Initialize the saved creds
            gauth.Authorize()
        # Save the current credentials to a file
        gauth.SaveCredentialsFile(self.path_prefix + "/credentials.json")

        drive = GoogleDrive(gauth)

        for file in drive.ListFile({'q': "'1Y20z_cAs780qNOm-hwXx0ork1dgIQJHb' in parents and trashed=false"}).GetList():
            if file['title'] == upload_filename:
                clooney_file = file
                clooney_file.FetchMetadata()
                break
        else:
            clooney_file = drive.CreateFile({
                'title': upload_filename, "parents": [
                    {"kind": "drive#fileLink", "id": '1Y20z_cAs780qNOm-hwXx0ork1dgIQJHb'}]
            })

        clooney_file.SetContentFile(filename)
        clooney_file.Upload({'convert': True})
        print("Uploaded Workbook at {}".format(upload_filename))


if __name__ == "__main__":
    db = '../db/db.sqlite'
    tba = TBA('GdZrQUIjmwMZ3XVS622b6aVCh8CLbowJkCs5BmjJl2vxNuWivLz3Sf3PaqULUiZW')
    filename = 'Clooney.xlsx'
    event_id = '2018oncmp2'
    event = tba.get_event_info(event_id)
    gen = SpreadsheetGenerator(db, tba)
    gen.create_spreadsheet_for_event(event_id, filename=filename)
    gen.upload_to_google_drive(filename, upload_filename='Clooney {}'.format(event['short_name']))
