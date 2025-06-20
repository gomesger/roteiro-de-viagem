import streamlit as st
from datetime import datetime
import json
from pathlib import Path
import base64
import locale
import urllib.parse

try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')

st.set_page_config(page_title="Roteiro de Viagem", layout="wide")

page_bg_css = '''
<style>
html, body, [data-testid="stApp"], .main, #root {
    background-color: black !important;
    color: white !important;
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen,
      Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
}
header, footer {
    display: none;
}
.block-container {
    padding-top: 0rem !important;
    padding-bottom: 1rem !important;
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
}
label, .stTextInput label, .stDateInput label, .stTimeInput label, .stNumberInput label, .stTextArea label, .stRadio label {
    color: white !important;
}
.titulo-laranja {
    font-size: 36px;
    font-weight: bold;
    color: white;
    margin-bottom: 10px;
    text-align: center;
    margin-top: 0;
}
span.laranja {
    color: #FFA500;
    display: block;
    text-align: center;
}
a.botao-link {
    display: inline-block;
    padding: 10px 20px;
    background-color: #222222;
    color: white !important;
    text-decoration: none;
    border-radius: 5px;
    font-weight: bold;
    text-align: center;
    user-select: none;
    margin-bottom: 8px;
    width: 100%;
    box-sizing: border-box;
}
a.botao-link:hover {
    background-color: #FFA500;
    color: black !important;
}
.stButton button {
    background-color: #000000 !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: bold !important;
    padding: 10px 20px !important;
    user-select: none !important;
    border: none !important;
    transition: background-color 0.3s ease, color 0.3s ease;
    box-shadow: none !important;
    width: 100% !important;
    box-sizing: border-box;
    margin-bottom: 8px;
}
.stButton button:hover,
.stButton button:focus,
.stButton button:active {
    background-color: #FFA500 !important;
    color: black !important;
    box-shadow: none !important;
}
input[type="text"], textarea, input[type="time"], input[type="date"], input[type="number"] {
    width: 100% !important;
    box-sizing: border-box;
}
img {
    max-width: 150px;
    height: auto;
    border-radius: 8px;
    margin-bottom: 5px;
}
.titulo-expander {
    font-size: 20px !important;
    font-weight: bold !important;
    margin-bottom: 5px !important;
    color: white !important;
    user-select: none;
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
    margin-top: 10px;
}
.titulo-expander span.emoji {
    font-size: 24px !important;
    line-height: 1 !important;
}
@media (max-width: 768px) {
    .css-1lcbmhc.e1fqkh3o3 {
        flex-direction: column !important;
    }
}
</style>
'''
st.markdown(page_bg_css, unsafe_allow_html=True)

SAVE_PATH = Path("dados_roteiro.json")

def salvar_dados(dados):
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def carregar_dados():
    if SAVE_PATH.exists():
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

dados = carregar_dados()

def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()

if "editando_titulo" not in st.session_state:
    st.session_state.editando_titulo = "titulo_viagem" not in dados

if "dias" not in st.session_state:
    st.session_state.dias = dados.get("dias", [])

def encontrar_dia_por_data(data_str):
    for idx, dia in enumerate(st.session_state.dias):
        if dia["data"] == data_str:
            return idx
    return None

def adicionar_dia(data_str):
    if encontrar_dia_por_data(data_str) is None:
        st.session_state.dias.append({
            "data": data_str,
            "eventos": []
        })

def remover_dia(data_str):
    idx = encontrar_dia_por_data(data_str)
    if idx is not None:
        del st.session_state.dias[idx]

def adicionar_evento(dia_idx):
    st.session_state.dias[dia_idx]["eventos"].append({
        "hora": "08:00",
        "local": "",
        "descricao": "",
        "link": "",
        "foto_b64": None
    })

def remover_evento(dia_idx, evento_idx):
    if 0 <= dia_idx < len(st.session_state.dias):
        eventos = st.session_state.dias[dia_idx]["eventos"]
        if 0 <= evento_idx < len(eventos):
            del eventos[evento_idx]

# --- Título da Viagem ---
if st.session_state.editando_titulo:
    novo_titulo = st.text_input("Título da Viagem", value=dados.get("titulo_viagem", ""), key="input_titulo")
    if st.button("📏 Salvar Título"):
        dados["titulo_viagem"] = novo_titulo.strip()
        salvar_dados(dados)
        st.session_state.editando_titulo = False
        safe_rerun()
else:
    titulo_viagem = dados.get("titulo_viagem", "")
    st.markdown(f"""
    <div style='text-align: center;'>
        <h1 class='titulo-laranja'>✈️ Roteiro de Viagem:</h1>
        <h1 class='titulo-laranja'><span class='laranja'>{titulo_viagem}</span></h1>
    </div>
    """, unsafe_allow_html=True)
    st.button("✏️ Editar Título", on_click=lambda: st.session_state.update({"editando_titulo": True}), key="botao_editar_titulo")

# --- Trajeto de Ida ---
st.markdown("<div class='titulo-expander'><span class='emoji'>🚗</span><span>Trajeto de Ida</span></div>", unsafe_allow_html=True)
with st.expander("", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        origem = st.text_input("Origem", dados.get("origem", "Fazenda Rio Grande"))
        data_ida = st.date_input("Data de Ida", datetime.strptime(dados.get("data_ida", "2025-07-21"), "%Y-%m-%d"))
        hora_saida = st.time_input("Hora de saída", datetime.strptime(dados.get("hora_saida", "06:00"), "%H:%M").time())
    with col2:
        destino = st.text_input("Destino", dados.get("destino", "Gramado"))
        data_chegada = st.date_input("Data de Chegada", datetime.strptime(dados.get("data_chegada", "2025-07-21"), "%Y-%m-%d"))
        hora_chegada = st.time_input("Hora de chegada", datetime.strptime(dados.get("hora_chegada", "13:00"), "%H:%M").time())

    if origem.strip() and destino.strip():
        origem_url = urllib.parse.quote(origem)
        destino_url = urllib.parse.quote(destino)
        st.markdown("### Rotas")
        col1r, col2r = st.columns(2)
        with col1r:
            st.markdown(f'<a href="https://www.google.com/maps/dir/?api=1&origin={origem_url}&destination={destino_url}" target="_blank" class="botao-link">➡️ Google Maps</a>', unsafe_allow_html=True)
        with col2r:
            st.markdown(f'<a href="https://waze.com/ul?q={origem_url}+to+{destino_url}" target="_blank" class="botao-link">➡️ Waze</a>', unsafe_allow_html=True)
    else:
        st.info("Preencha os campos Origem e Destino para visualizar as rotas.")

    distancia = st.number_input("Distância estimada (km)", value=dados.get("distancia", 550))
    consumo = st.number_input("Consumo do veículo (km/l)", value=dados.get("consumo", 12.0))
    preco = st.number_input("Preço do litro (R$)", value=dados.get("preco", 5.80), format="%.2f")

    litros = distancia / consumo if consumo else 0
    gasto = litros * preco
    st.success(f"⛽ Estimativa: {litros:.1f} L | R$ {gasto:,.2f}".replace(".", ","))

    paradas = st.text_area("Paradas e tempos (ex: Posto X - 20min)", dados.get("paradas", ""))

# --- Trajeto de Volta ---
st.markdown("<div class='titulo-expander'><span class='emoji'>🚗</span><span>Trajeto de Volta</span></div>", unsafe_allow_html=True)
with st.expander("", expanded=False):
    col3, col4 = st.columns(2)
    with col3:
        origem_volta = st.text_input("Origem (volta)", dados.get("origem_volta", "Gramado"))
        data_ida_volta = st.date_input("Data de Ida (volta)", datetime.strptime(dados.get("data_ida_volta", "2025-07-28"), "%Y-%m-%d"))
        hora_saida_volta = st.time_input("Hora de saída (volta)", datetime.strptime(dados.get("hora_saida_volta", "09:00"), "%H:%M").time())
    with col4:
        destino_volta = st.text_input("Destino (volta)", dados.get("destino_volta", "Fazenda Rio Grande"))
        data_chegada_volta = st.date_input("Data de Chegada (volta)", datetime.strptime(dados.get("data_chegada_volta", "2025-07-28"), "%Y-%m-%d"))
        hora_chegada_volta = st.time_input("Hora de chegada (volta)", datetime.strptime(dados.get("hora_chegada_volta", "17:00"), "%H:%M").time())

    if origem_volta.strip() and destino_volta.strip():
        origem_volta_url = urllib.parse.quote(origem_volta)
        destino_volta_url = urllib.parse.quote(destino_volta)
        st.markdown("### Rotas")
        colv1, colv2 = st.columns(2)
        with colv1:
            st.markdown(f'<a href="https://www.google.com/maps/dir/?api=1&origin={origem_volta_url}&destination={destino_volta_url}" target="_blank" class="botao-link">➡️ Google Maps</a>', unsafe_allow_html=True)
        with colv2:
            st.markdown(f'<a href="https://waze.com/ul?q={origem_volta_url}+to+{destino_volta_url}" target="_blank" class="botao-link">➡️ Waze</a>', unsafe_allow_html=True)
    else:
        st.info("Preencha os campos Origem e Destino para visualizar as rotas de volta.")

    distancia_volta = st.number_input("Distância estimada (km) - volta", value=dados.get("distancia_volta", 650))
    consumo_volta = st.number_input("Consumo do veículo (km/l) - volta", value=dados.get("consumo_volta", 12.0))
    preco_volta = st.number_input("Preço do litro (R$) - volta", value=dados.get("preco_volta", 6.50), format="%.2f")

    litros_volta = distancia_volta / consumo_volta if consumo_volta else 0
    gasto_volta = litros_volta * preco_volta
    st.success(f"⛽ Estimativa: {litros_volta:.1f} L | R$ {gasto_volta:,.2f}".replace(".", ","))

    paradas_volta = st.text_area("Paradas e tempos (volta)", dados.get("paradas_volta", ""))

# --- Linha do Tempo Diária recolhível ---
st.markdown("<div class='titulo-expander'><span class='emoji'>📅</span><span>Linha do Tempo Diária</span></div>", unsafe_allow_html=True)
with st.expander("", expanded=False):
    col_dias, col_main = st.columns([1,3])

    with col_dias:
        st.markdown("## Dias")
        def key_data(d):
            try:
                return datetime.strptime(d["data"], "%d/%m/%Y")
            except:
                return datetime.min
        st.session_state.dias.sort(key=key_data)

        lista_datas = [dia["data"] for dia in st.session_state.dias]

        if "data_selecionada" not in st.session_state:
            st.session_state.data_selecionada = lista_datas[0] if lista_datas else datetime.now().strftime("%d/%m/%Y")

        data_selecionada = st.radio("Selecione o dia:", lista_datas, index=lista_datas.index(st.session_state.data_selecionada) if st.session_state.data_selecionada in lista_datas else 0)

        st.session_state.data_selecionada = data_selecionada

        nova_data_input = st.date_input("Adicionar novo dia", value=datetime.now())
        nova_data_str = nova_data_input.strftime("%d/%m/%Y")
        if st.button("➕ Adicionar Dia"):
            if encontrar_dia_por_data(nova_data_str) is None:
                adicionar_dia(nova_data_str)
                st.session_state.data_selecionada = nova_data_str
                safe_rerun()
            else:
                st.warning(f"Dia {nova_data_str} já existe!")

        if st.button("❌ Excluir Dia Selecionado"):
            remover_dia(st.session_state.data_selecionada)
            lista_datas = [dia["data"] for dia in st.session_state.dias]
            if lista_datas:
                st.session_state.data_selecionada = lista_datas[0]
            else:
                st.session_state.data_selecionada = None
            safe_rerun()

    with col_main:
        st.markdown(f"## Eventos para o dia: **{st.session_state.data_selecionada}**")
        if st.session_state.data_selecionada is None:
            st.info("Nenhum dia criado ainda. Use o botão para adicionar um novo dia.")
        else:
            idx_dia = encontrar_dia_por_data(st.session_state.data_selecionada)
            if idx_dia is None:
                st.error("Erro: Dia não encontrado!")
            else:
                eventos = st.session_state.dias[idx_dia]["eventos"]

                col_add_ev, col_rem_ev = st.columns([1,1])
                with col_add_ev:
                    if st.button("➕ Adicionar Evento"):
                        adicionar_evento(idx_dia)
                        safe_rerun()
                with col_rem_ev:
                    if eventos:
                        eventos_para_remover = st.multiselect(
                            "Selecionar evento(s) para remover",
                            options=[f"{i+1} - {ev['local'] or 'Sem local'}" for i, ev in enumerate(eventos)],
                            key="multiselect_remover_eventos"
                        )
                        if st.button("− Remover Evento(s) Selecionado(s)"):
                            idxs_para_remover = sorted([int(s.split()[0]) - 1 for s in eventos_para_remover], reverse=True)
                            for i_ in idxs_para_remover:
                                remover_evento(idx_dia, i_)
                            safe_rerun()

                for i, ev in enumerate(eventos):
                    with st.expander(f"Evento {i+1} - {ev.get('local','Sem local')}", expanded=False):
                        hora = st.time_input("Hora", value=datetime.strptime(ev.get("hora", "08:00"), "%H:%M").time(), key=f"hora_{idx_dia}_{i}")
                        local = st.text_input("Local", value=ev.get("local", ""), key=f"local_{idx_dia}_{i}")
                        descricao = st.text_area("Descrição", value=ev.get("descricao", ""), key=f"desc_{idx_dia}_{i}")

                        localizacao = st.text_input("Endereço ou Localização", value=ev.get("link", ""), key=f"link_{idx_dia}_{i}", label_visibility="visible")
                        if localizacao.strip():
                            localizacao_url = urllib.parse.quote(localizacao)
                            if st.button("🌐 Abrir no Google Maps", key=f"btn_maps_{idx_dia}_{i}"):
                                url = f"https://www.google.com/maps/search/?api=1&query={localizacao_url}"
                                st.markdown(f"[Abrir Google Maps]({url})", unsafe_allow_html=True)

                        foto_b64 = ev.get("foto_b64")

                        if foto_b64:
                            st.image(base64.b64decode(foto_b64), width=150)
                            if st.button("❌ Remover Foto", key=f"remover_foto_{idx_dia}_{i}"):
                                st.session_state.dias[idx_dia]["eventos"][i]["foto_b64"] = None
                                safe_rerun()

                        foto = st.file_uploader("Foto (opcional)", type=["jpg", "png", "jpeg"], key=f"foto_{idx_dia}_{i}")
                        if foto:
                            foto_b64 = base64.b64encode(foto.read()).decode()
                            st.session_state.dias[idx_dia]["eventos"][i]["foto_b64"] = foto_b64
                            safe_rerun()

                        st.session_state.dias[idx_dia]["eventos"][i].update({
                            "hora": hora.strftime("%H:%M"),
                            "local": local,
                            "descricao": descricao,
                            "link": localizacao,
                            "foto_b64": st.session_state.dias[idx_dia]["eventos"][i]["foto_b64"]
                        })

if st.button("💾 Salvar Roteiro Completo"):
    dados_atualizados = {
        "titulo_viagem": dados.get("titulo_viagem", ""),
        "origem": origem,
        "destino": destino,
        "data_ida": data_ida.strftime("%Y-%m-%d"),
        "hora_saida": hora_saida.strftime("%H:%M"),
        "data_chegada": data_chegada.strftime("%Y-%m-%d"),
        "hora_chegada": hora_chegada.strftime("%H:%M"),
        "distancia": distancia,
        "consumo": consumo,
        "preco": preco,
        "paradas": paradas,
        "origem_volta": origem_volta,
        "destino_volta": destino_volta,
        "data_ida_volta": data_ida_volta.strftime("%Y-%m-%d"),
        "hora_saida_volta": hora_saida_volta.strftime("%H:%M"),
        "data_chegada_volta": data_chegada_volta.strftime("%Y-%m-%d"),
        "hora_chegada_volta": hora_chegada_volta.strftime("%H:%M"),
        "distancia_volta": distancia_volta,
        "consumo_volta": consumo_volta,
        "preco_volta": preco_volta,
        "paradas_volta": paradas_volta,
        "dias": st.session_state.dias
    }
    salvar_dados(dados_atualizados)
    st.success("Roteiro salvo com sucesso!")
