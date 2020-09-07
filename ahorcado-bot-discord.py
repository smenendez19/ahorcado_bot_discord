# Bot ahorcado Discord

# Modulos

import discord
import random
import configparser
import os
import re
import json
import asyncio
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont


class AhorcadoBot(discord.Client):

    # Variables compartidas
    vidas_totales = 6
    dicc_game = []

    # Metodos
    def calcular_palabra(self, lista_palabra, lista_letras_usadas):
        flag_letra = bool
        cant_letras = 0
        palabra = ""
        for letra in lista_palabra:
            flag_letra = False
            for letra_usada in lista_letras_usadas:
                if letra == letra_usada:
                    flag_letra = True
                    cant_letras += 1
                    break
            if flag_letra:
                palabra += f"{letra} "
            else:
                if letra.isalpha():
                    palabra += "- "
                else:
                    palabra += "  "
        return cant_letras, palabra

    def contar_palabra(self, palabra):
        cant_letras_real = 0
        for letra in palabra:
            if letra.isalpha():
                cant_letras_real += 1
        return cant_letras_real

    def dibujar_imagen(self, usuario, palabra, vidas=vidas_totales, correcto=-1, ganador=-1):
        # Sizes
        width = 500
        height = 400
        center = height//2
        # Colors
        white = (255, 255, 255)
        black = (0, 0, 0)
        # Fonts
        font_text = ImageFont.truetype("arial.ttf", 24)
        # Drawing
        ahorcado_imagen = Image.new("RGB", (width, height), white)
        draw = ImageDraw.Draw(ahorcado_imagen)
        # Horca
        draw.line([(width - 130, center + 50),
                   (width - 30, center + 50)], black, width=10)
        draw.line([(width - 80, center + 50),
                   (width - 80, center - 150)], black, width=5)
        draw.line([(width - 230, center - 150),
                   (width - 80, center - 150)], black, width=5)
        # Dibujar cada parte del tipo segun la cantidad de vidas perdidas
        if vidas < self.vidas_totales:
            if vidas <= 5:
                draw.ellipse([(width - 255, center - 150), (width - 205,
                                                            center - 100)], width=5, fill=white, outline=black)  # Head
            if vidas <= 4:
                draw.line([(width - 230, center - 100),
                           (width - 230, center - 50)], black, width=5)  # Body
            if vidas <= 3:
                draw.line([(width - 230, center - 50), (width - 270,
                                                        center - 10)], black, width=5)  # Left leg
            if vidas <= 2:
                draw.line([(width - 230, center - 50), (width - 190,
                                                        center - 10)], black, width=5)  # Right leg
            if vidas <= 1:
                draw.line([(width - 230, center - 70), (width - 270,
                                                        center - 70)], black, width=5)  # Left Arm
            if vidas == 0:
                draw.line([(width - 230, center - 70), (width - 190,
                                                        center - 70)], black, width=5)  # Right Arm
        # Images
        imagen_corazon = Image.open(os.path.join("images", "corazon.png"))
        imagen_corazon = imagen_corazon.resize((50, 50), Image.ANTIALIAS)
        # Word
        draw.text((10, center + 70), palabra, black, font=font_text)
        if correcto == 1:
            draw.text((0, 10), "La letra ingresada es CORRECTA",
                      black, font=font_text)
        elif correcto == 0:
            draw.text((0, 10), "La letra ingresada es INCORRECTA",
                      black, font=font_text)
        elif correcto == -1:
            if usuario == "global":
                pass
            else:
                if ganador == 1:
                    draw.text(
                        (0, 10), f"{client.get_user(usuario)} HA GANADO", black, font=font_text)
                elif ganador == 0:
                    draw.text(
                        (0, 10), f"{client.get_user(usuario)} HA PERDIDO", black, font=font_text)
        # Lifes
        draw.text((10, center + 140), "Vidas: ", black, font=font_text)
        for corazon_size in range(0, vidas):
            ahorcado_imagen.paste(
                imagen_corazon, (100 + (50 * corazon_size), center + 130), mask=imagen_corazon)
        # Save draw
        ahorcado_imagen.save(os.path.join(
            "images", str(usuario) + "_game.jpg"), "JPEG")

    def guardar_stats(self, usuario, ganador=True):
        now = datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        with open(os.path.join("data", 'stats.json'), 'rt') as json_file:
            dicc_stats = json.load(json_file)
        usuario_existente = False
        index_dicc = None
        for index, diccionario in enumerate(dicc_stats):
            if diccionario["usuario"] == usuario:
                usuario_existente = True
                index_dicc = index
                break
        if usuario_existente:
            dicc_stats[index_dicc]["partidas"] += 1
            if ganador:
                dicc_stats[index_dicc]["victorias"] += 1
            else:
                dicc_stats[index_dicc]["derrotas"] += 1
            dicc_stats[index_dicc]["ultima_partida"] = now
        else:
            dicc_nuevo = {
                "usuario": usuario,
                "nickname": (str(client.get_user(usuario)),"global")[usuario == "global"],
                "partidas": 1,
                "victorias": 0,
                "derrotas": 0,
                "ultima_partida": str(now)
            }
            if ganador:
                dicc_nuevo["victorias"] += 1
            else:
                dicc_nuevo["derrotas"] += 1
            dicc_stats.append(dicc_nuevo)
        with open(os.path.join("data", 'stats.json'), 'wt') as json_file:
            json.dump(dicc_stats, json_file, indent=4)

    # Eventos de discord
    async def on_message(self, message):
        # !iniciar_ahorcado
        if message.content.startswith("!iniciar_ahorcado"):
            usuario_existente = False
            index_dicc = None
            for index, diccionario in enumerate(self.dicc_game):
                if diccionario["usuario"] == message.author.id:
                    usuario_existente = True
                    index_dicc = index
                    break
            if not usuario_existente:
                diccionario = {
                    "usuario": None,
                    "juego_iniciado": None,
                    "palabra": [],
                    "letras_usadas": [],
                    "letras_acertadas": 0,
                    "vidas": self.vidas_totales,
                    "ganador": None
                }
                palabras_json_file = open(os.path.join(
                    "data", "palabras.json"), "rt", encoding="utf-8-sig")
                palabras_json = json.load(palabras_json_file)
                palabras_json_file.close()
                palabra_elegida = palabras_json["palabras"][random.randint(
                    0, len(palabras_json["palabras"]) - 1)]
                diccionario["juego_iniciado"] = True
                diccionario["usuario"] = message.author.id
                diccionario["palabra"] = [char for char in palabra_elegida]
                vidas_restantes = diccionario["vidas"]
                self.dicc_game.append(diccionario.copy())
                cant_letras = self.contar_palabra(diccionario["palabra"])
                cant_letras_usadas, palabra = self.calcular_palabra(
                    diccionario["palabra"], diccionario["letras_usadas"])
                embed_msg = discord.Embed(
                    title="Ahorcado", description="Inicio de juego", colour=0x00FF00)
                embed_msg.add_field(name="La palabra a adivinar tiene",
                                    value=f"{str(cant_letras)} letras", inline=False)
                embed_msg.add_field(
                    name="Palabra", value=f"{palabra}", inline=False)
                embed_msg.add_field(name="Vidas restantes",
                                    value=f"{vidas_restantes}", inline=True)
                self.dibujar_imagen(diccionario["usuario"], palabra)
            else:
                diccionario = self.dicc_game[index_dicc]
                cant_letras_usadas, palabra = self.calcular_palabra(
                    diccionario["palabra"], diccionario["letras_usadas"])
                letras_usadas = diccionario["letras_usadas"]
                vidas_restantes = diccionario["vidas"]
                embed_msg = discord.Embed(
                    title="Ahorcado", description=f"Ya existe una partida de ahorcado existente con el usuario <@{str(message.author.id)}>", colour=0x00FF00)
                embed_msg.add_field(
                    name="Palabra", value=f"{palabra}", inline=False)
                embed_msg.add_field(name="Letras usadas",
                                    value=f"{letras_usadas}", inline=False)
                embed_msg.add_field(name="Vidas restantes",
                                    value=f"{vidas_restantes}", inline=True)
                self.dibujar_imagen(
                    diccionario["usuario"], palabra, vidas_restantes)
            await message.channel.send(file=discord.File(os.path.join("images", str(diccionario["usuario"]) + "_game.jpg")))
            await message.channel.send(embed=embed_msg)
        # !ahorcado
        if message.content.startswith("!ahorcado"):
            usuario_existente = False
            index_dicc = None
            for index, diccionario in enumerate(self.dicc_game):
                if diccionario["usuario"] == message.author.id:
                    usuario_existente = True
                    index_dicc = index
                    break
            if not usuario_existente:
                embed_msg = discord.Embed(
                    title="Ahorcado", description=f"No fue iniciada una partida de ahorcado con el usuario <@{str(message.author.id)}>", colour=0xFF0000)
            else:
                dicc_actual = self.dicc_game[index_dicc]
                letra = re.compile(r"(!ahorcado )").sub("", message.content,)
                if len(letra) != 1 or not letra.isalpha():
                    embed_msg = discord.Embed(
                        title="Ahorcado", description=f"No se encuentra la letra ingresada, vuelva a intentarlo <@{str(message.author.id)}>", colour=0xFF0000)
                    usuario_existente = False
                elif len(letra) == 1:
                    letra = letra.lower()
                    embed_msg = discord.Embed(
                        title="Ahorcado", description=f"Partida en curso de <@{str(message.author.id)}>", colour=0xFFFFFF)
                    embed_msg.add_field(
                        name="Letra ingresada", value=f"{letra}", inline=False)
                    dicc_actual["letras_usadas"].append(letra)
                    letras_usadas = dicc_actual["letras_usadas"]
                    cant_letras, palabra_incompleta = self.calcular_palabra(
                        dicc_actual["palabra"], dicc_actual["letras_usadas"])
                    # COMPROBACION DE LETRA
                    if cant_letras > dicc_actual["letras_acertadas"]:
                        dicc_actual["letras_acertadas"] = cant_letras
                        vidas_restantes = dicc_actual["vidas"]
                        embed_msg.add_field(
                            name="Palabra", value=f"{palabra_incompleta}", inline=False)
                        embed_msg.add_field(
                            name="Letras usadas", value=f"{letras_usadas}", inline=False)
                        embed_msg.add_field(
                            name="Vidas restantes", value=f"{vidas_restantes}", inline=False)
                        self.dibujar_imagen(
                            dicc_actual["usuario"], palabra_incompleta, dicc_actual["vidas"], 1)
                    else:
                        dicc_actual["vidas"] -= 1
                        vidas_restantes = dicc_actual["vidas"]
                        embed_msg.add_field(
                            name="Palabra", value=f"{palabra_incompleta}", inline=False)
                        embed_msg.add_field(
                            name="Letras usadas", value=f"{letras_usadas}", inline=False)
                        embed_msg.add_field(
                            name="Vidas restantes", value=f"{vidas_restantes}", inline=False)
                        self.dibujar_imagen(
                            dicc_actual["usuario"], palabra_incompleta, dicc_actual["vidas"], 0)
                    # PERDEDOR
                    if dicc_actual["vidas"] == 0:
                        palabra_correcta = "".join(dicc_actual["palabra"])
                        embed_msg.add_field(
                            name="Has perdido", value="Tus vidas se acabaron", inline=False)
                        embed_msg.add_field(
                            name="Palabra correcta", value=f"{palabra_correcta}", inline=False)
                        dicc_actual["ganador"] = False
                        dicc_actual["juego_iniciado"] = False
                        self.dicc_game.pop(index_dicc)
                        self.dibujar_imagen(
                            dicc_actual["usuario"], palabra_correcta, dicc_actual["vidas"], ganador=0)
                        self.guardar_stats(
                            dicc_actual["usuario"], ganador=False)
                    # GANADOR
                    if cant_letras == self.contar_palabra(dicc_actual["palabra"]):
                        palabra_correcta = "".join(dicc_actual["palabra"])
                        embed_msg.add_field(
                            name="Has ganado", value=f"El usuario <@{str(message.author.id)}> acaba de ganar la partida", inline=False)
                        embed_msg.add_field(
                            name="Palabra correcta", value=f"{palabra_correcta}", inline=False)
                        dicc_actual["ganador"] = True
                        dicc_actual["juego_iniciado"] = False
                        self.dicc_game.pop(index_dicc)
                        self.dibujar_imagen(
                            dicc_actual["usuario"], palabra_incompleta, dicc_actual["vidas"], ganador=1)
                        self.guardar_stats(
                            dicc_actual["usuario"], ganador=True)
            if usuario_existente:
                await message.channel.send(file=discord.File(os.path.join("images", str(dicc_actual["usuario"]) + "_game.jpg")))
            await message.channel.send(embed=embed_msg)
        # !ayuda
        if message.content.startswith("!ayuda"):
            embed_msg = discord.Embed(title="Ahorcado", colour=0x00FF00)
            msg = "!iniciar_ahorcado -> Inicia una partida de ahorcado si aun no iniciaste ninguna\n"
            msg += "!ahorcado <letra> -> Ingresa la letra para adivinar la palabra/frase que te toco\n"
            msg += "!ayuda -> Ayuda del bot\n"
            msg += "!stats -> Mira tus stats de las partidas de ahorcado\n"
            msg += "!g_iniciar_ahorcado -> Inicia una partida de ahorcado si aun no hay una partida global pendiente\n"
            msg += "!g_ahorcado <letra> -> Ingresa la letra para adivinar la palabra/frase de la partida global\n"
            msg += "!top10_ahorcado -> Mira el top 10 de jugadores de ahorcado"
            embed_msg.add_field(name="Comandos", value=f"{msg}", inline=False)
            await message.channel.send(embed=embed_msg)
        # !stats
        if message.content.startswith("!stats"):
            dicc_stats = None
            with open(os.path.join("data", 'stats.json'), 'rt') as json_file:
                dicc_stats = json.load(json_file)
            usuario_existente = False
            index_dicc = None
            for index, diccionario in enumerate(dicc_stats):
                if diccionario["usuario"] == message.author.id:
                    usuario_existente = True
                    index_dicc = index
                    break
            if usuario_existente:
                embed_msg = discord.Embed(title="Ahorcado", colour=0x00FF00)
                msg = "Partidas jugadas: " + \
                    str(dicc_stats[index_dicc]["partidas"]) + "\n"
                msg += "Partidas ganadas: " + \
                    str(dicc_stats[index_dicc]["victorias"]) + "\n"
                msg += "Partidas perdidas: " + \
                    str(dicc_stats[index_dicc]["derrotas"]) + "\n"
                msg += "Ultima partida jugada: " + \
                    dicc_stats[index_dicc]["ultima_partida"]
                embed_msg.add_field(
                    name=f"Estadisticas de " + dicc_stats[index_dicc]["nickname"], value=f"{msg}", inline=False)
            else:
                embed_msg = discord.Embed(title="Ahorcado", colour=0x00FF00)
                msg = "No existen estadisticas del usuario " + \
                    dicc_stats[index_dicc]["nickname"]
                embed_msg.add_field(
                    name="Estadisticas de " + dicc_stats[index_dicc]["nickname"], value=f"{msg}", inline=False)
            await message.channel.send(embed=embed_msg)
        # !top10
        if message.content == "!top10_ahorcado":
            with open(os.path.join("data", 'stats.json'), 'rt') as json_file:
                dicc_stats = json.load(json_file)
            players_list = [(player["nickname"], player["partidas"], player["victorias"], player["derrotas"]) for player in dicc_stats]
            players_list.sort(reverse=True, key = lambda x : x[2])
            embed_msg = discord.Embed(title="Top 10", colour=0x00FF00)
            max_pos = len(players_list)
            if max_pos > 10:
                max_pos = 10
            for pos in range(0, max_pos):
                msg = "Victorias: " + str(players_list[pos][2]) + " Derrotas: " + str(players_list[pos][3])
                embed_msg.add_field(name=players_list[pos][0], value=msg, inline=False)
            await message.channel.send(embed=embed_msg)
        # !g_iniciar_ahorcado
        if message.content.startswith("!g_iniciar_ahorcado"):
            usuario_existente = False
            index_dicc = None
            for index, diccionario in enumerate(self.dicc_game):
                if diccionario["usuario"] == "global":
                    usuario_existente = True
                    index_dicc = index
                    break
            if not usuario_existente:
                diccionario = {
                    "usuario": "global",
                    "juego_iniciado": None,
                    "palabra": [],
                    "letras_usadas": [],
                    "letras_acertadas": 0,
                    "vidas": self.vidas_totales,
                    "ganador": None
                }
                palabras_json_file = open(os.path.join(
                    "data", "palabras.json"), "rt", encoding="utf-8-sig")
                palabras_json = json.load(palabras_json_file)
                palabras_json_file.close()
                palabra_elegida = palabras_json["palabras"][random.randint(
                    0, len(palabras_json["palabras"]) - 1)]
                diccionario["juego_iniciado"] = True
                diccionario["usuario"] = "global"
                diccionario["palabra"] = [char for char in palabra_elegida]
                vidas_restantes = diccionario["vidas"]
                self.dicc_game.append(diccionario.copy())
                cant_letras = self.contar_palabra(diccionario["palabra"])
                cant_letras_usadas, palabra = self.calcular_palabra(
                    diccionario["palabra"], diccionario["letras_usadas"])
                embed_msg = discord.Embed(
                    title="Ahorcado Global", description="Inicio de juego GLOBAL", colour=0x00FF00)
                embed_msg.add_field(name="La palabra a adivinar tiene",
                                    value=f"{str(cant_letras)} letras", inline=False)
                embed_msg.add_field(
                    name="Palabra", value=f"{palabra}", inline=False)
                embed_msg.add_field(name="Vidas restantes",
                                    value=f"{vidas_restantes}", inline=True)
                self.dibujar_imagen(diccionario["usuario"], palabra)
            else:
                diccionario = self.dicc_game[index_dicc]
                cant_letras_usadas, palabra = self.calcular_palabra(
                    diccionario["palabra"], diccionario["letras_usadas"])
                letras_usadas = diccionario["letras_usadas"]
                vidas_restantes = diccionario["vidas"]
                embed_msg = discord.Embed(
                    title="Ahorcado Global", description=f"Ya existe una partida de ahorcado existente de modo GLOBAL", colour=0x00FF00)
                embed_msg.add_field(
                    name="Palabra", value=f"{palabra}", inline=False)
                embed_msg.add_field(name="Letras usadas",
                                    value=f"{letras_usadas}", inline=False)
                embed_msg.add_field(name="Vidas restantes",
                                    value=f"{vidas_restantes}", inline=True)
                self.dibujar_imagen(
                    diccionario["usuario"], palabra, vidas_restantes)
            await message.channel.send(file=discord.File(os.path.join("images", str(diccionario["usuario"]) + "_game.jpg")))
            await message.channel.send(embed=embed_msg)
        #!g_ahorcado
        if message.content.startswith("!g_ahorcado"):
            usuario_existente = False
            index_dicc = None
            for index, diccionario in enumerate(self.dicc_game):
                if diccionario["usuario"] == "global":
                    usuario_existente = True
                    index_dicc = index
                    break
            if not usuario_existente:
                embed_msg = discord.Embed(
                    title="Ahorcado Global", description=f"No fue iniciada una partida de ahorcado de modo GLOBAL", colour=0xFF0000)
            else:
                dicc_actual = self.dicc_game[index_dicc]
                letra = re.compile(r"(!g_ahorcado )").sub("", message.content,)
                if len(letra) != 1 or not letra.isalpha():
                    embed_msg = discord.Embed(
                        title="Ahorcado Global", description=f"No se encuentra la letra ingresada, vuelva a intentarlo", colour=0xFF0000)
                    usuario_existente = False
                elif len(letra) == 1:
                    letra = letra.lower()
                    embed_msg = discord.Embed(
                        title="Ahorcado Global", description=f"Partida en curso modo GLOBAL", colour=0xFFFFFF)
                    embed_msg.add_field(
                        name="Letra ingresada", value=f"{letra}", inline=False)
                    dicc_actual["letras_usadas"].append(letra)
                    letras_usadas = dicc_actual["letras_usadas"]
                    cant_letras, palabra_incompleta = self.calcular_palabra(
                        dicc_actual["palabra"], dicc_actual["letras_usadas"])
                    # COMPROBACION DE LETRA
                    if cant_letras > dicc_actual["letras_acertadas"]:
                        dicc_actual["letras_acertadas"] = cant_letras
                        vidas_restantes = dicc_actual["vidas"]
                        embed_msg.add_field(
                            name="Palabra", value=f"{palabra_incompleta}", inline=False)
                        embed_msg.add_field(
                            name="Letras usadas", value=f"{letras_usadas}", inline=False)
                        embed_msg.add_field(
                            name="Vidas restantes", value=f"{vidas_restantes}", inline=False)
                        self.dibujar_imagen(
                            dicc_actual["usuario"], palabra_incompleta, dicc_actual["vidas"], 1)
                    else:
                        dicc_actual["vidas"] -= 1
                        vidas_restantes = dicc_actual["vidas"]
                        embed_msg.add_field(
                            name="Palabra", value=f"{palabra_incompleta}", inline=False)
                        embed_msg.add_field(
                            name="Letras usadas", value=f"{letras_usadas}", inline=False)
                        embed_msg.add_field(
                            name="Vidas restantes", value=f"{vidas_restantes}", inline=False)
                        self.dibujar_imagen(
                            dicc_actual["usuario"], palabra_incompleta, dicc_actual["vidas"], 0)
                    # PERDEDOR
                    if dicc_actual["vidas"] == 0:
                        palabra_correcta = "".join(dicc_actual["palabra"])
                        embed_msg.add_field(
                            name="Has perdido", value=f"Las vidas se acabaron gracias a <@{str(message.author.id)}>", inline=False)
                        embed_msg.add_field(
                            name="Palabra correcta", value=f"{palabra_correcta}", inline=False)
                        dicc_actual["ganador"] = False
                        dicc_actual["juego_iniciado"] = False
                        self.dicc_game.pop(index_dicc)
                        self.dibujar_imagen(
                            dicc_actual["usuario"], palabra_correcta, dicc_actual["vidas"], ganador=0)
                        self.guardar_stats(
                            dicc_actual["usuario"], ganador=False)
                    # GANADOR
                    if cant_letras == self.contar_palabra(dicc_actual["palabra"]):
                        palabra_correcta = "".join(dicc_actual["palabra"])
                        embed_msg.add_field(
                            name="Has ganado", value=f"El usuario <@{str(message.author.id)}> fue el ultimo en adivinar la palabra y acaba de ganar la partida GLOBAL", inline=False)
                        embed_msg.add_field(
                            name="Palabra correcta", value=f"{palabra_correcta}", inline=False)
                        dicc_actual["ganador"] = True
                        dicc_actual["juego_iniciado"] = False
                        self.dicc_game.pop(index_dicc)
                        self.dibujar_imagen(
                            dicc_actual["usuario"], palabra_incompleta, dicc_actual["vidas"], ganador=1)
                        self.guardar_stats(
                            dicc_actual["usuario"], ganador=True)
            if usuario_existente:
                await message.channel.send(file=discord.File(os.path.join("images", str(dicc_actual["usuario"]) + "_game.jpg")))
            await message.channel.send(embed=embed_msg)

    async def on_ready(self):
        print("Ahorcado-Bot Iniciado")
        print(f"Iniciado como {client.user}")
        file_json = open(os.path.join("data", 'datos.json'), "rt")
        self.dicc_game = json.load(file_json)
        print("Los datos fueron cargados correctamente")
        client.loop.create_task(self.save_info())

    async def save_info(self):
        while True:
            await asyncio.sleep(15)
            now = datetime.now()
            now = str(now.strftime("%Y-%m-%d %H:%M:%S"))
            with open(os.path.join("data", 'datos.json'), 'wt') as json_file:
                json.dump(self.dicc_game, json_file, indent=4)
            print(
                f"Se realizo una copia de seguridad de la informacion del juego a la hora {now}")


# Config environment
config = configparser.ConfigParser()
config.read(os.path.join("conf", 'conf.ini'))

client = AhorcadoBot()
client.run(config['TOKEN']['secret_token'])
