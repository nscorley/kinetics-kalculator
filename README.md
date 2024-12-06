# Kinetics Kalculator

Kinetics Kalculator is a Python package designed for analyzing biochemical kinetics data. It provides tools for loading experimental data, calculating reaction rates, adjusting for background activity, and visualizing results using various plots. This package is particularly useful for experiments involving enzyme kinetics and Michaelis-Menten analysis.

## Installation

You can install Kinetics Kalculator from PyPI using pip:
```bash
pip install kinetics-kalculator
```

Alternatively, you can install it in editable mode if you're working with the source code:
```bash
git clone https://github.com/yourusername/kinetics-kalculator.git
cd kinetics-kalculator
pip install -e .
```


## Usage

Below is a an illustrative example of how to use `KineticsKalculator`. This example demonstrates how to load data, label conditions, convert measurements, calculate rates, and visualize results.
For more details and a worked example, see the `examples` folder.

### Example Workflow

```python
import pandas as pd
from pathlib import Path
from kinetics_kalculator.kinetics_kalculator import KineticsKalculator

# Define paths to your data files
kinetics_data_path = Path("examples/EX_kinetics_data.csv")
standard_curves_path = Path("examples/EX_standard_curves.json")

# Load standard curves into a dictionary
all_standard_curves = pd.read_json(standard_curves_path, typ="series").to_dict()
experiment_specific_standard_curve = all_standard_curves[21062324]["mscarlett"]

# Initialize the KineticsKalculator
kalculator = KineticsKalculator(
    data_path=kinetics_data_path,
    standard_curve_parameters=experiment_specific_standard_curve,
)

# Label replicates and conditions
kalculator.label_replicates_and_conditions(
    condition_columns=["substrate_concentration", "enzyme_concentration"]
)

# Convert "value" column to concentration using the standard curve
kalculator.convert_values_to_concentration_with_standard_curve()

# Visualize concentration vs. time for different conditions
kalculator.plot_concentration_vs_time_for_each_condition()

# Subset data to a specific time range
kalculator.subset_dataframe_to_time_range(100, 400)

# Calculate rates of change
kalculator.calculate_rates(
    time_column="time",
    value_column="value",
    group_by_columns=["condition"],
    print_fit_summary=True,
)

# Adjust rates for background activity
kalculator.adjust_rates_for_background(
    rate_column="rate",
    sample_type_column="sample_type",
    negative_control="negative_control",
)

# Plot Michaelis-Menten curve
kalculator.plot_michaelis_menten_curve()
```

### Output graph examples:

![example concentration vs. time graph](/examples/example_concentration_time_graph.png)
![example concentration vs. time graph](/examples/example_michaelis_menten_graph.png)


## Data Dictionary

The `KineticsKalculator` relies on a dataframe to perform calculations. The required columns are below; any of the "generated" columns may also be pre-populated.

### Input DataFrame (Required)

| Name                   | Type        | Required | Description                                                                 |
|------------------------|-------------|----------|-----------------------------------------------------------------------------|
| **time**               | float       | Yes      | The time at which each measurement was taken.  Can be any unit.|
| **value**              | float       | Yes      | The measured value (e.g., absorbance) that will be converted to concentration. Can be any unit.|
| **well**               | string      | Yes      | Identifier for the well or sample location in the experimental setup.        |
| **substrate_concentration** | float   | Yes      | Concentration of the substrate used in the experiment (units: molarity)  |
| **enzyme_concentration**    | float   | Yes      | Concentration of the enzyme used in the experiment (units: molarity)
| **sample_type**        | string      | Yes      | Type of sample, such as "negative_control", or "sample".            |

### Additional Columns (Generated)

| Name                   | Type        | Description                                                                 |
|------------------------|-------------|-----------------------------------------------------------------------------|
| **condition**          | string      | Generated experimental condition description, typically a combination of substrate and enzyme concentrations. |
| **rate**               | float       | Calculated rate of change for each condition.                               |
| **intercept**          | float       | Intercept from the linear fit used to calculate the rate.                   |
| **r_value**            | float       | Correlation coefficient from the linear fit.                                |
| **p_value**            | float       | P-value from the hypothesis test for the linear fit slope.                  |
| **std_err**            | float       | Standard error of the estimated gradient.                                   |
| **rate_minus_background** | float | Rate measurment with background activity removed. Used to calculate final kinetic constants.



