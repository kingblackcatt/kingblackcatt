"""Refresh only public GitHub metrics; no private repository data is requested."""
import datetime as dt
import html
import json
import os
from pathlib import Path
import urllib.request

USER = 'kingblackcatt'
ROOT = Path(__file__).resolve().parents[1]


def get(path):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': USER+'-profile'}
    token = os.environ.get('GH_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer '+token
    with urllib.request.urlopen(urllib.request.Request('https://api.github.com'+path, headers=headers), timeout=30) as response:
        return json.load(response)


def metrics():
    user = get('/users/'+USER)
    repos = []
    for page in range(1, 101):
        batch = get(f'/users/{USER}/repos?type=owner&per_page=100&page={page}')
        repos.extend(r for r in batch if not r.get('private') and not r.get('fork') and r['name'].casefold()!=USER.casefold())
        if len(batch)<100:
            break
    return [('PROJETOS PÚBLICOS', len(repos), 'experimentos e ferramentas'),
            ('ESTRELAS', sum(r['stargazers_count'] for r in repos), 'recebidas nos projetos'),
            ('SEGUIDORES', user['followers'], 'pessoas por aqui')]


def render(rows, date):
    cards = []
    for index, (title, value, caption) in enumerate(rows):
        x = 28 + index*384
        color = ['#c4a7ff', '#5eead4', '#e9d89a'][index]
        cards.append(f'''<g transform="translate({x} 76)">
          <rect width="360" height="137" rx="18" fill="#ffffff" fill-opacity=".025" stroke="#302b40"/>
          <rect x="24" y="25" width="4" height="16" rx="2" fill="{color}"/>
          <text x="40" y="38" fill="#b0a3c3" font-size="12" letter-spacing="1.5">{html.escape(title)}</text>
          <text x="24" y="92" fill="{color}" font-size="42" font-weight="700">{int(value)}</text>
          <text x="24" y="117" fill="#93869f" font-size="13">{html.escape(caption)}</text>
        </g>''')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="254" viewBox="0 0 1200 254" role="img" aria-label="Dados públicos do GitHub">
      <rect x="1" y="1" width="1198" height="252" rx="22" fill="#0e0e19" stroke="#302b40"/>
      <g font-family="Segoe UI,Arial,sans-serif">
        <circle cx="34" cy="39" r="4" fill="#5eead4"/>
        <text x="48" y="44" fill="#ddd2ee" font-size="14" font-weight="600">PUBLIC ACTIVITY / GITHUB</text>
        <text x="1170" y="44" text-anchor="end" fill="#93869f" font-size="12">{date:%d.%m.%Y} · UTC</text>
        {''.join(cards)}
        <text x="30" y="237" fill="#6e647c" font-size="11">Repositórios próprios e públicos · exclui forks e este perfil</text>
      </g>
    </svg>\n'''


def render_mobile(rows, date):
    cards = []
    for index, (title, value, caption) in enumerate(rows):
        color = ['#c4a7ff', '#5eead4', '#e9d89a'][index]
        cards.append(f'''<g transform="translate(18 {64+index*124})">
          <rect width="364" height="110" rx="16" fill="#ffffff" fill-opacity=".025" stroke="#302b40"/>
          <text x="20" y="27" fill="#b0a3c3" font-size="13" letter-spacing="1">{html.escape(title)}</text>
          <text x="20" y="70" fill="{color}" font-size="38" font-weight="700">{int(value)}</text>
          <text x="20" y="94" fill="#a297ad" font-size="13">{html.escape(caption)}</text>
        </g>''')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="460" viewBox="0 0 400 460" role="img" aria-label="Dados públicos do GitHub">
      <rect x="1" y="1" width="398" height="458" rx="20" fill="#0e0e19" stroke="#302b40"/>
      <g font-family="Segoe UI,Arial,sans-serif">
        <circle cx="23" cy="28" r="3" fill="#5eead4"/>
        <text x="35" y="33" fill="#ddd2ee" font-size="12" font-weight="600">GITHUB · DADOS PÚBLICOS</text>
        <text x="20" y="51" fill="#93869f" font-size="11">Atualizado em {date:%d.%m.%Y} · UTC</text>
        {''.join(cards)}
        <text x="20" y="447" fill="#93869f" font-size="10">Projetos próprios · exclui forks e este perfil</text>
      </g></svg>\n'''


if __name__ == '__main__':
    rows = metrics()
    date = dt.datetime.now(dt.timezone.utc).date()
    (ROOT/'assets/pulse.svg').write_text(render(rows, date), encoding='utf-8')
    (ROOT/'assets/pulse-mobile.svg').write_text(render_mobile(rows, date), encoding='utf-8')
    print('Public profile metrics updated.')
