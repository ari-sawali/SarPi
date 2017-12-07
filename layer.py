# -*- coding: utf-8 -*-
import os, subprocess, time, logging, random, wikipedia
from threading import Thread

from yowsup.layers.interface                           import YowInterfaceLayer                 #Reply to the message
from yowsup.layers.interface                           import ProtocolEntityCallback            #Reply to the message
from yowsup.layers.protocol_messages.protocolentities  import TextMessageProtocolEntity         #Body message
from yowsup.layers.protocol_presence.protocolentities  import AvailablePresenceProtocolEntity   #Online
from yowsup.layers.protocol_presence.protocolentities  import UnavailablePresenceProtocolEntity #Offline
from yowsup.layers.protocol_presence.protocolentities  import PresenceProtocolEntity            #Name presence
from yowsup.layers.protocol_chatstate.protocolentities import OutgoingChatstateProtocolEntity   #is writing, writing pause
from yowsup.common.tools                               import Jid                               #is writing, writing pause
from yowsup.layers.protocol_media.protocolentities     import *                                 #media thing
from yowsup.layers.protocol_media.mediauploader        import MediaUploader

name = "SarPI"
print("Bienvenido, bot en funcionamiento")

class EchoLayer(YowInterfaceLayer):
    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):
        if messageProtocolEntity.getType() == 'text':
            self.toLower(messageProtocolEntity.ack()) #Set received (double v)
            time.sleep(0.5)
            self.toLower(PresenceProtocolEntity(name = name)) #Set name SarPi
            self.toLower(AvailablePresenceProtocolEntity()) #Set online
            time.sleep(0.5)
            self.toLower(messageProtocolEntity.ack(True)) #Set read (double v blue)
            time.sleep(0.5)
            message = messageProtocolEntity.getBody()
            print("Mensaje: "+str(message))
            if message[0] == '.':
                self.toLower(OutgoingChatstateProtocolEntity(OutgoingChatstateProtocolEntity.STATE_TYPING, Jid.normalize(messageProtocolEntity.getFrom(False)) )) #Set is writing
                time.sleep(1)
                self.toLower(OutgoingChatstateProtocolEntity(OutgoingChatstateProtocolEntity.STATE_PAUSED, Jid.normalize(messageProtocolEntity.getFrom(False)) )) #Set no is writing
                self.onTextMessage(messageProtocolEntity) #Send the answer
                time.sleep(2.5)
            self.toLower(UnavailablePresenceProtocolEntity()) #Set offline
            
##########Uploads###########

    def image_send(self, number, path, caption = None):
        jid = number
        mediaType = "image"
        entity = RequestUploadIqProtocolEntity(mediaType, filePath = path)
        successFn = lambda successEntity, originalEntity: self.onRequestUploadResult(jid, mediaType, path, successEntity, originalEntity, caption)
        errorFn = lambda errorEntity, originalEntity: self.onRequestUploadError(jid, path, errorEntity, originalEntity)
        self._sendIq(entity, successFn, errorFn)

    def doSendMedia(self, mediaType, filePath, url, to, ip = None, caption = None):
        entity = ImageDownloadableMediaMessageProtocolEntity.fromFilePath(filePath, url, ip, to, caption = caption)
        self.toLower(entity)

    def onRequestUploadResult(self, jid, mediaType, filePath, resultRequestUploadIqProtocolEntity, requestUploadIqProtocolEntity, caption = None):
        if resultRequestUploadIqProtocolEntity.isDuplicate():
            self.doSendMedia(mediaType, filePath, resultRequestUploadIqProtocolEntity.getUrl(), jid,
                             resultRequestUploadIqProtocolEntity.getIp(), caption)
        else:
            successFn = lambda filePath, jid, url: self.doSendMedia(mediaType, filePath, url, jid, resultRequestUploadIqProtocolEntity.getIp(), caption)
            mediaUploader = MediaUploader(jid, self.getOwnJid(), filePath,
            resultRequestUploadIqProtocolEntity.getUrl(),
            resultRequestUploadIqProtocolEntity.getResumeOffset(),
            successFn, self.onUploadError, self.onUploadProgress, async=False)
            mediaUploader.start()

    def onRequestUploadError(self, jid, path, errorRequestUploadIqProtocolEntity, requestUploadIqProtocolEntity):
        #logger.error("Request upload for file %s for %s failed" % (path, jid))
        print ("Request upload for file %s for %s failed" % (path, jid))

    def onUploadError(self, filePath, jid, url):
        #logger.error("Upload file %s to %s for %s failed!" % (filePath, url, jid))
        print ("Upload file %s to %s for %s failed!" % (filePath, url, jid))

    def onUploadProgress(self, filePath, jid, url, progress):
        print("%s => %s, %d%% \r" % (os.path.basename(filePath), jid, progress))
        #sys.stdout.flush()

############################

    def alarm(self, taim, recipient, recordatorio):
        time.sleep(taim)
        answer = recordatorio
        self.toLower(TextMessageProtocolEntity(answer, to = recipient ))
        print(answer)
        
        
    def buscarLineas(self, texto, nlineas, saltar):
        encontrada = 0
        resultado = ''
        print("#Buscando "+texto)
        perfiles = open("perfiles.txt")
        for linea in perfiles:
            if linea.lower() == (texto.lower()+'\n') and not encontrada:
                if saltar:
                    saltar -= 1
                else:
                    resultado = linea
                    nlineas -= 1
                encontrada = 1
                
            elif encontrada and nlineas > 0:
                if saltar:
                    saltar -= 1
                else:
                    resultado = resultado + linea
                    nlineas -= 1
                
            elif nlineas == 0:
                perfiles.close()
                print(resultado)
                return resultado
        perfiles.close()
                
    def buscarReemplazar(self, texto, saltar, reemplazo):
        encontrada = 0
        perfiles_o = open("perfiles.txt")
        perfiles_m = open("perfiles.txt", 'r+')
        for linea in perfiles_o:
            if linea.lower() == (texto.lower()+'\n') and not encontrada:
                if saltar:
                    saltar -= 1
                    perfiles_m.write(linea)
                else:
                    perfiles_m.write(reemplazo.replace('\n', '/n')+'\n')
                encontrada = 1
                
            elif encontrada and saltar:
                perfiles_m.write(linea)
                saltar -= 1
                
            elif encontrada and not saltar:
                perfiles_m.write(reemplazo.replace('\n', '/n')+'\n')
                saltar -= 1
            else:
                perfiles_m.write(linea) 
        perfiles_o.close()
        perfiles_m.close()        
        return encontrada
        
    def crearPerfil(self, remitente, nombre):
        perfiles = open ("perfiles.txt", "a")
        perfiles.write(remitente+'\n'+nombre.replace('\n', ' ')+'\nEstado vacío\n3\n👥\n')
        perfiles.close()

    '''@ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        print(entity.ack())
        self.toLower(entity.ack())'''
      
      
    def onTextMessage(self,messageProtocolEntity):
        namemitt   = messageProtocolEntity.getNotify()
        message    = messageProtocolEntity.getBody()
        recipient  = messageProtocolEntity.getFrom()
        remitente  = messageProtocolEntity.getParticipant()
        textmsg    = TextMessageProtocolEntity
        answer     = '⚠ Se ha producido un error, contacte con el administrador'
        comando    = ''
        i = 1
             
        if remitente is None:
            remitente = recipient

        print("Mensaje de "+remitente+' ('+namemitt+"): "+str(message))
        
        while i < len(message) and message[i] != ' ':
            comando = comando+message[i].lower()
            i += 1
        print(comando)
        if comando == 'hola':
            answer = "_Hola, bienvenido al Servicio Automatizado de Respuesta 'PI', *SarPI* para los amigos. Espero servirle de ayuda._\nPuede ver los comandos disponibles con *.list*"
            self.toLower(textmsg(answer, to = recipient ))
            self.image_send(recipient, 'sarpi.png', 'SarPI, Versión Alpha')
            print(answer)

        elif comando == 'hora':
            hora = time.asctime( time.localtime(time.time()) )
            answer = 'Hora y fecha actuales: *'+hora+'*'
            self.toLower(textmsg(answer, to = recipient ))
            print(answer)
            
        elif comando == 'gracias':
            answer = "De nada ❤"
            self.toLower(textmsg(answer, to = recipient ))
            print(answer)
            
        elif comando == 'list':
            answer = "Los comandos disponibles son: \n.hola\n.list\n.perfil\n.cookie\n.calc\n.gracias\n.wiki\n.reco\n.aquesi\n.hora\n.ping"
            self.toLower(textmsg(answer, to = recipient ))
            print(answer)
            
        elif comando == 'reco':
            tiempo = ''
            multiplicador = 'm'
            recordatorio = 'Te recuerdo:'
            answer = '⛔ Introduzca el tiempo seguido de s, m o h; y después el recordatorio.\nEjemplo: .reco 10m Sacar comida del horno'
            i += 1
            if i < len(message):
                while i < len(message) and message[i].isdigit():
                    tiempo = tiempo+message[i]
                    i += 1
                if i < len(message):
                    if message[i] == 's' or message[i] == 'm' or message[i] == 'h':
                        multiplicador = message[i]
                        i += 1
                
                    while i < len(message):
                        recordatorio = recordatorio+message[i]
                        i += 1
                
                    if tiempo != '' and recordatorio != '':
                        answer = recordatorio+' en '+tiempo
                
                        # joe, en python no hay switch
                        if multiplicador == 'h':
                            tiempo = int(tiempo)*3600
                            answer = answer + ' horas'
                        elif multiplicador == 'm':
                            tiempo = int(tiempo)*60
                            answer = answer + ' min'
                        else:
                            answer = answer + ' segundos'

                        th = Thread(target = self.alarm, args = (int(tiempo), recipient, recordatorio))
                        th.start()
            self.toLower(textmsg(answer, to = recipient ))
            print(answer)

        elif comando == 'calc':
            operacion = ''
            for i in range (i, len(message)):
                operacion = operacion+message[i]
                if not (message[i].isdigit() or message[i] == '+' or message[i] == '-' or message[i] == '*' or message[i] == '/' or message[i] == ' ') :
                    operacion = ''
                    break
                
            if operacion != '':
                answer = 'La respuesta es: '+str(eval(operacion))
            else:
                answer = '⛔ No ha introducido una operación válida'
				
            self.toLower(textmsg(answer, to = recipient ))
            print(answer)
        
        elif comando == 'cookie':
            nombre = ''
            i += 1
            while i < len(message):
                nombre = nombre + message[i]
                i +=1
            cookies = self.buscarLineas(remitente, 1, 3)
            if nombre == '':
                if cookies is not None:
                    cookies = int(cookies)+1
                    self.buscarReemplazar(remitente, 3, str(cookies))
                    answer = '🍪 ¡Has obtenido una galleta!'
                else:
                    answer = '✅ No ha creado un perfil.'
            else:
                cookiesReceptor = self.buscarLineas(nombre, 1, 2)
                if cookies is None:
                    answer = '✅ No ha creado un perfil.'
                elif cookiesReceptor is None:
                    answer = '✅ No existe el perfil del receptor.'
                elif int(cookies) > 0:
                    cookies = int(cookies)-1
                    cookiesReceptor = int(cookiesReceptor)+1
                    self.buscarReemplazar(remitente, 3, str(cookies))
                    self.buscarReemplazar(nombre, 2, str(cookiesReceptor))
                    answer = 'Se ha transferido una galleta a '+nombre
                elif int(cookies) == 0:
                    answer = 'No tienes galletas suficientes.'
            self.toLower(textmsg(answer, to = recipient ))
            print(answer)
        
        elif comando == 'perfil':
            subcomando = ''
            nombre = ''
            mencion = 0
            
            i += 1
            if i<len(message) and message[i] == '@':
                mencion = True
                i += 1
            while i < len(message) and message[i] != ' ':
                subcomando = subcomando + message[i].lower()
                i += 1
            i += 1
            while i < len(message):
                nombre = nombre + message[i].lower()
                i +=1
                
            answer = '⛔ No se ha encontrado el perfil.'
            if subcomando == '':
                texto = self.buscarLineas(remitente, 2, 1)
                emote = self.buscarLineas(remitente, 1, 4)
                cookies = self.buscarLineas(remitente, 1, 3)
                if texto is not None:
                    answer = emote+texto.replace('\n', '\n---------------------\n').replace('/n', '\n')+'Cookies: '+cookies
                
            elif subcomando == 'nombre':
                if nombre != '':
                    if self.buscarReemplazar(remitente, 1, nombre):
                        answer = '✅ Se ha modificado su perfil con éxito.'
                    else:
                        self.crearPerfil(remitente, nombre)
                        answer = '✅ Se ha creado su perfil con éxito.'
                else:
                    answer = '⛔ Coloque su nombre después del comando.'
            elif subcomando == 'estado':
                if nombre != '':
                    if self.buscarReemplazar(remitente, 2, nombre):
                        answer = '✅ Se ha modificado su perfil con éxito.'
                    else:
                        answer = '⛔ No ha creado un perfil.'
                else:
                    answer = '⛔ Coloque el estado después del comando.'
            elif subcomando == 'emote':
                if nombre != '':
                    if self.buscarReemplazar(remitente, 4, nombre[0]):
                        answer = '✅ Se ha modificado su perfil con éxito.'
                    else:
                        answer = '⛔ No ha creado un perfil.'
                else:
                    answer = '⛔ Coloque un emoticono después del comando.'
            elif subcomando == 'info':
                answer = '----------ℹ----------\n·Para crear un nuevo perfil o cambiar el nombre de su perfil actual utilice el subcomando *nombre* y, posteriormente, el nombre de usuario a su elección.\n·Para mostrar su perfil introduzca el subcomando *mostrar*. También puede ver el perfil de otras personas introduciendo a continuación su nombre de usuario.\n·Con el subcomando *estado* puede cambiar la descripción de su perfil.\n·Con *emote* puede cambiar el emoticono de su perfil.\nEjemplo de utilización:\n *.perfil mostrar SarPi*'
            else:
                if mencion:
                    subcomando = subcomando + '@s.whatsapp.net'
                texto   = self.buscarLineas(subcomando, 2, 0 + mencion)
                emote   = self.buscarLineas(subcomando, 1, 3 + mencion)
                cookies = self.buscarLineas(subcomando, 1, 2 + mencion)
                if texto is not None:
                    answer = emote + texto.replace('\n', '\n---------------------\n').replace('/n', '\n') + 'Cookies: ' + cookies
            self.toLower(textmsg(answer, to = recipient ))
            print(answer)
        elif comando == 'ping':
            if os.system("ping -c 1 c1.whatsapp.net") == 0:
                answer = ' 🏓 Pong!'
            else:
                answer = 'No se ha podido contactar con los servidores de Whatsapp. Entonces... ¿Por qué estás recibiendo esto?'
            self.toLower(textmsg(answer, to=recipient))
            print(answer)
        elif comando == 'aquesi':
            respuestas = [
                '¡Por supuesto!',
                'Mis transistores indican que \n\n\nş̶̛̠̜͓̦̪̙͔̣̠̗̥̲̘̥͕̟̤͋͂̇̔̇̊̄̊͠i̶̢̯̩̱̖̜̝͚̯͍̻̫̭̟͒̒̋͊͜ͅn̷̨̧̟̱̻̣̯̰̻͔̈́͐̓̇́͊̎̓̋͑̇͑ò̸̮̯͒̍̂̊̉́̓͒̏̾͋̓̔̚͠͠ş̷͍̙̮̘͍̋̑͛̌͛͋̊̆̅͋̿̐̐͊̿̒̓̅̿̎͐͐̃͑̕͜͝͝͠ȋ̷̧̨̢̛̛̛̙͖͉̩͕͖̮͔̠͈̙̭̣̹̞̥̙̈̇̂̄͂́̄́͑͜͠ņ̵̨̢̝̩͎͖̯̭̯̫̻͕̖̰̻̭͖̟͕͔͍͉̗̠̰͕̺̲̜̘̜͔̗̬̈́̇͂̐͜͝o̵̧̡̨̨̻͚̣̺̗̪̥̖̦̲̞̞̬̲͈̦̣̙̝͚̭̪̓̐̏̔̉̌̓̉͌̅̐͘͝͝͝ş̴̳͔̣̺̳͔͓͙̌̾̇̄̆̏̒̓͗͂͛͊̊̎̅͗́̄͒̕͠í̷̢̠͎̭̫͈̣̟̤̺̼̤̗͎̠̜̬̻́̒͂̆̑͌̓͂͂͐̀̾̊͑̂̃͆̈̎̚͝͠ņ̶̬̺͉̠͙̣̦̺̝͔̣̰͓̤̜̖̋̍ó̶̢̢̦̟̪̼̩͖͚͈͇͚̹̻̥͔͙͍̻̼͉̝̟̘̮̖͍̰́͑̑̽͋̋̒̈́̿̑͘̕͝͠s̴͕̥̯͍͐͊̌̏̒̍͊̀̓̉̅̐̅̂̓͗͛̽̆̑̑̈̀̏̚͘͝͠͝͝ͅí̸̢̧̛͚̣̼̱̥̖̦̰̥̖͚̞͓̹̗͔̯͖̰̘̟̣̯̪͇̻͈͖̱̠̠̪̺̂̃̑̀̽̏̔̇̎̇̓̿̌͊̆̈́͗̓̿̈̓͛̈́͋͒͝ͅn̴̜͓̤͑̈̉́̊͛̄̋͛̔͆̚͝͠͠͠ơ̸̡̡̨̳̰̮̣͚͉̙̳̫̻̰̞̾̒̾̈́̑́̎̆͂̀͂͋̈́̕͝͠ş̸̛̫̼͍͍̠̺͈͎̼͕̘̩͓̩̌͊̇̾́͑̃͋̿̒̄̓̎͐̂́́͆̑̽̈́̈́͒̔̓̌̍̚͝͝͝į̶̖̘͕̗͇̰͉̞̳̩̻̜̤̜̱͕̞̥͎͈̖̘̫̹̺̗͗̀̍̒̿̋͠͠ņ̷̡̧̛͓͙̝̠̮̠̺͙͉͎̗̥̻̍̃̉̂̀̈́̏̽̌̇̒̈́̔̓̏̓̒̈́̊̊́̈́̈́̊͘͝͝͝ǫ̶̡̨̧̛̱̹̣̤̯͍̩̭́͒͒̅͆̂̉͐͆̐̓̄̓͋̉͒̎̔̔̾̾̈́̔̃̀̔͂̏̚̕͝s̸̨̨̛̼̺̞̦̯̉̔̈̎͋̈́̆͛͊̀͒͛̔͗̓͛̈́̐́̑̉͋͑͘͠͝í̵̧̛̛̟̞͉͇̫͚̭̺͋̔͋̿̆̓͊̀̅͐́̈̀̐̊͒́̉̊͑͛̃̆̉ň̴̨̡̝̜̞̾͋̈́͆͆̐̆͛̅̈͊̈̉̔͝ọ̴̡̧̡͚̬͖̤͖̫̠̬͍̫̘̭̟͖̩͍̘̹͈͈̭͚͎̜̼͂̎̓̈́͆̓͌̅̎̏̑̓̔̈̑̓̅́̀̍̓͒̑̆́̊̕̕͝͠',
                'Más claro, agua',
                '¡Claro que si, campeón!',
                'Sigue viviendo en tu mundo...',
                'Jaja *NO*',
                'Jaja *SI*',
            ]
            answer = random.choice(respuestas)
            self.toLower(textmsg(answer, to=recipient))
            print(answer)
        elif comando == 'wiki':
            subcomando = ''
            i += 1
            while i < len(message):
                subcomando = subcomando + message[i].lower()
                i += 1
            if subcomando != '':
                answer = wikipedia.summary(subcomando)
            else:
                answer = '⛔ Introduzca el término de búsqueda'
            self.toLower(textmsg(answer, to=recipient))
            print(answer)
        else:
            answer = '⛔ Comando inválido. Para ver la lista de comandos, utilice el comando *.list*'
            self.toLower(textmsg(answer, to = recipient ))
            print(answer)        


