'''
	MHI com Telegram
	
  Arquivo telegram.py
  Adicione seu Token do telegram nos links da API do Telegram
	
	https://youtube.com/c/IQCoding
	
'''

import json
import requests
from time import sleep
from threading import Thread, Lock

global config
config = {'url': 'https://api.telegram.org/botTOKEN_AQUI/', 'lock': Lock(), 'url_file': 'https://api.telegram.org/file/botTOKEN_AQUI/'}

def del_update(data):
	global config	
	
	config['lock'].acquire()
	requests.post(config['url'] + 'getUpdates', {'offset': data['update_id']+1})
	config['lock'].release()

def send_message(data, msg):
	global config
	
	config['lock'].acquire()
	requests.post(config['url'] + 'sendMessage', {'chat_id': data['message']['chat']['id'], 'text': str(msg)})
	config['lock'].release()

def get_file(file_path):
	global config
	
	return requests.get(config['url_file'] + str(file_path)).content

def upload_file(data, file):
	global config	
	
	formatos = {'png': {'metodo': 'sendPhoto', 'send': 'photo'},
				'text': {'metodo': 'sendDocument', 'send': 'document'} }
	
	return requests.post(config['url'] + formatos['text' if '.txt' in file else 'png']['metodo'], {'chat_id': data['message']['chat']['id']}, files={formatos['text' if '.txt' in file else 'png']['send']: open(file, 'rb')}).text

def conf(data = False): # {"estado": True}
	default = {"estado": False,
				"chat_id": 0,
				"operacao": 1,
				"tipo_mhi": 1,
				"par": "",
				"valor_entrada": 2.0,
				"valor_entrada_b": 2.0,
				"martingale": 1,
				"stop_loss": 0,
				"stop_gain": 0}
				
	config = open('config.json', 'r').read()
	
	if config.strip() == '':
		with open('config.json', 'w') as old_config:
			json.dump(default, old_config, indent=1)
		
		config = default
	else:
		config = json.loads(config)
	
	if data != False:
		for conf in data:
			config[conf] = data[conf]
	
		with open('config.json', 'w') as old_config:
			json.dump(config, old_config, indent=1)
	
	else:
		return config


while True:
	
	x = ''
	while 'result' not in x:
		try:
			x = json.loads(requests.get(config['url'] + 'getUpdates').text)
		except Exception as e:
			x = ''
			if 'Failed to establish a new connection' in str(e):
				print('Perca de conexão')
			else:
				print('Erro desconhecido: ' + str(e))
	
	
	if len(x['result']) > 0:
		for data in x['result']:
			Thread(target=del_update, args=(data, )).start()
			config_mhi = conf()
			
			if 'document' in data['message']:
			
				print(json.dumps(data['message'], indent=1))
				
				file = get_file(json.loads(requests.post(config['url'] + 'getFile?file_id=' + data['message']['document']['file_id']).text)['result']['file_path'])
				open(data['message']['document']['file_name'], 'wb').write(file)
			
			elif data['message']['text'] == 'foto':
				print(upload_file(data, 'logo_canal.png'))
				
				
			elif data['message']['text'] == 'texto':
				print(upload_file(data, 'documento_exemplo.txt'))		
			
			elif 'entities' in data['message']:
				if data['message']['entities'][0]['type'] == 'bot_command':
					
					if '/start' in data['message']['text']:
						msg = '''
Bem vindo ao exemplo de MHI via Telegram!\n
						
Use os commandos abaixo!
/start - Mensagem do inicio
/ligar - Ligar ou desligar bot
/operacao - digital ou binario
/par - indique o par para operar
/tipo_mhi - Minoria ou maioria
/valor_entrada - Defina o valor de entrada
/martingale - Quantos martingales utilizar
/stop_loss - Valor para Stop Loss
/stop_gain - Valor para Stop Gain
							'''
						
						Thread(target=send_message, args=(data, msg)).start()
					
					if '/ligar' in data['message']['text']:
						if config_mhi["estado"] == True:
							conf({"estado": False, "chat_id": data['message']["chat"]["id"]})
							Thread(target=send_message, args=(data, "Bot MHI desativado!")).start()
						else:
							conf({"estado": True, "chat_id": data['message']["chat"]["id"]})
							Thread(target=send_message, args=(data, "Bot MHI ativado!")).start()
					
					if '/par' in data['message']['text']:
						text = data['message']['text'].replace('/par', '')
						
						if text.strip() != '':
							conf({"par": str(text.upper()).strip()})
							Thread(target=send_message, args=(data, "Paridade alterada para " + str(text.upper()).strip() + "!")).start()
						else:
							Thread(target=send_message, args=(data, "Paridade selecionado atualmente é " + config_mhi['par'] + "!")).start()
					
					if '/operacao' in data['message']['text']:
						text = data['message']['text'].replace('/operacao', '')
						
						if text.strip() != '':
							if 'digital' in text:
								conf({"operacao": 1})
								Thread(target=send_message, args=(data, "Tipo de Operação alterado para DIGITAL!")).start()
								
							elif 'bin' in text:
								conf({"operacao": 2})
								Thread(target=send_message, args=(data, "Tipo de Operação alterado para BINARIO!")).start()
							
							
						else:
							Thread(target=send_message, args=(data, "Tipo de operação atual está para " + ('DIGITAL' if config_mhi['operacao'] == 1 else 'BINARIO') )).start()
					
					if '/tipo_mhi' in data['message']['text']:
						text = data['message']['text'].replace('/tipo_mhi', '')
						
						if text.strip() != '':
							if 'minoria' in text:
								conf({"tipo_mhi": 1})
								Thread(target=send_message, args=(data, "Tipo de analise alterado para MINORIA!")).start()
								
							elif 'maioria' in text:
								conf({"tipo_mhi": 2})
								Thread(target=send_message, args=(data, "Tipo de analise alterado para MAIORIA!")).start()
							
						else:
							Thread(target=send_message, args=(data, "Tipo de analise atual está para " + ('MINORIA' if config_mhi['tipo_mhi'] == 1 else 'MAIORIA') )).start()
					
					if '/valor_entrada' in data['message']['text']:
						text = ''
						try:
							text = float((str(data['message']['text']).replace('/valor_entrada', '')).replace(',', '.'))							
						except:
							Thread(target=send_message, args=(data, "Valor de entrada invalido!")).start()
						
						if str(text).strip() != '':
							conf({"valor_entrada": text, "valor_entrada_b": text})
							Thread(target=send_message, args=(data, "Valor de entrada alterado para $" + str(text) + "!")).start()
							
						else:
							Thread(target=send_message, args=(data, "Seu valor de entrada atual é de $" + str(config_mhi['valor_entrada']) )).start()
					
					if '/martingale' in data['message']['text']:
						text = ''
						try:
							text = int(str(data['message']['text']).replace('/martingale', ''))							
						except:
							Thread(target=send_message, args=(data, "Quantia de MARTINGALE invalido!")).start()
						
						if str(text).strip() != '':
							
							if text <= 0:
								conf({"martingale": 1})
								Thread(target=send_message, args=(data, "Quantia de MARTINGALE alterado para 0!")).start()
							
							else:
								conf({"martingale": text+1})
								Thread(target=send_message, args=(data, "Quantia de MARTINGALE alterado para " + str(text) + "!")).start()
							
						else:
							Thread(target=send_message, args=(data, "Sua quantia de MARTINGALE atual é de " + str(config_mhi['martingale']-1) )).start()
							
					if '/stop_loss' in data['message']['text']:
						text = ''
						try:
							text = abs(float((str(data['message']['text']).replace('/stop_loss', '')).replace(',', '.')))
						except:
							Thread(target=send_message, args=(data, "Valor para Stop Loss invalido!")).start()
						
						if str(text).strip() != '':
							conf({"stop_loss": text})
							Thread(target=send_message, args=(data, "Valor para Stop Loss alterado para $" + str(text) + "!")).start()
							
						else:
							Thread(target=send_message, args=(data, "Seu Valor para Stop Loss atual é de $" + str(config_mhi['stop_loss']) )).start()
						
					if '/stop_gain' in data['message']['text']:
						text = ''
						try:
							text = abs(float((str(data['message']['text']).replace('/stop_gain', '')).replace(',', '.')))
						except:
							Thread(target=send_message, args=(data, "Valor para Stop Gain invalido!")).start()
						
						if str(text).strip() != '':
							conf({"stop_gain": text})
							Thread(target=send_message, args=(data, "Valor para Stop Gain alterado para $" + str(text) + "!")).start()
							
						else:
							Thread(target=send_message, args=(data, "Seu Valor para Stop Gain atual é de $" + str(config_mhi['stop_gain']) )).start()
						
							
			else:			
			
				print(json.dumps(data, indent=1))
				if data['message']['text'] == 'oi':
					Thread(target=send_message, args=(data, 'Olá, tudo bem?')).start()
		
		sleep(1.5)	
	
