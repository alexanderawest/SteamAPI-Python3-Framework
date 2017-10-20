import json
import urllib.parse
import urllib.request
from time import time

class SteamUser:
	def __init__(self, id: int):
		self.ID64 = id
		self._load_API_key()
		self.FRIENDS = set()
		self.GAMES = set()
		self.name = str()
			
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
	
	def games(self, id_only = False) -> {'SteamGame'}:
		if self.GAMES: return self.GAMES
		base_url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?'
		query_parameters = [('key', self.API_KEY), ('include_appinfo', '1'), ('steamid', self.ID64)]
		request_URL = base_url + urllib.parse.urlencode(query_parameters)
		dic_json = _api_request(request_URL)
		if id_only:
			return set(game['appid'] for game in dic_json['response']['games'])
		for game in dic_json['response']['games']:
			self.GAMES.add(SteamGame(game['appid']))
		return self.GAMES
	
	def num_games(self) -> int:
		return len(self.GAMES)
	
	def get_display_name(self) -> str:
		if self.name: return self.name
		self.name = _get_player_summary('personaname')
		return self.name
	
	def get_profile_url(self) -> str:
		return self._get_player_summary('profileurl')
	
	def get_full_avatar(self) -> str:
		return self._get_player_summary('avatarfull')
	
	def get_online_status(self) -> int:
		return self._get_player_summary('personastate')
	
	def is_offline(self) -> bool:
		return self.get_online_status() == 0
	
	def is_online(self) -> bool:
		return self.get_online_status() == 1
	
	def is_busy(self) -> bool:
		return self.get_online_status() == 2
		
	def is_away(self) -> bool:
		return self.get_online_status() == 3
	
	def is_snooze(self) -> bool:
		return self.get_online_status() == 4
	
	def is_looking_to_trade(self) -> bool:
		return self.get_online_status() == 5
	
	def is_looking_to_play(self) -> bool:
		return self.get_online_status() == 6
		
	def was_online_24(self) -> bool:
		return self.was_online_unix(86400) #24 Hours
	
	def was_online_7(self) -> bool:
		return self.was_online_unix(604800) #1 Week or 7 Days
	
	def was_online_unix(self, unix: int) -> bool:
		last_online = self._get_player_summary('lastlogoff')
		return(int(time()) - last_online) <= unix
	
	def _get_player_summary(self, field: str) -> dict:
		base_url = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?'
		query_parameters = [('key', self.API_KEY), ('steamids', str(self.ID64))]
		request_URL = base_url + urllib.parse.urlencode(query_parameters)
		return _api_request(request_URL)['response']['players'][0][field]
		
	def _load_API_key(self) -> None:
		try:
			self.API_KEY = open('api_key.txt', 'r').readline().strip('\n')
		except (FileNotFoundError):
			print('A Steam API Key is missing!')
			self.API_KEY = input('Please enter an API key: ')
			if 'Y' == input('Would you like to save this key? [Y/N]: '):
				open('api_key.txt', 'w').write(self.API_KEY)
		

class SteamGame:
	def __init__(self, id: int):
		self.ID = id
		self.load_all_info()
		self.name = str()
		self.multiplayer = None
		self.controller_support = None
		
		self.get_name()
		self.get_controller_support()
		self.get_multiplayer()
	
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
			self.multiplayer = False
		return self.controller_support
	
	def get_multiplayer(self) -> bool:
		if self.multiplayer != None: return self.multiplayer
		try:
			for category in self.massJSON['categories']:
				if category['description'] == 'Multi-player':
					self.multiplayer = True
					return self.multiplayer
		except (KeyError):
			self.multiplayer = False
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

class SteamAnalytics:
	def GameMatcher(self, all_users: {'SteamUser'}, multiplayer_only = True, id_only = False) -> {SteamGame}:
		# id_only and multiplayer_only need to be implemented (even though this is a huge performace hit with huge information loss)
		temp = all_users.pop().games(True)
		for user in all_users:
			if user.games(True):
				temp.intersection_update(user.games(True))
		if id_only and not multiplayer_only:
			return temp
		elif id_only and multiplayer_only:
			for game in temp.copy():
				if not SteamGame(game).get_multiplayer(): temp.pop(game)
			return temp
		else:
			games = set()
			for game in temp:
				if multiplayer_only:
					x = SteamGame(game)
					if x.get_multiplayer():
						games.add(x)
				else:
					games.add(SteamGame(game))
			return games
