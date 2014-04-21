import xmlrpclib
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox

s = xmlrpclib.ServerProxy('http://192.168.1.23:8000/RPC2')
		
class amrs_app(App):
	def widget_AllMembers(self):
		dropdown = DropDown()
		for i in range(10):
			btn = Button(text=str(i),size_hint_y=None,height=30)
			btn.bind(on_release=lambda btn: dropdown.select(btn.text))
			dropdown.add_widget(btn)
		return dropdown

	def commitUnit(self,data):
		return
	
	def screen_AddUnit(self):
		print "TODO: Add this"
		addLayout = GridLayout(cols = 2,size_hint_y=None)
		addLayout.bind(minimum_height=addLayout.setter('height'))
		data = {
			'UnitName':None,
			'UnitType':None,
			'Landed':None,
			'Zips':None,
			'LeaderId':None,
			'LordsRepId':None,
			'CommonRepId':None,
			'HeraldId':None,
			'MarshalId':None,
			'YearEndFunds':None,
			'YearlyDues':None,
		}
		title = Label(text="Add Unit")
		spacer = Label(text="")
		nameLabel = Label(text="Unit Name:", width="75")
		nameField = TextInput()
		typeLabel = Label(text="Unit Type:", width="75")
		typeField = TextInput()
		landLabel = Label(text="Landed:", width = "75")
		landCheck = CheckBox()
		leadLabel = Label(text="Leader:", width = "75")
		leadSelect = self.widget_AllMembers()
		
		addLayout.add_widget(title)
		addLayout.add_widget(spacer)
		addLayout.add_widget(nameLabel)
		addLayout.add_widget(nameField)
		addLayout.add_widget(typeLabel)
		addLayout.add_widget(typeField)
		addLayout.add_widget(landLabel)
		addLayout.add_widget(landCheck)
		addLayout.add_widget(leadLabel)
		#addLayout.add_widget(leadSelect)
		
		return addLayout
	def addUnit_Switch(self,btn):
		self.changeScreen(self.screen_AddUnit())
		return
	def viewHousehold(self):
		return
		
	def screen_Unit(self):
		unitLayout = GridLayout(cols = 1,size_hint_y=None)
		unitLayout.bind(minimum_height=unitLayout.setter('height'))
		res = s.fetchAllUnits()
		#print res
		
		for row in res:
			print row[1]
			btn = Button(text=row[1],size_hint_y=None, height=40)
			unitLayout.add_widget(btn)
		addBtn = Button(text="+ Add Household +", size_hint_y=None, height=40)
		addBtn.bind(on_release=self.addUnit_Switch)
		unitLayout.add_widget(addBtn)
		
		return unitLayout
	def changeScreen(self,screen):
		self.root.clear_widgets()
		self.root.add_widget(screen)
	def build(self):
		self.root = ScrollView(size_hint=(None, None), size=(400, 400),
			pos_hint={'center_x':.5, 'center_y':.5})
		self.changeScreen(self.screen_Unit())
		return self.root
		
amrs_app().run()
