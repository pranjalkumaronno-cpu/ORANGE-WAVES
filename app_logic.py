def safe_float(entry):
    """Safely extracts text contents and returns a clean float value."""
    raw = entry.get()
    try:
        return float(raw) if raw else 0.0
    except ValueError:
        return 0.0


def process_marks_summary(row_entries, split_marks=False):
    """Calculates total obtained and max possible scores from active entry rows."""
    total_obtained = 0.0
    max_possible = 0.0
    for row in row_entries:
        if split_marks:
            proj_t = max(safe_float(row["proj_total"]), 0)
            proj_o = min(max(safe_float(row["proj_obtained"]), 0), proj_t)
            assess_t = max(safe_float(row["assess_total"]), 0)
            assess_o = min(max(safe_float(row["assess_obtained"]), 0), assess_t)
            exam_t = max(safe_float(row["exam_total"]), 0)
            exam_o = min(max(safe_float(row["exam_obtained"]), 0), exam_t)
            total_obtained += (proj_o + assess_o + exam_o)
            max_possible += (proj_t + assess_t + exam_t)
        else:
            tot = max(safe_float(row["total"]), 0)
            obt = min(max(safe_float(row["obtained"]), 0), tot)
            total_obtained += obt
            max_possible += tot
    percentage = (total_obtained / max_possible * 100) if max_possible > 0 else 0.0
    return total_obtained, max_possible, percentage


def build_per_subject_marks(row_entries, subjects, split_marks=False):
    """
    Helper used by main.py's Calculate button: returns {subject_name: percentage}
    so results can be handed to user_profile.save_calculated_marks() and picked
    up later by goal_setter.py's 'Auto-Build From Marks' feature.
    """
    result = {}
    for sub, row in zip(subjects, row_entries):
        if split_marks:
            proj_t = max(safe_float(row["proj_total"]), 0)
            proj_o = min(max(safe_float(row["proj_obtained"]), 0), proj_t)
            assess_t = max(safe_float(row["assess_total"]), 0)
            assess_o = min(max(safe_float(row["assess_obtained"]), 0), assess_t)
            exam_t = max(safe_float(row["exam_total"]), 0)
            exam_o = min(max(safe_float(row["exam_obtained"]), 0), exam_t)
            tot = proj_t + assess_t + exam_t
            obt = proj_o + assess_o + exam_o
        else:
            tot = max(safe_float(row["total"]), 0)
            obt = min(max(safe_float(row["obtained"]), 0), tot)
        pct = (obt / tot * 100) if tot > 0 else 0.0
        result[sub] = pct
    return result
