from modelChecker.checks import all_checks

all_presets = [
    ("All", {check.name for check in all_checks}),
    ("Environment", {'poles'}),
    ("Character", set()),
    ("Previz", set()),
]