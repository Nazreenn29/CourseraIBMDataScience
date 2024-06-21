#!/usr/bin/env python
# coding: utf-8

# In[1]:


import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, callback, dcc, html, no_update

URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv"

df = pd.read_csv(URL)
print("Data downloaded and read into a dataframe!")

# DataFrame Const Variables
df_rec = df[df["Recession"] == 1]

# Other formatting Consts
vehicle_type_names = {
    "Supperminicar": "Super Mini Car",
    "Mediumfamilycar": "Medium Family Car",
    "Smallfamiliycar": "Small Family Car",
    "Sports": "Sports Car",
    "Executivecar": "Executive Car",
}
label_names = {
    "Automobile_Sales": "Automobile Sales",
    "Vehicle_Type": "Vehicle Type",
    "Advertising_Expenditure": "Advertising Expenditure",
    "unemployment_rate": "Unemployment Rate",
}
month_order = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

external_scripts = [{"src": "https://cdn.tailwindcss.com"}]
app = Dash(
    __name__,
    external_scripts=external_scripts,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
# Clear the layout and do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True

app.layout = html.Main(
    children=[
        html.H1(
            "Automobile Sales Statistics Dashboard",
            className="mt-8 text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl",
        ),
        html.Div(
            [
                html.Label(
                    "Select Report Type:",
                    className="text-base font-semibold text-gray-900",
                    htmlFor="input-report",
                ),
                html.P(
                    "Which report would you like to display, yearly or recession?",
                    className="text-sm text-gray-500",
                ),
                dcc.Dropdown(
                    options=[
                        {"label": "Yearly Statistics", "value": "Yearly"},
                        {"label": "Recession Period Statistics", "value": "Recession"},
                    ],
                    value="Yearly",
                    id="input-report",
                ),
            ],
            className="mt-4",
        ),
        html.Div(
            [
                html.Label(
                    "Year:",
                    className="text-base font-semibold text-gray-900",
                    htmlFor="input-year",
                ),
                html.P(
                    "Which year would you like to display for the yearly report?",
                    className="text-sm text-gray-500",
                ),
                dcc.Dropdown(
                    sorted(df.Year.unique()), value=2005, id="input-year", disabled=True
                ),
            ],
            className="mt-4",
        ),
        html.Section(
            [
                dcc.Graph(id="plot-1"),
                dcc.Graph(id="plot-2"),
                dcc.Graph(id="plot-3"),
                dcc.Graph(id="plot-4"),
            ],
            className="flex flex-wrap items-center justify-center",
        ),
    ],
    className="flex flex-col items-center",
)


@callback(Output("input-year", "disabled"), Input("input-report", "value"))
def disable_year(report_value):
    if report_value == "Recession":
        return True
    else:
        return False


@callback(
    [
        Output(component_id="plot-1", component_property="figure"),
        Output(component_id="plot-2", component_property="figure"),
        Output(component_id="plot-3", component_property="figure"),
        Output(component_id="plot-4", component_property="figure"),
    ],
    [
        Input(component_id="input-report", component_property="value"),
        Input(component_id="input-year", component_property="value"),
    ],
)
def display_graphs(report_value, entered_year):
    if report_value == "Recession":
        return recession_graphs()
    else:
        return year_graphs(entered_year)


def recession_graphs():
    # Line Graph, Avg Sales by year
    fig_line = px.line(
        df_rec[["Year", "Automobile_Sales"]].groupby("Year").mean().reset_index(),
        x="Year",
        y="Automobile_Sales",
        title="Average Automobile Sales by Year during Recession Periods",
        color_discrete_sequence=["#C45A9A"],
        labels=label_names,
    )
    # fig_line.show()
    # Bar Graph 1, Avg sales by vehicle type
    bar_df = (
        df_rec[["Vehicle_Type", "Automobile_Sales"]]
        .groupby("Vehicle_Type")
        .mean()
        .reset_index()
    )
    bar_df["Vehicle_Type"] = bar_df["Vehicle_Type"].map(vehicle_type_names)
    fig_bar_1 = px.bar(
        bar_df,
        x="Vehicle_Type",
        y="Automobile_Sales",
        title="Average Automobile Sales by Vehicle Type during Recession Periods",
        color_discrete_sequence=["#C45A9A"],
        labels=label_names,
    )
    # fig_bar_1.show()
    # Pie graph Sum ad expense by vehicle type
    pie_df = (
        df_rec[["Vehicle_Type", "Advertising_Expenditure"]]
        .groupby("Vehicle_Type")
        .sum()
        .reset_index()
    )
    pie_df["Vehicle_Type"] = pie_df["Vehicle_Type"].map(vehicle_type_names)
    fig_pie = px.pie(
        pie_df,
        values="Advertising_Expenditure",
        names="Vehicle_Type",
        title="Total Advertising Expenditure by Vehicle Type during Recession Periods",
        labels=label_names,
    )
    # fig_pie.show()
    # Bar Graph 2, Sales per vehicle type by unemployment rate
    bar2_df = (
        df_rec[["unemployment_rate", "Vehicle_Type", "Automobile_Sales"]]
        .groupby(["Vehicle_Type", "unemployment_rate"])
        .sum()
        .reset_index()
    )
    fig_bar_2 = px.bar(
        bar2_df,
        x="unemployment_rate",
        y="Automobile_Sales",
        color="Vehicle_Type",
        labels=label_names,
        title="Automobile Sales by Vehicle Type Per Unemployment Rate during Recession Periods",
    )
    # Change the car names to remove underscores in legend and on hover
    fig_bar_2.for_each_trace(
        lambda t: t.update(
            name=vehicle_type_names[t.name],
            legendgroup=vehicle_type_names[t.name],
            hovertemplate=t.hovertemplate.replace(t.name, vehicle_type_names[t.name]),
        )
    )
    # fig_bar_2.show()
    return [fig_line, fig_bar_1, fig_pie, fig_bar_2]


def year_graphs(entered_year):
    # Get the DataFrame for selected year
    df_year = df[df["Year"] == entered_year]
    # Line graph, Average sales per year
    df_line = df[["Year", "Automobile_Sales"]].groupby("Year").mean()
    fig_line = px.line(
        df_line,
        y="Automobile_Sales",
        labels=label_names,
        title="Yearly Average Automobile Sales",
        color_discrete_sequence=["#C45A9A"],
    )
    # fig_line.show()
    # Line Graph 2, total monthly sales for year
    fig_line_2 = px.line(
        df_year,
        x="Month",
        y="Automobile_Sales",
        labels=label_names,
        title=f"Total Automobile Sales per Month in {entered_year}",
        color_discrete_sequence=["#C45A9A"],
    )
    # fig_line_2.show()
    # Bar chart, Avg sales per month by vehicle type
    df_bar = (
        df_year[["Vehicle_Type", "Automobile_Sales"]]
        .groupby("Vehicle_Type")
        .sum()
        .reset_index()
    )
    df_bar["Automobile_Sales"] = (
        df_bar["Automobile_Sales"] / 12
    )  # dividing by 12 to get monthly average
    df_bar["Vehicle_Type"] = df_bar["Vehicle_Type"].map(vehicle_type_names)
    fig_bar = px.bar(
        df_bar,
        x="Vehicle_Type",
        y="Automobile_Sales",
        labels=label_names,
        title=f"Average Monthly Automobile Sales by Vehicle Type in {entered_year}",
        color_discrete_sequence=["#C45A9A"],
    )
    # fig_bar.show()
    # Pie graph, total ad expense by vehicle type
    pie_df = (
        df_year[["Advertising_Expenditure", "Vehicle_Type"]]
        .groupby("Vehicle_Type")
        .sum()
        .reset_index()
    )
    pie_df["Vehicle_Type"] = pie_df["Vehicle_Type"].map(vehicle_type_names)
    fig_pie = px.pie(
        pie_df,
        values="Advertising_Expenditure",
        names="Vehicle_Type",
        labels=label_names,
        title=f"Total Advertising Expenditure by Vehicle Type in {entered_year}",
    )
    # fig_pie.show()
    return [fig_line, fig_line_2, fig_bar, fig_pie]


if __name__ == "__main__":
    app.run_server(debug=True, port=8051)


# In[1]:


import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, callback, dcc, html, no_update

URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv"

df = pd.read_csv(URL)
print("Data downloaded and read into a dataframe!")

# DataFrame Const Variables
df_rec = df[df["Recession"] == 1]

# Other formatting Consts
vehicle_type_names = {
    "Supperminicar": "Super Mini Car",
    "Mediumfamilycar": "Medium Family Car",
    "Smallfamiliycar": "Small Family Car",
    "Sports": "Sports Car",
    "Executivecar": "Executive Car",
}
label_names = {
    "Automobile_Sales": "Automobile Sales",
    "Vehicle_Type": "Vehicle Type",
    "Advertising_Expenditure": "Advertising Expenditure",
    "unemployment_rate": "Unemployment Rate",
}
month_order = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

external_stylesheets = ["https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css"]
app = Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
# Clear the layout and do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True

app.layout = html.Main(
    children=[
        html.H1(
            "Automobile Sales Statistics Dashboard",
            className="mt-8 text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl text-center",
        ),
        html.Div(
            [
                html.Label(
                    "Select Report Type:",
                    className="text-base font-semibold text-gray-900",
                    htmlFor="input-report",
                ),
                html.P(
                    "Which report would you like to display, yearly or recession?",
                    className="text-sm text-gray-500",
                ),
                dcc.Dropdown(
                    options=[
                        {"label": "Yearly Statistics", "value": "Yearly"},
                        {"label": "Recession Period Statistics", "value": "Recession"},
                    ],
                    value="Yearly",
                    id="input-report",
                ),
            ],
            className="mt-4 w-full max-w-sm mx-auto",
        ),
        html.Div(
            [
                html.Label(
                    "Year:",
                    className="text-base font-semibold text-gray-900",
                    htmlFor="input-year",
                ),
                html.P(
                    "Which year would you like to display for the yearly report?",
                    className="text-sm text-gray-500",
                ),
                dcc.Dropdown(
                    sorted(df.Year.unique()), value=2005, id="input-year", disabled=True
                ),
            ],
            className="mt-4 w-full max-w-sm mx-auto",
        ),
        html.Section(
            [
                dcc.Graph(id="plot-1", className="w-full max-w-3xl mx-auto"),
                dcc.Graph(id="plot-2", className="w-full max-w-3xl mx-auto"),
                dcc.Graph(id="plot-3", className="w-full max-w-3xl mx-auto"),
                dcc.Graph(id="plot-4", className="w-full max-w-3xl mx-auto"),
            ],
            className="flex flex-wrap items-center justify-center",
        ),
    ],
    className="flex flex-col items-center",
)


@callback(Output("input-year", "disabled"), Input("input-report", "value"))
def disable_year(report_value):
    if report_value == "Recession":
        return True
    else:
        return False


@callback(
    [
        Output(component_id="plot-1", component_property="figure"),
        Output(component_id="plot-2", component_property="figure"),
        Output(component_id="plot-3", component_property="figure"),
        Output(component_id="plot-4", component_property="figure"),
    ],
    [
        Input(component_id="input-report", component_property="value"),
        Input(component_id="input-year", component_property="value"),
    ],
)
def display_graphs(report_value, entered_year):
    if report_value == "Recession":
        return recession_graphs()
    else:
        return year_graphs(entered_year)


def recession_graphs():
    # Line Graph, Avg Sales by year
    fig_line = px.line(
        df_rec[["Year", "Automobile_Sales"]].groupby("Year").mean().reset_index(),
        x="Year",
        y="Automobile_Sales",
        title="Average Automobile Sales by Year during Recession Periods",
        color_discrete_sequence=["#C45A9A"],
        labels=label_names,
    )
    # fig_line.show()
    # Bar Graph 1, Avg sales by vehicle type
    bar_df = (
        df_rec[["Vehicle_Type", "Automobile_Sales"]]
        .groupby("Vehicle_Type")
        .mean()
        .reset_index()
    )
    bar_df["Vehicle_Type"] = bar_df["Vehicle_Type"].map(vehicle_type_names)
    fig_bar_1 = px.bar(
        bar_df,
        x="Vehicle_Type",
        y="Automobile_Sales",
        title="Average Automobile Sales by Vehicle Type during Recession Periods",
        color_discrete_sequence=["#C45A9A"],
        labels=label_names,
    )
    # fig_bar_1.show()
    # Pie graph Sum ad expense by vehicle type
    pie_df = (
        df_rec[["Vehicle_Type", "Advertising_Expenditure"]]
        .groupby("Vehicle_Type")
        .sum()
        .reset_index()
    )
    pie_df["Vehicle_Type"] = pie_df["Vehicle_Type"].map(vehicle_type_names)
    fig_pie = px.pie(
        pie_df,
        values="Advertising_Expenditure",
        names="Vehicle_Type",
        title="Total Advertising Expenditure by Vehicle Type during Recession Periods",
        labels=label_names,
    )
    # fig_pie.show()
    # Bar Graph 2, Sales per vehicle type by unemployment rate
    bar2_df = (
        df_rec[["unemployment_rate", "Vehicle_Type", "Automobile_Sales"]]
        .groupby(["Vehicle_Type", "unemployment_rate"])
        .sum()
        .reset_index()
    )
    fig_bar_2 = px.bar(
        bar2_df,
        x="unemployment_rate",
        y="Automobile_Sales",
        color="Vehicle_Type",
        labels=label_names,
        title="Automobile Sales by Vehicle Type Per Unemployment Rate during Recession Periods",
    )
    # Change the car names to remove underscores in legend and on hover
    fig_bar_2.for_each_trace(
        lambda t: t.update(
            name=vehicle_type_names[t.name],
            legendgroup=vehicle_type_names[t.name],
            hovertemplate=t.hovertemplate.replace(t.name, vehicle_type_names[t.name]),
        )
    )
    # fig_bar_2.show()
    return [fig_line, fig_bar_1, fig_pie, fig_bar_2]


def year_graphs(entered_year):
    # Get the DataFrame for selected year
    df_year = df[df["Year"] == entered_year]
    # Line graph, Average sales per year
    df_line = df[["Year", "Automobile_Sales"]].groupby("Year").mean()
    fig_line = px.line(
        df_line,
        y="Automobile_Sales",
        labels=label_names,
        title="Yearly Average Automobile Sales",
        color_discrete_sequence=["#C45A9A"],
    )
    # fig_line.show()
    # Line Graph 2, total monthly sales for year
    fig_line_2 = px.line(
        df_year,
        x="Month",
        y="Automobile_Sales",
        labels=label_names,
        title=f"Total Automobile Sales per Month in {entered_year}",
        color_discrete_sequence=["#C45A9A"],
    )
    # fig_line_2.show()
    # Bar chart, Avg sales per month by vehicle type
    df_bar = (
        df_year[["Vehicle_Type", "Automobile_Sales"]]
        .groupby("Vehicle_Type")
        .sum()
        .reset_index()
    )
    df_bar["Automobile_Sales"] = (
        df_bar["Automobile_Sales"] / 12
    )  # dividing by 12 to get monthly average
    df_bar["Vehicle_Type"] = df_bar["Vehicle_Type"].map(vehicle_type_names)
    fig_bar = px.bar(
        df_bar,
        x="Vehicle_Type",
        y="Automobile_Sales",
        labels=label_names,
        title=f"Average Monthly Automobile Sales by Vehicle Type in {entered_year}",
        color_discrete_sequence=["#C45A9A"],
    )
    # fig_bar.show()
    # Pie graph, total ad expense by vehicle type
    pie_df = (
        df_year[["Advertising_Expenditure", "Vehicle_Type"]]
        .groupby("Vehicle_Type")
        .sum()
        .reset_index()
    )
    pie_df["Vehicle_Type"] = pie_df["Vehicle_Type"].map(vehicle_type_names)
    fig_pie = px.pie(
        pie_df,
        values="Advertising_Expenditure",
        names="Vehicle_Type",
        labels=label_names,
        title=f"Total Advertising Expenditure by Vehicle Type in {entered_year}",
    )
    # fig_pie.show()
    return [fig_line, fig_line_2, fig_bar, fig_pie]


if __name__ == "__main__":
    app.run_server(debug=True, port=8055)


# In[3]:


import dash
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

# Sample data URL
URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv"

# Load data
df = pd.read_csv(URL)

# Prepare list of years
year_list = [i for i in range(1980, 2024, 1)]

# Initialize the Dash app
app = Dash(__name__)

# Define the app layout
app.layout = html.Div(
    children=[
        html.H1(
            "Automobile Sales Statistics Dashboard",
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 24}
        ),
        html.Div(
            [
                dcc.Dropdown(
                    id='dropdown-statistics',
                    options=[
                        {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
                        {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
                    ],
                    placeholder='Select a report type',
                    style={'width': '80%', 'padding': '3px', 'font-size': '20px', 'text-align-last': 'center'}
                )
            ],
            style={'display': 'flex', 'justify-content': 'center', 'margin-bottom': '20px'}
        ),
        html.Div(
            [
                dcc.Dropdown(
                    id='select-year',
                    options=[{'label': i, 'value': i} for i in year_list],
                    placeholder='Select a year',
                    style={'width': '80%', 'padding': '3px', 'font-size': '20px', 'text-align-last': 'center'}
                )
            ],
            style={'display': 'flex', 'justify-content': 'center', 'margin-bottom': '20px'}
        ),
        html.Div(
            [
                html.Div(id='output-container', className='chart-grid', style={'display': 'flex'})
            ]
        )
    ]
)

# Define callbacks to update the graphs based on dropdown selections
@app.callback(
    Output('output-container', 'children'),
    Input('dropdown-statistics', 'value'),
    Input('select-year', 'value')
)
def update_output(report_type, year):
    if report_type == 'Yearly Statistics' and year:
        return year_graphs(year)
    elif report_type == 'Recession Period Statistics':
        return recession_graphs()
    return html.Div()

def year_graphs(selected_year):
    # Filter data for the selected year
    df_year = df[df['Year'] == selected_year]

    # Line graph: Average sales per year
    fig_line = px.line(
        df.groupby('Year')['Automobile_Sales'].mean().reset_index(),
        x='Year', y='Automobile_Sales',
        title='Yearly Average Automobile Sales'
    )

    # Line graph: Total monthly sales for selected year
    fig_line_2 = px.line(
        df_year,
        x='Month', y='Automobile_Sales',
        title=f'Total Automobile Sales per Month in {selected_year}'
    )

    # Bar chart: Avg sales per month by vehicle type
    df_bar = df_year.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
    fig_bar = px.bar(
        df_bar,
        x='Vehicle_Type', y='Automobile_Sales',
        title=f'Average Monthly Automobile Sales by Vehicle Type in {selected_year}'
    )

    # Pie chart: Total ad expense by vehicle type
    df_pie = df_year.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
    fig_pie = px.pie(
        df_pie,
        values='Advertising_Expenditure', names='Vehicle_Type',
        title=f'Total Advertising Expenditure by Vehicle Type in {selected_year}'
    )

    return [
        dcc.Graph(figure=fig_line),
        dcc.Graph(figure=fig_line_2),
        dcc.Graph(figure=fig_bar),
        dcc.Graph(figure=fig_pie)
    ]

def recession_graphs():
    df_rec = df[df['Recession'] == 1]

    # Line graph: Avg Sales by year
    fig_line = px.line(
        df_rec.groupby('Year')['Automobile_Sales'].mean().reset_index(),
        x='Year', y='Automobile_Sales',
        title='Average Automobile Sales by Year during Recession Periods'
    )

    # Bar chart: Avg sales by vehicle type
    df_bar = df_rec.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
    fig_bar = px.bar(
        df_bar,
        x='Vehicle_Type', y='Automobile_Sales',
        title='Average Automobile Sales by Vehicle Type during Recession Periods'
    )

    # Pie chart: Sum ad expense by vehicle type
    df_pie = df_rec.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
    fig_pie = px.pie(
        df_pie,
        values='Advertising_Expenditure', names='Vehicle_Type',
        title='Total Advertising Expenditure by Vehicle Type during Recession Periods'
    )

    # Bar chart: Sales per vehicle type by unemployment rate
    df_bar_2 = df_rec.groupby(['unemployment_rate', 'Vehicle_Type'])['Automobile_Sales'].sum().reset_index()
    fig_bar_2 = px.bar(
        df_bar_2,
        x='unemployment_rate', y='Automobile_Sales', color='Vehicle_Type',
        title='Automobile Sales by Vehicle Type Per Unemployment Rate during Recession Periods'
    )

    return [
        dcc.Graph(figure=fig_line),
        dcc.Graph(figure=fig_bar),
        dcc.Graph(figure=fig_pie),
        dcc.Graph(figure=fig_bar_2)
    ]

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)


# In[ ]:




