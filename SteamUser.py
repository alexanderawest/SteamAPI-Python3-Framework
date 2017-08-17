import json
import urllib.parse
import urllib.request

class SteamUser:
	
	def __init__(self, id: int):
		self.ID64 = id #int()
		try:
			self.API_KEY = open('api_key.txt', 'r').readline().strip('\n') #str()
		except (FileNotFoundError):
			print('A Steam API Key is missing!')
			self.API_KEY = input('Please enter an API key: ')
			if 'Y' == input('Would you like to save this key? [Y/N]: '):
				open('api_key.txt', 'w').write('self.API_KEY')
		self.FRIENDS = set()
		self.GAMES = set()
			
	def friends(self) -> {int}:
		"""
		If this user does not have friends localy, it will be fetched.
		If user has friends localy, the set will be returned
		"""
		if len(self.FRIENDS) != 0: return self.FRIENDS
		base_url = 'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?'
		query_parameters = [('key', self.API_KEY), ('steamid', str(self.ID64)), ('relationship', 'friend')]
		request_URL = base_url + urllib.parse.urlencode(query_parameters)
		
		dic_json = self._api_request(request_URL)
		friend_list = dic_json['friendslist']['friends']
		for friend in friend_list:
			self.FRIENDS.add(friend['steamid'])
		return self.FRIENDS
	
	def num_friends(self) -> int:
		return len(self.FRIENDS)
	
	def games(self) -> {int}:
		"""
		Should create a game object, for now it is spripped down to app ID
		"""
		if len(self.GAMES) != 0: return self.GAMES
		base_url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?'
		query_parameters = [('key', self.API_KEY), ('include_appinfo', '1'), ('steamid', self.ID64)]
		request_URL = base_url + urllib.parse.urlencode(query_parameters)
		dic_json = self._api_request(request_URL)
		for game in dic_json['response']['games']:
			self.GAMES.add(game['appid'])
		return self.GAMES
	
	def num_games(self) -> int:
		return len(self.GAMES)
	
	def _api_request(self, link: str) -> dict():
		response = urllib.request.urlopen(link)
		json_txt = response.read().decode(encoding='UTF-8')
		dic_json = json.loads(json_txt)
		return dic_json

if __name__ == '__main__':
	print('/!\ TESTING SteamUser Class /!\\')
	FlyingSentry = SteamUser(76561198046935622)
	print(FlyingSentry.ID64, 'friend list:')
	for x in FlyingSentry.friends():
		print(x)
	for x in FlyingSentry.games():
		print(x)
	print(FlyingSentry.ID64, "has", FlyingSentry.num_friends(), "friends and", FlyingSentry.num_games(), "games.")
	
		
	