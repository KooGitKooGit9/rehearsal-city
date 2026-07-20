from engine.population.db_source import aggregate_age_gender


def test_aggregate_age_gender_sums_across_rows():
    rows = [
        {"TOT_LVPOP_CO": "100", "MALE_F0T9_LVPOP_CO": "10", "FEMALE_F0T9_LVPOP_CO": "12"},
        {"TOT_LVPOP_CO": "90", "MALE_F0T9_LVPOP_CO": "5", "FEMALE_F0T9_LVPOP_CO": "8"},
    ]

    weights = aggregate_age_gender(rows)

    assert weights[("MALE", "F0T9")] == 15.0
    assert weights[("FEMALE", "F0T9")] == 20.0
    assert all(gender != "TOT" for gender, _ in weights)
