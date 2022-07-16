from dash import Dash, html, dcc, ctx
from datetime import date, datetime
from dash.exceptions import PreventUpdate
from database_service import MongoDBServices
from constants import Constants
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ClientsideFunction
import pytz
import dash_daq as daq

# initialise the application
app = Dash(__name__, external_scripts=["https://cdnjs.cloudflare.com/ajax/libs/dragula/3.7.2/dragula.min.js", 
                        "https://epsi95.github.io/dash-draggable-css-scipt/script.js"], 
    external_stylesheets=["https://epsi95.github.io/dash-draggable-css-scipt/dragula.css", dbc.themes.BOOTSTRAP])

server = app.server

# initialise the db connection
mongo_service_obj = MongoDBServices()

sub_category_dict = {"Personal": {"learning": "learning", "implementing": "implementing"},
					 "Office": {"debugging": "debugging", "coding": "coding"}}

def greetings():
	current_hour = datetime.now(pytz.timezone('Asia/Calcutta')).hour
	if current_hour < 12:
		return "Morning"
	elif current_hour < 18:
		return "Afternoon"
	else:
		return "Evening"

def last_task_added():
	task_list = sorted(list(mongo_service_obj.load_documents(Constants.IN_PROGRESS_TASK_COLLECTION,{})), key=lambda d: d["task_date"])
	return task_list[-1]["task_date"]

# build the layout
def page_layout():
	return html.Div([
			dcc.ConfirmDialog(id='display-message'),
			dcc.Store(id="store"),
			dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Mark this task as Complete"), close_button=False),
                dbc.ModalBody("Sure?"),
                dbc.ModalFooter([
                    dbc.Button("Yes", id="mark-complete", className="ms-auto"),
                    dbc.Button("No", id="dont-mark-complete")]
                ),
            ],
            	id="modal-confirm-complete",
            	is_open=False,
        	),
			html.Div([html.H5("Experimental Work Tracking Application")], style={"textAlign": "center"}),
			html.Div([html.H4("Good {}, user".format(greetings())), html.H5("Let's get Productive")], style={"padding-top":"10px"}),
			html.Div([
				html.Div(id="div1", children=[

					html.Div(children=[
							html.H4("You have added {} tasks".format(len(list(mongo_service_obj.load_documents(Constants.IN_PROGRESS_TASK_COLLECTION,{}))))),
							html.H6("Click to view, drag to rearrange")

						]) 

				], style={"border":"2px solid blue", "width":"100%", "height": "100%", "align-items": "center", "display":"flex"}),
				
				html.Div(id="div2", children="Last task was added {}".format(last_task_added()), style={"border":"2px solid green", "width":"100%", "height": "100%", "align-items": "center", "display": "flex"}),
				html.Div(id="div3", children=[html.H4("Check out your task analytics")], style={"border":"2px solid yellow", "width":"100%", "height": "100%", "align-items": "center", "display": "flex"})
				], style={"display": "flex", "justify-content": "space-between", "height": "150px", "margin-top": "20px", "align-items": "center"}),
			
			

			html.Div(id="display", hidden=True, style={"height": "250px", "border":"2px solid black"}),

			html.Div([html.Button(id="add-task", children="Add a New Task")], style={"padding-top": "20px", "display": "flex", "justify-content":"center"}),
			
			html.Div(id="add-task-block", hidden=True, children=[
								html.Div([
					# create radio button for category of Work
					# has 2 categories - Personal and Office
					# currently defaults to Personal
					html.Div([
						html.Pre("Task Category:"),
						html.Div([dcc.RadioItems(id="work-category", options=["Personal", "Office"], value="Personal")])
							]),
					
					# populate the sub-category based on the work category
					# since the options have to change dynamically, we have to use callbacks here
					html.Div([
						html.Pre("Task Sub Category:"),
						html.Div([dcc.Dropdown(id="sub-category", value="none", style={"width": "200px"}), html.Button(id="add-sub-category-btn", hidden=True, children="+")], style={"display":"flex", "justify-content":"space-around"})
							]),

					
					# choose date
					# by default it shows today's date
					html.Div([
						html.Pre("Task Started on:"),
						html.Div([dcc.DatePickerSingle(id="start-date", date=date.today(), max_date_allowed=date.today())])
							]),

					


				], style={"display": "flex", "justify-content": "space-between", "padding-left": "100px", "padding-right": "100px"}),
			html.Div([
					dcc.Input(id="work-description", type="text", placeholder="Enter your task description here", spellCheck=True, size="100"),
					html.Button(id="submit-button", children="Submit")
				], style={"display": "flex", "justify-content": "center", "padding-top": "50px", "height": "100px"}),

			html.Div([
					html.Div([
						html.Pre("Task Status: "),
						html.Div([daq.ToggleSwitch(id="task-status", label=["In-progress", "Complete"], value=False)])	
						]),
					html.Div(id="date-completed", children=[
						html.Pre("Task completed on:"),
						html.Div([dcc.DatePickerSingle(id="end-date", date=date.today(), max_date_allowed=date.today())])
							], hidden=True)

				], style={"display":"flex", "justify-content": "space-evenly"})

					]), 

			
			
			html.Div([html.Details([
						html.Summary(id="task_info", children="Task Count: {}".format(len(list(mongo_service_obj.load_documents(Constants.IN_PROGRESS_TASK_COLLECTION,{})))) ),
						html.Div(id="drag_tasks")
				])],style={"padding-top": "50px", "textAlign": "center"})

			
			

	])

# this will reload and update the changes in layout for every page refresh
app.layout = page_layout


# function to dynamically populate the dropdown
@app.callback([Output(component_id="sub-category", component_property="options"), Output("sub-category", "value")], [Input(component_id="work-category", component_property="value"), Input("add-task", "n_clicks")])
def populate_dropdown(work_category, n_clicks):
	if work_category or n_clicks:
		return sub_category_dict[work_category], None


@app.callback(Output("work-category", "value"), Input("add-sub-category-btn", "n_clicks"), [State(component_id="store", component_property="data"), State("work-category", "value")])
def update_sub_tasks(n_clicks, data_store, work_category):
	if n_clicks is None:
		raise PreventUpdate

	else:
		print(data_store)
		print(work_category)
		if data_store[-1] not in sub_category_dict[work_category].keys():
			sub_category_dict[work_category][data_store[-1]] = data_store[-1]
		return work_category


# this function will save the searched sub category into a temporary data store
@app.callback(
    Output("store", "data"),
    Input('sub-category', 'search_value'),
    State("store", "data") 
)
def get_search_value(search_value, data_store):
	search_list = []
	if search_value is not None and search_value != "":
		data_store = search_value
		search_list.append(data_store)
		return search_list
	else:
		return data_store



# function to open/close the modal to confirm if a task should be marked as complete
@app.callback(Output("modal-confirm-complete", "is_open"), 
	[Input("task-status", "value"), Input("mark-complete", "n_clicks"), Input("dont-mark-complete", "n_clicks")])
def show_modal(task_status, mark_complete_click, dont_mark_complete_click):
	# to open, one must click on the toggle bar of the task status
	# to close one must click on the yes-no button
	# since multiple inputs can affect the same component
	# we need to know what is the trigger, and perform accordingly
	triggered_by = ctx.triggered_id if not None else None

	# if there is a valid trigger
	if triggered_by:

		# if the trigger is the change in the task status, then display the modal
		if triggered_by == "task-status" and task_status:
			# return true to enable modal display
			return True
		# if the trigger is button click, then disable modal display
		else:
			return False


# function to confirm the status of the task as completed
# if the user clicks on the toggle without the intention of marking the task as complete
# then the user can click on the No button of the modal
# when the user clicks on the No button, the status of the toggle should revert back to In-Progress 
@app.callback(Output("task-status", "value"), [Input("mark-complete", "n_clicks"), Input("dont-mark-complete", "n_clicks")], State("task-status", "value"))
def update_task_status(mark_complete_click, dont_mark_complete_click, current_value):
	# there are 2 triggers for this operation - click on the Yes button / click on the No button
	triggered_by = ctx.triggered_id if not None else None

	# if there is a valid trigger
	if triggered_by:
		# toggle status Complete
		if triggered_by == "mark-complete":
			return True

		# toggle status reverted to In progress
		elif triggered_by == "dont-mark-complete":
			return False
	else:
		return current_value


# function to display the task completion date when user toggles the task status to Complete
@app.callback(Output(component_id="date-completed", component_property="hidden"), Input(component_id="task-status", component_property="value"))
def show_completed_date(task_status):
	if task_status:
		return False
	return True

# function to set the min_date_allowed for the task completion as the task start date
# user should not be able to choose an end date which is before the start date
@app.callback(Output("end-date", "min_date_allowed"), [Input("date-completed", "hidden"), Input("start-date", "date")], State("start-date", "date"))
def set_min_date_for_completion(hide_completed_date, start_date_changed, current_start_date):
	if not hide_completed_date or start_date_changed:
		return current_start_date


# this callback displays the + button beside the subcategory dropdown when a value is searched
@app.callback(Output(component_id="add-sub-category-btn", component_property="hidden"), [Input(component_id="sub-category", component_property="search_value")], [State(component_id="add-sub-category-btn", component_property="hidden")])
def enable_button(search_value, hidden):
	if not search_value and hidden:
		return True

	else:
		return False



# function to display the contents of the output block
@app.callback([Output(component_id="display", component_property="hidden"), Output(component_id="display", component_property="children"), Output(component_id="div1", component_property="n_clicks"), Output(component_id="div2", component_property="n_clicks"), Output(component_id="div3", component_property="n_clicks")], [Input(component_id="div1", component_property="n_clicks"), Input(component_id="div2", component_property="n_clicks"), Input(component_id="div3", component_property="n_clicks")], State(component_id="display", component_property="hidden"))
def div1_content_display(div1_clicks, div2_clicks, div3_clicks, hidden):
	button_id = ctx.triggered_id if not None else None
	if button_id:
		if button_id=="div1":
			message = "You clicked div 1"
			if div1_clicks == 2:
				return True, "", 0,0,0
			else:
				return False, message, 1,0,0

		elif button_id=="div2":
			message = "You clicked div 2"
			if div2_clicks == 2:
				return True, "", 0,0,0
			else:
				return False, message, 0,1,0
		else:
			message = "You clicked div 3"
			if div3_clicks == 2:
				return True, "", 0,0,0
			else:
				return False, message, 0,0,1
		
	else:
		return True, "", 0,0,0



# this function generates the final dictionary structure when the user submits a task
# added a new feature of task status
# added task end date if user marks the task as complete
@app.callback([Output(component_id="display-message", component_property="message"), 
	Output(component_id="display-message", component_property="displayed"), 
	Output(component_id="work-description", component_property="value"),
	Output(component_id="task_info", component_property="children")],
	[Input(component_id="submit-button", component_property="n_clicks")], 
	[State(component_id="work-category", component_property="value"), 
	State(component_id="sub-category", component_property="value"), 
	State(component_id="start-date", component_property="date"),
	State(component_id="work-description", component_property="value"),
	State(component_id="task-status", component_property="value"),
	State(component_id="end-date", component_property="date")])
def submit_task(n_clicks, task_category, sub_category, start_date, task_description, task_status, end_date):
	if n_clicks is None:
		raise PreventUpdate

	if task_description and task_description != None:
		# task_dict[datetime.now().strftime("%Y%m%d%H%M%S")] = {"category": task_category, "sub_category": sub_category, "task_date": task_date, "task_description": task_description}
		task_dict= {
			"_id": datetime.now().strftime("%Y%m%d%H%M%S"),
			"category": task_category,
			"sub_category": sub_category,
			"start_date": start_date,
			"task_description": task_description,
			"task_status": 0 if not task_status else 1
		}
		mongo_service_obj.insert_document(Constants.IN_PROGRESS_TASK_COLLECTION, task_dict)

		updated_in_prog_tasks = mongo_service_obj.load_documents(Constants.IN_PROGRESS_TASK_COLLECTION, {})
		doc_list = list(updated_in_prog_tasks)

		# return "Task added successfully", True, "", len(task_dict)
		return "Task added successfully", True, "", "Task Count: {}".format(len(doc_list))
	else:
		#load_documents added here for the situation when in a single session if the flow comes to else part
		# after executing the if part
		updated_in_prog_tasks = mongo_service_obj.load_documents(Constants.IN_PROGRESS_TASK_COLLECTION, {})
		doc_list = list(updated_in_prog_tasks)

		return "Just write something about the task so that you can remember later!", True, "", "Task Count: {}".format(len(doc_list))

@app.callback(Output(component_id="drag_tasks", component_property="children"), [Input(component_id="task_info", component_property="n_clicks")])
def show_tasks(n_clicks):
	if n_clicks:
		updated_in_prog_tasks = mongo_service_obj.load_documents(Constants.IN_PROGRESS_TASK_COLLECTION, {})
		doc_list = list(updated_in_prog_tasks)
		card_list = []
		for doc in doc_list:
			card_list.append(dbc.Card([
    			dbc.CardHeader(doc["task_date"]),
    			dbc.CardBody(doc["task_description"])
    			]))

		return card_list


@app.callback(Output(component_id="add-task-block", component_property="hidden"), Input(component_id="add-task", component_property="n_clicks"), State(component_id="add-task-block", component_property="hidden"))
def show_add_task_div(n_clicks, hidden):
	if n_clicks:
		return not hidden
	else:
		return True


app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="make_draggable"),
    Output("drag_tasks", "data-drag"),
    [Input("drag_tasks", "id")],
)

if __name__ == '__main__':
	# start the application server
	app.run_server(debug=True)
