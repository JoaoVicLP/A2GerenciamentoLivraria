import sqlite3
import csv
import os
from pathlib import Path
from datetime import datetime
import shutil

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = BASE_DIR / "backups"
EXPORT_DIR = BASE_DIR / "exports"

DB_PATH = DATA_DIR / "livraria.db"

for directory in [DATA_DIR, BACKUP_DIR, EXPORT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)




#crud
def criar_banco():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            ano_publicacao INTEGER,
            preco REAL
        )
    """)
    conn.commit()
    conn.close()


def adicionar_livro(titulo, autor, ano, preco):
    backup_banco()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO livros (titulo, autor, ano_publicacao, preco) VALUES (?, ?, ?, ?)",
                   (titulo, autor, ano, preco))
    conn.commit()
    conn.close()


def exibir_livros():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM livros")
    livros = cursor.fetchall()
    conn.close()
    return livros


def atualizar_preco(titulo, novo_preco):
    backup_banco()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE livros SET preco = ? WHERE titulo LIKE ?", (novo_preco, f"%{titulo}%"))
    conn.commit()
    conn.close()


def remover_livro(titulo):
    backup_banco()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM livros WHERE titulo LIKE ?", (f"%{titulo}%",))
    conn.commit()
    conn.close()


def buscar_por_autor(autor):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM livros WHERE autor LIKE ?", (f"%{autor}%",))
    livros = cursor.fetchall()
    conn.close()
    return livros



#backup
def backup_banco():
    if DB_PATH.exists():
        data = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_path = BACKUP_DIR / f"backup_livraria_{data}.db"
        shutil.copy(DB_PATH, backup_path)
        limpar_backups()

def limpar_backups(max_backups=5):
    backups = sorted(BACKUP_DIR.glob("backup_livraria_*.db"), key=os.path.getmtime, reverse=True)
    for old_backup in backups[max_backups:]:
        old_backup.unlink()



#funcões csv
def exportar_csv():
    livros = exibir_livros()
    export_path = EXPORT_DIR / "livros_exportados.csv"
    with open(export_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "titulo", "autor", "ano_publicacao", "preco"])
        writer.writerows(livros)

def importar_csv(caminho_csv):
    backup_banco()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    with open(caminho_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute(
                "INSERT INTO livros (titulo, autor, ano_publicacao, preco) VALUES (?, ?, ?, ?)",
                (row["titulo"], row["autor"], int(row["ano_publicacao"]), float(row["preco"]))
            )
    conn.commit()
    conn.close()




def menu():
    criar_banco()

    while True:
        print("\n=== SISTEMA LIVRARIA ===")
        print("1 Adicionar livro")
        print("2 Exibir livros")
        print("3 Atualizar preço de um livro")
        print("4 Remover livro")
        print("5 Buscar livros por autor")
        print("6 Exportar dados para CSV")
        print("7 Importar dados CSV")
        print("8 Fazer backup do banco de dados")
        print("9 Sair\n")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            titulo = input("Título: ")
            autor = input("Autor: ")
            ano = int(input("Ano de Publicação: "))
            preco = float(input("Preço: "))
            adicionar_livro(titulo, autor, ano, preco)
        elif opcao == "2":
            livros = exibir_livros()
            for livro in livros:
                print(livro)
        elif opcao == "3":
            titulo = input("Título do livro: ")
            novo_preco = float(input("Novo preço: "))
            atualizar_preco(titulo, novo_preco)
        elif opcao == "4":
            titulo = input("Título do livro a remover: ")
            remover_livro(titulo)
        elif opcao == "5":
            autor = input("Nome do autor: ")
            livros = buscar_por_autor(autor)
            for livro in livros:
                print(livro)
        elif opcao == "6":
            exportar_csv()
            print("Dados exportados para CSV com sucesso!")
        elif opcao == "7":
            caminho = input("Caminho do arquivo CSV: ")
            importar_csv(caminho)
            print("Dados importados com sucesso!")
        elif opcao == "8":
            backup_banco()
            print("Backup realizado com sucesso!")
        elif opcao == "9":
            break
        else:
            print("Opção inválida!")




if __name__ == "__main__":
    menu()
