import streamlit as st
import time
from time import sleep
import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import html

# ver emojis em https://emojipedia.org/coin/

st.set_page_config(page_title='Informações sobre Fundos Imobiliários', 
                   page_icon=':moneybag', layout='centered', initial_sidebar_state='expanded' )

#para esconder o menu do próprio streamlit 
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
#buscador-de-informa-es-sobre-fundos-imobili-rios-no-mercado-financeiro {padding: 0rem 0px 1rem !important;}
</style>
"""
# passa javascript e estilos
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def main():
    with st.sidebar:
        st.header('Guia de uso')
        st.write('1 - Cole na caixa ao lado a lista dos identificadores (ticker) de seus fundos imobiliários (ex.: VINO11, HSML11) separados por vírgula, espaço ou enter. Códigos duplicados serão automaticamente removidos.')
        st.write('2 - Aperte o botão para executar a pesquisa e aguarde.')
        st.write('3 - Será apresentado um quadro com um resumo simples de cada fundo e um link para a fonte.')
        st.write('4 - Para facilitar uma nova consulta dos mesmos fundos, ao retornar ao site o texto já estará preenchido com sua última informação. Você pode manter os códigos ou modificar à vontade.')
            
        st.header('Sobre')
        st.write('‼️ ⚠️ Projeto em elaboração! Confira as informações para certificação dos dados.')
        st.write('Os detalhes e o código fonte sobre este projeto podem ser encontrados em https://github.com/htsnet/StreamlitFundos')
        st.write('As informações são obtidas através do site https://www.fundsexplorer.com.br/')
        
    # título
    Title = f'Buscador de Informações sobre Fundos Imobiliários no Mercado Financeiro'
    st.title(Title)
    st.subheader('Uma forma de se avaliar rapidamente alguns parâmetros básicos de fundos imobiliários')

    text_base = 'VINO11, HSML11, '
    # se tem texto anterior 
    if 'texto_anterior' in st.session_state:
        text_base = ''
        #verifica
        for i in st.session_state.texto_anterior:
            text_base = text_base + " " + i

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
        # guarda conteúdo para próxima execução
        st.session_state.texto_anterior = final
        return final

    def pegaResultado(valor):
        if valor:
            return valor.replace('\n', '')
        else:
            return None
        
    progress_text = "Iniciando..."
    qtde_ok = 0
    percent = 0.0

    containerSuperior = st.expander('Lista de Tickers', expanded=True)
    with containerSuperior:
        # text = st.text_area("Cole a lista de códigos de fundo (ticker) na caixa abaixo", 
        #                     value=text_base, key='fieldText', max_chars=1000, height=100)
        # botSummary = st.button("Executar a busca das informações")   
        
        #agrupando em um formulário para assumir o texto mesmo sem ENTER
        with st.form('Meu formulário'):
            text = st.text_area("Cole a lista de códigos de fundo (ticker) na caixa abaixo", 
                            value=text_base, key='fieldText', max_chars=1000, height=100)
            botSummary = st.form_submit_button("Executar a busca das informações")   

    if botSummary:
        if check_text(text):
            with st.spinner('Tome um café enquanto aguarda o resultado... 😉'):
                
                listaTotal = ajustaEntrada(text)
                listaUnica = list(dict.fromkeys(listaTotal))
                totalCodigos = len(listaUnica)
                st.info('Foram identificados ' + str(len(listaUnica)) + ' fundos distintos.')
                # st.write(str(listaUnica))
                
                # Define a tabela com as colunas
                table = PrettyTable()
                table.field_names = ['Título', 'Último rendimento', 'Dividend Yield', 'Rentabilidade no mês', 'P/VP']
                table.align['Ticker'] = "r"
                table.align['Último rendimento'] = "r"
                table.align['Dividend Yield'] = "r"
                table.align['Rentabilidade no mês'] = "r"
                table.align['P/VP'] = "r"
                # table.align['Variação 12 meses'] = "r"
                
                progress_text="Execução em andamento..."
                my_bar = st.progress(0, text=progress_text)
                qtde_total = 0
                
                #fecha container de alguns elementos da tela
                st.session_state['is_expanded'] = False
                
                for i in listaUnica:
                    qtde_total += 1
                    percent = (1/totalCodigos)*qtde_total # calcula o % com base no total de códigos
                    if percent > 1:
                        percent = 1 
                    progress_text = i
                    # atualiza a barra de progresso
                    # st.write(percent)   
                    my_bar.progress(percent, text=progress_text)
                    
                    # Loop através de cada URL e buscar os campos desejados
                    url = 'https://www.fundsexplorer.com.br/funds/' + i
                    # st.write(url)

                    try:
                        # Solicitação HTTP para obter o conteúdo HTML da página
                        response = requests.get(url, timeout=30)
                        if response.status_code == 200:
                            
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
                                # variacao = soup.find_all('span', {'class': 'secondary-value'})
                                # st.write(divs)
                                # st.write(divs[1].get_text())
                                # # Imprima os campos da página atual
                                # st.subheader(f'Título {i}')
                                # st.write(f'Último rendimento: {divs[0].get_text()}')
                                # st.write(f'Dividend Yield: {divs[1].get_text()}')
                                # st.write(f'Rentabilidade no mês: {divs[4].get_text()}')
                                # st.write(f'P/VP: {divs[5].get_text()}')
                                table.add_row(['<a target="_blank" href="' + url + '"}>' + i + '</a>', # código e link 
                                            pegaResultado(divs[1].get_text()),  # último rendimento
                                            pegaResultado(divs[2].get_text()),  # dividend yield
                                            pegaResultado(divs[5].get_text()),  # rentabilidade no mês
                                            pegaResultado(divs[6].get_text())  # p/vp
                                            # pegaResultado(variacao[2].get_text()) # variação 12 meses
                                            ])
                                qtde_ok += 1
                            else:
                                st.write(f'Informações sobre o título {i} não foram encontradas.')    
                        else:
                            st.write(f'Não foi possível acessar a página do título {i}.') 
                    except requests.exceptions.RequestException as e:
                        st.write(f'Erro ao buscar o título {i}: {e}')
                    except Exception as e:
                        st.write(f'Erro ao extrair os campos da página {i}: {e}')
                
                    
                my_bar.progress(100, text="Finalizado")
                if qtde_ok > 0:
                    text = table.get_html_string(format=True)
                    text = html.unescape(text)
                    st.markdown(text, unsafe_allow_html=True)
                    st.success('Processamento concluído!')
                    st.balloons()
                else:
                    st.write('😒 Nenhuma informação foi obtida...')

                # remove da tela a barra de progresso
                my_bar.empty()
                
                # coloca botão para possibilitar recarregar a página
                # botRestart = st.button("Recarregar para nova pesquisa")
                # if botRestart:
                #     st.experimental_rerun()
                    
if __name__ == '__main__':
	main()                     