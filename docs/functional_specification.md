# Functional Specification: Kinetics Kalculator

## Background

Biochemists frequently need to determine the kinetics of enzymes through experimental analysis. This involves conducting experiments across multiple plates and wells, correcting for background signals, evaluating against controls, and calculating kinetic parameters. Currently, these processes are highly individualized, with custom scripts that vary by person and lab, lacking general applicability. A standardized package that streamlines and automates these workflows, while providing visualization capabilities, would significantly enhance efficiency and be readily adopted by lab members.


The primary users are computationally-inclined biochemists focused on determining the Michaelis-Menten kinetics of enzymes. They are proficient in functional programming, primarily using Jupyter Notebooks, and are skilled in data manipulation with Pandas and NumPy. While they are adept at using package APIs, they have less experience with the intricacies of software development. Users have access to:

-   Experimental data, including negative controls.
-   Standard curve parameters specific to their equipment and solvents.
-   Slope and intercept data for converting raw measurements (e.g., absorbance) into concentration units.

## Use Cases

The following use cases describe typical interactions between the users and the Kinetics Kalculator system. Users may execute all or a subset of these use cases as part of their analysis workflow.

### Use Case 1: Convert Concentration Using a Standard Curve

**Objective:** Convert raw measurement data into concentration values using a linear standard curve.

**Interactions:**

1. **User** loads a dataframe into a variable `df`.
2. **User** executes the function `convert_to_concentration_using_standard_curves(df)`.
3. **Program** applies the standard curve parameters to adjust raw measurements to concentration units.

### Use Case 2: Filter Data by Time Range

**Objective:** Restrict data analysis to a specific time range.

**Interactions:**

1. **User** loads a dataframe into a variable `df`.
2. **User** executes the function `filter_by_time_range(df, start_time, end_time)`.
3. **Program** truncates the data to only include entries within the specified time range.

### Use Case 3: Compute Reaction Rates

**Objective:** Calculate reaction rates from concentration data.

**Interactions:**

1. **User** loads a dataframe into a variable `df`.
2. **User** converts raw values to concentrations using `convert_to_concentration_using_standard_curves(df)`.
3. **User** executes the function `add_rate_column(df)`.
4. **Program** performs a linear fit to compute the reaction rate and averages across replicates as necessary.

### Use Case 4: Remove Background Absorbance

**Objective:** Eliminate background noise from absorbance measurements.

**Interactions:**

1. **User** loads a dataframe into a variable `df`.
2. **User** converts values to concentrations using Use Case 1.
3. **User** computes rates using Use Case 3.
4. **User** executes `remove_background_absorbance(df, sample_key='negative_control')`.
5. **Program** groups data by the specified sample key, fits a linear model, and subtracts background absorbance from each rate measurement.

### Use Case 5: Compute Michaelis-Menten Kinetics

**Objective:** Determine the Michaelis-Menten kinetic parameters.

**Interactions:**

1. **User** completes the necessary steps from Use Case 1 and Use Case 3.
2. **User** executes `compute_michaelis_menten_kinetics(df)`.
3. **Program** analyzes the data to derive kinetic parameters such as Km and Vmax.

### Use Case 6: Visualize Results of Michaelis-Menten Kinetics

**Objective:** Generate visual representations of kinetic data.

**Interactions:**

1. **User** completes the steps from Use Case 5.
2. **User** executes `visualize_kinetics_results(df)`.
3. **Program** produces plots and graphs to illustrate the Michaelis-Menten kinetics, facilitating easier interpretation and presentation of results.
