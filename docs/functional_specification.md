# Functional Specification: Kinetics Kalculator

## Background

### Overview
Biochemists frequently need to determine the kinetics of enzymes through experimental analysis. This process involves conducting experiments across multiple wells, subsetting to a well-behaved time interval, correcting for background signals, calculating kinetic parameters, and visualizing all results. Currently, these processes are highly individualized, with custom scripts that vary by person and lab, lacking general applicability. A standardized package that streamlines and automates these workflows, while providing visualization capabilities, would significantly enhance efficiency and be readily adopted by lab members.

### Users

The primary users are **computationally-inclined biochemists** focused on determining the Michaelis-Menten kinetics of enzymes. They are proficient in functional programming, primarily with Jupyter Notebooks, and are skilled in data manipulation with Pandas and NumPy. While they are adept at using package APIs, they have less experience with the intricacies of software development. 

Users are assumed to have access to:

-   Experimental data, including negative controls, formatted into a `pandas`-compatible format (e.g., CSV) that adheres to a pre-defined data dictionary (see *component_specification* for more details)
-   Standard curve parameters specific to their equipment and solvents (slope and y-intercept) to convert raw measurements (e.g., absorbance) into concentration units

## Use Cases

`KineticsKalculator` supports a full-featured kinetics analysis workflow. 

There are are series of use cases users may want spanning data cleaning, visualization, curve fitting, and validation; users my execute all or a subset of these use cases as a part of their particular worklow. Thus, the use cases are "opt-in," where they are not dependent on previous operations (so long as the dataframe has the correct columns populated by the user).

### Use Case 1: Automatically Label Condition Replicates

**Objective:** Enable users to label rows in the dataframe that represent the same experimental conditions, such as replicates. For example,
every duplicate well with the same substrate concentration and enzyme concentration might represent a replicate. Replicates allow experimentalists to express and calculate the uncertainty in their estimated values, since they can calculate the mean and standard deviation of all parameters.

**Interactions:**

1. **User** loads a dataframe into the class property `self.data` via instantiation of `KineticsKalculator` with the appropriate columns (see data dictionary in `component_specification.md`)
2. **User** executes the class method `label_replicates_and_conditions`, providing the condition columns and well column as arguments.
3. **Program** groups the rows based on the specified conditions columns and labels wells with the same conditions as replicates for later analysis.

### Use Case 2: Convert Values to Concentration Using a Standard Curve

**Objective:** Convert raw measurement data into concentration values using a linear standard curve. Lab devices do not directly measure concentration; instead, they measure a proxy value (e.g., absorbance), which can be converted into concentration through device-specific curves.

**Interactions:**

1. **User** loads a dataframe into a class property `self.data` via instantiation of `KineticsKalculator` with the appropriate columns.
2. **User** executes the class method `convert_to_concentration_using_standard_curves`, passing as an argument the standard curve parameters.
3. **Program** applies the standard curve parameters to adjust raw measurements to concentration units, and adjusts the relevant column (e.g., "value") in-place.

### Use Case 3:  Visualize Concentration vs. Time, Grouped by Condition

**Objective:** Allow users to visualize concentration changes over time for each experimental condition. Such a visualization is helpful to determine what time limits should be used to compute the initial rate constants (before the substrate concentration begins to influence the rate).

**Interactions**
1. **User** loads a dataframe into a class property `self.data` via instantiation of `KineticsKalculator` with the appropriate columns.
2. **User** performs any preceding use cases to setup and clean their data
3. **User** executes the class method `plot_concentration_vs_time_for_each_condition`, specifying the columns for time, value, and condition.
4. **Program** generates plots showing concentration versus time for each condition, including visual indications of mean and variance.

### Use Case 3: Filter Data by Time Range

**Objective:** Restrict data analysis to a specific time range; e.g., where the rate appears to be linear.

**Interactions:**
1. **User** loads a dataframe into a class property `self.data` via instantiation of `KineticsKalculator` with the appropriate columns.
2. **User** performs any preceding use cases to setup and clean their data
3. **User** executes the class method `filter_by_time_range`, passing the start and end time as arguments. Often, this step may be after visualizing the concentration vs. time curves.
4. **Program** truncates the data to only include entries within the specified time range.

### Use Case 4: Compute Reaction Rates

**Objective:** Calculate reaction rates from concentration data.

**Interactions:**

1. **User** loads a dataframe into a class property `self.data` via instantiation of `KineticsKalculator` with the appropriate columns.
2. **User** converts raw values to concentrations using `convert_to_concentration_using_standard_curves()`; in addition, users may (optionally) visualize the concentration vs. time plot and filter to a well-behaved time interval
3. **User** executes the class method `calculate_rates`, providing as input the x-column (e.g., time), y-column (e.g., rate), and columns to group the data within before fitting the model (e.g., "well", since we want one rate per well)
4. **Program** performs a linear fit to compute the reaction rate within the grouped columns, adding the fit parameters to the dataframe
5. **Program** prints the fit for each well, indicating visually which fits are suspect (as defined by a fit parameter cutoff, and labels of "negative control" examples, which are expected to have poor fits).

### Use Case 5: Remove Background Rate

**Objective:** Eliminate background rates from measurements, given wells that represent negative controls.

**Interactions:**
1. **User** loads a dataframe into a class property `self.data` via instantiation of `KineticsKalculator` with the appropriate columns.
2. **User** performs any preceding use cases to setup and clean their data. A `rate` column must be present, but it does not matter how it was created.
4. **User** executes the class method `adjust_rates_for_background`, passing the relevant sample type column, rate column, and negative control information (e.g., which column to look at, and what value in that column indicates a negative control)
5. **Program** groups data by the specified sample key, fits a linear model, and subtracts background absorbance from each rate measurement. A new column is created indicating the rate after adjusting for background activity.

### Use Case 6: Compute and Visualize Michaelis-Menten Kinetics

**Objective:** Fit and visualize the Michaelis-Menten Kinetics, generating a visually-appealing plot that displays the curve and also the relevant parameters.

**Interactions:**
1. **User** loads a dataframe into a class property `self.data` via instantiation of `KineticsKalculator` with the appropriate columns.
2. **User** performs any preceding use cases to setup and clean their data. A `rate_minus_background` column must be present, but it does not matter how it was created.
3. **User** executes `plot_michaelis_menten_curve`.
4. **Program** Fits the data to derive kinetic parameters such as Km and Vmax using `scipy` and displays a Michaelis Menten curve

## Preliminary Project Plan

### Immediate Goals (Next 2 Weeks)

1. **Develop Utilities**: Develop functional utilities for common operations, and write thorough tests. For example, I can start by writing utilities to fit Michaelis Menten constants, and ensure the results are correct.
2. **Convert Utilities into a class-based Interface**: Build a class-based stateful API for users to access the underlying utilities (with possible additional methods).

### Next Steps
3. **Write Visualization Tools**: Expand on the initial functionality by writing visualization tools that the user can use to generate plots.
4. **Create Complete Test Suite**: Use `pytest` to build a complete testing suite
5. **Make the Package Installable**: Setup the package with `pyproject.toml` such that it is `pip`-installable
6. **Write Documentation**: Write thorough documentation, including a Jupyter notebook with examples and a Sphinx webpage


