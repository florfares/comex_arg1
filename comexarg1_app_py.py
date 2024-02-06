#!/usr/bin/env python
# coding: utf-8

# ## Librerias

# In[7]:

# !pip install dash # si la libreria no esta instalada
from dash import Dash, html, dcc, Input, Output
import plotly.express as px

#charming data
# !pip install dash_bootstrap_components
import dash_bootstrap_components as dbc
# import dash_html_components as html #The dash_html_components package is deprecated

import pandas as pd

# ## Design

# In[8]:


#Colours for graphs
colores=[
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf',  # blue-teal
    '#fecb52',
    '#00cc96'
]

## Theme of the App
app = Dash(__name__,  external_stylesheets=[dbc.themes.UNITED])
serve = app.server


# ## Contenido: graficos

# ### Intensidad Importadora

# In[9]:

lista_base_sectores=['wgt_mip97RRNN_AGRO.xlsx' , 'wgt_mip97RRNN_OTROS.xlsx' , 'wgt_mip97BT_TEXTILES.xlsx' , 
    'wgt_mip97BT_OTROS.xlsx' , 'wgt_mip97MT_AUTOMOTRIZ.xlsx' , 'wgt_mip97MT_INGENIERIA.xlsx' , 'wgt_mip97MT_PROCESOS.xlsx' , 
    'wgt_mip97HT_ELECTRONICO_Y_ELECTRICO.xlsx' , 'wgt_mip97HT_OTROS.xlsx', 'wgt_mip97PP.xlsx']

orden=[9,0,1,2,3,4,5,6,7,8]
lista_base_sectores=[lista_base_sectores[i] for i in orden] #ordenar los sectores
lista_base_sectores

url = 'https://github.com/florfares/comex_arg1/raw/main/data/'
df=pd.read_excel(url+lista_base_sectores[0])
df.index=[lista_base_sectores[0].replace('wgt_mip97','').replace('.xlsx','') for i in range(df.shape[0])] 
      #de esta forma genero una lista con la cantidad de obs necesarias (cant. de filas) para el indice con el nombre del sector. 
df
lista_base_sectores[1:]

for i, elem in enumerate(lista_base_sectores[1:]): #que haga el loop desde la segunda observaciones - recordar la pri. posicion en python es 0
    df_aux=pd.read_excel(url+lista_base_sectores[1:][i])
    print(elem, i)
    df_aux.index=[elem.replace('wgt_mip97','').replace('.xlsx','') for i in range(df_aux.shape[0])] 
    df=pd.concat([df, df_aux])
    
df.index.name='sector'  
df.rename(columns={'Unnamed: 0':'ag'}, inplace=True)
df


# ### Composición del comercio exterior

# In[10]:

df_indec=pd.read_excel(url+'indec.xlsx') #levantar base
df_indec.iloc[:4,:] #ver encabezado para decidir que borrar
df_indec.iloc[1,0]='fecha' #agregar referencia para no eliminarla en el siguiente paso

df_indec1=df_indec.loc[:,df_indec.iloc[1,:].notna()] #quedarme con las columnas que me interesan
df_indec1.set_index('Fecha', inplace=True)
df_indec1.columns=[df_indec1.iloc[1,:]]
df_expo=df_indec1.iloc[2:,:10] #crear base expo
df_impo=df_indec1.iloc[2:,10:20] #crear base impo

#acomodar variables
lista_bases=[df_expo, df_impo]

for i,b in enumerate(lista_bases):
    lista_bases[i].columns=[x for x in df.index.get_level_values('sector').unique()] #nombrar columnas
    lista_bases[i]=b.melt(ignore_index=False).reset_index() #reshape wide to long
    lista_bases[i]['Fecha']=lista_bases[i]['Fecha'].astype(int)
    lista_bases[i].columns=['Fecha','sector','USD'] #volver a nombrar columnas
    lista_bases[i].USD=lista_bases[i].USD.astype(float)
    
#unificar bases
lista_bases[0]['Flujo']='Expo'
lista_bases[1]['Flujo']='Impo'
base=pd.concat([lista_bases[0], lista_bases[1]])
base


lista_sectores=[x for x in df.index.get_level_values('sector').unique()] #para ordenar sectores en el gráfico
dict_order=dict(zip(lista_sectores, lista_sectores))
dict_order

## Componente de la APP
compo_fig = px.bar(base,
         x='USD', y='sector',
         color='Flujo',
         title="Composición sectorial de los flujos comerciales",
         template="simple_white", color_discrete_sequence=colores,
         labels={'sector':''},
         barmode='group', 
         animation_frame="Fecha", animation_group="sector", category_orders=dict_order, range_x=[0,40000])


# ### Evolución del comercio exterior

# In[11]:


## componentes de la APP
#trade_dropdown = 

#graph
sector='PP'
base_sector=base[base.sector==sector]
trade_fig = px.bar(base_sector,
                           x='Fecha', y='USD',
                           color='Flujo',
                           title="Valor exportado e importado en Millones de USD corrientes",
                           template="simple_white", color_discrete_sequence=colores,
                           labels={'FECHA':''}, 
                           barmode='group')


# In[ ]:





# ### Provincias

# In[12]:


# cargar base

df_indec_prov=pd.read_excel(url+'indec.xlsx', sheet_name='hoja2') #importo base
df_indec=df_indec_prov.iloc[1:,:]
df_indec['FECHA']=df_indec['FECHA'].astype(int)
df_indec=df_indec.set_index('FECHA')

#generar multiindex
multi_index=pd.DataFrame(list(zip(df_indec_prov.columns, df_indec_prov.iloc[0,:])))
multi_index=multi_index.iloc[1:,]
multi_index.columns=['Provincia', 'Destino'] #nombrar col
# multi_index['Provincia'].to_string() #para asegurarme que sea un string

#debo quitar los .NN que aparecen al final del nombre de cada prov
import re
def cleaner(string):
    return re.sub(r'.\d\d|.\d', '', str(string))

multi_index.loc[:,'Provincia']=multi_index['Provincia'].map(cleaner)

eliminar_provincias=multi_index[multi_index['Provincia'].str.contains(r'[tT]otal|Continental|Indeterminado|Extranjero')==True].Provincia.unique() 
    #armo una lista de las provincias que quiero eliminar, todas aquellas que contienen los siguientes strings: total, Total o totales, Indeterminado, Continental, Extranjero.
eliminar_provincias=list(eliminar_provincias)

#indexar las columnas
df_indec.columns=pd.MultiIndex.from_frame(multi_index)
df_indec
#pasar wide to long
df_prov_long=df_indec.melt(ignore_index=False).reset_index()
df_prov=df_prov_long.set_index(['Provincia','Destino'])
df_prov.drop(eliminar_provincias, axis=0, inplace=True) 


## componentes de la App
#prov_dropdown = 

#graph


# ### Tabla provincias

# In[13]:


df_prov_prc=df_prov[df_prov['FECHA']>2011].groupby(['Provincia']).sum()
tabla_prc=df_prov_prc.apply(lambda g: g / g.sum()).sort_values(by='value',ascending=False)  #creando porcentajes
tabla_prc.drop('FECHA', axis=1, inplace=True) #eliminando la columna fecha
tabla_prc['value']=tabla_prc['value']*100 #generando porcentajes


tabla_prc['value']=tabla_prc['value'].astype(float).round(1)
tabla_prc.columns=['%']
tabla_1=tabla_prc.iloc[:12,:]
tabla_2=tabla_prc.iloc[13:,:]

## componente de la App
table_prov1 = dbc.Table.from_dataframe(tabla_1, striped=True, bordered=True, hover=True, index=True)
table_prov2 = dbc.Table.from_dataframe(tabla_2, striped=True, bordered=True, hover=True, index=True)


# In[14]:


## componente de la App mapa
mapa=dbc.NavItem(
            dbc.NavLink(
                "Mapa de Argentina obtenido del Ministerio de Defensa (IGN)",
                href="https://mapa.ign.gob.ar/?zoom=5&lat=-34.7285&lng=-59.7217&layers=argenmap,provincia_FA003",
                external_link= 'True',
                target='_blank', style={'background-color': '#FF6500', 'color':'White', 'text-align': 'center', 'marginTop': 10, 'marginBottom': 15}
            )
        )


# ### Empresas

# In[15]:
#cargar base de datos
df_indec_empresas=pd.read_excel(url+'indec.xlsx', sheet_name='hoja3') #importo base
df_indec_empresas=df_indec_empresas.iloc[:,1:8] #selecciono
df_group_año=df_indec_empresas.groupby(['año']).sum() #agrupo
df_empresas=df_group_año.melt(ignore_index=False).reset_index() #reshapeo wide to long
df_empresas.columns=['fecha','sector','cantidad']

#figura
empresas1_fig = px.line(df_empresas, x="fecha", y="cantidad", 
                        title='Cantidad de empresas exportadoras por sectores (1996-2018)',
                        color='sector', 
                        template="simple_white", color_discrete_sequence=colores, 
                        labels={'cantidad':'Cantidad', 'fecha':'Fecha', 'sector':'Sector'}, 
                        range_x=[1996,2018], markers=True)


# In[16]:


delta=df_empresas.groupby(['sector'], as_index=False).pct_change()
df_empresas['delta']=delta['cantidad'].round(2)*100

## componente de la App
empresas2_fig = px.bar(df_empresas,
         x='delta', y='sector',
         color='sector',
         title="Tasa de crecimiento de la cantidad de empresas",
         template="simple_white", color_discrete_sequence=colores,
         labels={'sector':'', 'delta':'% de crecimiento', 'fecha':'Fecha'},
         barmode='group', 
         animation_frame="fecha", animation_group="sector", range_x=[-40,40])


# ## Contenido: texto

# In[17]:


texto_intro='''
## Intro
En este documento se exploran y discuten algunas estadísticas relacionadas al comercio exterior argentino de las últimas décadas 📊.

La curiosidad por este tema surgió durante el desarrollo de mi tesis de maestría (versión publicada Fares y Zack, 2023), donde intenté identificar qué factores se encontraban detrás de las *performance* de los flujos de comercio exterior, tanto a nivel agregado como desagregado.

En efecto, se encuentran grandes heterogeneidades entre los determinantes del comercio a medida que pasamos del análisis macro al micro. Aunque utilizar datos a nivel de firmas sería fenomenal, no existen estadísticas oficiales que nos permitan ver estos comportamientos. Además algunos autores, como Goldstein y Khan (1985), mantienen algunas reservas con el empleo de datos muy desagregados (problemas de identificación, errores de medición, discontinuidades temporales, etc.).

Este documento comienza con la evolución del balance comercial por distintos rubros de productos basados en la clasificación elaborada por Lall (2000):

-   Productos primarios (PP): Fruta fresca, carne, arroz, cacao, té, café, madera, carbón, petróleo crudo, gas

-   Manufacturas basadas en Recursos Naturales (RR.NN.):

    -   Basadas en el agro: Carnes/frutas preparadas, bebidas, productos de madera, aceites vegetales

    -   Otras: Concentrados de mineral, productos de petróleo/caucho, cemento, gemas talladas, vidrio

-   Manufacturas de contenido tecnológico bajo (BT):

    -   Textiles: Tejidos, confección, sombrerería, calzado, marroquinería, artículos de viaje

    -   Otras: Cerámica, piezas/estructuras metálicas sencillas, muebles, joyería, juguetes, productos de plástico

-   Manufacturas de contenido tecnológico medio (MT):

    -   Automotriz: Vehículos de pasajeros y piezas, vehículos comerciales, motocicletas y piezas

    -   Procesos: Fibras sintéticas, productos químicos y pinturas, fertilizantes, plásticos, hierro, tuberías/tubos

    -   Ingeniería: Motores, maquinaria industrial, bombas, conmutadores, barcos, relojes

-   Manufacturas de contenido tecnológico alto (HT):

    -   Electrónicos y eléctricos: Motores, maquinaria industrial, bombas, conmutadores, barcos, relojes

    -   Otras: Industria farmacéutica, aeroespacial, instrumentos ópticos y de medición, cámaras fotográficas

Luego, se muestra cómo han evolucionado la cantidad de empresas exportadoras (en grandes rubros) y cómo se compone sectorialmente la demanda de importaciones para cada rubro mencionado.

Por último, muestro cómo se compone territoralmente la canasta exportadora y cómo evolucionaron las ventas externas por provincia y destino.

La idea de este documento es explorar las distintas librerias que permiten la interacción con el usuario, de manera tal que los gráficos permitan seleccionar/deseleccionar series y/o cambiar de sectores en la barra desplegable. Estas son las herramientas utilizadas :

-   Dash

-   Plotly

Mis fuentes de datos se acotan a las estadisticas oficiales publicadas por el Instituto Nacional de Estadísticas y Censos de Argentina ([INDEC](https://www.indec.gob.ar/indec/web/Nivel3-Tema-3-2)). Para trabajar con la demanda importadora, además, empleé las matrices de insumo-producto (1997), lo cual supuso un desafio adicional en términos de la manipulación de datos y construcción de indicadores. En mi [GitHub](https://github.com/florfares/importintensity) hay un repo con una notebook sobre el tema.

Disfrutalo y, si tenes alguna duda, ¡escribime! 📩

Más misceláneas en [mi web](https://sites.google.com/view/florenciafares/) 📍
'''


# In[18]:


texto1_sec1='''
## Evolución de los flujos comerciales

El marco temporal del análisis en está sección se acota al periodo 1995-2016. A pesar de que solo involucra 20 años, la evolución de la macroeconomía argentina ha sido muy heterogenea. La serie arranca con el segundo ciclo de la convertibilidad (1995-2001), un modelo basado en la liberalización de los flujos de capitales y del comercio, una moneda más bien apreciada y una economía que empezaba a mostrar signos de debilidad. En 2001/2002 se produce una profunda crisis económica, social y política. Entre 2003-2008 la economía se recupera, lo cual se refleja en menores niveles de desempleo, pobreza y desigualdad y un gran crecimiento de los salarios reales. A partir de 2011, estas dinámicas se agotan y la economía empieza a mostrar signos de estancamiento, sin lograr retomar una trayectoria de crecimiento sostenible.

Los flujos de comercio reflejan claramente estas dinámicas. En general, uno observa que los sectores de mayor contenido tecnológico suelen ser estructuralmente deficitarios, mientras que los sectores primarios son altamente superavitarios. Solo el año 2002 se observa un comportamiento muy atípico, por la gran caida de los flujos de importaciones, explicado por la profunda crisis económica. La recuperación de la actividad económica doméstica implica siempre una mayor demanda de importaciones, como muestran los periodos subsiguientes. Sin embargo, si las exportaciones no crecen en la misma medida, esta dinámica se vuelve problemática a largo plazo. Por eso, es necesario impulsar el crecimiento económico sustentado en la expansión de la oferta transable.
'''

texto2_sec1='''
En el siguiente gráfico es más fácil observar el impacto del ciclo económico sobre la evolución del balance comercial a nivel sectorial. Por ejemplo, el sector de Recursos Naturales: Otros, donde se encuentran los energías y combustibles, suele ser superavitario en los periodos de baja actividad económica y se vuelve deficitario con la expansión doméstica. Algo similar sucede con el sector textil.'''


# In[19]:


texto1_sec2='''
## ¿Quiénes demandan y quiénes compran?
En esta segunda sección, te muestro la evolución de la cantidad de empresas exportadoras y la composición que tiene la demanda de importaciones en Argentina. En el primer caso, los datos disponibles me limitaron para mantener la desagregación por contenido tecnológico, y los datos sobre la demanda de importaciones se corresponden con la matriz insumo-producto de 1997. Si bien existen algunas versiones más recientes de la matriz producidas por la CEPAL e ICIO, son extrapolaciones realizadas por investigaciones independientes ya que el gobierno argentino no ha vuelto a actualizar los datos oficiales. Cuando se observa la composicion sectorial, como en el apartado anterior, es evidente que no hubo grandes cambios estructurales para ninguno de los flujos. Esto me lleva a suponer que tampoco lo hubo entre los demandantes de importaciones, más no es posible probarlo. Por esto, me parece necesario que se actualicen estos datos ya que son una foto de las transacciones intra e intersectoriales de la economia en su conjunto.

Por otro lado, trabajar con matrices insumo-producto permite computar no solo la demanda directa de importaciones (por ejemplo, una persona que vive en Argentina e importa un libro), sino también la indirecta (por ejemplo, una firma argentina que importa insumos para producir un bien o servicio que tiene como destino al consumidor final). Esto requiere de un manejo específico sobre matrices y sus transformaciones. Mi trabajo se basó en lo realizado por Bussière **et al.** (2013), por si queres consultarlo.

El siguiente gráfico permite observar la evolución temporal de la cantidad de empresas exportadoras argentina. La industria manufacturera resalta a simple vista. Sin embargo, no debemos dejarnos engañar por las escalas, porque si bien se observa un fuerte crecimiento entre 2003-2008, esto podría verse afectado por el nivel base de comparación.

(Comentario: si querés clickea sobre la legenda para seleccionar y deseleccionar las series.)'''

texto2_sec2='''
Como destaca el siguiente gráfico, ahora es más evidente que la tasa de crecimiento de las empresas exportadoras (es decir, el porcentaje de incremento de la cantidad de empresas exportadoras cada año -ojo, si es negativo significa que hay empresas que dejan de exportar) es mucho más pareja entre los sectores. El nivel nos estaba engañando en el gráfico anterior.

Entre 2004-2008 se mantienen las tasas positivas de crecimiento en todos los sectores, y lo contrario sucede desde 2013 en adelante. El declive que se observa en el gráfico anterior al final del periodo corresponde al 2018. Aquí es evidente la estrepitosa del crecimiento exportador en todos los sectores.
'''

texto3_sec2='''
Veamos ahora los datos sobre la demanda de importaciones. La idea es contestar, ¿para qué importamos los argentinos? ¿con qué fin demandamos los distintos productos importados? Para eso, analicé la demanda de las importaciones por componentes de la demanda agregada: Consumo privado (C), Inversión privada (I), Gasto público (G) y las Exportaciones (X). Como se observa nuevamente, existe una gran heterogeneidad en el destino de las importaciones, pero es evidente la predominancia de las exportaciones y la inversión. Muchos productos importados son utilizados por los sectores exportadores, por lo cual, esto abre nuevas preguntas sobre los efectos que pueden tener las politicas de control de las importaciones. ¿Podría este tipo de medidas perjudicar a las firmas exportadoras ya que no pueden hacerse de los insumo necesarios para su producción?'''


# In[20]:


texto1_sec3='''
Finalmente, me gustaría poner en relieve la dimension espacial de nuestras exportaciones. Si no conoces Argentina geográficamente, aquí debajo te dejo un mapa. Si tuviera que describir rápidamente la dimensión economico espacial del pais, diría que gran parte de la actividad industrial se concentra en la zona pampeana. Aquí también se localizan las tierras fértiles que hicieron famosa a la Argentina a principios del siglo pasado. Más recientemente, el avance tecnológico ha permitido que la actividad agropecuaria se desplace a otras zonas, en ambas direcciones, al norte y al sur de las pampas.
'''
texto12_sec3=''' 
 
La tabla a la derecha muestra la participación de cada provincia en el acumulado del valor exportado de los últimos 10 años. El grueso de las ventas externas se concentra en Buenos Aires, Santa Fe y Cordoba, lo cual no resulta para nada llamativo, ya que estas provincias conforman la zona pampeana.
'''

texto2_sec3='''
Al explorar los socios comerciales, existe cierta heterogeneidad asociada al tipo de productos que exporta cada provincia, y por lo tanto, también en referencia a los destinos. Sin embargo, algunos nombres se repiten: Brasil, China, Estados Unidos, y otros paises de la región. Esto destaca la importancia que tienen las relaciones comerciales con estos paises y lo relevantes que son para las economias regionales. Luego de los estudios que realicé, no cabe duda de que Argentina necesita no solo diversificar su canasta exportadora, sino también ampliar el abanico de socios comerciales, sin que esto repercuta negativamente en los destinos que ya conoce. Debemos exportar más y llegar más lejos.
'''


# In[21]:


texto_conclu='''
## Comentarios finales
En definitiva, en este documento descriptivo intenté mostrar cómo ha sido la evolución reciente del comercio exterior argentino, su composición sectorial y territorial. Creo que hay mucho espacio para la mejora en este sentido y hoy es el momento de definir las reglas que nos van a permitir crecer de manera sostenible.

Particularmente, siempre me gustaron los tópicos relacionados al sector externo. En mis inicios en la investigación, realicé una estimación de los precios de las exportaciones e importaciones a niveles desagregados por tipos de productos y luego, avancé con la estimación de las elasticidades del comercio exterior. En @fares_sectoral_2020 pueden encontrar la metodología que empleé para calcular los indices de valor unitario, que, por cierto, es el único trabajo que ha provisto de esta importante información estadística ya que no hay datos oficiales.

Los desafios asociados al sector externo siempre me han parecido un tema desafiante y más que relevante para mi pais. Hoy en día en mi curso de Análisis Económico Aplicado tratamos estos temas. No solo revisamos los avances teóricos sobre la estimación de indices de valor unitario, las elasticidades del comercio exterior, las crisis de balanza de pagos y, más en general, las estadisticas del sector externo, sino que además trabajamos en Stata con los .do files para ver "la cocina" de los trabajos académicos. Creo que de esa forma contribuyo a que más personas se acerquen a la investigación, o más bien, que la disciplina muestre todo lo que puede aportar a las discusiones que deben darse en la sociedad.

Si te gustó esta publicación, podes reaccionar o compartirla en [LinkedIn](https://www.linkedin.com/in/florencia-m-fares/), asi gana mayor visibilidad!

Si te interesa conocer el código detrás de los gráficos, pronto lo voy a estar subiendo en mi [GitHub](https://github.com/florfares)!

Gracias por leerme ;)'''


# In[22]:


texto_biblio='''
## Bibliografía

* Bussière, Matthieu, Giovanni Callegari, Fabio Ghironi, Giulia Sestieri, y Norihiko Yamano. 2013. «Estimating trade elasticities: Demand composition and the trade collapse of 2008-2009». *American economic Journal: macroeconomics*, 5 (3): 118-51.
* Fares, Florencia Melisa, y Guido Zack. 2023. «Influence of demand and supply factors on trade flows: Evidence for Argentina (1996–2016)». *Metroeconomica*, octubre, 1-64. [https://doi.org/10.1111/meca.12450](https://doi.org/10.1111/meca.12450).
* Fares, Florencia Melisa, Guido Zack, y Ricardo Gabriel Martinez. 2020. «Sectoral price and quantity indexes of Argentine foreign trade». *Lecturas de Economía*, n.º 93: 297-328. [https://doi.org/https://doi.org/10.17533/udea.le.n93a338277](https://doi.org/https://doi.org/10.17533/udea.le.n93a338277).
* Goldstein, Morris, y Mohsin S Khan. 1985. «Income and price effects in foreign trade». En *Handbook of international economics*, R. W. Jones & P. B. Kenen (Eds.), 2:1041-1105. Amsterdam: North-Holland: Elsevier.
* Lall, Sanjaya. 2000. «The Technological structure and performance of developing country manufactured exports, 1985‐98». *Oxford development studies*, 28 (3): 337-69. [https://doi.org/https://doi.org/10.1080/713688318](https://doi.org/https://doi.org/10.1080/713688318).

'''


# ## App

# In[23]:


## layout
app.layout=dbc.Container([
                dbc.Row([ 
                    dbc.Col(dcc.Markdown('''
                    # Comercio exterior en Argentina
                    Creado por Florencia M. Fares en febrero de 2024
                    '''),
                            width=12, style={'background-color': '#FF6500', 'color':'White', 'text-align': 'center'} 
                           )
                ]),   
                dbc.Row([ 
                    dbc.Col(dcc.Markdown(texto_intro),
                            width=12, style={'text-align': 'justify'}
                           )
                ]),   
                dbc.Row([
                    dbc.Col(dcc.Markdown(texto1_sec1), 
                            width=12, style={'text-align': 'justify'}
                         )
                         
                ]),
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id="compo-graph", figure=compo_fig)
                    ],  width=12)
                ]),   
                dbc.Row([
                    dbc.Col(dcc.Markdown(texto2_sec1), 
                            width=12, style={'text-align': 'justify'}
                         )
                         
                ]),   
                dbc.Row([ 
                    dbc.Col([
                        dcc.Dropdown(id='dd_trade', options=base['sector'].unique(),value='PP'),
                        dcc.Graph(id="trade-graph", figure={})
                    ],  width=12)
                ]),   
    
                dbc.Row([
                    dbc.Col(dcc.Markdown(texto1_sec2), 
                            width=12, style={'text-align': 'justify'}
                         )
                         
                ]),
       
                dbc.Row([ 
                    dbc.Col([
                        dcc.Graph(id="empresas1-graph", figure=empresas1_fig)
                        
                    ],  width=12)
                ]),   
    
                dbc.Row([
                    dbc.Col(dcc.Markdown(texto2_sec2), 
                            width=12, style={'text-align': 'justify'}
                         )
                         
                ]),   
    
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id="empresas2-graph", figure=empresas2_fig)
                        
                    ],  width=12)
                
                
                ]),   
    
                dbc.Row([
                    dbc.Col(dcc.Markdown(texto3_sec2), 
                            width=12, style={'text-align': 'justify'}
                         )
                         
                ]),   
    
                dbc.Row([ 
                    dbc.Col([
                        dcc.Dropdown(id='dd_impo', options=df.index.get_level_values('sector').unique(), value='PP'),
                        dcc.Graph(id="impo-graph", figure={})
                        
                    ],  width=12)
                
                
                ]),
       
                dbc.Row([
                    dbc.Col(dcc.Markdown('''
                                ## ¿Desde dónde y hacia dónde exportamos?
                                '''), 
                            width=12, style={'text-align': 'justify'}
                         )

                         
                ]),
                dbc.Row([ 
                        dbc.Col([dcc.Markdown(texto1_sec3),
                                mapa,
                                dcc.Markdown(texto12_sec3)], 
                            width=4, style={'text-align': 'justify', 'marginTop': 10, 'marginBottom': 10}
                         ),
                    
                        dbc.Col(table_prov1, width=4),
                        dbc.Col(table_prov2, width=4)
                ]),
    
                dbc.Row([
                    dbc.Col(dcc.Markdown(texto2_sec3), 
                            width=12, style={'text-align': 'justify'}
                         )
                         
                ]),
    
                dbc.Row([ 
                    dbc.Col([
                        dcc.Dropdown(id='dd_prov',options=df_prov.index.get_level_values('Provincia').unique(), value='Chaco'),
                        dcc.Graph(id="prov-graph", figure={})
                    ],  width=12)
                ]),
    
                dbc.Row([
                    dbc.Col(dcc.Markdown(texto_conclu), 
                            width=12, style={'text-align': 'justify'}
                         )
                         
                ]),
    
                dbc.Row([
                    dbc.Col(dcc.Markdown(texto_biblio), 
                            width=12, style={'text-align': 'justify'}
                         )
                         
                ])
    
])

##callbacks
#Trade
@app.callback(
    Output(component_id='trade-graph', component_property='figure'),
    Input(component_id='dd_trade', component_property='value')
)

def update_trade_graph(sector):
    base_sector=base[base.sector==sector]
    trade_fig = px.bar(base_sector,
                       x='Fecha', y='USD',
                       color='Flujo',
                       title="Valor exportado e importado en Millones de USD corrientes",
                       template="simple_white", color_discrete_sequence=colores,
                       labels={'FECHA':''}, 
                       barmode='group')
    return trade_fig

# #impo graph
@app.callback(
    Output(component_id='impo-graph', component_property='figure'),
    Input(component_id='dd_impo', component_property='value')
)

def update_impo_graph(sector):
    df_sector=df[df.index==sector]
    impo_fig = px.pie(df_sector,
                           values='wgt', names='ag',
                           color='ag',
                           title='Demanda importadora de '+sector+' por componente de la DA',
                           template="simple_white", color_discrete_sequence=colores)
    return impo_fig

# #prov graph
@app.callback(
    Output(component_id='prov-graph', component_property='figure'),
    Input(component_id='dd_prov', component_property='value')
)

def update_prov_graph(provincia):
    base_prov=df_prov.loc[[provincia]]
    prov_fig = px.line(base_prov,
                           x='FECHA', y='value',
                           color=base_prov.index.get_level_values('Destino'),
                           title="Valor exportado desde {} en Millones de USD corrientes".format(provincia),
                           template="simple_white", color_discrete_sequence=colores,
                           labels={'FECHA':'Fecha','value':'USD', 'color':'Socio comercial'})
    return prov_fig

##launch the app

if __name__=='__main__':
     app.run_server(debug=True)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




