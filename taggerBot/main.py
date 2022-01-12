import os
import telebot
import numpy as np 
import pandas as pd

import paho.mqtt.client as mqtt
import json


# globales

label = ""
cdir = os.getcwd()


# cliente MQTT
def on_connect(client, userdata, flags, rc):
    print("connected with result code "+str(rc))

    client.subscribe("/gw/oficina/status")


def on_message(client, userdata, msg): 
    """
    Al recibir un mensaje lo guarda en un csv
    """
    label = userdata
    dato = msg.payload.decode("utf-8")
    dato = json.loads(dato)
    gateway = dato[0]["mac"]
    for entry in dato[1:]:
        MAC = entry["mac"]
        timestamp = entry["timestamp"]
        rssi = entry["rssi"]

        try: 
            df = pd.read_csv("data.csv", index_col=0)
        except:
            df = pd.DataFrame()
        df = df.append({"MAC": MAC,"timestamp" : timestamp, "rssi": rssi, "label":label, "gateway":gateway}, ignore_index=True)
        df.to_csv("data.csv")
    print(f"Dispositivos: {len(dato)-1} Origen: {gateway} Label: {label}")

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.0.115", 1883,keepalive=5)




# BOT telegram

keypath = os.path.abspath(os.path.join(cdir, os.pardir))

API_KEY = open(keypath+"/key.txt", "r").read()

bot = telebot.TeleBot(API_KEY)



# Comandos
@bot.message_handler(commands=["start"])
def start(message):

    content = message.text.split()
    
    if len(content) == 2:
        label = content[1]
        client.loop_stop()
        client._userdata = label
        print("Start")
        bot.send_message(message.chat.id, f"Inicio toma datos: {label}.")
        client.loop_start()

    else:
        client.loop_stop()
        bot.send_message(message.chat.id, "/start *label*")

@bot.message_handler(commands=["stop"])
def stop(message):
    client.loop_stop()
    print("Stop")
    bot.send_message(message.chat.id, "Fin toma datos.")


# Manejo de data

@bot.message_handler(commands=["new"])
def new(message):

    filename = "unnamed"
    bot.send_message(message.chat.id, f"Archivo guardado como: {filename}.csv")
    try:
        df = pd.read_csv("data.csv", index_col=0)
        df.to_csv(cdir+"/data/"+filename+".csv")
    except:
        pass

    df = pd.DataFrame()
    bot.send_message(message.chat.id, "Nuevo archivo creado")

@bot.message_handler(commands=["save"])
def save(message):

    content = message.text.split()

    if len(content) == 2:
        filename = content[1]
        bot.send_message(message.chat.id, f"Archivo guardado como: {filename}.csv")
        try:
            df = pd.read_csv("data.csv", index_col=0)
            df.to_csv(cdir+"/data/"+filename+".csv")
        except:
            bot.send_message(message.chat.id, "No hay data")

    else:
        client.loop_stop()
        bot.send_message(message.chat.id, "/save *name*")

@bot.message_handler(commands=["ls"])
def ls(message):
    reply = ""
    for filename in os.listdir(cdir+"/data"):
        file = open(cdir+"/data/"+filename)
        length = len([row for row in file])-1
        reply += f"{filename}   {length}\n"
    if reply == "":
        bot.send_message(message.chat.id, "no hay archivos")
    else:
        bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=["rm"])
def rm(message):
    content = message.text.split()

    if len(content) == 2:
        filename = content[1]
        try:
            os.remove(cdir+"/data/"+filename)
            bot.send_message(message.chat.id, f"Archivo {filename} eliminado.")
        except:
            bot.send_message(message.chat.id, "archivo no existe")

    else:
        client.loop_stop()
        bot.send_message(message.chat.id, "/save *filename*")



print("Bot Ready")

bot.polling()




