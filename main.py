# Created by Navillion
# Note: This was created to be deployed on replit.com!

# Add your discord ID here if you want to have access to special commands
SPECIAL_COMMANDS_DISCORD_ID = ""

import discord
import random
import os
from replit import db
from keep_alive import keep_alive
import requests

client = discord.Client()

@client.event
async def on_ready():
  print("We have logged in as {0.user}".format(client))

# Get the balance of a specified user
def getBalance(user):
  balance = None
  try:
    balance = db[str(user)]
  except:
    db[str(user)] = 1000
  if balance == None:
    balance = 1000
  return balance

# Get the value of a specific datastore, or return 0
def Get(user, key):
  value = None
  try:
    value = db[str(user) + ' - ' + str(key)]
  except:
    db[str(user) + ' - ' + str(key)] = 0
  if value == None:
    value = 0
  return value

# Set a value to a specific datastore
def Set(user, key, value):
  db[str(user) + ' - ' + str(key)] = value
  return value

# Add a value to a specific datastore
def Increment(user, key, value):
  data = Get(user, key)
  Set(user, key, data + value)
  return data + value

def Remove(user, key):
  try:
    del db[str(user) + ' - ' + str(key)]
  except:
    pass
  return 0

SpammingDisconnect = False
  
# When a message is sent...
@client.event
async def on_message(message):
  msg = message.content

  # If the bot wrote the message, ignore it
  if message.author == client.user:
    return

  # If the message was sent in a channel called general, and isn't the .say command then ignore it
  #if str(message.channel) == 'general' and not msg.startswith('.say'):
  #  return
  
  # The start of the gamble command (this thing is super long)
  if msg.startswith('.gamble') or msg.startswith('.bet'):

    balance = getBalance(message.author.id)

    bet = msg.split(" ", 1)[1]

    try:
      float(bet)
    except:
      if bet.lower() == 'all':
        bet = balance
      else:
        await message.channel.send(f'You must provide a valid number. You said: **\'{bet}\'**')
        return
    if float(bet) > balance:
      await message.channel.send(f'You obviously can\'t afford this bet! Your balance is **${balance}!**')
      return
    if float(bet) < 0:
      await message.channel.send(f'You can\'t do that. Stop!')
      return
    if float(bet) == 0:
      await message.channel.send(f'You can\'t gamble nothing.')
      return
    
    bet = float(bet)
    chance = random.random() > 0.5
    percentWon = round(random.random() * 3, 2)

    if chance:
      newBalance = round(balance + bet * (percentWon), 2)
      await message.channel.send(f'You **won the game** at a **{round(percentWon * 100)}%**. Your new balance is **${newBalance}.**')
      Increment(message.author.id, 'BetEarned', bet * (percentWon))
    else:
      percentWon = percentWon / 6
      newBalance = round(balance - (bet * (percentWon)), 2)
      if newBalance < 0:
        newBalance = 0
        await message.channel.send(f'You lost the game at a **{round(percentWon * 100)}%**! Loser! You are now **broke** with **no money**. I suggest retrying your hand at life with **".del"**')
      else:
        await message.channel.send(f'You lost the game at a **{round(percentWon * 100)}%**! Loser! Your new balance is: **${newBalance}.**')
      Increment(message.author.id, 'BetLost', (bet * (percentWon)))
    
    db[str(message.author.id)] = newBalance
  
  # Delete your data for whatever reason, usually because you are broke
  elif msg.startswith('.del'):
    del db[str(message.author.id)]
    await message.channel.send('Deleted your balance')

    try:
      if msg.split(' ')[1] == 'all':
        Remove(message.author.id, 'BetEarned')
        Remove(message.author.id, 'BetLost')
        Remove(message.author.id, 'DiceEarned')
        Remove(message.author.id, 'DiceLost')
        await message.channel.send('Deleted ALL your DATA')
    except:
      pass
  # Beg for a free dollar
  elif msg.startswith('.beg'):
    balance = getBalance(message.author.id) 
    await message.channel.send(f'Broke b****, have a coin. Your new balance is **${balance+1}.**')
    db[str(message.author.id)] = balance + 1
  
  # Check your balance
  elif msg.startswith('.bal') or msg.startswith('.balance'):
    await message.channel.send(f'Your current balance is **${getBalance(message.author.id)}.**')
  
  # Spawn in money
  elif msg.startswith('.spawn'):
    if str(message.author.id) != SPECIAL_COMMANDS_DISCORD_ID:
      await message.channel.send(f'*You don\'t have access to this command!*')
      return
    
    bet = msg.split(" ", 1)[1]
    try:
      float(bet)
    except:
        await message.channel.send(f'You must provide a valid number. You said: \'{bet}\'')
        return
    
    bet = float(bet)
    balance = getBalance(message.author.id)
    await message.channel.send(f'I gotchu, **${bet}** has been added to your balance, bringing you to **${balance+bet}.**')
    db[str(message.author.id)] = balance + bet
  
  # check leaderboard (not implemented yet!)
  elif msg.startswith('.leaderboard'):
    await message.channel.send(f'Will add this once I figure out Python dictionaries!')
    return
  
  # say the specific message (add delete og message in the future)
  elif msg.startswith('.say'):
      if (str(message.author.id) != SPECIAL_COMMANDS_DISCORD_ID):
        await message.channel.send(f'*You don\'t have access to this command!*')
        return
      content = msg.split(" ", 1)[1]
      await message.channel.send(content)
  
  # set (useless feature)
  elif msg.startswith('.set'):
      if (str(message.author.id) != SPECIAL_COMMANDS_DISCORD_ID):
        await message.channel.send(f'*You don\'t have access to this command!*')
        return
      channelToSend = msg.split(".set ", 1)[1]
      await message.channel.send(f'**[Doesn\'t Work] Will send messages to \'{channelToSend}\'. Current channel: {message.channel}**')

  # roll a dice for incredible gains but low wins
  elif msg.startswith('.dice') or msg.startswith('.roll'):
    
    balance = getBalance(message.author.id)

    try:
      bet = msg.split(" ", 2)[1]
    except:
      await message.channel.send(f'You must provide 2 arguments - your bet and what number you want to roll (1/2/3/4/5/6)')
      return
    try:
      expected = msg.split(" ", 2)[2]
    except:
      expected = random.randint(1,6)

    try:
      float(bet)
    except:
      if bet.lower() == 'all' or bet.lower() == 'max':
        bet = balance
      else:
        await message.channel.send(f'You must provide a valid number. You said: **\'{bet}\'** and **\'{expected}\'**')
        return
    try:
      int(expected)
    except:
      await message.channel.send(f'You must provide a valid integer for your second argument.')
    if float(bet) > balance:
      await message.channel.send(f'You obviously can\'t afford this bet! Your balance is **${balance}!**')
      return
    if float(bet) < 0:
      await message.channel.send(f'You can\'t do that. Stop!')
      return
    if float(bet) == 0:
      await message.channel.send(f'You can\'t gamble nothing.')
      return
    if int(expected) < 1 or int(expected) > 6:
      await message.channel.send(f'You must provide a number between 1 and 6 as your second argument.')
      return
    
    bet = float(bet)
    expected = int(expected)

    await message.channel.send(f'Rolling dice for **${bet}** for number **{expected}**. There is a __1 in 6__ chance of winning, but a large payout!')

    chance = random.randint(1,6)
    percentWon = round(random.random(), 2) * 6

    if chance == expected:
      newBalance = round(balance + (bet * percentWon), 2)
      await message.channel.send(f'**Wow! You won the game at a {round(percentWon * 100)}%! Your new balance is ${newBalance}.**')
      Increment(message.author.id, 'DiceEarned', (bet * percentWon))
    else:
      newBalance = round(balance - (bet * percentWon / 8), 2)
      await message.channel.send(f'You lost idiot! You lost **{round(percentWon / 8 * 100)}%** of your bet, since the dice rolled **{chance}**! Your new balance is **${newBalance}.**')
      Increment(message.author.id, 'DiceLost', (bet * percentWon / 8))

    db[str(message.author.id)] = newBalance
    
    return
  elif msg.startswith('.stat'):
    balance = getBalance(message.author.id)
    diceEarned = Get(message.author.id, 'DiceEarned')
    diceLost = Get(message.author.id, 'DiceLost')

    betEarned = Get(message.author.id, 'BetEarned')
    betLost = Get(message.author.id, 'BetLost')

    await message.channel.send(f'Your balance is **${round(balance, 2)}**.\nYou have won **${round(diceEarned, 2)}** and lost **${round(diceLost, 2)}** in dice. Net Gain: **${round(diceEarned - diceLost, 2)}**\nYou have won **${round(betEarned, 2)}** and lost **${round(betLost, 2)}** in gamble. Net Gain: **${round(betEarned - betLost, 2)}**')




    
keep_alive()
client.run(os.environ['TOKEN'])
