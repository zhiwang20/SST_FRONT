import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import numpy as np
from dash.dependencies import Input, Output, State
from pymongo import MongoClient


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout=html.Div([
    html.Div([html.H4(children='NOAA SST')], style={'padding-bottom': '20px'}),
    
    html.Div(
    [
    
        html.H3("choose your platform and instrument first and input your coordinate bound, then press graph it"),
              
            dcc.Dropdown(
                id='demo-dropdown',
                options=[
                #MetOP-A is a satellite and virrs is a instrument
                #could put value = ""
                {'label': 'Polar Instrument: VIRRS onboard N20', 'value': 'VIRRS,N20'},
                {'label': 'Polar Instrument: VIRRS onboard NPP', 'value': 'VIRRS,NPP'},
                {'label': 'Polar Instrument: MODIS onboard Aqua', 'value': 'MODIS,Aqua'},
                {'label': 'Polar Instrument: MODIS onboard Terra', 'value': 'MODIS,Terra'},
                {'label': 'Polar Instrument: AVHRR onboard MetOP-A', 'value': 'AVHRR,MetOP-A'},
                {'label': 'Polar Instrument: AVHRR onboard MetOP-B', 'value': 'AVHRR,MetOP-B'},
                {'label': 'Polar Instrument: AVHRR onboard MetOP-C', 'value': 'AVHRR,MetOP-C'},
                {'label': 'Geo Instrument: ABI onboard G-16', 'value': 'ABI,G-16'},
                {'label': 'Geo Instrument: ABI onboard G-17', 'value': 'ABI,G-17'},
                {'label': 'Geo Instrument: AHI onboard Himawari-8', 'value': 'AHI,Himawari-8'}
                ]
            ),
            
            html.Br(),
            
            dcc.Input(
                    id="input-time-min",
                    placeholder="Add minimum time bound",
                    type="text",
                    value="",
                ),
            dcc.Input(
                    id="input-time-max",
                    placeholder="add maximum time bound",
                    type="text",
                    value="",
                ),

            dcc.Input(
                    id="input-min-lon",
                    placeholder="Add minimum longtiude",
                    type="number",
                    value="",
                ),
            
            dcc.Input(
                    id="input-min-lat",
                    placeholder="Add minimum latitude",
                    type="number",
                    value="",
                ),
    
            dcc.Input(
                    id="input-max-lon",
                    placeholder="Add maximum longtiude",
                    type="number",
                    value="",
                ),
                
            dcc.Input(
                    id="input-max-lat",
                    placeholder="Add maximum latitude",
                    type="number",
                    value="",
                ),
                
            html.Button('Graph it', id='submit-val', n_clicks=0),
            
            html.Br(),
            html.Br(),
            html.Div(id="output"),
            html.Br(),
            html.P('input time needs to in this format: 2020-09-29 00:04:56', style={'color': 'red'}),
            html.P('2020-09-29 00:00:58------2020-09-29 00:09:58; 11, -24, 14, -22', style={'color': 'red'}),
            html.P('example: bottom-left [11, -24] and top-right [14,-22]; ', style={'color': 'red'}),
    ]),
    

    html.Div(id='scatter'),
])

#Input is what triggers, State does not
#some same latitude andl longitude less rounding?
@app.callback(Output('scatter','children'),
              [Input('submit-val', 'n_clicks')],
              [State("demo-dropdown", "value"),State("input-time-min", "value"),State("input-time-max", "value"),
              State("input-min-lon", "value"), State("input-min-lat", "value"), State("input-max-lon", "value"), State("input-max-lat", "value")],
              )
def update_output_scatter_marker(n_clicks, dropdown, search_time_min, search_time_max , min_lon, min_lat, max_lon, max_lat):
    if n_clicks == 0:  #won't continue to run codes below when just loading the app
        return None
    #print(type(dropdown))  #<class 'NoneType'>--if not a dropdown option is selected
    #print(type(min_lon))    #<class 'str'>---empty string when no user input
    if dropdown is None or search_time_min == '' or search_time_max == '' or min_lon== '' or min_lat== '' or max_lon== '' or max_lat== '':
        return 'make sure to select a platform instrument and fill out bounds before graph it'
    #n_clicks only for triggering button, not used as a variable
    client = MongoClient('mongodb://localhost:27017/')
    dropdowns = dropdown.split(',')
    #db = client.capstone
    #collection = db.test
    database_name = dropdowns[0]
    collection_name = dropdowns[1]
    db = client[database_name]
    collection = db[collection_name]

    #search time bound inclusively: string comparison to compare time
    agg = collection.aggregate([
        { '$match': {'time': {'$gte':search_time_min, '$lte':search_time_max}}},  #'$match': {'time': search_time}},  #'time': "2020-09-29 00:09:58  #"2020-09-29 00:04:56"
        { '$addFields':
            {"coordinate": { "$zip": { "inputs": [ "$lon", "$lat" ] } }}
        },   
        { "$project": {
            "_id": 0,
            #"time":1,
            "coordinate": 1,
            "sst":1,
            'satellite_zenith_angle':1,
            'sst_gradient_magnitude':1
            #[ [ -86.61, -3.49 ], [ -86.51, -3.39 ] ] } }  
            #[ <bottom left coordinates> ],[ <upper right coordinates> ]   ---> [<min_lon,min_lat>],[<max_lon,max_lat>]  --->
        }}
    ])
        
    def FindPoint(x1, y1, x2, y2, x, y) :  #make inclusive
        if (x >= x1 and x <= x2 and y >= y1 and y <= y2) : 
            return True
        else : 
            return False
            
    #min_lon, min_lat, max_lon, max_lat = -86.61, -3.49 , -86.51, -3.39   #bottom-left [-86.61, -3.49] and top-right [-86.51, -3.39]

    
    #By default, MongoDB will automatically close a cursor when the client has exhausted all results in the cursor.
    #agg is one time usage, so we cannot use len(list(agg)) before
    # is agg is not found or len(list(agg)) is 0, then this for loop won't run
    loop_run = False
    coor_found = False
    graph_list = []
    fig = go.Figure()
    for a in agg:
        coord_list = []
        sst_list = []
        angle_list = []
        magnitude_list = []
        #time_list = []
        loop_run = True #this means the search is found
        #print(type(a)) #<class 'dict'>
        #for value in a.values():
        wanted_index = 0
        for coord in a['coordinate']:
            if FindPoint(min_lon, min_lat, max_lon, max_lat, coord[0], coord[1]) : 
                coor_found = True
                print('yes: ', coord)
                coord_list.append(coord)
                #alternative: sst_list.extend([a['sst'][wanted_index]]) #'float' object is not iterable so use [] around it
                sst_list.append(a['sst'][wanted_index]) #wants sst matches the coordinate within the bound
                angle_list.append(a['satellite_zenith_angle'][wanted_index])
                magnitude_list.append(a['sst_gradient_magnitude'][wanted_index])
                #time_list.append(a['time'])
            else:
                print('not in bound: ', coord)
            wanted_index += 1
        if len(coord_list) == 0:  #skip to next for loop execution because this 'time' has not coordiante found
            continue  #continue skips the statements after it, whereas pass do nothing like that

        '''       
        def euclidian_distance(a, b):
            print(a,b)
            print(np.linalg.norm(a - b))
            return np.linalg.norm(a - b) #return to point, which is the distance value
        coords = np.array(coord_list)
        coords2 = sorted(coords, key=lambda point: euclidian_distance(point, coords[0])) #sort by distance---distnace is computed by comparing coords[0]
        a = np.matrix(coords2) # matrix is only for formatting for readability purposes
        '''
        def euclidian_distance(a, b):
            return np.linalg.norm(a - b)
        coords = np.array(coord_list) #need numpy array to work
        dist_list = []
        for pt in coords:
            dist = euclidian_distance(pt, coords[0])
            dist_list.append(dist)
        
        data_initial = pd.DataFrame(coord_list,columns=['lon','lat'])
        #other_features = pd.DataFrame({'sst':sst_list,'angle':angle_list,'magnitude':magnitude_list, 'time':time_list})
        other_features = pd.DataFrame({'sst':sst_list,'angle':angle_list,'magnitude':magnitude_list,'dist':dist_list})
        result = pd.concat([data_initial,other_features],axis=1)
        result = result.sort_values(by=['dist'])
     
        # Define a hover-text generating function (returns a list of strings)
        def make_text(result):
            return 'SST: %s\
            <br>satellite_zenith_angle: %s\
            <br>sst_gradient_magnitude: %s K/km'\
            % (result['sst'], result['angle'], result['magnitude'])

        #print(data_initial)
        
        
        trace = go.Scatter(
                        #x = scatter_x,
                        #y = scatter_y,
                        x = result['lon'],
                        y = result['lat'],
                        mode='lines+markers',
                        line = dict(color = ('rgb(22, 96, 167)')), #so each trace didn't have same color  #,width=1

                        showlegend = False,
                        text=result.apply(make_text, axis=1).tolist()
                      )
        graph_list.append(trace)
        
    
    if loop_run is False:
        return 'The time-search is not found, please try again'  #when time bound is wrong time format or time order(small to large); #when platform wrong too
    if coor_found is False:
        return 'The time-search is found but not a coordinate within the coordinate-bound, please try again'
    layout = go.Layout(
                    xaxis=dict(title='Longtiude',range=[min_lon,max_lon]),
                    yaxis=dict(title='Latiude', range=[min_lat,max_lat])
                    #axis='title': 'Longtiude', range = [min_lon,max_lon]}, #not work in this format
                    #xaxis={'title': 'Latiude'},#will autoscale
                    #yaxis={'title': 'Latiude'} #will autoscale
                    )
    fig = go.Figure(data=graph_list,layout=layout)
    return dcc.Graph(figure=fig)
    
if __name__ == '__main__':
    app.run_server(debug=True)
    
    
'''
                        mode = 'markers',
                        marker = dict(
                            #size = 8,
                            #opacity = 0.8,
                            #reversescale = True,
                            #autocolorscale = False,
                            #symbol = 'square',
                            line = dict(
                                width=1,
                                #color = ('rgb(22, 96, 167)')
                            ),
                            #colorscale = scl,
                            #cmin = result['sst'].min(),
                            color = result['sst'],
                            #cmax = result['sst'].max(),
                            colorbar=dict(
                                title="SST", tickvals=[result['sst'].min(),result['sst'].max()]  #different component has differnt max color value
                            )
                        ),
'''

'''
        fig.add_trace(go.Scatter(
                        #x = scatter_x,
                        #y = scatter_y,
                        x = result['lon'],
                        y = result['lat'],
                        mode='lines+markers',
                        #mode='markers',
                        text=result.apply(make_text, axis=1).tolist()
                      ))
        fig.update_layout(go.Layout(
                    xaxis=dict(title='Longtiude',range=[min_lon,max_lon]),
                    yaxis=dict(title='Latiude', range=[min_lat,max_lat])
                    #axis='title': 'Longtiude', range = [min_lon,max_lon]}, #not work in this format
                    #xaxis={'title': 'Latiude'},#will autoscale
                    #yaxis={'title': 'Latiude'} #will autoscale
                    ))
                    
                    
                    --------------------------
                    fig.add_trace(go.Scatter(
                        #x = scatter_x,
                        #y = scatter_y,
                        x = result['lon'],
                        y = result['lat'],
                        line = dict(color = ('rgb(22, 96, 167)'), width = 1), #so each trace didn't have same color

                        showlegend = False,
                        text=result.apply(make_text, axis=1).tolist()
                      ))
        fig.update_layout(go.Layout(
                    #xaxis=dict(title='Longtiude',range=[min_lon,max_lon]),
                    #yaxis=dict(title='Latiude', range=[min_lat,max_lat])
                    #axis='title': 'Longtiude', range = [min_lon,max_lon]}, #not work in this format
                    xaxis={'title': 'Latiude'},#will autoscale
                    yaxis={'title': 'Latiude'} #will autoscale
                    ))
                    
                    
                    return dcc.Graph(figure=fig,layout=go.Layout(
                    #xaxis=dict(title='Longtiude',range=[min_lon,max_lon]),
                    #yaxis=dict(title='Latiude', range=[min_lat,max_lat])
                    #axis='title': 'Longtiude', range = [min_lon,max_lon]}, #not work in this format
                    xaxis={'title': 'Latiude'},#will autoscale
                    yaxis={'title': 'Latiude'} #will autoscale
                    ))
 '''