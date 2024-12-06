import logging
import sys

import pandas as pd

sys.path.append("..")  # noqa

from kinetics_kalculator.kinetics_kalculator import KineticsKalculator


def test_load_data_csv(tmp_path):
    # Create a temporary CSV file
    data = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    file_path = tmp_path / "test.csv"
    data.to_csv(file_path, index=False)

    # Initialize KineticsKalculator
    kk = KineticsKalculator(data_path=file_path)
    pd.testing.assert_frame_equal(kk.data, data)


def test_label_replicates_and_conditions():
    # Create a test DataFrame
    data = pd.DataFrame(
        {
            "well": ["A1", "A1", "A2", "A2"],
            "condition": ["cond1", "cond1", "cond2", "cond2"],
        }
    )
    kk = KineticsKalculator(data_path=data)

    # Apply labeling
    kk.label_replicates_and_conditions(
        condition_columns=["condition"], well_column="well"
    )
    expected_replicate_n = [1, 2, 1, 2]
    assert kk.data["replicate_n"].tolist() == expected_replicate_n


def test_calculate_rates_with_warning(caplog):
    # Create a test DataFrame
    data = pd.DataFrame(
        {
            "time": [0, 1, 2, 3],
            "value": [0, 8, -4, 3],
            "well": ["A1", "A1", "A1", "A1"],
            "sample_type": ["sample", "sample", "sample", "sample"],
        }
    )
    kk = KineticsKalculator(data_path=data)

    # Calculate rates
    with caplog.at_level(logging.WARNING):
        kk.calculate_rates(
            time_column="time", value_column="value", group_by_columns=["well"]
        )
        assert "Poor fit detected" in caplog.text


def test_plot_concentration_vs_time_for_each_condition():
    # Smoke test for plotting
    data = pd.DataFrame(
        {"time": [0, 1, 2, 3], "value": [0, 1, 2, 3], "condition": ["A", "A", "A", "A"]}
    )
    kk = KineticsKalculator(data_path=None)
    kk.data = data

    # This is a smoke test; visually inspect the plot
    kk.plot_concentration_vs_time_for_each_condition()


def test_plot_michaelis_menten_curve():
    # Smoke test for plotting
    data = pd.DataFrame(
        {
            "substrate_concentration": [0.1, 0.2, 0.3, 0.4],
            "rate_minus_background": [0.05, 0.1, 0.15, 0.2],
        }
    )
    kk = KineticsKalculator(data_path=None)
    kk.data = data

    # This is a smoke test; visually inspect the plot
    kk.plot_michaelis_menten_curve()
