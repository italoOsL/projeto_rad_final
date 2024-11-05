import mysql.connector
from mysql.connector import Error
import tkinter as tk
from tkinter import messagebox

# Função para criar a conexão com o banco de dados
def criar_conexao():
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            user='root',  # substitua pelo seu usuário
            password='root',  # substitua pela sua senha
            database='cadastro_rad'
        )
        return conexao
    except Error as err:
        print(f'Erro ao conectar: {err}')
        return None

# Função para criar as tabelas
def criar_tabela():
    conexao = criar_conexao()
    if conexao is None:
        return

    try:
        cursor = conexao.cursor()
        # Criação da tabela usuario
        sql_usuario = '''CREATE TABLE IF NOT EXISTS usuario (
            id INT PRIMARY KEY AUTO_INCREMENT,
            matricula INT UNIQUE,
            nome VARCHAR(100) NOT NULL,
            senha VARCHAR(100) NOT NULL,
            tipo ENUM('aluno', 'professor') NOT NULL
        );'''
        cursor.execute(sql_usuario)
        
        # Criação da tabela nota
        sql_nota = '''CREATE TABLE IF NOT EXISTS nota (
            id INT PRIMARY KEY AUTO_INCREMENT,
            matricula INT NOT NULL,
            avaliacao1 FLOAT DEFAULT NULL,
            avaliacao2 FLOAT DEFAULT NULL,
            FOREIGN KEY (matricula) REFERENCES usuario(matricula)
        );'''
        cursor.execute(sql_nota)
        
        conexao.commit()
        print('Tabelas criadas com sucesso!')
    except Error as err:
        print('Erro de banco de dados', err)
    finally:
        if conexao.is_connected():
            cursor.close()
            conexao.close()

# Função para verificar login
def verificar_login(matricula, senha):
    conexao = criar_conexao()
    if conexao is None:
        return None

    try:
        cursor = conexao.cursor()
        cursor.execute('SELECT tipo FROM usuario WHERE matricula = %s AND senha = %s', (matricula, senha))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None
    except Error as err:
        print('Erro ao verificar login', err)
        return None
    finally:
        if conexao.is_connected():
            cursor.close()
            conexao.close()

# Função para inserir dados do aluno
def inserir_dados_alunos(matricula, nome):
    conexao = criar_conexao()
    if conexao is None:
        return

    try:
        cursor = conexao.cursor()
        # Insere o aluno na tabela usuario
        sql_usuario = '''INSERT INTO usuario (matricula, nome, senha, tipo)
                         VALUES (%s, %s, %s, 'aluno') ON DUPLICATE KEY UPDATE nome=%s;'''
        cursor.execute(sql_usuario, (matricula, nome, 'senha123', nome))  # Ajuste a senha conforme necessário

        # Insere o aluno na tabela nota com valor NULL
        sql_nota = '''INSERT INTO nota (matricula, avaliacao1, avaliacao2) VALUES (%s, NULL, NULL)
                      ON DUPLICATE KEY UPDATE avaliacao1=avaliacao1, avaliacao2=avaliacao2;'''
        cursor.execute(sql_nota, (matricula,))

        conexao.commit()
        messagebox.showinfo("Sucesso", "Aluno cadastrado com sucesso!")
    except Error as err:
        messagebox.showerror("Erro", f'Erro de banco de dados: {err}')
    finally:
        if conexao.is_connected():
            cursor.close()
            conexao.close()

# Função para alterar dados do aluno
def alterar_dados_aluno(matricula, nome):
    conexao = criar_conexao()
    if conexao is None:
        return

    try:
        cursor = conexao.cursor()
        comando = 'UPDATE usuario SET nome=%s WHERE matricula=%s;'
        cursor.execute(comando, (nome, matricula))
        conexao.commit()
        messagebox.showinfo("Sucesso", "Dados do aluno alterados com sucesso!")
    except Error as err:
        messagebox.showerror("Erro", f'Erro de banco de dados: {err}')
    finally:
        if conexao.is_connected():
            cursor.close()
            conexao.close()

# Função para excluir aluno
def excluir_aluno(matricula):
    conexao = criar_conexao()
    if conexao is None:
        return

    try:
        cursor = conexao.cursor()
        comando1 = 'DELETE FROM nota WHERE matricula=%s;'
        comando2 = 'DELETE FROM usuario WHERE matricula=%s;'

        cursor.execute(comando1, (matricula,))
        cursor.execute(comando2, (matricula,))
        conexao.commit()
        messagebox.showinfo("Sucesso", "Aluno excluído com sucesso!")
    except Error as err:
        messagebox.showerror("Erro", f'Erro de banco de dados: {err}')
    finally:
        if conexao.is_connected():
            cursor.close()
            conexao.close()

# Função para lançar ou atualizar a nota do aluno
def lancar_nota(matricula, avaliacao1, avaliacao2):
    conexao = criar_conexao()
    if conexao is None:
        return

    try:
        cursor = conexao.cursor()
        
        # Atualiza as notas na tabela nota para o aluno com a matrícula especificada
        sql_nota = '''UPDATE nota 
                      SET avaliacao1 = %s, avaliacao2 = %s 
                      WHERE matricula = %s;'''
        cursor.execute(sql_nota, (avaliacao1, avaliacao2, matricula))

        conexao.commit()
        messagebox.showinfo("Sucesso", "Notas lançadas com sucesso!")
    except Error as err:
        messagebox.showerror("Erro", f'Erro de banco de dados: {err}')
    finally:
        if conexao.is_connected():
            cursor.close()
            conexao.close()

# Função para consultar a aprovação do aluno
def consultar_aprovacao(matricula):
    dados_aluno = buscar_dados_aluno(matricula)
    if dados_aluno['nome'] == "Nome não encontrado":
        messagebox.showerror("Erro", "Aluno não encontrado!")
        return

    # Exibe informações de aprovação
    media = (dados_aluno.get('avaliacao1', 0) + dados_aluno.get('avaliacao2', 0)) / 2
    status = "Aprovado" if media >= 6 else "Reprovado"
    messagebox.showinfo("Aprovação", f"Aluno: {dados_aluno['nome']}\nStatus: {status}")

# Função para buscar dados do aluno
def buscar_dados_aluno(matricula):
    conexao = criar_conexao()
    dados = {}
    if conexao is None:
        return dados

    try:
        cursor = conexao.cursor()
        cursor.execute('SELECT nome FROM usuario WHERE matricula = %s', (matricula,))
        resultado = cursor.fetchone()
        dados['nome'] = resultado[0] if resultado else "Nome não encontrado"
        
        # Buscar notas
        cursor.execute('SELECT avaliacao1, avaliacao2 FROM nota WHERE matricula = %s', (matricula,))
        resultados_notas = cursor.fetchone()
        if resultados_notas:
            avaliacao1, avaliacao2 = resultados_notas
            dados['avaliacao1'] = avaliacao1 if avaliacao1 is not None else "N/A"
            dados['avaliacao2'] = avaliacao2 if avaliacao2 is not None else "N/A"
            media = (avaliacao1 + avaliacao2) / 2 if avaliacao1 is not None and avaliacao2 is not None else 0
            dados['status'] = "Aprovado" if media >= 6 else "Reprovado"
        else:
            dados['avaliacao1'] = "N/A"
            dados['avaliacao2'] = "N/A"
            dados['status'] = "Sem notas"
    except Error as err:
        messagebox.showerror("Erro", f'Erro de banco de dados: {err}')
    finally:
        if conexao.is_connected():
            cursor.close()
            conexao.close()
    return dados

# Função para voltar à tela de login
def voltar_login():
    for widget in app.winfo_children():
        widget.destroy()  # Limpa a tela
    criar_tela_login()  # Recria a tela de login

# Função para criar a tela de login
def criar_tela_login():
    label_matricula = tk.Label(app, text="Matrícula:", fg='white', bg="#2b2b2b")
    label_matricula.pack(pady=10)
    entry_matricula = tk.Entry(app)
    entry_matricula.pack(pady=5)

    label_senha = tk.Label(app, text="Senha:", fg='white', bg="#2b2b2b")
    label_senha.pack(pady=10)
    entry_senha = tk.Entry(app, show='*')
    entry_senha.pack(pady=5)

    btn_login = tk.Button(app, text="Login", command=lambda: fazer_login(entry_matricula.get(), entry_senha.get()))
    btn_login.pack(pady=10)

def fazer_login(matricula, senha):
    tipo_usuario = verificar_login(matricula, senha)
    if tipo_usuario is None:
        messagebox.showerror("Erro", "Matrícula ou senha inválidos!")
    elif tipo_usuario == "aluno":
        criar_tela_aluno(matricula)
    elif tipo_usuario == "professor":
        criar_tela_professor(matricula)

# Função para criar a tela do aluno
def criar_tela_aluno(matricula):
    for widget in app.winfo_children():
        widget.destroy()

    dados_aluno = buscar_dados_aluno(matricula)

    label_nome = tk.Label(app, text=f"Nome: {dados_aluno['nome']}", fg='white', bg="#2b2b2b")
    label_nome.pack(pady=10)

    label_info = tk.Label(app, text=f"Avaliação 1: {dados_aluno.get('avaliacao1', 'N/A')},\nAvaliação 2: {dados_aluno.get('avaliacao2', 'N/A')}")
    label_info.pack()

    label_status = tk.Label(app, text=f"Status: {dados_aluno['status']}", fg='white', bg="#2b2b2b")
    label_status.pack(pady=10)

    btn_voltar = tk.Button(app, text="Voltar", command=voltar_login)
    btn_voltar.pack(pady=20)

# Função para criar a tela do professor
def criar_tela_professor(matricula):
    for widget in app.winfo_children():
        widget.destroy()

    label_matricula = tk.Label(app, text="Matrícula do aluno:", fg='white', bg="#2b2b2b")
    label_matricula.pack(pady=10)
    entry_matricula_aluno = tk.Entry(app)
    entry_matricula_aluno.pack(pady=5)

    label_nome = tk.Label(app, text="Nome do aluno:", fg='white', bg="#2b2b2b")
    label_nome.pack(pady=10)
    entry_nome_aluno = tk.Entry(app)
    entry_nome_aluno.pack(pady=5)

    btn_cadastrar = tk.Button(app, text="Cadastrar Aluno", command=lambda: inserir_dados_alunos(entry_matricula_aluno.get(), entry_nome_aluno.get()))
    btn_cadastrar.pack(pady=10)

    btn_alterar = tk.Button(app, text="Alterar aluno", command=lambda: alterar_dados_aluno(entry_matricula_aluno.get(), entry_nome_aluno.get()))
    btn_alterar.pack(pady=10)

    btn_excluir = tk.Button(app, text="Excluir aluno", command=lambda: excluir_aluno(entry_matricula_aluno.get()))
    btn_excluir.pack(pady=10)

    btn_consultar = tk.Button(app, text="Consultar Aprovação", command=lambda: consultar_aprovacao(entry_matricula_aluno.get()))
    btn_consultar.pack(pady=10)

    label_nota1 = tk.Label(app, text="Nota Avaliação 1:", fg='white', bg="#2b2b2b")
    label_nota1.pack(pady=10)
    entry_nota1 = tk.Entry(app)
    entry_nota1.pack(pady=5)

    label_nota2 = tk.Label(app, text="Nota Avaliação 2:", fg='white', bg="#2b2b2b")
    label_nota2.pack(pady=10)
    entry_nota2 = tk.Entry(app)
    entry_nota2.pack(pady=5)

    btn_lancar_nota = tk.Button(app, text="Lançar Nota", command=lambda: lancar_nota(entry_matricula_aluno.get(), entry_nota1.get(), entry_nota2.get()))
    btn_lancar_nota.pack(pady=10)

    btn_voltar = tk.Button(app, text="Voltar", command=voltar_login)
    btn_voltar.pack(pady=20)

# Criar a interface gráfica principal
app = tk.Tk()
app.title("Sistema de Cadastro de Alunos")
app.geometry("400x500")
app.configure(bg="#2b2b2b")
criar_tela_login()

app.mainloop()
