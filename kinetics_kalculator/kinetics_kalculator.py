import logging
from os import PathLike
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from rich.console import Console
from rich.table import Table

from kinetics_kalculator.utils import (
    add_rate_column,
    adjust_rates_for_background,
    convert_to_concentration_using_linear_standard_curve,
    filter_by_time_range,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KineticsKalculator:
    def __init__(
        self,
        data_path: Path | PathLike | pd.DataFrame | None,
        standard_curve_parameters: dict | None = None,
    ):
        """Initialize the KineticsKalculator by loading the data from the specified file path.

        Args:
            data_path (Path | PathLike | pd.DataFrame | None): The path to the data file to load or the DataFrame itself. Supported file formats include:
                - CSV: .csv
                - Excel: .xls, .xlsx
                - JSON: .json
                - Parquet: .parquet
                - Feather: .feather
                - HDF5: .hdf
                - Pickle: .pkl
                If None, we expect the data to be set explicitly using the 'data' attribute.
            standard_curve_parameters (dict | None): A dictionary containing the parameters of the standard curve.
                For example, {"slope": 2, "y_intercept": 1}, if using a linear standard curve of the form y = mx + c.
                NOTE: Currently only linear standard curves are supported.

        Returns:
            None: The KineticsKalculator object is initialized with the loaded data and standard curve parameters.
        """
        if isinstance(data_path, pd.DataFrame):
            self.data = data_path
        elif data_path is not None:
            # Convert to a Path, if necessary
            self.data_path = Path(data_path)

            # Load data based on file extension
            self.data = self._load_data()

        # Save the standard curve parameters
        self.standard_curve_parameters = standard_curve_parameters

    def _load_data(self):
        """Load data from the file path based on the file extension.

        Returns:
            DataFrame: The loaded data.
        """
        file_extension = self.data_path.suffix.lower()

        if file_extension == ".csv":
            return pd.read_csv(self.data_path)
        elif file_extension in [".xls", ".xlsx"]:
            return pd.read_excel(self.data_path)
        elif file_extension == ".json":
            return pd.read_json(self.data_path)
        elif file_extension == ".parquet":
            return pd.read_parquet(self.data_path)
        elif file_extension == ".feather":
            return pd.read_feather(self.data_path)
        elif file_extension == ".hdf":
            return pd.read_hdf(self.data_path)
        elif file_extension == ".pkl":
            return pd.read_pickle(self.data_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

    def label_replicates_and_conditions(
        self, condition_columns: list[str], well_column: str = "well"
    ):
        """Label rows in the dataframe that represent the same experimental conditions; e.g., replicates.

        Args:
            condition_columns (list[str]): The names of the columns that define the experimental conditions. For example, ["substrate_concentration", "enzyme_concentration"].
            well_column (str): The name of the column containing the well information. Defaults to 'well'. We will label each well within a condition as a replicate.

        Returns:
            None: The DataFrame is modified in-place.
        """
        assert (
            well_column in self.data.columns
        ), f"Column '{well_column}' not found in the DataFrame."
        assert all(
            column in self.data.columns for column in condition_columns
        ), f"Columns {condition_columns} not found in the DataFrame."

        # Create a "condition" column, which is unique for each set of conditions
        self.data["condition"] = self.data[condition_columns].apply(
            lambda row: ", ".join(f"{col}: {row[col]}" for col in condition_columns),
            axis=1,
        )

        # Create a "replicate" column, which is unique for each well within a condition
        self.data["replicate_n"] = (
            self.data.groupby(["condition", well_column]).cumcount() + 1
        )

    def calculate_rates(
        self,
        time_column: str,
        value_column: str,
        group_by_columns: list[str],
        print_fit_summary: bool = True,
        sample_type_column: str = "sample_type",
        negative_control: str = "negative_control",
        poor_fit_threshold: float = 0.5,
    ):
        """Calculate the rates of change in the 'value' column over time, and add a new column to the DataFrame containing the calculated rates.

        NOTE: The rates are calculated as the first derivative of the values with respect to time. We assume that
        the "value" column represents the appropriate unit (e.g., concentration).

        Args:
            time_column (str): The name of the column containing the time values.
            value_column (str): The name of the column containing the values to calculate rates from.
            group_by_columns (list[str]): The names of the columns to group the data by before calculating rates. E.g., "well" or "replicate".
            sample_type_column (str): The name of the column containing the sample type information. Defaults to "sample_type". Used for validation of results.
            negative_control (str): The value to use as the negative control. Defaults to "negative_control". Used for validation of results.
            poor_fit_threshold (float): The threshold for determining a poor fit. Defaults to 0.5.

        Returns:
            None: The DataFrame is modified in-place.
        """
        # Calculate the rates of change
        self.data = add_rate_column(
            self.data, time_column, value_column, group_by_columns
        )

        # Assert that necessary columns are present
        columns_to_check = [
            "rate",
            "intercept",
            "r_value",
            "p_value",
            "std_err",
            sample_type_column,
        ]
        assert all(
            column in self.data.columns for column in columns_to_check
        ), f"Columns {columns_to_check} not found in the DataFrame."

        # Assert that within a group, the added columns are constant
        grouped = self.data.groupby(group_by_columns)[columns_to_check]
        for col in columns_to_check:
            assert (
                grouped.nunique()[col] == 1
            ).all(), f"Column {col} is not constant within each group."

        if print_fit_summary:
            # Print a table showing the "rate", "intercept", "r-value", "p-value", and "std_err" for each group
            console = Console()
            table = Table(title="Rates of Change by Group")

            # Add columns to the table
            for col in group_by_columns + columns_to_check:
                table.add_column(col, justify="right", style="cyan")

            # Group the data and add rows to the table
            grouped_data = self.data.groupby(group_by_columns).first().reset_index()
            for _, row in grouped_data.iterrows():
                # Check if the fit is poor and the sample type is not negative control
                r_squared = row["r_value"] ** 2
                is_poor_fit = r_squared < poor_fit_threshold
                is_not_negative_control = row[sample_type_column] != negative_control

                row_style = "red" if is_poor_fit and is_not_negative_control else None

                # Format each value to 4 decimal places if it's a float
                formatted_row = [
                    f"{row[col]:.6f}" if isinstance(row[col], float) else str(row[col])
                    for col in group_by_columns + columns_to_check
                ]

                # Add row with conditional styling
                table.add_row(*formatted_row, style=row_style)

                # Print a warning if the fit is poor and the sample type is not negative control
                if is_poor_fit and is_not_negative_control:
                    logger.warning(
                        f"Poor fit detected for group {row[group_by_columns]} with r^2 = {r_squared:.2f}"
                    )

            # Print the table
            console.print(table)

    def convert_values_to_concentration_with_standard_curve(self):
        """Convert the 'value' column in the DataFrame to concentration units using the provided slope and y-intercept of the standard curve.

        NOTE: Only supports linear standard curves of the form y = mx + c.

        Returns:
            None: The DataFrame is modified in-place.
        """
        # Ensure the standard curve parameters are provided
        assert (
            self.standard_curve_parameters is not None
        ), "Standard curve parameters are required."

        # Unpack the standard curve parameters and apply the conversion
        self.data = convert_to_concentration_using_linear_standard_curve(
            self.data, **self.standard_curve_parameters
        )

    def subset_dataframe_to_time_range(self, lower_bound: float, upper_bound: float):
        """Subset the underlying DataFrame to only include rows where the 'time' column is within the specified range.

        Args:
            lower_bound (float): The lower bound of the time range.
            upper_bound (float): The upper bound of the time range.

        Returns:
            None: The DataFrame is modified in-place.

        Raises:
            ValueError: If the DataFrame does not contain the required 'time' column.
        """
        self.data = filter_by_time_range(self.data, lower_bound, upper_bound)

    def adjust_rates_for_background(
        self,
        rate_column: str,
        sample_type_column: str = "sample_type",
        negative_control: str = "negative_control",
        remove_negative_controls: bool = True,
    ):
        """Adjust the rates in the DataFrame by subtracting the provided background value.

        Adds a new column containing the adjusted rates, '{rate_column}_minus_background', to the DataFrame.

        Args:
            rate_column (str): The name of the column containing the rates to adjust.
            sample_type_column (str): The name of the column containing the sample type information. Defaults to "sample_type".
            negative_control (str): The value to use as the negative control. Defaults to "negative_control".
            remove_negative_controls (bool): Whether to remove the negative control rows after adjusting the rates. Defaults to True.

        Returns:
            None: The DataFrame is modified in-place.
        """

        self.data = adjust_rates_for_background(
            df=self.data,
            rate_column=rate_column,
            sample_type_column=sample_type_column,
            negative_control=negative_control,
            epsilon=1e-10,
        )

        # Remove the negative control rows if specified
        if remove_negative_controls:
            self.data = self.data[self.data[sample_type_column] != negative_control]
            # Assert that the negative control rows have been removed
            assert negative_control not in self.data[sample_type_column].values

    def plot_concentration_vs_time_for_each_condition(
        self,
        time_column: str = "time",
        value_column: str = "value",
        condition_column: str = "condition",
        time_units: str = "s",
        concentration_units: str = "M",
    ):
        """Plot measured target concentration over time for each experimental condition in the DataFrame.

        Args:
            time_column (str): The name of the column containing the time values. Defaults to 'time'.
            value_column (str): The name of the column containing the concentration values. Defaults to 'value'.
            condition_column (str): The name of the column containing the condition labels. Defaults to 'condition'.
            time_units (str): The units of time to display on the x-axis. Defaults to 's'.
            concentration_units (str): The units of concentration to display on the y-axis. Defaults to 'M'.

        Returns:
            None: Displays a plot for each condition showing substrate concentration over time.

        Raises:
            AssertionError: If any of the specified columns do not exist in the DataFrame.
        """
        assert (
            time_column in self.data.columns
        ), f"Column '{time_column}' not found in the DataFrame."
        assert (
            value_column in self.data.columns
        ), f"Column '{value_column}' not found in the DataFrame."
        assert (
            condition_column in self.data.columns
        ), f"Column '{condition_column}' not found in the DataFrame."

        sns.set_theme(style="whitegrid")
        unique_conditions = self.data[condition_column].unique()

        for condition in unique_conditions:
            condition_data = self.data[self.data[condition_column] == condition]

            plt.figure(figsize=(10, 6))
            sns.lineplot(data=condition_data, x=time_column, y=value_column, marker="o")
            plt.title(f"Target Concentration vs Time for Condition: {condition}")
            plt.xlabel(f"Time ({time_units})")
            plt.ylabel(f"Target Concentration ({concentration_units})")
            plt.xticks(rotation=45)

            plt.tight_layout()
            plt.show()

    def plot_michaelis_menten_curve(
        self, substrate_concentration_column: str = "substrate_concentration"
    ) -> None:
        """Plot the Michaelis-Menten curve using Seaborn.

        NOTE: Assumes that the column `rate_minus_background` has been added to the DataFrame.

        Args:
            substrate_concentration_column (str): The name of the column containing the substrate concentration values. Defaults to 'substrate_concentration'.

        Returns:
            None: Displays the Michaelis-Menten curve plot, with the data points, the fitted curve, and the kinetics parameters.
        """
        assert (
            "rate_minus_background" in self.data.columns
        ), "Column 'rate_minus_background' not found in the DataFrame."

        constants = self.calculate_michaelis_menten_constants()
        Vmax = constants["Vmax"]
        Km = constants["Km"]

        # Plot data points
        sns.set_theme(style="whitegrid")
        plt.figure(figsize=(10, 6))

        # Scatter plot of the data
        sns.scatterplot(
            x="substrate_concentration",
            y="rate_minus_background",
            data=self.data,
            color="blue",
            label="Data",
        )

        # Fit curve
        S_fit = np.linspace(0, self.data[substrate_concentration_column].max(), 100)
        rate_fit = (Vmax * S_fit) / (Km + S_fit)
        plt.plot(
            S_fit,
            rate_fit,
            color="red",
            label=f"Michaelis-Menten Fit Parameters: $V_{{max}}={Vmax:.4f}$, $K_m={Km:.4f}$",
        )

        plt.xlabel("Substrate Concentration")
        plt.ylabel("Initial Rate")
        plt.title("Michaelis-Menten Kinetics")
        plt.legend()
        plt.tight_layout()
        plt.show()
