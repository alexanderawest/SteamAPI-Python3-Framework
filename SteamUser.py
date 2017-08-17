import json
import urllib.parse
import urllib.request

class SteamUser:
	def __init__(self, id: int):
		self.ID64 = id
		try:
			self.API_KEY = open('api_key.txt', 'r').readline().strip('\n')
		except (FileNotFoundError):
			print('A Steam API Key is missing!')
			self.API_KEY = input('Please enter an API key: ')
			if 'Y' == input('Would you like to save this key? [Y/N]: '):
				open('api_key.txt', 'w').write(self.API_KEY)
		self.FRIENDS = set()
		self.GAMES = set()
			
	def friends(self) -> {int}:
		if self.FRIENDS: return self.FRIENDS
		base_url = 'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?'
		query_parameters = [('key', self.API_KEY), ('steamid', str(self.ID64)), ('relationship', 'friend')]
		request_URL = base_url + urllib.parse.urlencode(query_parameters)
		dic_json = _api_request(request_URL)
		friend_list = dic_json['friendslist']['friends']
		for friend in friend_list:
			self.FRIENDS.add(friend['steamid'])
		return self.FRIENDS
	
	def num_friends(self) -> int:
		return len(self.FRIENDS)
	
	def games(self) -> {int}:
		if self.GAMES: return self.GAMES
		base_url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?'
		query_parameters = [('key', self.API_KEY), ('include_appinfo', '1'), ('steamid', self.ID64)]
		request_URL = base_url + urllib.parse.urlencode(query_parameters)
		dic_json = _api_request(request_URL)
		for game in dic_json['response']['games']:
			self.GAMES.add(SteamGame(game['appid']))
		return self.GAMES
	
	def num_games(self) -> int:
		return len(self.GAMES)

class SteamGame:
	def __init__(self, id: int):
		self.ID = id
		self.load_all_info()
		self.name = str()
		self.multiplayer = None
		self.controller_support = None
		
		self.get_name()
		self.get_multiplayer()
		self.get_controller_support()
	
	def get_name(self) -> str:
		if self.name: return self.name
		try:
			self.name = self.massJSON['name']
		finally:
			return self.name
	
	def get_controller_support(self) -> bool:
		if self.controller_support != None: return self.controller_support
		try:
			if self.massJSON['controller_support']: self.controller_support = True
		except (KeyError):
			pass
		return self.controller_support
	
	def get_multiplayer(self):
		if self.multiplayer != None: return self.multiplayer
		try:
			for category in self.massJSON['categories']:
				if category['description'] == 'Multi-player':
					self.multiplayer = True
					return self.multiplayer
		except (KeyError):
			pass
		return self.multiplayer
	
	def load_all_info(self):
		#Doesn't handle non-games
		request_URL = 'http://store.steampowered.com/api/appdetails?appids=' + str(self.ID)
		self.massJSON = _api_request(request_URL)[str(self.ID)]
		if self.massJSON['success'] == True and self.massJSON['data']['type'] == 'game':
			self.massJSON = self.massJSON['data']
			
	def delete_massJSON(self):
		self.massJSON.clear()

def _api_request(link: str) -> dict():
		print(link)
		response = urllib.request.urlopen(link)
		json_txt = response.read().decode(encoding='UTF-8')
		dic_json = json.loads(json_txt)
		return dic_json


if __name__ == '__main__':
	print('/!\ TESTING SteamUser Class /!\\')
	FlyingSentry = SteamUser(76561198041376516) # PearBear ID
	#FlyingSentry.games()
	for x in FlyingSentry.games():
		print(x.get_name(), 'has multiplayer:', x.get_multiplayer())
	#x = SteamGame(550)
	#print(FlyingSentry.ID64, "has", FlyingSentry.num_friends(), "friends and", FlyingSentry.num_games(), "games.")
	
		
	