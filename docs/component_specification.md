# Component Specification: Kinetics Kalculator

## Inputs

### Data Specification

The input data must be in a Pandas DataFrame format or a file path to a supported file type (CSV, Excel, JSON, Parquet, Feather, HDF5, Pickle). The DataFrame should adhere to the following structure:

| Name                   | Type        | Required | Description                                                                 |
|------------------------|-------------|----------|-----------------------------------------------------------------------------|
| **time**               | float       | Yes      | The time at which each measurement was taken.  Can be any unit.|
| **value**              | float       | Yes      | The measured value (e.g., absorbance) that will be converted to concentration. Can be any unit.|
| **well**               | string      | Yes      | Identifier for the well or sample location in the experimental setup.        |
| **substrate_concentration** | float   | Yes      | Concentration of the substrate used in the experiment (units: molarity)  |
| **enzyme_concentration**    | float   | Yes      | Concentration of the enzyme used in the experiment (units: molarity)
| **sample_type**        | string      | Yes      | Type of sample, such as "negative_control", or "sample".            |

Throughout the execution of the pipeline, additional pipelines will be added. Namely:

| Name                   | Type        | Description                                                                 |
|------------------------|-------------|-----------------------------------------------------------------------------|
| **condition**          | string      | Generated experimental condition description, typically a combination of substrate and enzyme concentrations. |
| **rate**               | float       | Calculated rate of change for each condition.                               |
| **intercept**          | float       | Intercept from the linear fit used to calculate the rate.                   |
| **r_value**            | float       | Correlation coefficient from the linear fit.                                |
| **p_value**            | float       | P-value from the hypothesis test for the linear fit slope.                  |
| **std_err**            | float       | Standard error of the estimated gradient.                                   |
| **rate_minus_background** | float | Rate measurment with background activity removed. Used to calculate final kinetic constants.

However, should the user have an existing column (e.g., condition), we will also support ingesting that column at any step of the pipeline.

## Software Component

![design](../assets/design.png)

### KineticsKalculator

**Description:**  
The `KineticsKalculator` class is the central organizing entity responsible for loading, analyzing, and visualizing biochemical kinetics data. 
It processes a single DataFrame, performing data transformations and computations to derive kinetic parameters.
All class methods operate on this dataframe, either manipulating data, adding columns, or plotting visualization.

Users will interact with this interface through a Jupyter notebook (see the example notebook in `examples`) for all visualizations and computations.

**Inputs to `KineticsKalculator`:**
-    `data_path`: Path to data file or a Pandas DataFrame. See `Data Specification` above for a data dictionary of the input.
-    `standard_curve_parameters`: Dictionary containing keys `slope` and `y-intercept` for standard curve conversion. Only required if performing
   conversion from values (e.g., absorbance) to concentrations.

**Outputs:**
-    Processed DataFrame with additional columns for concentrations, reaction rates, and other calculated parameters.
-    Graphical plots for data visualization.

**Functionalities:**
Note: Functionalities are grouped logically by category, not in the order that they will be used.

1. **Initialization:**
   - Load data from specified file path or DataFrame, using the generic `_load_data` class method, which accepts a wide range of file types
   - Store standard curve parameters as a dictionary for later use in concentration conversion.

2. **Data Labeling:**
   - `label_replicates_and_conditions`: Label rows in the DataFrame to identify replicates and conditions. This should not be required, if the column already exists.
      For example, in many cases, experimentalists might have multiple replicates of a given condition to reduce variance and increase result confidence. They may want to average over these "replicates."
      - **Parameters:** `condition_columns`, `well_column` (default: "well").

3. **Concentration Conversion:**
   - `convert_values_to_concentration_with_standard_curve`: Convert raw measurement values to concentrations using standard curve parameters.

5. **Data Filtering:**
   - `subset_dataframe_to_time_range`: Filter data to include only rows within a specified time range.
     - **Parameters:** `lower_bound`, `upper_bound`.

6. **Rate Calculation:**
   - `calculate_rates`: Compute reaction rates from concentration data.
     - **Parameters:** `time_column`, `value_column`, `group_by_columns` (subsets within which to perform the linear fit), `print_fit_summary` (whether to print a summary of the linear fit)

7. **Background Adjustment:**
   - `adjust_rates_for_background`: Adjust reaction rates by subtracting background values from negative controls. Support dynamic column and value selection for negative controls.
     - **Parameters:** `rate_column`, `sample_type_column` (default: "sample_type"), `negative_control` (default: "negative_control"), `remove_negative_controls` (default: True).

8. **Visualization:**
   - `plot_concentration_vs_time_for_each_condition`: Plot concentration vs. time for each experimental condition. Produce a visually-appealing plot that can be used to determine appropriate time range.
     - **Parameters:** `time_column` (default: "time"), `value_column` (default: "value"), `condition_column` (default: "condition"), `time_units` (default: "s"), `concentration_units` (default: "M").
   - `plot_michaelis_menten_curve`: Plot the Michaelis-Menten curve using calculated kinetic parameters.
     - **Parameters:** `substrate_concentration_column` (default: "substrate_concentration").

## Interactions to Accomplish Use Cases

![use cases](../assets/workflow.png)

See the functional specification fo details step-by-step walkthrough of user interactions to accomplish use cases, and program steps for each.
