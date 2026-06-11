#!/usr/bin/env python3
"""
Conferência do concurso 7046
Resultado: 02, 12, 37, 68, 76 (09/06/2026)
"""

import json
import os

# Resultado oficial do concurso 7046
RESULTADO_7046 = [2, 12, 37, 68, 76]

def load_games(filename):
    """Carrega jogos do arquivo"""
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def check_games(games, result):
    """Verifica acertos"""
    acertos = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

    for game in games:
        matches = len(set(game) & set(result))
        acertos[matches] += 1

    return acertos

def main():
    print("=" * 70)
    print("CONFERÊNCIA CONCURSO 7046")
    print("=" * 70)
    print(f"\n Resultado: {RESULTADO_7046}")
    print(f" Data: 09/06/2026")
    print()

    # Carregar jogos da Opção 1 (56 jogos)
    games_56_file = "memory/quina_56_games_latest.json"
    if os.path.exists(games_56_file):
        data_56 = load_games(games_56_file)
        games_56 = data_56.get('portfolio', [])
    else:
        games_56 = []

    # Carregar jogos da Opção 2 (70 jogos)
    games_70_file = "memory/quina_70_games_latest.json"
    if os.path.exists(games_70_file):
        data_70 = load_games(games_70_file)
        games_70 = data_70.get('portfolio', [])
    else:
        games_70 = []

    print("=" * 70)
    print("OPÇÃO 1: 56 JOGOS")
    print("=" * 70)

    if games_56:
        # Extrair números dos jogos
        games_56_nums = [g['numbers'] for g in games_56]
        acertos_56 = check_games(games_56_nums, RESULTADO_7046)

        print(f"\n Total de jogos conferidos: {len(games_56_nums)}")
        print(f"\n ACERTOS:")
        print(f"   5 números: {acertos_56[5]} jogos")
        print(f"   4 números: {acertos_56[4]} jogos")
        print(f"   3 números: {acertos_56[3]} jogos")
        print(f"   2 números: {acertos_56[2]} jogos")
        print(f"   1 número:  {acertos_56[1]} jogos")
        print(f"   0 números: {acertos_56[0]} jogos")

        # Mostrar jogos com 3+ acertos
        print(f"\n JOGOS COM 3+ ACERTOS:")
        count = 0
        for game in games_56:
            game_nums = game['numbers']
            matches = len(set(game_nums) & set(RESULTADO_7046))
            if matches >= 3:
                print(f"   Jogo {game['id']}: {game_nums} -> {matches} acertos")
                count += 1
        if count == 0:
            print("   Nenhum jogo com 3+ acertos")
    else:
        print(" Arquivo de jogos não encontrado")

    print()
    print("=" * 70)
    print("OPÇÃO 2: 70 JOGOS")
    print("=" * 70)

    if games_70:
        # Extrair números dos jogos
        games_70_nums = [g['numbers'] for g in games_70]
        acertos_70 = check_games(games_70_nums, RESULTADO_7046)

        print(f"\n Total de jogos conferidos: {len(games_70_nums)}")
        print(f"\n ACERTOS:")
        print(f"   5 números: {acertos_70[5]} jogos")
        print(f"   4 números: {acertos_70[4]} jogos")
        print(f"   3 números: {acertos_70[3]} jogos")
        print(f"   2 números: {acertos_70[2]} jogos")
        print(f"   1 número:  {acertos_70[1]} jogos")
        print(f"   0 números: {acertos_70[0]} jogos")

        # Mostrar jogos com 3+ acertos
        print(f"\n JOGOS COM 3+ ACERTOS:")
        count = 0
        for game in games_70:
            game_nums = game['numbers']
            matches = len(set(game_nums) & set(RESULTADO_7046))
            if matches >= 3:
                print(f"   Jogo {game['id']}: {game_nums} -> {matches} acertos")
                count += 1
        if count == 0:
            print("   Nenhum jogo com 3+ acertos")
    else:
        print(" Arquivo de jogos não encontrado")

    print()
    print("=" * 70)

if __name__ == "__main__":
    main()