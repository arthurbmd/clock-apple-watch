#! usr/bin/env python
# coding: utf-8
#
## packing: clock
#
import json
from math import sin, cos, pi
from datetime import *
import sys
from tkinter import *
from astral import LocationInfo
from astral.sun import sun
import pytz
from timezonefinder import TimezoneFinder
from math import degrees

# Simula um relógio análogico, com base na interface do Apple Watch
# e permite a visualização de um quarto ponteiro, que seria um fuso escolhido
# pelo usuário
# 
class Clock(object):
    
    ##
    # O objeto clock inicia tendo como parâtemetro a raiz do Tkinter, ou seja
    # a tela onde será construída o relógio
    # @param root tela do TKinter onde será desenhado o relógio
    #
    def __init__(self, root):
        # Inicia falso para que nenhum ponteiro gmt seja desenhado
        self.chosed = False
        
        self.delta = -3
        # Listas onde são guardadas as cidades e coordenadas que serão utilizadas no ponteiro gmt
        self.c_cities = []
        self.c_coordinates = []
        self.readFile()
        
        self.root = root
        self.new_value = 584/2
        self.canvas_height = 584
        self.canvas_width = 584
        self.canvas = Canvas(self.root, height=self.canvas_height, width=self.canvas_width, bg='black')
        self.canvas.pack(side= TOP, fill='both', expand=True)
        
        
        self.center = (self.canvas_height/2, self.canvas_width/2)
        # self.drawArcSun()
        
        # Função que permite o loop e atualização frequente do relógio
        self.poll()
        
        # Evento que gera o evento do clique e permite inputar um fuso horário
        self.canvas.bind('<Double-Button-1>', self.fuses)
        self.canvas.bind('<Configure>', self.resize)
        
    
    def resize(self, event):
        self.canvas.delete(ALL)
        if self.root.winfo_height() <= self.root.winfo_width():
            self.new_value = self.root.winfo_height()/2
            self.canvas_width = self.canvas_height = self.root.winfo_height()
        else:
            self.new_value = self.root.winfo_width()/2
            self.canvas_width = self.canvas_height = self.root.winfo_width()
        #self.canvas.create_rectangle(0,0, self.canvas_height, self.canvas_width, fill='black')
        #self.canvas = Canvas(self.root, height=self.canvas_height, width=self.canvas_width, bg='black')
        #self.canvas.pack(expand=True)
        self.canvas.configure(width=self.canvas_width, height=self.canvas_height)
        
        self.center = (self.root.winfo_width()/2, self.root.winfo_height()/2)
        self.drawArcSun()
        # self.drawNumber()
        # self.drawNumberGmt()
        # self.poll()
    
    
    ##
    # Função lê um arquivo do tipo json e preenche as listas c_cities e c_coordinates
    def readFile(self):
        
        # A função limpa as listas para evitar duplicação na informação de ambas as listas
        self.c_cities.clear()
        self.c_coordinates.clear()
        self.c_cities.append(('Padrão', None))
        self.c_coordinates.append((None, None))
        
        
        # Lê o arquivo json e gera uma exceção caso o mesmo não exista
        try:
            f = open('./localtime.json', 'r')
            data = json.load(f)
        except Exception as e:
            sys.exit(f'File not found')
        
        # Preenche as listas tratando os nomes das cidades, removendo o underline ("_") e com as coordenadas
        for c in data['cities']:
            city = c['city']
            if "_" in city:
                city = city.replace('_', ' ')
                
            self.c_cities.append((city, c['offset']))
            self.c_coordinates.append((c['coordinates']['latitude'], c['coordinates']['longitude'])) 
            
    
    ##
    # Define o fuso horário através de um evento de clique
    # @param event evento gerado automaticamente pelo clique do usuário da tela
    def fuses(self, event):
        # Cria uma variável que recebe o valor escolhido pelo usuário 
        self.choosenFuse = StringVar(value=self.c_cities)
        
        # Cria uma Listbox com as opções de fuso, e selecionar, chama a função setFuse()
        
        self.menu = Toplevel(self.root)
        self.menu.title('Escolha o fuso horário')
        self.menu.geometry('180x200')
        self.listbox = Listbox(self.menu,listvariable=self.choosenFuse, height=10, selectmode='browse')
        self.listbox.grid(column=0, row=0, sticky='nwes')
        btn = Button(self.menu, text='Escolher', command=self.setFuse)
        btn.grid(column=0, row=11)
        scroll = Scrollbar(self.menu, orient='vertical', command=self.listbox.yview)
        self.listbox['yscrollcommand'] = scroll.set
        scroll.grid(column=1, row=0, sticky='ns')
        
    
    ## Calcula a hora do fuso horario escolhido pelo usuário e desenha o ponteiro GMT
    # após a operação, o option menu é destruído 
    # @param chosen opção escolhida pelo usuário no option menu criado na função fuses()
    def setFuse(self):
        # Seta a varíavel self.chosed para True, para o ponteiro manter-se na tela
        chosen = self.listbox.curselection()
        opt = self.c_cities[chosen[0]]
        if  opt[0] != 'Padrão':
            self.chosed = True
        
            # Define as coordenadas baseada no índice retornado
            latitude, longitude = self.c_coordinates[chosen[0]]
            
            # Cria um objeto timezonefinder para resgatar o por e nascer do sol a partir 
            # da latitude e longitude
            tf = TimezoneFinder()
            
            # retorna a região/local
            timezone = tf.timezone_at(lat=latitude, lng=longitude)
            
            # Atribui em duas variáveis os valores splitados
            region, local = timezone.split('/')
            
            # retorna um objeto datetime para retornar os dados do sol
            city = LocationInfo(local, region, timezone, latitude, longitude)
            today = datetime.date(datetime.now())
            
            # Gera dados e guarda em um dicionário
            sun_data = sun(city.observer, today, tzinfo=pytz.timezone(timezone))
            
            # retorna hora, minutos e segundos em uma tupla
            h_rise, m_rise, _ = datetime.timetuple(sun_data['sunrise'])[3:6]
            h_set, m_set, _ = datetime.timetuple(sun_data['sunset'])[3:6]
            
            # A cada 15° é uma hora no formato 24h
            twoMinutes = pi / 12
            
            # Calcula os radianos do horario do por e nascer do sol
            hour_rise = (h_rise + m_rise / 60) * twoMinutes
            hour_set = (h_set + m_set / 60) * twoMinutes 
                            
            # Define a hora do fuso inputado pelo usuário 
            self.delta_gmt = float(opt[1])
            # Retorna o horario utc
            utc = datetime.utcnow()
            self.h, m, s = datetime.timetuple(datetime.utcnow()+ timedelta(hours = self.delta_gmt))[3:6]

            # Calcula os minutos, por causa do fuso de Cálcuta, pode ter diferença
            minutes = (self.delta_gmt - int(self.delta_gmt)) * 100
            
            # Calcula os radianos, a cada 15° é uma hora no formato de 24h.
            self.utc_h = twoMinutes * (self.h + (utc.minute + minutes)/ 60)
            self.utc_h %= 24
        else:
            self.chosed = False   
            hour_rise = hour_set = None 
        # Chama o método que desenha os arcos.
        self.drawArcSun(hour_rise, hour_set)

        # Destroi o menu de escolha de fuso
        self.menu.destroy()
      
      
    ## Desenha os números das horas até 12 e até 24 (para os fusos horários)
    # define também a posição deles no relógio
    def drawNumber(self):
        self.canvas.delete('numbers')
        # Desenho do círculo, cria dos arcos que serão as áreas diurnas e noturnas, o limite é dado pelo nascer e por do sol
        
        # Escreve a cada 30° um número de 1 a 12, referente ao relógio analógico        
        for i in range(1,13):
            h = pi * i / 6
            x, y = self.polar2Cartesian(h, 0.62)
            x += self.center[0]
            y += self.center[1]
            
            self.canvas.create_text(x, y, text = i, font='Arial 30 bold', justify=CENTER, 
                                    fill='white', tag='numbers')
            
        # Cria uma linha pequena referente aos números do relógio, minutos/segundos. 
        # A cada 5, cria uma linha maior
        for i in range (1,61):
            h = pi * i / 30
            x1, y1 = self.polar2Cartesian(h, 0.76)
            
            if i % 5 == 0:
                x2, y2 = self.polar2Cartesian(h, 0.71)
            else:
                x2, y2 = self.polar2Cartesian(h, 0.73)
                
            x1 += self.center[0]
            y1 += self.center[1]
            x2 += self.center[0]
            y2 += self.center[1]
            
            self.canvas.create_line(x1, y1, x2, y2, width=1.5, fill='white', capstyle='round', tag='numbers')
    
    ## Desenha os arcos em volta do relógio, azul para o período noturno, vermelho para diurno.
    # Os valores nulos referem quando não há fuso horário definido, criando arcos começando 
    # e finalizando no eixo x.
    # @param hrise horario do nascer do sol, default None
    # @param hset horario do por do sol, default None
    def drawArcSun(self, hrise=None, hset=None):
        # deleta qualquer arco existente
        self.canvas.delete('arc')
        
        # Testa se os valores foram setados ou não
        if (hrise == None or hset == None):
            hrise = 0
            hset = 180
            extent_rise = extent_set = 180 
        else:
            # Converte o horário antes em radianos para graus
            # subtrai 90 graus para determinar o 0° na hora 0/24
            # hrise -> multiplica por -1 para que os graus andarem no sentido horário
            # hset -> subtrai da circunferência o grau correnspondente.
            hrise = - (degrees(hrise)-90)
            hset = 360 - (degrees(hset)-90)
            
            # Extent são as extensões do arco.
            extent_set = -hrise + hset
            extent_rise = 360 - extent_set
        
        x1, y1 = self.polar2Cartesian(21*pi/12, 1.35)
        x2, y2 = self.polar2Cartesian(9*pi/12, 1.35)
        x1 += self.center[0]
        y1 += self.center[1]
        x2 += self.center[0]
        y2 += self.center[1]
        # Cria o arco azul, começando no horario do nascer do sol e indo até o por do sol.
        self.canvas.create_arc(x1, y1, x2, y2, start=hrise, extent = extent_set, fill='#0f3f5a', 
                               style=PIESLICE, tag='arc')
        
        # Cria o arco vermelho, começando no horario do por do sol e indo até o nascer do sol.
        self.canvas.create_arc(x1, y1, x2, y2, start=hset, extent = extent_rise, fill ='#c43b3b', 
                               style=PIESLICE, tag='arc')
        
        # Cria um circulo preto de acabamento.
        self.canvas.create_oval((self.center[0] + self.new_value*0.80), (self.center[1]+ self.new_value*0.80), (self.center[0] - self.new_value*0.80), 
                                    (self.center[1] - self.new_value*0.80), width=3, fill='#000000', tag='arc')
        
        # chama a função de desenho de números em cima do círculo preto e depois do gmt em cima dos arcos
        self.drawNumber()
        self.drawNumberGmt()
        
    # Escreve a cada 15° um número de 1 a 24, referente ao relógio analógico GMT
    def drawNumberGmt(self): 
        self.canvas.delete('gmtNumber')   
        for i in range(0, 24):
            h = pi * i /12
            x1, y1 = self.polar2Cartesian(h, 0.89)
            x2, y2 = self.polar2Cartesian(h, 0.84)
            x1 += self.center[0]
            y1 += self.center[1]
            x2 += self.center[0]
            y2 += self.center[1]
            
            if (self.chosed) and int(self.h) == i:
                self.canvas.create_text(((x1 + x2) / 2), ((y1 + y2) / 2), text = (f'{24 if i % 24 == 0 else i}'), 
                                        font='Arial 20 bold', justify=CENTER, fill='white', tag='gmtNumber')
            else:   
                self.canvas.create_line(x1, y1, x2, y2, width=5, fill='white', capstyle='round', tag='gmtNumber')
        
        
    ## Converte coordenadas polares, trabalhadas em trigonometrica e ângulos, 
    # em coordenadas de plano cartersianas
    # @param angle ângulo do descolamento
    # @param radius raio do círculo
    # @return Retorna uma tupla com as coordenadas x e y nessa ordem.
    def polar2Cartesian(self, angle, radius=1):
        angle -= pi/2       # É subtraído 90° para que a coordenada de 0° coincida com a hora 0 ou 12/24
        radius = self.new_value * radius
        x = radius * cos(angle)
        y = radius * sin(angle)
        return (x, y)
    
    
    ## Função para desenhar os ponteiros do relógio.
    # @param angle ângulo de deslocamento desde o grau 0°
    # @param len tamanho do ponteiro, sen 1 a borda do relógio
    # @param wid largura, ou grossura, do ponteiro
    # @param color cor do ponteiro
    def drawHandle(self, angle, len, wid=None, color='black', outline=False, extend=False, gmt=False) :
        x, y = self.polar2Cartesian(angle, len)
        x += self.center[0]
        y += self.center[1]
        
        x_start = self.center[0]
        y_start = self.center[1]
        
        if outline:
            x_start, y_start = self.polar2Cartesian(angle, 0.1)
            x_start += self.center[0]
            y_start += self.center[1]
            
            # desenha o acabamento
            self.canvas.create_oval((self.center[0] + self.new_value*0.04), (self.center[1]+ self.new_value*0.04), (self.center[0] - self.new_value*0.04), 
                                    (self.center[1] - self.new_value*0.04), fill='white', tag='handle')

            # Desenha a base do ponteiro
            self.canvas.create_line(self.center[0], self.center[1], x_start, y_start, tag = 'handle', fill='white', 
                                    width=wid*0.3, capstyle='round')
            
            # Desenha o contorno
            self.canvas.create_line(x_start, y_start, x, y, tag = 'handle', fill='white', width=wid, capstyle='round')
            self.canvas.create_line(x_start, y_start, x, y, tag = 'handle', fill=color, width=wid*0.6, capstyle='round')
        else:
            
            # desenha o acabamento
            self.canvas.create_oval((self.center[0]+self.new_value*0.03), (self.center[1]+self.new_value*0.03), (self.center[0]-self.new_value*0.03), 
                                    (self.center[1]-self.new_value*0.03), fill=color, tag='handle')
            if extend:
                x_start, y_start = self.polar2Cartesian(angle, -0.1)
                x_start += self.center[0]
                y_start += self.center[1]
                
                # desenha a parte contrária do ponteiro de segundos    
                self.canvas.create_line(self.center[0], self.center[1], x_start, y_start, tag = 'handle', fill=color, 
                                        width=wid, capstyle='round')    
        
            
            # Desenha o ponteiro    
            self.canvas.create_line(self.center[0], self.center[1], x, y, tag = 'handle', fill=color, width=wid, 
                                    capstyle='round')
            
            if gmt:    
                self.canvas.create_oval((x + 10), (y + 10), (x - 10), (y - 10), fill=color, tag= 'handle')
                self.canvas.create_oval((x + 6), (y + 6), (x - 6), (y - 6), fill='white', tag= 'handle')
                self.drawNumberGmt()

    ## Calcula as horas e desenha os ponteiros do relógio a partir do horário do sistema.
    # 
    def paintHandles(self):
        # Deleta os ponteiros existentes anteriormente e recria apenas os ponteiros para atualização do horário
        self.canvas.delete('handle')
        self.canvas.delete('day')
        
        
        
        # Calcula as horas e retorna em uma tupla, para o nosso horario, delta = -3
        d, h, m, s = datetime.timetuple(datetime.utcnow()+ timedelta(hours = self.delta))[2:6]

        
        oneMinute = pi / 30     # A cada 1 minuto, o ponteiro anda 6°
        fiveMinute = pi / 6     # A cada 5 minutos, ou uma hora, o ponteiro anda 30°
        
        d_angle = fiveMinute * 3
        x, y = self.polar2Cartesian(d_angle, 0.47)
        x += self.center[0]
        y += self.center[1]
        self.canvas.create_text(x, y, text=d, fill='#f99703', font='Arial 20 bold', justify=CENTER, tag='day')
        
        
        h = fiveMinute * (h + m / 60)
        m = oneMinute * (m + s / 60)
        s = oneMinute * s
        
        # Testa se o fuso horário foi escolhido pelo usuário, caso não, o ponteiro GMT não é desenhado
        if self.chosed:         
            self.drawHandle(self.utc_h, 0.76, 3, 'red', gmt=True)
            
        self.drawHandle(h, 0.5, 15, 'black', outline = True)
        self.drawHandle(m, 0.8, 15, 'black', outline = True)
        self.drawHandle(s, 0.85, 3, 'grey', extend = True)
        
        self.canvas.create_oval((self.center[0]+self.new_value*0.01), (self.center[1]+self.new_value*0.01), (self.center[0]-self.new_value*0.01), 
                                (self.center[1]-self.new_value*0.01), fill='black')
        
        

    
    ## Função que atualiza a cada 200ms para redesenhar os ponteiros e acompanhar o horário.
    def poll(self):
        self.paintHandles()
        self.root.after(200, self.poll)
        
## Inicia a janela e a classe clock para que o relógio funcione
# o mainloop() mantém a janela aberta até ela ser fechada
def main(): 
    root = Tk()
    root.geometry('600x600')
    c = Clock(root)
    
    mainloop()

if __name__ == '__main__':
    sys.exit(main())
    