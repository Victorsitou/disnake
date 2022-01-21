.. image:: ./assets/banner.png
    :alt: Disnake Banner

disnake
=======

.. image:: https://discord.com/api/guilds/808030843078836254/embed.png
   :target: https://discord.gg/gJDbCw8aQy
   :alt: Discord server invite
.. image:: https://img.shields.io/pypi/v/disnake.svg
   :target: https://pypi.python.org/pypi/disnake
   :alt: PyPI version info
.. image:: https://img.shields.io/pypi/pyversions/disnake.svg
   :target: https://pypi.python.org/pypi/disnake
   :alt: PyPI supported Python versions
.. image:: https://img.shields.io/github/commit-activity/w/DisnakeDev/disnake.svg
   :target: https://github.com/DisnakeDev/disnake/commits
   :alt: Commit activity

Una librería de API moderna, fácil de usar, rica en características y preparada para async para Discord escrita en Python.

Acreca de disnake
-------------

Todos los colaboradores y desarrolladores, asociados con disnake, están tratando de hacer todo lo posible para añadir nuevas características a la biblioteca tan pronto como sea posible. Nos esforzamos por revivir la mayor librería de Python para la API de Discord y mantenerlo actualizado.

Características principales
------------

- API moderna de Python con ``async`` y ``await``.
- Funciones añadidas para facilitar la escritura de código.
- Manejo adecuado del límite de tasa.
- Optimizado tanto en velocidad como en memoria.

Instalación
----------

**Se requiere una versión de Python 3.8 o superior**

Para instalar la librería sin soporte de voz completo, sólo tiene que ejecutar el siguiente comando:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U disnake

    # Windows
    py -3 -m pip install -U disnake

En el caso que quiera soporte de voz debe ejecutar el siguiente comando:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U "disnake[voice]"

    # Windows
    py -3 -m pip install -U disnake[voice]


Para instalar la versión de desarrollo, haga lo siguiente:

.. code:: sh

    $ git clone https://github.com/DisnakeDev/disnake
    $ cd disnake
    $ python3 -m pip install -U .[voice]


Paquetes opcionales
~~~~~~~~~~~~~~~~~

* `PyNaCl <https://pypi.org/project/PyNaCl/>`__ (para el soporte de voz)

Por favor, ten en cuenta que en Linux instalando voice debes instalar los siguientes paquetes a través de tu gestor de paquetes favorito (por ejemplo ``apt``, ``dnf``, etc) antes de ejecutar los comandos anteriores:

* libffi-dev (or ``libffi-devel`` on some systems)
* python-dev (e.g. ``python3.6-dev`` for Python 3.6)

Quick Example
-------------

.. code:: py

    import disnake

    class MyClient(disnake.Client):
        async def on_ready(self):
            print('Logged on as', self.user)

        async def on_message(self, message):
            # don't respond to ourselves
            if message.author == self.user:
                return

            if message.content == 'ping':
                await message.channel.send('pong')

    client = MyClient()
    client.run('token')

Bot Example
~~~~~~~~~~~

.. code:: py

    import disnake
    from disnake.ext import commands

    bot = commands.Bot(command_prefix='>')

    @bot.command()
    async def ping(ctx):
        await ctx.send('pong')

    bot.run('token')

Slash Commands Example
~~~~~~~~~~~~~~~~~~~~~~

.. code:: py

    import disnake
    from disnake.ext import commands

    bot = commands.Bot(command_prefix='>', test_guilds=[12345])

    @bot.slash_command()
    async def ping(inter):
        await inter.response.send_message('pong')

    bot.run('token')

Context Menus Example
~~~~~~~~~~~~~~~~~~~~~

.. code:: py

    import disnake
    from disnake.ext import commands

    bot = commands.Bot(command_prefix='>', test_guilds=[12345])

    @bot.user_command()
    async def avatar(inter):
        embed = disnake.Embed(title=str(inter.target))
        embed.set_image(url=inter.target.avatar.url)
        await inter.response.send_message(embed=embed)

    bot.run('token')

You can find more examples in the examples directory.

Links
------

- `Documentation <http://disnake.rtfd.io/>`_
- `Official Discord Server <https://discord.gg/gJDbCw8aQy>`_
- `Discord API <https://discord.gg/discord-api>`_
