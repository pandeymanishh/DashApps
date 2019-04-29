import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pickle
import pandas as pd

os.chdir('F:\\Learning\\Python Stuff\\\Plotly_Dash\\Dash_1')


with open('model_.pkl' , 'rb') as file:
    coeff = pickle.load(file)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.config['suppress_callback_exceptions']=True

# Get the Upload Component
upload_component = dcc.Upload(id='upload-data'
                               , children=html.Div(['Drag and Drop or '
                                                    ,html.A('Select Files')])
                               , style={'height': '100%',
                                        'borderWidth': '1px',
                                        'borderStyle': 'dashed',
                                        'borderRadius': '2px',
                                        'textAlign': 'center', 'padding':'4px'}
                               , multiple=True)

# Parse the upload contents
def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    
    # Now get the scores and the score summary
    
    df['score'] = df['xval']*coeff[0]+df['yval']*coeff[1]
    
    # Get the summary of the changes made 
    
    
    
    return {'contents':{'File Name':filename
            ,'Last Modified':datetime.datetime.fromtimestamp(date)
            , 'Rows':df.shape[0]
            , 'Columns':df.shape[1]},
            'processed':{'File Name':filename, 'Min Score':df['score'].min()
                         , 'Max Score':df['score'].max()},
            'data':{'filename':filename,'dt':df},
            'proc_dt':{'filename':filename,'dt':df[['id', 'score']]}}


# --------------------------------------App Layout---------------------------#

app.layout = html.Div([html.Div(upload_component, className='ui red segment')
                       , html.Div(className="ui divider")
                       , html.Div(id='output-data-upload', className='ui red segment')]
                     , className='ui raised segment')

# --------------------------------------Callback-----------------------------#

# Call back to read the uploaded contents and get the relevant div to display
@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        
        # Parse the file contents
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        
        # Get the file summary
        file_summ = [x['contents'] for x in children]
        
        upload_s = pd.DataFrame(file_summ)
             
        upload_s = upload_s[['File Name', 'Last Modified', 'Rows', 'Columns']]
        
        # Get the scored summary of the files
        scr_summ = [x['processed'] for x in children]
        
        scr_summ = pd.DataFrame(scr_summ)
             
        scr_summ = scr_summ[['File Name', 'Min Score', 'Max Score']]        
        
  
        return html.Div([html.Div('File Import Summary', className='ui red header')
                         , html.Br()
                         , dash_table.DataTable(data=upload_s.to_dict('rows')
                                              , columns=[{'name': i, 'id': i} for i in upload_s.columns]
                                              , style_as_list_view=False
                                              , style_cell={'padding': '1px', 'textAlign': 'center'}
                                              , style_header={'backgroundColor': 'red'
                                                              ,'fontWeight': 'bold'
                                                              , 'color':'white'}
                                              , style_cell_conditional=[{'if': {'row_index': 'odd'}
                                              , 'backgroundColor': 'rgb(248, 248, 248)' }])
                        , html.Br()
                        , html.Div('File Scoring Summary', className='ui red header')
                        , dash_table.DataTable(data=scr_summ.to_dict('rows')
                                              , columns=[{'name': i, 'id': i} for i in scr_summ.columns]
                                              , style_as_list_view=False
                                              , style_cell={'padding': '1px', 'textAlign': 'center'}
                                              , style_header={'backgroundColor': 'red'
                                                              ,'fontWeight': 'bold'
                                                              , 'color':'white'}
                                              , style_cell_conditional=[{'if': {'row_index': 'odd'}
                                              , 'backgroundColor': 'rgb(248, 248, 248)' }])])



if __name__ == '__main__':
    app.run_server()
    
    

df = pd.DataFrame({
    'a': [1, 2, 3, 4],
    'b': [2, 1, 5, 6],
    'c': ['x', 'x', 'y', 'y']
})


def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


app = dash.Dash(__name__)
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
app.layout = html.Div([
    html.Label('Filter'),

    dcc.Dropdown(
        id='field-dropdown',
        options=[
            {'label': i, 'value': i} for i in
            (['all'] + list(df['c'].unique()))],
        value='all'
    ),
    html.Div(id='table'),
    html.A(
        'Download Data',
        id='download-link',
        download="rawdata.csv",
        href="",
        target="_blank"
    )
])


def filter_data(value):
    if value == 'all':
        return df
    else:
        return df[df['c'] == value]


@app.callback(
    dash.dependencies.Output('table', 'children'),
    [dash.dependencies.Input('field-dropdown', 'value')])
def update_table(filter_value):
    dff = filter_data(filter_value)
    return generate_table(dff)


@app.callback(
    dash.dependencies.Output('download-link', 'href'),
    [dash.dependencies.Input('field-dropdown', 'value')])
def update_download_link(filter_value):
    dff = filter_data(filter_value)
    csv_string = dff.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.quote(csv_string)
    return csv_string


if __name__ == '__main__':
    app.run_server(debug=True)