# Add parent directory to the path
import sys

import pandas as pd
import pytest

sys.path.append("..")  # noqa

from kinetics_kalculator.utils import (
    add_rate_column,
    adjust_rates_for_background,
    calculate_michaelis_menten_constants,
    convert_to_concentration_using_linear_standard_curve,
    filter_by_time_range,
)


def test_convert_to_concentration_using_linear_standard_curve():
    # Create a test DataFrame
    df = pd.DataFrame({"value": [1, 2, 3, 4, 5]})
    expected_values = [(x - 1) / 2 for x in df["value"]]

    # Apply the conversion function
    convert_to_concentration_using_linear_standard_curve(df, slope=2, y_intercept=1)

    # Assert that the conversion is correct
    assert df["value"].tolist() == expected_values


def test_filter_by_time_range():
    # Create a test DataFrame
    df = pd.DataFrame({"time": [0, 5, 10, 15, 20, 25], "value": [1, 2, 3, 4, 5, 6]})
    lower_bound = 5
    upper_bound = 20

    # Apply the filter function
    filtered_df = filter_by_time_range(df, lower_bound, upper_bound)

    # Assert that the filtering is correct
    assert filtered_df["time"].min() >= lower_bound
    assert filtered_df["time"].max() <= upper_bound
    assert filtered_df.shape[0] == 4  # Only 4 rows should remain


def test_adjust_rates_for_background():
    # Create a test DataFrame
    df = pd.DataFrame(
        {
            "sample_type": ["negative_control", "sample", "sample"],
            "rate": [0.1, 0.5, 0.6],
        }
    )

    # Expected adjusted rates
    expected_adjusted_rates = [0.0, 0.4, 0.5]  # Adjusted by subtracting 0.1

    # Apply the adjustment function
    adjust_rates_for_background(df, negative_control="negative_control", epsilon=0.01)

    # Assert that the adjustment is correct
    assert df["rate_minus_background"].tolist() == expected_adjusted_rates


def test_add_rate_column():
    # Create a test DataFrame
    df = pd.DataFrame(
        {
            "well": ["A1", "A1", "A1", "A2", "A2", "A2"],
            "time": [0, 1, 2, 0, 1, 2],
            "value": [0, 1, 2, 0, 2, 4],
        }
    )

    # Apply the rate calculation function
    result_df = add_rate_column(
        df, x_column="time", y_column="value", group_by_columns=["well"]
    )

    # Check that the rates are calculated correctly
    assert result_df.loc[result_df["well"] == "A1", "rate"].iloc[0] == pytest.approx(
        1.0
    )
    assert result_df.loc[result_df["well"] == "A2", "rate"].iloc[0] == pytest.approx(
        2.0
    )


def test_calculate_michaelis_menten_constants():
    # Create a spoofed DataFrame with expected columns
    data = pd.DataFrame(
        {
            "substrate_concentration": [0.1, 0.2, 0.5, 1.0, 2.0],
            "rate_minus_background": [0.05, 0.1, 0.2, 0.4, 0.5],
        }
    )

    # Call the function
    constants = calculate_michaelis_menten_constants(data)

    # Check if the keys exist in the returned dictionary
    assert "Vmax" in constants
    assert "Km" in constants

    # Check if the values are floats
    assert isinstance(constants["Vmax"], float)
    assert isinstance(constants["Km"], float)

    # Check if the values are within a reasonable range
    assert constants["Vmax"] > 0
    assert constants["Km"] > 0


if __name__ == "__main__":
    pytest.main()
