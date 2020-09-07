# ahorcado-bot-discord

## Descripcion

Bot de Discord para jugar al Ahorcado.

## Modulos necesarios

Los modulos que se necesitan instalar/actualizar en Python para la utilizacion del bot son los siguientes:

- discord
- PIL

## Como Instalar

1) Instalar los modulos necesarios de Python 3 que se indicaron anteriormente
2) Se debe hostear en algun servidor de deployment como por ejemplo: heroku, repl, glitch o en la propia PC (no recomendado si vas a dejarlo encendido)
3) Crear un bot de discord y obtener el token secreto (guardarlo para mas adelante)
4) Con Oauth2 armar el link de invitacion como bot y agregarlo a un canal de discord existente
5) Con el secret token, agregarlo al archivo de configuracion que se encuentra en la carpeta conf/ en el parametro secret_token="token" (sin comillas)
6) Ejecutar el script de python **ahorcado-bot-discord.py** para empezar a jugar con el bot.

## Comandos del bot

- **!iniciar_ahorcado** : Inicia una partida de ahorcado si aun no iniciaste ninguna
- **!ahorcado (letra)** : Ingresa la letra para adivinar la palabra/frase que te toco
- **!ayuda** : Ayuda del bot
- **!stats** : Mira tus stats de las partidas de ahorcado
- **!g_iniciar_ahorcado** : Inicia una partida de ahorcado si aun no hay una partida global pendiente
- **!g_ahorcado (letra)** : Ingresa la letra para adivinar la palabra/frase de la partida global
- **!top10_ahorcado** : Mira el top 10 de jugadores de ahorcado

## Agregado de palabras y frases

Desde **data/palabras.json** es posible agregar mas palabras y frases para jugar con el bot simplemente agregandolos dentro de la lista de palabras despues de una coma.

Ejemplo:

    "palabras": [
        "gato",
        "murcielago",
        "foca",
        "comida",
        "futbol",
        "argentina",
        "cometa",
        "<nueva_palabra>",
        ... ]
