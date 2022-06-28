from dash import Dash, html, dcc, Input, Output, State
from datetime import date, datetime
from dash.exceptions import PreventUpdate
from database_service import MongoDBServices
from constants import Constants

# initialise the application
app = Dash(__name__)
server = app.server

# initialise the db connection
mongo_service_obj = MongoDBServices()

# build the layout
def page_layout():
	return html.Div([
			dcc.ConfirmDialog(id='display-message'),
			html.H2("Experimental Work Track App", style={"textAlign": "center"}),
			html.Div([
					# create radio button for category of Work
					# has 2 categories - Personal and Office
					# currently defaults to Personal
					html.Div([
						html.Pre("Choose the Task Category:"),
						html.Div([dcc.RadioItems(id="work-category", options=["Personal", "Office"], value="Personal")])
							]),
					
					# populate the sub-category based on the work category
					# since the options have to change dynamically, we have to use callbacks here
					html.Div([
						html.Pre("Choose the Task Sub Category:"),
						html.Div([dcc.Dropdown(id="sub-category", value="none")])
							]),

					# choose date
					# by default it shows today's date
					html.Div([
						html.Pre("Choose the Task Date:"),
						html.Div([dcc.DatePickerSingle(id="work-date", date=date.today())])
							])
				], style={"display": "flex", "justify-content": "space-between", "padding-left": "100px", "padding-right": "100px"}),
			html.Div([
					dcc.Input(id="work-description", type="text", placeholder="Enter your task description here", spellCheck=True, size="100"),
					html.Button(id="submit-button", children="Submit")
				], style={"display": "flex", "justify-content": "center", "padding-top": "50px", "height": "100px"}),

			
			html.Div([
						html.Pre("Task Count:"),
						# html.Div([html.H1(id="update-task-count", children=len(task_dict))])
						html.Div([html.H1(id="update-task-count", children=len(list(mongo_service_obj.load_documents(Constants.IN_PROGRESS_TASK_COLLECTION,{}))) )])
							], style = {"textAlign": "center"})

						#todo: Adding 2 counts featuring-
						# 1.total tasks(in progress + completed)
						# 2.only in progress task count

	])

# this will reload and update the changes in layout for every page refresh
app.layout = page_layout

# function to dynamically populate the dropdown
@app.callback(Output(component_id="sub-category", component_property="options"), [Input(component_id="work-category", component_property="value")])
def populate_dropdown(work_category):
	if work_category == "Personal":
		return {"learning": "Learning", "experimenting": "Experimenting"}
	else:
		return {"development": "Development", "bug fixing": "Bug Fixing"}

@app.callback([Output(component_id="display-message", component_property="message"), 
	Output(component_id="display-message", component_property="displayed"), 
	Output(component_id="work-description", component_property="value"),
	Output(component_id="update-task-count", component_property="children")],
	[Input(component_id="submit-button", component_property="n_clicks")], 
	[State(component_id="work-category", component_property="value"), 
	State(component_id="sub-category", component_property="value"), 
	State(component_id="work-date", component_property="date"),
	State(component_id="work-description", component_property="value")])
def submit_task(n_clicks, task_category, sub_category, task_date, task_description):
	if n_clicks is None:
		raise PreventUpdate

	if task_description and task_description != None:
		# task_dict[datetime.now().strftime("%Y%m%d%H%M%S")] = {"category": task_category, "sub_category": sub_category, "task_date": task_date, "task_description": task_description}
		task_dict= {
			"_id": datetime.now().strftime("%Y%m%d%H%M%S"),
			"category": task_category,
			"sub_category": sub_category,
			"task_date": task_date,
			"task_description": task_description
		}
		mongo_service_obj.insert_document(Constants.IN_PROGRESS_TASK_COLLECTION, task_dict)

		updated_in_prog_tasks = mongo_service_obj.load_documents(Constants.IN_PROGRESS_TASK_COLLECTION, {})
		doc_list = list(updated_in_prog_tasks)

		# return "Task added successfully", True, "", len(task_dict)
		return "Task added successfully", True, "", len(doc_list)
	else:
		#load_documents added here for the situation when in a single session if the flow comes to else part
		# after executing the if part
		updated_in_prog_tasks = mongo_service_obj.load_documents(Constants.IN_PROGRESS_TASK_COLLECTION, {})
		doc_list = list(updated_in_prog_tasks)

		return "Just write something about the task so that you can remember later!", True, "", len(doc_list)

if __name__ == '__main__':
	# start the application server
	app.run_server(debug=True)
