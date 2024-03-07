from pathlib import Path
import pandas as pd
import json
import random
from bokeh.layouts import column, row
from bokeh.plotting import figure, curdoc
from bokeh.models import ColumnDataSource, Dropdown, Select

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

COMPANY_COLUMN_NAME = "mfr"
cereal_df = None
nutrition_columns = None
company_names = None
company_names_lookup = None
copmany_reverse_lookup = None

plot_dataset = ColumnDataSource(dict(company=[], amount=[]))
rating_dataset = ColumnDataSource(dict(company=[], rating=[]))

def get_datafile_path(fname):
     return Path(__file__).parent / "data" / fname

def load_company_names():
     global company_names, company_names_lookup, copmany_reverse_lookup
     company_names_path = get_datafile_path("company_names.json")
     company_names_lookup = json.load(open(company_names_path, "r"))
     company_names_lookup = {k: v.replace(" ", "\n") for k, v in company_names_lookup.items()}
     copmany_reverse_lookup = {v: k for k, v in company_names_lookup.items()}
     company_names = list(copmany_reverse_lookup.keys())

def load_cereal_df():
    global cereal_df, nutrition_columns
    csv_path = get_datafile_path("cereal.csv")
    cereal_df = pd.read_csv(csv_path)

#     print(cereal_df.head())
    #assume that the first three columns are non-nutrition columns
    nutrition_columns = [str(x) for x in cereal_df.columns[3:]]

    cereal_df = cereal_df.groupby(COMPANY_COLUMN_NAME).agg(
        {x: "mean" for x in nutrition_columns}
    )

def grab_nutrition_data(nutrition_item):
     return {
          "company": company_names,
          "amount": [
               cereal_df.loc[copmany_reverse_lookup[company]][nutrition_item]
               for company in company_names
          ],
     }

def grab_rating_data():
    return {
        "company": company_names,
        "rating": [cereal_df.loc[copmany_reverse_lookup[company]]['rating']
               for company in company_names]  # Sample random ratings for demonstration
    }

def update_plot(event):
     global plot_dataset
#      print(event.item)
     new_data = grab_nutrition_data(event.item)
     plot_dataset.data = new_data

def update_rating_plot():
    global rating_dataset
    new_data = grab_rating_data()
    rating_dataset.data = new_data

def main():
    global cereal_df, nutrition_columns, company_names, plot_dataset, rating_dataset

    # Data prep
    load_cereal_df()
    load_company_names()
    
    # Bokeh visualization
    p = figure(x_range=company_names, title="Nutritional values")
    p2 = figure(x_range=company_names, title="Average Rating")

    p.vbar(
        x='company',
        top = 'amount',
        source=plot_dataset,
        width=0.9,
        color="blue"
    )

    p2.line(
        x='company',
        y='rating',
        source=rating_dataset,
        line_width=2,
        color="green"
    )

    dropdown = Dropdown(label="Nutrition item", menu=nutrition_columns)
    dropdown.on_event("menu_item_click", update_plot)
    
    update_rating_plot()  
    
    curdoc().add_root(column(dropdown, row(p, p2))) 
#     curdoc().add_root(column(dropdown, p))
        

main()

