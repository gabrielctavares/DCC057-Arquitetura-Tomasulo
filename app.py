import streamlit as st
from core.cpu import TomasuloCPU

st.set_page_config(layout="wide", page_title="Simulador Tomasulo")
st.title("Simulador Tomasulo")

# =========================
# Estado da aplicação
# =========================
if "cpu" not in st.session_state:
    st.session_state.cpu = None

if "program_text" not in st.session_state:
    st.session_state.program_text = ""

# =========================
# Sidebar – Entrada do Programa
# =========================
st.sidebar.header("Entrada do Programa")

input_mode = st.sidebar.radio(
    "Modo de entrada",
    ["Inserir manualmente", "Carregar arquivo .txt"]
)

# ---- Modo 1: Upload de arquivo ----
if input_mode == "Carregar arquivo .txt":
    uploaded_file = st.sidebar.file_uploader(
        "Selecione o arquivo",
        type=["txt"]
    )

    if uploaded_file is not None:
        content = uploaded_file.read().decode("utf-8")
        st.session_state.program_text = content
else:
    program_text = st.sidebar.text_area(
        "Código binário (1 instrução por linha)",
        height=220,
        value=st.session_state.program_text
    )

# =========================
# Botões de controle
# =========================
if st.sidebar.button("Carregar Programa"):
    try:
        program = [
            int(line.strip(), 2)
            for line in st.session_state.program_text.splitlines()
            if line.strip()
        ]

        st.session_state.cpu = TomasuloCPU(program)
        st.success("Programa carregado com sucesso")

    except ValueError:
        st.error("Erro: verifique se todas as linhas são binárias (0 e 1).")

if st.sidebar.button("Reset"):
    st.session_state.cpu = None
    st.session_state.program_text = ""
    st.success("Simulador resetado")

# =========================
# Execução
# =========================
cpu = st.session_state.cpu

if cpu:
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Executar 1 ciclo"):
            cpu.step()

    with col2:
        if st.button("Executar até o fim"):
            while not cpu.finished():
                cpu.step()

    # =========================
    # Estado da CPU
    # =========================
    st.subheader("Estado da CPU")
    st.write(f"Ciclo atual: {cpu.cycle}")
    st.write(f"PC: {cpu.pc}")

    # =========================
    # Registradores
    # =========================
    st.subheader("Registradores de Ponto Flutuante")
    st.table([
        {
            "Registrador": f"F{i}",
            "Valor": cpu.regs.fp[i],
            "Qi": cpu.regs.qi[i]
        }
        for i in range(8)
    ])

    # =========================
    # Estações de Reserva
    # =========================
    st.subheader("Estações de Reserva")
    st.table([
        {
            "RS": rs.name,
            "Busy": rs.busy,
            "Op": rs.op,
            "Vj": rs.Vj,
            "Vk": rs.Vk,
            "Qj": rs.Qj,
            "Qk": rs.Qk,
            "Time": rs.time
        }
        for rs in cpu.rs_add + cpu.rs_mul
    ])


    st.subheader("Unidades Funcionais")

    uf_data = []

    for fu in [cpu.fu_add, cpu.fu_mul]:
        if fu.rs:
            uf_data.append({
                "Unidade Funcional": fu.name,
                "RS": fu.rs.name,
                "Operação": fu.rs.op,
                "Vj": fu.rs.Vj,
                "Vk": fu.rs.Vk,
                "Tempo Restante": fu.rs.time
            })
        else:
            uf_data.append({
                "Unidade Funcional": fu.name,
                "RS": None,
                "Operação": "Livre",
                "Vj": None,
                "Vk": None,
                "Tempo Restante": None
            })

    st.table(uf_data)


    st.subheader("Memória de Dados (palavras de 4 bytes)")

    mem_table = cpu.memory.dump_words()

    st.dataframe(mem_table, height=300)