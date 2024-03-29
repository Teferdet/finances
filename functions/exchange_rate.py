import re 
import pymongo
import time 
import __main__ as main
import config
import parser
import language
import keyboard

bot = main.bot
client = pymongo.MongoClient(config.data(["database"]))
user_db = client["finances"]["Users"]
settings = client["finances"]["Settings"]

currency_list = [
    'American Dollar', 'British Pound','Bulgarian Lev',
    'Chinese Yuan Renminbi', 'Czech Koruna', 'Euro', 'Indian Rupee', 
    'Israeli New Shekel', 'Japanese Yen', 'Polish Zloty',
    'Swiss Franc', 'Turkish Lira', 'Ukraine Hryvnia', "Russian Ruble"    
]
data = 'exchange rate'

class ExchangeRate:
    def __init__(self, message):
        self.message = message
        language = message.from_user.language_code
        
        if language in config.data(['block language']):
            bot.send_message(
                message.chat.id,
                "¯\_(ツ)_/¯ I do not understand your language",
                reply_markup=keyboard.communication_link(message),
                parse_mode='MarkdownV2'
            )    

        else:
            self.message_handler()
    
    def message_handler(self):
        ID = self.message.from_user.id

        self.currency_name = re.findall(r"\b[a-zA-Z]{3}\b", self.message.text)
        self.amount = re.findall(r"\d+\.*\d*", self.message.text)

        if self.currency_name != []:
            self.currency_name = self.currency_name[0].upper()
            self.amount = self.amount[0] if self.amount != [] else 1

            user_db.update_one(
                {'_id':ID}, 
                {'$set':{"Convert":self.amount}}
            )
            self.request()

        else:
            text = language.translate(self.message, data, "currency user error")
            bot.send_message(self.message.chat.id, text)
    
    def request(self):
        self.keypad = keyboard.alternative_currency_keyboard(self.message, self.currency_name)

        if self.currency_name in ['BTC', 'ETH']:
            index = 0
            self.keypad = None 
        
        else:
            currency = self.currency_name
            index = 1
        
        if self.currency_name.upper() in config.data(["block currency"]): 
            bot.send_message(self.message.chat.id, "❌")           
            
        else:
            self.parser = parser.CurrencyHandler(
                self.currency_name, self.amount,
                currency_list, index
            )
            self.publishing()

    def publishing(self):
        day = time.strftime("%d.%m.%y")
        keypad = None

        if self.parser == "server error":
            text = language.translate(self.message, data, "server error")

        elif self.parser == "bad request":
            text = language.translate(self.message, data, "currency user error")

        else:
            rate = language.translate(self.message, data, 'rate') 
            text = f"{rate}{day}\n{self.parser}",
            keypad = self.keypad
        
        bot.send_message(
            self.message.chat.id, 
            text, reply_markup=self.keypad
        )

class AlternativeCurrency:
    def __init__(self, call, currency_name):
        ID = call.from_user.id
        self.call = call 
        
        query = {'_id':ID}
        for amount in user_db.find(query, {'_id':0, 'Convert':1}):
            amount = amount['Convert']
            
        self.parser = parser.CurrencyHandler(currency_name, amount, currency_list, 0)
        self.publishing()
        
    def publishing(self):
        day = time.strftime("%d.%m.%y")
        
        if self.parser == "server error":
            text = language.translate(self.call, data, "server error")

        else:
            rate = language.translate(self.call, data, 'rate') 
            text = f"{rate}{day}\n{self.parser}"

        bot.edit_message_text(
            chat_id=self.call.message.chat.id, 
            message_id=self.call.message.id,
            text=text
        )
