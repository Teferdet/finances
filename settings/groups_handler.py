import __main__ as main
import keyboard 
import language 
import re
import pymongo 
import config 

bot = main.bot 

client = pymongo.MongoClient(config.data(["database"]))
group = client['finances']['Groups']
users = client['finances']['Users']

output_currency = {
    'ARS':'Argentine Peso', 'AUD':'Australian Dollar',
    'GBP':'British Pound', 'BGN':'Bulgarian Lev',
    'CAD':'Canadian Dollar', 'CNY':'Chinese Yuan Renminbi',
    'CZK':'Czech Koruna','DKK':'Danish Krone',
    'EGP':'Egyptian Pound', 'EUR':'Euro',
    'ISK':'Iceland Krona', 'INR':'Indian Rupee',
    'ILS':'Israeli New Shekel', 'JPY':'Japanese Yen',
    'KRW':'Korean Won', 'NOK':'Norwegian Krone',
    'PLN':'Polish Zloty', 'RON':'Romanian Leu',
    'SGD':'Singapore Dollar', 'SEK':'Swedish Krona',
    'CHF':'Swiss Franc', 'TRY':'Turkish Lira',
    'UAH':'Ukraine Hryvnia', 'USD':'American Dollar'
}

currency_code = [
    'ARS','GBP', 'CAD', 'CZK', 'EGP', 'ISK',
    'ILS', 'KRW', 'PLN', 'SGD','CHF', 'UAH',
    'AUD', 'BGN', 'CNY', 'DKK', 'EUR', 'INR', 
    'JPY', 'NOK', 'RON', 'SEK', 'TRY', 'USD'
]

data = "settings"

class GroupSettingsHandler:
    def __init__(self, call, data):
        self.call = call 
        self.data = data
        self.ID = self.call.from_user.id  
    
        if self.data[0] == 'group' and len(self.data) == 1:
            self.get_admins_data() 
        
        elif len(self.data) == 2:
            self.group_setup()
        
        else: 
            self.edit_group_settings()

    def get_admins_data(self):
        admin_access = [
            item['Admin groups'] 
            for item in users.find({'_id':self.ID})
        ]

        if admin_access != [{}]:
            text = language.translate(self.call, data, 'choose group')
            keypad = keyboard.groups_keypad(admin_access)

        else:
            text = language.translate(self.call, data, 'error group list')
            keypad = keyboard.add_bot(self.call)

        bot.edit_message_text(
            chat_id=self.call.message.chat.id, 
            message_id=self.call.message.id,
            text=text, reply_markup=keypad
        )   

    def group_setup(self):
        group_ID = self.call.data.split()[2]
        text = language.translate(self.call, data, 'group item')

        bot.edit_message_text(
            chat_id=self.call.message.chat.id, 
            message_id=self.call.message.id, text=text,
            reply_markup=keyboard.group_settings(self.call, group_ID)
        ) 

    def edit_group_settings(self):
        ID = int(self.call.data.split()[4])
        
        if self.data[1] == 'input':
            InputCurrency(self.call, ID)
        
        elif self.data[1] == "output":
            OutputCurrency(self.call, ID)

class InputCurrency:
    def __init__(self, call, ID):
        self.call = call
        self.ID = ID

        text = language.translate(self.call, data, 'write input')

        bot.delete_message(
            self.call.message.json['chat']['id'], 
            self.call.message.message_id
        )
        
        msg = bot.send_message(
            chat_id=self.call.message.chat.id, text=text,
            reply_markup=keyboard.cancel(self.call)
        ) 

        bot.register_next_step_handler(msg, self.input_data)
    
    def input_data(self, msg):
        if msg.text.split()[0] == '❌':
            text = language.translate(self.call, data, 'exit')
        
        else:  
            text = re.findall(r"\b[a-zA-Z]{3}\b", msg.text)
            group.update_one(
                {'_id':self.ID},
                {'$set':{"Currency input list":text}}
            )

            text = language.translate(self.call, data, 'success')

        bot.send_message(
            chat_id=self.call.message.chat.id, 
            text=text,
            reply_markup=keyboard.currency_keyboard 
        )

class OutputCurrency:
    def __init__(self, call, ID):
        self.call = call
        self.ID = ID
        
        text = language.translate(self.call, data, 'write input')

        bot.delete_message(
            self.call.message.json['chat']['id'], 
            self.call.message.message_id
        )

        msg = bot.send_message(
            chat_id=self.call.message.chat.id, text=text,
            reply_markup=keyboard.cancel(self.call)
        ) 

        bot.register_next_step_handler(msg, self.output)

    def output(self, msg):
        export = []

        if msg.text.split()[0] == '❌':
            text = language.translate(self.call, data, 'exit')
        
        else:  
            text = re.findall(r"\b[a-zA-Z]{3}\b", msg.text)
            
            for item in text:
                item = item.upper()
                error = language.translate(self.call, data, 'item error')

                if item in currency_code:
                    export.append(output_currency[item])

                else: 
                    bot.answer_callback_query(
                        self.call.id, 
                        f"{item} {error}",
                        show_alert=False
                    )                
            
            if export != []:
                group.update_one(
                    {'_id':self.ID},
                    {'$set':{"Currency output list":export}}
                )
                text = language.translate(self.call, data, 'success')

            else:
                text = "Error"

        bot.send_message(
            chat_id=self.call.message.chat.id, 
            text=text,
            reply_markup=keyboard.currency_keyboard 
        )

