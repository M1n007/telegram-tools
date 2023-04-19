from ntpath import join
from telethon import TelegramClient, functions, events
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser, InputGroupCall, InputPeerSelf
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import StartBotRequest
from telethon.tl.functions.messages import GetHistoryRequest, GetBotCallbackAnswerRequest
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.phone import JoinGroupCallRequest
from telethon.tl.types import ChannelParticipantsSearch, DataJSON
from telethon.tl.types.account import PasswordInputSettings
from smsactivateru import Sms, SmsService, GetNumber, SmsTypes, GetBalance, GetStatus, SetStatus
from dotenv import load_dotenv
import pytgcalls


import platform
import traceback
from pathlib import Path
import os
import asyncio
import sys
import names
import signal
import time
import re
import random
import json
from FiveSim import FiveSim



print('\n')
license = 'mysession'
load_dotenv()

wrapper = Sms(os.getenv('SMS_ACTIVATE_API_KEY'))



if Path(f'./session-{license}').is_dir() == False:
   Path(f"./session-{license}").mkdir(parents=True, exist_ok=False)
   
for filename in os.listdir(f'./session-{license}'):
    if not filename.endswith('.session'):
        file_path = os.path.join(f'./session-{license}', filename)
        os.remove(file_path)


api_id = os.getenv('TELE_API_ID')
api_hash = os.getenv('TELE_API_HASH')

print('''
 Welcome To Tele Automate

 1. Add Session
 2. Join session To Public Group
 3. Create Account [ Manual OTP, session auto added and ready for use ]
 4. Create Account [ Auto OTP from SMS-Activate, session auto added and ready for use ]
 5. Get All Channel/Group participants and Invite To Another Channel/Group ( warn : flooding )
 6. Get OTP From Service Notification
 7. Check active session
 8. Complete Airdrop Task with session ( Not Maintened )
 9. Add 2FA Password to Session
 10. Bulk send message to grup by session ( one group, one session, one message )
 11. Bulk send message to grup by session ( one session, multiple group, one message )
 12. Auto join all session to group call
 13. Join session to grup and send message
 14. Create Account [ Auto OTP from 5Sim.net, session auto added and ready for use ]

''')

chooseMenu = input('Choose Menu : ')
print('')

async def createSession(phoneNumber):
    try:
      client = TelegramClient('./session-{license}/'+phoneNumber, api_id, api_hash)
      await client.connect()
      if not await client.is_user_authorized():
          await client.send_code_request(phoneNumber, force_sms=True)
          try:
            await client.sign_in(phoneNumber, input('Enter the code: '))
            print('Success Add Session')
          except SessionPasswordNeededError:
            password = input("Enter password: ")
            await client.sign_in(password=password)
            print('Success Add Session') 
      else:
          print('Session Already Added.')
    except Exception as e:
      print(e)


async def joinGrup(sessionNumber, channelName):
    client = TelegramClient(f'./session-{license}/'+sessionNumber, api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        print('Session Disconnected for number '+ sessionNumber.split('.')[0])
    else:
        try:
          await client(JoinChannelRequest(channelName))
          print('Success join number '+ sessionNumber.split('.')[0]+' to channel/group '+channelName)
        except Exception as e:
          print(e)

async def createAccountManual(phoneNumber):
    try:
      client = TelegramClient(f'./session-{license}/'+phoneNumber, api_id, api_hash)
      await client.connect()
      if not await client.is_user_authorized():
          await client.send_code_request(phoneNumber, force_sms=True)
          await client.sign_up(input('Enter the code: '), names.get_first_name(), names.get_last_name())
          print('Success Registered user')
      else:
          print('User Already Registered.')
    except Exception as e:
      os.unlink(f'./session-{license}/'+phoneNumber+'.session')
      print(e)

async def createAccount(activation, wrapper):
    try:
      client = TelegramClient(f'./session-{license}/'+activation.phone_number, api_id, api_hash)
      await client.connect()
      if not await client.is_user_authorized():
          await client.send_code_request(str(activation.phone_number), force_sms=True)
          print('Waiting OTP...')
          while True:
              time.sleep(1)
              response = GetStatus(id=activation.id).request(wrapper)
              if response['code']:
                print('Your code : {} '.format(response['code']))
                await client.sign_up(response['code'], names.get_first_name(), names.get_last_name())
                break
         
          print('Success Registered user')
      else:
          print('User Already Registered.')
    except Exception as e:
      os.unlink(f'./session-{license}/'+activation.phone_number+'.session')
      print(e)
      
      
async def createAccount5sim(numberId, phoneNumber, faPassword, faPasswordHint):
    try:
      FiveSimNew = FiveSim()
      client = TelegramClient(f'./session-{license}/'+phoneNumber, api_id, api_hash)
      await client.connect()
      if not await client.is_user_authorized():
          await client.send_code_request(str(phoneNumber), force_sms=True)
          otpCode = 0
          print('Waiting sms')
          timeout = time.time() + 60*5
          retryCount = 0
          while otpCode == 0:
              if retryCount >= 3:
                  print('It`s to long for waiting otp :`( ')
                  break
              checkStatusNumber = FiveSimNew.checkOrder(numberId)
              if len(json.loads(checkStatusNumber)['sms']) == 1:
                  otpCode = json.loads(checkStatusNumber)['sms'][0]['code']
              if time.time() > timeout:
                  print('It`s to long for waiting otp, retry send otp.')
                  await client.send_code_request(str(phoneNumber), force_sms=True)
                  timeout = time.time() + 60*5
                  retryCount = retryCount + 1
          
          print('Your code : {} '.format(otpCode))
          await client.sign_up(otpCode, names.get_first_name(), names.get_last_name())
          FiveSim.updateStatus(FiveSimNew, 'finish', numberId);
          
          # await client.dis
          
    
          # client = TelegramClient(f'./session-{license}/'+phoneNumber, api_id, api_hash)
          # await client.connect()
          try:
            print('Try setup 2fa.')
            result = await client.edit_2fa(new_password=faPassword, hint=faPasswordHint)
            client.sign_in(password=faPassword)
            print(result)
            if result == True:
              print('Success add password to session : {}'.format(sessionNumber))
            else:
              print('Failed add password to session : {}'.format(sessionNumber))
          except Exception as e:
            print(str(e))
         
          print('Success Registered user')
      else:
          print('User Already Registered.')
    except Exception as e:
      os.unlink(f'./session-{license}/'+phoneNumber+'.session')
      print(str(e)+ ' ' +', canceling number.')
      FiveSim.updateStatus(FiveSimNew, 'cancel', numberId);

async def GetChannelParticipantsAndInviteToAnother(sessionNumber, channelName):
    client = TelegramClient(f'./session-{license}/'+sessionNumber, api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        print('Session Disconnected for number '+ sessionNumber.split('.')[0])
    else:
        try:
          channel = await client(ResolveUsernameRequest(channelName))
          user_list = client.iter_participants(entity=channel)
          
          newUser = []
          async for _user in user_list:
              newUser.append(_user)

          print('{} Total user from group {}'.format(len(newUser), channelName))

          chats = []
          last_date = None
          chunk_size = 200
          groups=[]

          result = await client(GetDialogsRequest(
                      offset_date=last_date,
                      offset_id=0,
                      offset_peer=InputPeerEmpty(),
                      limit=chunk_size,
                      hash = 0
                  ))

          chats.extend(result.chats)

          for chat in chats:
              try:
                  if chat.megagroup== True:
                      groups.append(chat)
              except:
                  continue
          
          print('')
          print('Choose a group to add members : ')
          print('')
          i=0
          for group in groups:
              print(str(i) + '. ' + group.title)
              i+=1

          print('')
          g_index = input("Choose group / if not shown please input grup/channel username ex (airdropermaniax) > ")
          
          regnumber = re.compile(r'^\d+(?:,\d*)?$')
          
          target_group = ''
          target_group_entity = ''
          channel_id = ''
          channel_access_hash = ''

          if regnumber.match(g_index):
              target_group=groups[int(g_index)]
              target_group_entity = InputPeerChannel(target_group.id,target_group.access_hash)
          else:
              target_group=g_index;
              chann= await client.get_entity(g_index) 
              channel_id = chann.id;
              channel_access_hash = chann.access_hash
              target_group_entity = InputPeerChannel(channel_id, channel_access_hash)
              
          targetMemberParticipants = await client.get_participants(target_group)
          
          targetMemberParticipantsList = []
          for user in targetMemberParticipants:
                targetMemberParticipantsList.append(user.id)

          success = 0
          for index,user in enumerate(newUser, start=1):
              try:
                     
                  if user.id in targetMemberParticipantsList:
                        print('')
                        print('Member already on the channel/group')
                        time.sleep(1)
                        continue
                      
                  print ("Try Adding user {} ".format(user.id))
                  
                  user_to_add = InputPeerUser(user.id, user.access_hash)
                  
                  if regnumber.match(g_index):
                      user_to_add = InputPeerUser(user.id, user.access_hash)
                  else:
                      user_to_add = await client.get_entity(user.id)
                    
              
                  await client(InviteToChannelRequest(target_group_entity,[user_to_add]))
                  success += 1
                  time.sleep(random.randint(2, 9))
                  
                  if index % 20 == 0:
                     print('')
                     print('Sleep 10 second for prevent flooding...')
                     print('')
                     time.sleep(10);
              except PeerFloodError:
                  print("Getting Flood Error from telegram. Script is stopping now. Please try again after some time. Sleep for 30 second...")
                  print('')
                  time.sleep(30)
              except UserPrivacyRestrictedError:
                  print("The user's privacy settings do not allow you to do this. Skipping.")
                  print('')
              except Exception as e:
                  print('Error adding userId {} to channel, error {}'.format(user.id, e))
                  print('')
                  continue

          print('Success add '+ success +' member channel/group '+ channelName+' to channel/group '+target_group.name)
        except Exception as e:
          print(e)

async def getChatOtpFromServiceNotifications(sessionNumber):
    client = TelegramClient(f'./session-{license}/'+sessionNumber, api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        try:
          await client.send_code_request(sessionNumber.split('.')[0], force_sms=True)
          print(await client.is_user_authorized())
          print('Session Disconnected for number '+ sessionNumber.split('.')[0])
        except Exception as e:
          print(sessionNumber.split('.')[0]+' '+str(e))
    else:
        try:
          print('')
          @client.on(events.NewMessage)
          async def handler(event):
              message = event.message.message;
              print(message)
              if message.find('Login code') != -1:
                 print('Your code{}'.format(message.split('Login code')[1].split('.')[0]))
                 
              if message.find('Kode masuk Anda') != -1:
                 print('Your code{}'.format(message.split('Kode masuk Anda')[1].split('.')[0]))

              input('If done, just enter.')
              os._exit(0)


          
          await client.run_until_disconnected()
          
        except Exception as e:
          print(e)
          
async def checkActiveSession():
    try:
      listInsideDir = os.listdir(f'./session-{license}')
      print('List Active session : ')
      print('')
      for index,value in enumerate(listInsideDir, start=1):
          if value.endswith('.session'):
            if value.endswith('.session'):
              client = TelegramClient(f'./session-{license}/'+value, api_id, api_hash)
              await client.connect()
              if not await client.is_user_authorized():
                  os.unlink(f'./session-{license}/'+value)
                  return ''
              else:
                  print('{}. {}'.format(index, value.split('.')[0]))
      print('')
    except Exception as e:
      print(e)
      
      
async def checkActiveSessionToList():
    try:
      listInsideDir = os.listdir(f'./session-{license}')
      print('List Active session : ')
      print('')
      newList = []
      for index,value in enumerate(listInsideDir, start=1):
          if value.endswith('.session'):
            client = TelegramClient(f'./session-{license}/'+value.split('.')[0], api_id, api_hash)
            await client.connect()
            if not await client.is_user_authorized():
                print('')
            else:
                print('{}. {}'.format(index, value.split('.')[0]))
                newList.append(value.split('.')[0])
              
      return newList
    except Exception as e:
      print(e)
      
async def getBotLastMessage(client, peerUsername):
  return await client(GetHistoryRequest(
                      peer=peerUsername,
                      limit=1, #ini dimaksud kita hanya mengambil 1 pesan terakhir
                      offset_date=None,
                      offset_id=0,
                      max_id=0,
                      min_id=0,
                      add_offset=0,
                      hash=0
                    )
                  )
      
async def completeAirdrop(sessionNumber, linkChatBot):
    client = TelegramClient(f'./session-{license}/'+sessionNumber, api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        print('Session Disconnected for number '+ sessionNumber.split('.')[0])
    else:
        try:
          botUsername = linkChatBot.split('/')[3].split('?')[0]
          paramString = linkChatBot.split('/')[3].split('?start=')[1]
          request = StartBotRequest(botUsername, botUsername, paramString)
          await client(request)
          
          # accessing bot
          @client.on(events.NewMessage(chats = botUsername))
          async def my_event_handler(event):
              global text_found
              text_found = event.raw_text
              
              if hasattr(event.original_update.message, 'reply_markup') and hasattr(event.original_update.message.reply_markup, 'rows'):
                if len(event.original_update.message.reply_markup.rows) > 0:
                  all_external_task = []
                  submit_button = []
                  
                  print('')
                  for item in event.original_update.message.reply_markup.rows:
                            
                            
                      if hasattr(item.buttons[0], 'url'):
                          # joining internal telegram task
                          if item.buttons[0].url.find('t.me') != -1:
                             try:
                                await client(JoinChannelRequest(item.buttons[0].url.split('/')[3]))
                                print('Complete join task {}'.format(item.buttons[0].text))
                             except:
                                print('Failed join task {}'.format(item.buttons[0].text))
                          else:
                              all_external_task.append(item.buttons[0])
                      elif hasattr(item.buttons[0], 'data'):
                        submit_button.append(item.buttons[0])
                        
                        
                      if re.search(r"Skip", item.buttons[0].text, re.DOTALL) != None: 
                        print('')
                        print(text_found)
                        yourAnswer = input('You want {} (y/n) ? '.format(item.buttons[0].text))
                        if yourAnswer == 'y':
                            await client.send_message(botUsername,item.buttons[0].text)
                        else:
                          print('')
                          print(text_found)
                          yourAnswer = input('Your answer ? ')
                          await client.send_message(botUsername,yourAnswer)
                      elif re.search(r"Yes", item.buttons[0].text, re.DOTALL) != None:
                        print('')
                        print(text_found)
                        yourAnswer = input('Choose (y/n) ? ')
                        if yourAnswer == 'y':
                            await client.send_message(botUsername,'Yes')
                        else:
                            await client.send_message(botUsername,'No')
                  
                  
                  if len(all_external_task) > 0:
                    print('')
                    print('You have external task, please complete the task : ')
                    print('')
                    for index,value in enumerate(all_external_task, start=1):
                        print('{}. {}, url : {}'.format(index, value.text, value.url))
                    
                    print('')
                    input('If done complete external task, please enter.')
                    # click submit details
                    try:
                      await client(GetBotCallbackAnswerRequest(
                        botUsername,
                        event.original_update.message.id,
                        data=submit_button[0].data
                      ))
                    except:
                      print('Whoops, error at submit details.')
                      sys.exit(0)
              elif (text_found.find('enter') != -1 or text_found.find('submit') != -1 or 
                    re.search(r"submit", text_found, re.DOTALL) != None or 
                    re.search(r"enter", text_found, re.DOTALL) != None or
                    re.search(r"add", text_found, re.DOTALL) != None):
                print('')
                print('Submit Details : ')
                print('')
                print(text_found)
                yourAnswer = input('Your answer ? ')
                await client.send_message(botUsername,yourAnswer)
              elif text_found.find('Wrong') != -1:
                print(text_found)
                yourAnswer = input('Wrong answer, please try input again ? ')
                await client.send_message(botUsername,yourAnswer)
                            
                      
                    
              # solve simple math
              if text_found.find('solving this simple math task') != -1:
                  allMath = text_found.split(':')[1].split('=')[0].strip().split(' ')
                  resultEval = eval(str(''.join(allMath)))
                  
                  await client.send_message(botUsername,str(resultEval))
                  
            
          
          await client.run_until_disconnected()
          
        except Exception as e:
          print(e)

async def Add2FAPasswordToSession(sessionNumber):
  faPassword = input('Input password 2FA : ')
  faPasswordHint = input('Input password hint 2FA : ')
  client = TelegramClient(f'./session-{license}/'+sessionNumber, api_id, api_hash)
  await client.connect()
  result = await client.edit_2fa(new_password=faPassword, hint=faPasswordHint)
  if result == True:
     print('Success add password to session : {}'.format(sessionNumber))
  else:
     print('Failed add password to session : {}'.format(sessionNumber))
     
async def BulkSendMessageToGroupBySession(sessionNumber, channelName):
  
  client = TelegramClient(f'./session-{license}/'+sessionNumber, api_id, api_hash)
  await client.connect()
  await client(JoinChannelRequest(channelName))
  with open('pesan.txt') as f:
    lines = f.readlines()
    s = ''
    await client.send_message(channelName, s.join(lines))
  print('Done')

async def BulkSendMessageToGroupBySessionMultiple(sessionNumber):
  client = TelegramClient(f'./session-{license}/'+sessionNumber, api_id, api_hash)
  await client.connect()
  with open('grup.txt') as f:
    lines = f.readlines()
    for item in lines:
        await client(JoinChannelRequest(item))
        with open('pesan.txt') as f:
          linesPesan = f.readlines()
          s = ''
          await client.send_message(item, s.join(linesPesan))
          
  print('Done')
          
async def AutoJoinGroupCall(sessionNumber, channelName):
    client = TelegramClient(f'./session-{license}/'+sessionNumber, api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        print('Session Disconnected for number '+ sessionNumber.split('.')[0])
    else:
        try:
          print('')
          chann = await client.get_entity(channelName) 
          channel_id = chann.id;
          channel_access_hash = chann.access_hash;
          await client.start()
          group_call_factory = pytgcalls.GroupCallFactory(client, pytgcalls.GroupCallFactory.MTPROTO_CLIENT_TYPE.TELETHON)
          group_call = group_call_factory.get_file_group_call('input.raw')
          print('@'+channelName)
          await group_call.start('@'+channelName)
          await client.run_until_disconnected()

          print(channel_id, channel_access_hash)
          # await asyncio.sleep(2)
          # await client.disconnect()
          
        except Exception as e:
          print(e)
          
async def JoinGrupAndSendMessage(sessionNumber, channelName):
  messageToChannel = input('Input message to channel ( if no input just enter ) : ')
  client = TelegramClient(f'./session-{license}/'+sessionNumber, api_id, api_hash)
  await client.connect()
  await client(JoinChannelRequest(channelName))
  if messageToChannel:  
      await client.send_message(channelName, messageToChannel)

async def run_task_autoJoinGroupCall():
    try:
        listInsideDir = os.listdir(f'./session-{license}')
        channelName = input('Enter channel/group username ex( TestGrupPublic ) : ')
        print('')
        tasks = []
        for sessionNumber in listInsideDir:
            task = asyncio.create_task(AutoJoinGroupCall(sessionNumber, channelName))
            tasks.append(task)

        await asyncio.gather(*tasks)
    except Exception as e:
        print(e)


if (chooseMenu.find('1') != -1 or  
  chooseMenu.find('2') != -1 or chooseMenu.find('3') != -1 or 
  chooseMenu.find('4') != -1 or chooseMenu.find('5') != -1 or 
  chooseMenu.find('6') != -1 or chooseMenu.find('7') != -1 or 
  chooseMenu.find('8') != -1 or chooseMenu.find('9') != -1 or
  chooseMenu.find('10') != -1 or chooseMenu.find('11') != -1 or 
  chooseMenu.find('12') != -1 or chooseMenu.find('13') != -1 or
  chooseMenu.find('14') != -1):
  if chooseMenu == '1':
    phoneNumber = input('Masukan no hp ex(628xxxxxxx) : ')
    if platform.system()=='Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(createSession(phoneNumber))
  if chooseMenu == '2':
     listInsideDir = os.listdir(f'./session-{license}')
     channelName = input('Enter channel/group username ex( TestGrupPublic ) : ')
     print('')
     for sessionNumber in listInsideDir:
        if platform.system()=='Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(joinGrup(sessionNumber, channelName))
  if chooseMenu == '3':
    phoneNumber = input('Masukan no hp ex(628xxxxxxx) : ')
    if platform.system()=='Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(createAccountManual(phoneNumber))

  if chooseMenu == '4':

    balance = GetBalance().request(wrapper)
    if int(balance) >= 1:

      try:
        activation = GetNumber(
          service=SmsService().Telegram,
          country=SmsTypes.Country.ID
        ).request(wrapper)

        print('Try register telegram with phoneNumber : {}'.format(str(activation.phone_number)))

        response = GetStatus(id=activation.id).request(wrapper)

        set_as_sent = SetStatus(
          id=activation.id,
          status=SmsTypes.Status.SmsSent
        ).request(wrapper)
        if platform.system()=='Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(createAccount(activation, wrapper))

        # SetStatus(
        #   id=activation.id,
        #   status=SmsTypes.Status.End
        # ).request(wrapper)
        
      except Exception as e:
        print(e)

      
    else:
      print('Your balance is low, please recharge.')

  if chooseMenu == '5':
    listInsideDir = os.listdir(f'./session-{license}')
    channelName = input('Enter channel/group username ex( TestGrupPublic ) : ')
    print('List Session, select session u want to use : ')
    print('')
    for index,value in enumerate(listInsideDir, start=1):
        print('{}. {}'.format(index, value.split('.')[0]))

    print('')
    sessionSelect = input('Select session > ')
    
    try:
      sessionNumber = listInsideDir[int(sessionSelect)-1]
      if platform.system()=='Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
      asyncio.run(GetChannelParticipantsAndInviteToAnother(sessionNumber, channelName))
      
    except:
      print('Session not found!')

  if chooseMenu == '6':
    listInsideDir = os.listdir(f'./session-{license}')
    print('List Session, select session u want to use : ')
    print('')
    for index,value in enumerate(listInsideDir, start=1):
        print('{}. {}'.format(index, value.split('.')[0]))

    print('')
    sessionSelect = input('Select session > ')
    
    try:
      sessionNumber = listInsideDir[int(sessionSelect)-1]
      if platform.system()=='Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
      asyncio.run(getChatOtpFromServiceNotifications(sessionNumber))
      
    except Exception as e:
      print(e)
      print('Session not found!')
  
  if chooseMenu == '7':
      try:
        if platform.system()=='Windows':
          asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(checkActiveSession())
      except Exception as e:
        print(e)

  if chooseMenu == '8':
        
        if platform.system()=='Windows':
           asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        resultSessionlist = asyncio.run(checkActiveSessionToList())
        print('')
        sessionSelect = input('Select session > ')
    
        try:
          sessionNumber = resultSessionlist[int(sessionSelect)-1]
          urlBot = input('Input airdrop bot url : ')
          if platform.system()=='Windows':
              asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
          asyncio.run(completeAirdrop(sessionNumber, urlBot))
        except Exception as e:
          print(e)
          
  if chooseMenu == '9':
    listInsideDir = os.listdir(f'./session-{license}')
    print('List Session, select session u want to use : ')
    print('')
    for index,value in enumerate(listInsideDir, start=1):
        print('{}. {}'.format(index, value.split('.')[0]))

    print('')
    sessionSelect = input('Select session > ')
    
    try:
      sessionNumber = listInsideDir[int(sessionSelect)-1]
      if platform.system()=='Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
      asyncio.run(Add2FAPasswordToSession(sessionNumber))
      
    except Exception as e:
      print(e)
      
  if chooseMenu == '10':
    try:
      listInsideDir = os.listdir(f'./session-{license}')
      channelName = input('Enter channel/group username ex( TestGrupPublic ) : ')
      print('')
      for sessionNumber in listInsideDir:
          if platform.system()=='Windows':
              asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
          asyncio.run(BulkSendMessageToGroupBySession(sessionNumber, channelName))
      
    except Exception as e:
      print(e)
      
  if chooseMenu == '11':
    listInsideDir = os.listdir(f'./session-{license}')
    print('List Session, select session u want to use : ')
    print('')
    for index,value in enumerate(listInsideDir, start=1):
        print('{}. {}'.format(index, value.split('.')[0]))

    print('')
    sessionSelect = input('Select session > ')
    
    try:
      sessionNumber = listInsideDir[int(sessionSelect)-1]
      if platform.system()=='Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
      asyncio.run(BulkSendMessageToGroupBySessionMultiple(sessionNumber))
      
    except Exception as e:
      print(e)
      
  if chooseMenu == '12':
        try:
          asyncio.run(run_task_autoJoinGroupCall())
        except Exception as e:
            print(e)
          
  if chooseMenu == '13':
      listInsideDir = os.listdir(f'./session-{license}')
      print('List Session, select session u want to use : ')
      print('')
      for index,value in enumerate(listInsideDir, start=1):
          print('{}. {}'.format(index, value.split('.')[0]))

      print('')
      sessionSelect = input('Select session > ')
      print('')
      
      channelName = input('Enter channel/group username ex( TestGrupPublic ) : ')
      
      try:
        sessionNumber = listInsideDir[int(sessionSelect)-1]
        if platform.system()=='Windows':
          asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(JoinGrupAndSendMessage(sessionNumber, channelName))
        
      except Exception as e:
        print(e)
        
  if chooseMenu == '14':
        
    howManyAccount = input('how many accounts to create ? ')
    faPassword = input('Input password 2FA : ')
    faPasswordHint = input('Input password hint 2FA : ')
    print('')
    
    many = 0
    while many < int(howManyAccount):
        FiveSimNew = FiveSim()
        balance = FiveSimNew.getProfileUser()
        
        if json.loads(balance)['balance'] >= 5:

          try:
            buyActivationNumberResult = 'no free phones'
            numberId = 0;
            phoneNumber = 0;
            print('Try to get free numbers.')
            while buyActivationNumberResult == 'no free phones':
                buyActivationNumberResult = FiveSimNew.buyActivationNumber()
                if buyActivationNumberResult != 'no free phones':
                    numberId = json.loads(buyActivationNumberResult)['id']
                    phoneNumber  = json.loads(buyActivationNumberResult)['phone']
                    
            print('Try register telegram with phoneNumber : {}'.format(str(phoneNumber.split('+')[1])))
        


            if platform.system()=='Windows':
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            asyncio.run(createAccount5sim(numberId, phoneNumber, faPassword, faPasswordHint))
            
            many = many + 1

          except Exception as e:
            print(e)

      
        else:
          print('Your balance is low, please recharge.')
          break
          
else:
    print('Tidak ada menu tersebut')
