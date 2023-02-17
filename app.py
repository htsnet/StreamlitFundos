import streamlit as st
import re
import time

with st.sidebar:
    st.header('Guia de uso')
    st.write('1 - Cole na caixa ao lado a lista dos identificadores de seus fundos (ex. VINO11) separados por vírgula, espaço ou enter.')
    st.write('2 - Aperte o botão para executar a pesquisa e aguarde.')
    st.write('3 - Será apresentado um quadro com um resumo simples de cada fundo e um link para a fonte.')
        
    st.header('Sobre')
    st.write('Os detalhes e o código fonte sobre este projeto podem ser encontrados em https://github.com/htsnet/StreamlitFundos')
    st.write('As informações são obtidas através do site https://www.fundsexplorer.com.br/')
    
# título
Title = f'Buscador de Informações sobre Fundos no Mercado Financeiro'
st.title(Title)

text_base = ''

text = st.text_area("Cole a lista de códigos de fundo na caixa abaixo", value=text_base, max_chars=4000, height=400, key='text_area_field')


def check_text(text):
    if text:
        return True
    st.warning('A caixa de textos está vazia!', icon="⚠️")
    return False

def ajustaEntrada(text):
    auxiliar = text.replace(",", "#")
    auxiliar = auxiliar.replace(" ", "#")
    auxiliar = auxiliar.replace("\n", "#")    
    return auxiliar.split("#")

st.write('Busca das informações')
botSummary = st.button("Executar")
if botSummary:
    if check_text(text):
        with st.spinner('Tome um café enquanto aguarda o resultado...'):
            listaTotal = ajustaEntrada(text)
            listaUnica = list(dict.fromkeys(listaTotal))
            st.info('Foram identificados ' + len(listaUnica) + ' fundos distintos.')
        
                