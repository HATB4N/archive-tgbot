from tgbot import CmdTgbot
from tgbot import SendTgbot


tokens = [] # len(tokens) = num of coworkers

if __name__ == '__main__':
    cbot = CmdTgbot.Tgbot(token = 'token', chat_id = 'chat_id')
    cbot.run()

    sbots = [SendTgbot.Tgbot(token = token, chat_id = 'chat_id') for token in tokens] # add bot idx
    for sbot in sbots:
        sbot.run()