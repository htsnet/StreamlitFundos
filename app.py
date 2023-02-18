import streamlit as st
import re
import time
from time import sleep
import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable

with st.sidebar:
    st.header('Guia de uso')
    st.write('1 - Cole na caixa ao lado a lista dos identificadores de seus fundos imobiliários (ex.: VINO11, HSML11) separados por vírgula, espaço ou enter.')
    st.write('2 - Aperte o botão para executar a pesquisa e aguarde.')
    st.write('3 - Será apresentado um quadro com um resumo simples de cada fundo e um link para a fonte.')
        
    st.header('Sobre')
    st.write('‼️ ⚠️ Projeto em elaboração! Confira as informações para certificação dos dados.')
    st.write('Os detalhes e o código fonte sobre este projeto podem ser encontrados em https://github.com/htsnet/StreamlitFundos')
    st.write('As informações são obtidas através do site https://www.fundsexplorer.com.br/')
    
# título
Title = f'Buscador de Informações sobre Fundos Imobiliários no Mercado Financeiro'
st.title(Title)

text_base = ''

text = st.text_area("Cole a lista de códigos de fundo na caixa abaixo", value=text_base, max_chars=1000, height=150, key='text_area_field')


def check_text(text):
    if text:
        return True
    st.warning('A caixa de textos está vazia!', icon="⚠️")
    return False

def ajustaEntrada(text):
    auxiliar = text.replace(",", "#")
    auxiliar = auxiliar.replace(" ", "#")
    auxiliar = auxiliar.replace("\n", "#") 
    auxiliar = auxiliar.split("#")
    final = []
    for i in auxiliar:
        if i:
             final.append(i.upper())  
    final.sort()
    return final

def pegaResultado(valor):
    if valor:
        return valor.replace('\n', '')
    else:
        return None
      

# st.write('Busca das informações')
botSummary = st.button("Executar a busca das informações")
if botSummary:
    if check_text(text):
        with st.spinner('Tome um café enquanto aguarda o resultado... 😉'):
            listaTotal = ajustaEntrada(text)
            listaUnica = list(dict.fromkeys(listaTotal))
            st.info('Foram identificados ' + str(len(listaUnica)) + ' fundos distintos.')
            # st.write(str(listaUnica))
            
            # Define a tabela com as colunas
            table = PrettyTable()
            table.field_names = ['Título', 'Último rendim.', 'Dividend Yield', 'Rentab. no mês', 'P/VP', 'Link']
            table.align['Título'] = "r"
            table.align['Último rendim.'] = "r"
            table.align['Dividend Yield'] = "r"
            table.align['Rentab. no mês'] = "r"
            table.align['P/VP'] = "r"
            
            for i in listaUnica:
                # Loop através de cada URL e buscar os campos desejados
                url = 'https://www.fundsexplorer.com.br/funds/' + i
                # st.write(url)

                try:
                    # Solicitação HTTP para obter o conteúdo HTML da página
                    response = requests.get(url, timeout=30)
                    
                    # Usando o Beautiful Soup para analisar o HTML e encontrar os campos
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # print(soup.prettify())
                    
                    # Aguarda até que o elemento 'title' seja encontrado
                    element_found = None
                    element_not_found = None
                    start_time = time.time()
                    while not (element_found or element_not_found):
                        element_found = soup.find_all('span', {'class': 'indicator-value'})
                        element_not_found = soup.find('img', {'id': '#not-found>span'})

                        if not (element_found or element_not_found) :
                            time.sleep(0.5)
                            elapsed_time = time.time() - start_time
                            if elapsed_time > 20:
                                raise Exception('Timeout ao aguardar a página carregar')

                    # Extrai o campo da página
                    if element_found:
                        divs = soup.find_all('span', {'class': 'indicator-value'})
                        # st.write(divs)
                        # st.write(divs[1].get_text())
                        # # Imprima os campos da página atual
                        # st.subheader(f'Título {i}')
                        # st.write(f'Último rendimento: {divs[0].get_text()}')
                        # st.write(f'Dividend Yield: {divs[1].get_text()}')
                        # st.write(f'Rentabilidade no mês: {divs[4].get_text()}')
                        # st.write(f'P/VP: {divs[5].get_text()}')
                        table.add_row([i, 
                                       pegaResultado(divs[1].get_text()), 
                                       pegaResultado(divs[2].get_text()), 
                                       pegaResultado(divs[5].get_text()), 
                                       pegaResultado(divs[6].get_text()),
                                       url
                                       ])
                    else:
                        st.write(f'Informações sobre o título {i} não foram encontradas.')    
                    
                except requests.exceptions.RequestException as e:
                    st.write(f'Erro ao buscar o título {i}: {e}')
                except Exception as e:
                    st.write(f'Erro ao extrair os campos da página {i}: {e}')
                    
                sleep(5)
            st.write(table)