#!/usr/bin/env python3
"""Render README files from data/templates.json. Listings stay empty until the roster is filled."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CATEGORIES = [
    "Assistants",
    "Engineering",
    "Research",
    "Money",
    "Sales",
    "Creative",
    "Life",
]

CATEGORY_LABELS = {
    "en": {
        "Assistants": "Assistants",
        "Engineering": "Engineering",
        "Research": "Research",
        "Money": "Money",
        "Sales": "Sales",
        "Creative": "Creative",
        "Life": "Life",
    },
    "zh-CN": {
        "Assistants": "助理",
        "Engineering": "工程",
        "Research": "研究",
        "Money": "金钱",
        "Sales": "销售",
        "Creative": "创意",
        "Life": "生活",
    },
    "zh-TW": {
        "Assistants": "助理",
        "Engineering": "工程",
        "Research": "研究",
        "Money": "金錢",
        "Sales": "銷售",
        "Creative": "創意",
        "Life": "生活",
    },
    "ja": {
        "Assistants": "アシスタント",
        "Engineering": "エンジニアリング",
        "Research": "リサーチ",
        "Money": "マネー",
        "Sales": "セールス",
        "Creative": "クリエイティブ",
        "Life": "ライフ",
    },
    "ko": {
        "Assistants": "어시스턴트",
        "Engineering": "엔지니어링",
        "Research": "리서치",
        "Money": "머니",
        "Sales": "세일즈",
        "Creative": "크리에이티브",
        "Life": "라이프",
    },
    "es": {
        "Assistants": "Asistentes",
        "Engineering": "Ingeniería",
        "Research": "Investigación",
        "Money": "Dinero",
        "Sales": "Ventas",
        "Creative": "Creativo",
        "Life": "Vida",
    },
    "fr": {
        "Assistants": "Assistants",
        "Engineering": "Ingénierie",
        "Research": "Recherche",
        "Money": "Argent",
        "Sales": "Ventes",
        "Creative": "Créatif",
        "Life": "Vie",
    },
    "de": {
        "Assistants": "Assistenten",
        "Engineering": "Engineering",
        "Research": "Research",
        "Money": "Geld",
        "Sales": "Vertrieb",
        "Creative": "Kreativ",
        "Life": "Leben",
    },
    "pt-BR": {
        "Assistants": "Assistentes",
        "Engineering": "Engenharia",
        "Research": "Pesquisa",
        "Money": "Dinheiro",
        "Sales": "Vendas",
        "Creative": "Criativo",
        "Life": "Vida",
    },
    "ru": {
        "Assistants": "Ассистенты",
        "Engineering": "Инжиниринг",
        "Research": "Исследования",
        "Money": "Деньги",
        "Sales": "Продажи",
        "Creative": "Креатив",
        "Life": "Жизнь",
    },
}

LANGS = [
    ("en", "English", "README.md"),
    ("zh-CN", "简体中文", "README.zh-CN.md"),
    ("zh-TW", "繁體中文", "README.zh-TW.md"),
    ("ja", "日本語", "README.ja.md"),
    ("ko", "한국어", "README.ko.md"),
    ("es", "Español", "README.es.md"),
    ("fr", "Français", "README.fr.md"),
    ("de", "Deutsch", "README.de.md"),
    ("pt-BR", "Português (Brasil)", "README.pt-BR.md"),
    ("ru", "Русский", "README.ru.md"),
]

COPY = {
    "en": {
        "tagline": "A curated list of community Grok Bot templates. Official share links only.",
        "intro": (
            "A [Grok Bot](https://docs.x.ai/grok-bot/get-started) is an always-on xAI agent. "
            "Owners can publish a share link so other people can add a copy. "
            "This repository is an independent awesome list of those public templates."
        ),
        "disclaimer": (
            "Not affiliated with xAI. Each listing is a name, one-line description, "
            "optional public Twitter handle, and the official `https://x.ai/bot/…` share URL. "
            "This list does not rehost prompts, packed configs, memory dumps, or secrets."
        ),
        "howto_h": "How to use a listing",
        "howto": (
            "1. Open the official share link (`https://x.ai/bot/…`).\n"
            "2. Choose **Add to Grok Bot** and confirm in the Grok Bot app.\n"
            "3. Connect the plugins that bot needs.\n"
            "\n"
            "Docs: [Get started](https://docs.x.ai/grok-bot/get-started) · [Bots](https://docs.x.ai/grok-bot/bots)"
        ),
        "contents": "Contents",
        "related_h": "Related",
        "related": (
            "- [Grok Bot docs](https://docs.x.ai/grok-bot/get-started)\n"
            "- [Bots](https://docs.x.ai/grok-bot/bots)\n"
            "- [Official share host](https://x.ai/bot)\n"
            "- [sindresorhus/awesome](https://github.com/sindresorhus/awesome)"
        ),
        "contrib_h": "Contributing",
        "contrib": "See [CONTRIBUTING.md](CONTRIBUTING.md). The only required URL is a real `https://x.ai/bot/…` share link.",
        "license_h": "License",
        "license": "[CC0 1.0 Universal](LICENSE).",
        "empty": "*Contributions welcome.*",
    },
    "zh-CN": {
        "tagline": "社区 Grok Bot 模板精选。仅收录官方分享链接。",
        "intro": (
            "[Grok Bot](https://docs.x.ai/grok-bot/get-started) 是 xAI 的常驻智能体。"
            "所有者可以发布分享链接，让其他人添加副本。"
            "本仓库是这些公开模板的独立 awesome 列表。"
        ),
        "disclaimer": (
            "与 xAI 无隶属关系。每条记录包含名称、一行简介、可选的公开 Twitter 账号，以及官方 `https://x.ai/bot/…` 分享链接。"
            "本列表不转载提示词、打包配置、记忆转储或密钥。"
        ),
        "howto_h": "如何使用条目",
        "howto": (
            "1. 打开官方分享链接（`https://x.ai/bot/…`）。\n"
            "2. 选择 **Add to Grok Bot**，并在 Grok Bot 应用中确认。\n"
            "3. 连接该 Bot 需要的插件。\n"
            "\n"
            "文档：[入门](https://docs.x.ai/grok-bot/get-started) · [Bots](https://docs.x.ai/grok-bot/bots)"
        ),
        "contents": "目录",
        "related_h": "相关",
        "related": (
            "- [Grok Bot 文档](https://docs.x.ai/grok-bot/get-started)\n"
            "- [Bots](https://docs.x.ai/grok-bot/bots)\n"
            "- [官方分享主机](https://x.ai/bot)\n"
            "- [sindresorhus/awesome](https://github.com/sindresorhus/awesome)"
        ),
        "contrib_h": "贡献",
        "contrib": "见 [CONTRIBUTING.md](CONTRIBUTING.md)。唯一必填的 URL 是真实的 `https://x.ai/bot/…` 分享链接。",
        "license_h": "许可",
        "license": "[CC0 1.0 Universal](LICENSE)。",
        "empty": "*欢迎投稿。*",
    },
    "zh-TW": {
        "tagline": "社群 Grok Bot 模板精選。只收錄官方分享連結。",
        "intro": (
            "[Grok Bot](https://docs.x.ai/grok-bot/get-started) 是 xAI 的常駐智慧體。"
            "擁有者可以發布分享連結，讓其他人新增複本。"
            "本倉庫是這些公開模板的獨立 awesome 列表。"
        ),
        "disclaimer": (
            "與 xAI 無隸屬關係。每筆紀錄包含名稱、一行簡介、可選的公開 Twitter 帳號，以及官方 `https://x.ai/bot/…` 分享連結。"
            "本列表不轉載提示詞、打包設定、記憶轉儲或密鑰。"
        ),
        "howto_h": "如何使用條目",
        "howto": (
            "1. 開啟官方分享連結（`https://x.ai/bot/…`）。\n"
            "2. 選擇 **Add to Grok Bot**，並在 Grok Bot 應用程式中確認。\n"
            "3. 連接該 Bot 需要的外掛。\n"
            "\n"
            "文件：[開始使用](https://docs.x.ai/grok-bot/get-started) · [Bots](https://docs.x.ai/grok-bot/bots)"
        ),
        "contents": "目錄",
        "related_h": "相關",
        "related": (
            "- [Grok Bot 文件](https://docs.x.ai/grok-bot/get-started)\n"
            "- [Bots](https://docs.x.ai/grok-bot/bots)\n"
            "- [官方分享主機](https://x.ai/bot)\n"
            "- [sindresorhus/awesome](https://github.com/sindresorhus/awesome)"
        ),
        "contrib_h": "貢獻",
        "contrib": "見 [CONTRIBUTING.md](CONTRIBUTING.md)。唯一必填的 URL 是真實的 `https://x.ai/bot/…` 分享連結。",
        "license_h": "授權",
        "license": "[CC0 1.0 Universal](LICENSE)。",
        "empty": "*歡迎投稿。*",
    },
    "ja": {
        "tagline": "コミュニティ製 Grok Bot テンプレートの厳選リスト。公式シェアリンクのみ。",
        "intro": (
            "[Grok Bot](https://docs.x.ai/grok-bot/get-started) は xAI の常駐エージェントです。"
            "所有者はシェアリンクを公開し、他の人がコピーを追加できます。"
            "このリポジトリは、それらの公開テンプレートを集めた独立した awesome リストです。"
        ),
        "disclaimer": (
            "xAI とは無関係です。各項目は名前、一行の説明、任意の公開 Twitter アカウント、公式の `https://x.ai/bot/…` だけです。"
            "プロンプト本文、パック済み設定、メモリダンプ、秘密情報は再配布しません。"
        ),
        "howto_h": "項目の使い方",
        "howto": (
            "1. 公式シェアリンク（`https://x.ai/bot/…`）を開く。\n"
            "2. **Add to Grok Bot** を選び、Grok Bot アプリで確認する。\n"
            "3. その Bot が使うプラグインを接続する。\n"
            "\n"
            "ドキュメント: [Get started](https://docs.x.ai/grok-bot/get-started) · [Bots](https://docs.x.ai/grok-bot/bots)"
        ),
        "contents": "目次",
        "related_h": "関連",
        "related": (
            "- [Grok Bot ドキュメント](https://docs.x.ai/grok-bot/get-started)\n"
            "- [Bots](https://docs.x.ai/grok-bot/bots)\n"
            "- [公式シェアホスト](https://x.ai/bot)\n"
            "- [sindresorhus/awesome](https://github.com/sindresorhus/awesome)"
        ),
        "contrib_h": "コントリビューション",
        "contrib": "[CONTRIBUTING.md](CONTRIBUTING.md) を参照。必須な URL は実在する `https://x.ai/bot/…` シェアリンクだけです。",
        "license_h": "ライセンス",
        "license": "[CC0 1.0 Universal](LICENSE)。",
        "empty": "*コントリビューション歓迎。*",
    },
    "ko": {
        "tagline": "커뮤니티 Grok Bot 템플릿 큐레이션 목록. 공식 공유 링크만 수록합니다.",
        "intro": (
            "[Grok Bot](https://docs.x.ai/grok-bot/get-started)은 xAI의 상시 실행 에이전트입니다."
            "소유자는 공유 링크를 공개해 다른 사람이 사본을 추가하게 할 수 있습니다."
            "이 저장소는 그런 공개 템플릿을 모은 독립 awesome 목록입니다."
        ),
        "disclaimer": (
            "xAI와 제휴하지 않습니다. 각 항목은 이름, 한 줄 설명, 선택적 공개 Twitter 핸들, 공식 `https://x.ai/bot/…` 공유 URL뿐입니다."
            "프롬프트 본문, 패키지 설정, 메모리 덤프, 비밀값은 재호스팅하지 않습니다."
        ),
        "howto_h": "항목 사용 방법",
        "howto": (
            "1. 공식 공유 링크(`https://x.ai/bot/…`)를 엽니다.\n"
            "2. **Add to Grok Bot**을 선택한 뒤 Grok Bot 앱에서 확인합니다.\n"
            "3. 해당 봇이 필요로 하는 플러그인을 연결합니다.\n"
            "\n"
            "문서: [시작하기](https://docs.x.ai/grok-bot/get-started) · [Bots](https://docs.x.ai/grok-bot/bots)"
        ),
        "contents": "목차",
        "related_h": "관련",
        "related": (
            "- [Grok Bot 문서](https://docs.x.ai/grok-bot/get-started)\n"
            "- [Bots](https://docs.x.ai/grok-bot/bots)\n"
            "- [공식 공유 호스트](https://x.ai/bot)\n"
            "- [sindresorhus/awesome](https://github.com/sindresorhus/awesome)"
        ),
        "contrib_h": "기여",
        "contrib": "[CONTRIBUTING.md](CONTRIBUTING.md)를 보세요. 필수 URL은 실제 `https://x.ai/bot/…` 공유 링크뿐입니다.",
        "license_h": "라이선스",
        "license": "[CC0 1.0 Universal](LICENSE).",
        "empty": "*기여를 환영합니다.*",
    },
    "es": {
        "tagline": "Lista curada de plantillas comunitarias de Grok Bot. Solo enlaces oficiales de compartir.",
        "intro": (
            "Un [Grok Bot](https://docs.x.ai/grok-bot/get-started) es un agente permanente de xAI. "
            "Quien lo posee puede publicar un enlace para que otras personas añadan una copia. "
            "Este repositorio es una lista awesome independiente de esas plantillas públicas."
        ),
        "disclaimer": (
            "No está afiliado a xAI. Cada ficha es un nombre, una línea de descripción, "
            "un handle público de Twitter si existe, y la URL oficial `https://x.ai/bot/…`. "
            "Esta lista no republica prompts, configuraciones empaquetadas, volcados de memoria ni secretos."
        ),
        "howto_h": "Cómo usar una ficha",
        "howto": (
            "1. Abre el enlace oficial (`https://x.ai/bot/…`).\n"
            "2. Elige **Add to Grok Bot** y confirma en la app de Grok Bot.\n"
            "3. Conecta los plugins que el bot necesite.\n"
            "\n"
            "Docs: [Get started](https://docs.x.ai/grok-bot/get-started) · [Bots](https://docs.x.ai/grok-bot/bots)"
        ),
        "contents": "Contenido",
        "related_h": "Relacionado",
        "related": (
            "- [Documentación de Grok Bot](https://docs.x.ai/grok-bot/get-started)\n"
            "- [Bots](https://docs.x.ai/grok-bot/bots)\n"
            "- [Host oficial de compartir](https://x.ai/bot)\n"
            "- [sindresorhus/awesome](https://github.com/sindresorhus/awesome)"
        ),
        "contrib_h": "Contribuir",
        "contrib": "Ver [CONTRIBUTING.md](CONTRIBUTING.md). La única URL obligatoria es un enlace real `https://x.ai/bot/…`.",
        "license_h": "Licencia",
        "license": "[CC0 1.0 Universal](LICENSE).",
        "empty": "*Se aceptan contribuciones.*",
    },
    "fr": {
        "tagline": "Liste curatée de modèles Grok Bot communautaires. Liens officiels uniquement.",
        "intro": (
            "Un [Grok Bot](https://docs.x.ai/grok-bot/get-started) est un agent xAI toujours actif. "
            "Son propriétaire peut publier un lien de partage pour qu’autrui ajoute une copie. "
            "Ce dépôt est une awesome list indépendante de ces modèles publics."
        ),
        "disclaimer": (
            "Sans affiliation avec xAI. Chaque entrée est un nom, une ligne de description, "
            "un compte Twitter public s’il existe, et l’URL officielle `https://x.ai/bot/…`. "
            "Cette liste ne republie ni prompts, ni configs empaquetées, ni dumps mémoire, ni secrets."
        ),
        "howto_h": "Utiliser une entrée",
        "howto": (
            "1. Ouvrez le lien officiel (`https://x.ai/bot/…`).\n"
            "2. Choisissez **Add to Grok Bot** et confirmez dans l’app Grok Bot.\n"
            "3. Connectez les plugins dont le bot a besoin.\n"
            "\n"
            "Docs : [Get started](https://docs.x.ai/grok-bot/get-started) · [Bots](https://docs.x.ai/grok-bot/bots)"
        ),
        "contents": "Sommaire",
        "related_h": "Liens",
        "related": (
            "- [Docs Grok Bot](https://docs.x.ai/grok-bot/get-started)\n"
            "- [Bots](https://docs.x.ai/grok-bot/bots)\n"
            "- [Hôte officiel de partage](https://x.ai/bot)\n"
            "- [sindresorhus/awesome](https://github.com/sindresorhus/awesome)"
        ),
        "contrib_h": "Contribuer",
        "contrib": "Voir [CONTRIBUTING.md](CONTRIBUTING.md). La seule URL exigée est un vrai lien `https://x.ai/bot/…`.",
        "license_h": "Licence",
        "license": "[CC0 1.0 Universal](LICENSE).",
        "empty": "*Les contributions sont les bienvenues.*",
    },
    "de": {
        "tagline": "Kuratierte Liste von Community-Grok-Bot-Vorlagen. Nur offizielle Share-Links.",
        "intro": (
            "Ein [Grok Bot](https://docs.x.ai/grok-bot/get-started) ist ein dauerhaft laufender xAI-Agent. "
            "Wer ihn besitzt, kann einen Share-Link veröffentlichen, damit andere eine Kopie hinzufügen. "
            "Dieses Repository ist eine unabhängige Awesome-Liste dieser öffentlichen Vorlagen."
        ),
        "disclaimer": (
            "Nicht verbunden mit xAI. Jeder Eintrag ist Name, eine Zeile Beschreibung, "
            "optional ein öffentlicher Twitter-Handle und die offizielle `https://x.ai/bot/…`-URL. "
            "Diese Liste hostet keine Prompts, gepackten Configs, Memory-Dumps oder Geheimnisse."
        ),
        "howto_h": "Einen Eintrag nutzen",
        "howto": (
            "1. Öffne den offiziellen Share-Link (`https://x.ai/bot/…`).\n"
            "2. Wähle **Add to Grok Bot** und bestätige in der Grok-Bot-App.\n"
            "3. Verbinde die Plugins, die der Bot braucht.\n"
            "\n"
            "Docs: [Get started](https://docs.x.ai/grok-bot/get-started) · [Bots](https://docs.x.ai/grok-bot/bots)"
        ),
        "contents": "Inhalt",
        "related_h": "Verwandt",
        "related": (
            "- [Grok-Bot-Docs](https://docs.x.ai/grok-bot/get-started)\n"
            "- [Bots](https://docs.x.ai/grok-bot/bots)\n"
            "- [Offizieller Share-Host](https://x.ai/bot)\n"
            "- [sindresorhus/awesome](https://github.com/sindresorhus/awesome)"
        ),
        "contrib_h": "Mitwirken",
        "contrib": "Siehe [CONTRIBUTING.md](CONTRIBUTING.md). Die einzige Pflicht-URL ist ein echter `https://x.ai/bot/…`-Share-Link.",
        "license_h": "Lizenz",
        "license": "[CC0 1.0 Universal](LICENSE).",
        "empty": "*Beiträge willkommen.*",
    },
    "pt-BR": {
        "tagline": "Lista curada de templates comunitários de Grok Bot. Só links oficiais de compartilhamento.",
        "intro": (
            "Um [Grok Bot](https://docs.x.ai/grok-bot/get-started) é um agente xAI sempre ativo. "
            "Quem o possui pode publicar um link para outras pessoas adicionarem uma cópia. "
            "Este repositório é uma awesome list independente desses templates públicos."
        ),
        "disclaimer": (
            "Sem vínculo com xAI. Cada item é nome, uma linha de descrição, "
            "handle público do Twitter se existir, e a URL oficial `https://x.ai/bot/…`. "
            "Esta lista não republica prompts, configs empacotados, dumps de memória nem segredos."
        ),
        "howto_h": "Como usar um item",
        "howto": (
            "1. Abra o link oficial (`https://x.ai/bot/…`).\n"
            "2. Escolha **Add to Grok Bot** e confirme no app Grok Bot.\n"
            "3. Conecte os plugins de que o bot precisa.\n"
            "\n"
            "Docs: [Get started](https://docs.x.ai/grok-bot/get-started) · [Bots](https://docs.x.ai/grok-bot/bots)"
        ),
        "contents": "Conteúdo",
        "related_h": "Relacionado",
        "related": (
            "- [Documentação do Grok Bot](https://docs.x.ai/grok-bot/get-started)\n"
            "- [Bots](https://docs.x.ai/grok-bot/bots)\n"
            "- [Host oficial de compartilhamento](https://x.ai/bot)\n"
            "- [sindresorhus/awesome](https://github.com/sindresorhus/awesome)"
        ),
        "contrib_h": "Contribuindo",
        "contrib": "Veja [CONTRIBUTING.md](CONTRIBUTING.md). A única URL obrigatória é um link real `https://x.ai/bot/…`.",
        "license_h": "Licença",
        "license": "[CC0 1.0 Universal](LICENSE).",
        "empty": "*Contribuições bem-vindas.*",
    },
    "ru": {
        "tagline": "Курируемый список шаблонов Grok Bot от сообщества. Только официальные ссылки.",
        "intro": (
            "[Grok Bot](https://docs.x.ai/grok-bot/get-started) — постоянно работающий агент xAI. "
            "Владелец может опубликовать ссылку, чтобы другие добавили копию. "
            "Этот репозиторий — независимый awesome-список таких публичных шаблонов."
        ),
        "disclaimer": (
            "Не связан с xAI. Каждая запись — имя, одна строка описания, "
            "публичный Twitter, если он есть, и официальный URL `https://x.ai/bot/…`. "
            "Список не перепубликует промпты, упакованные конфиги, дампы памяти и секреты."
        ),
        "howto_h": "Как пользоваться записью",
        "howto": (
            "1. Откройте официальную ссылку (`https://x.ai/bot/…`).\n"
            "2. Выберите **Add to Grok Bot** и подтвердите в приложении Grok Bot.\n"
            "3. Подключите нужные плагины.\n"
            "\n"
            "Документация: [Get started](https://docs.x.ai/grok-bot/get-started) · [Bots](https://docs.x.ai/grok-bot/bots)"
        ),
        "contents": "Содержание",
        "related_h": "Связанное",
        "related": (
            "- [Документация Grok Bot](https://docs.x.ai/grok-bot/get-started)\n"
            "- [Bots](https://docs.x.ai/grok-bot/bots)\n"
            "- [Официальный хост ссылок](https://x.ai/bot)\n"
            "- [sindresorhus/awesome](https://github.com/sindresorhus/awesome)"
        ),
        "contrib_h": "Участие",
        "contrib": "См. [CONTRIBUTING.md](CONTRIBUTING.md). Единственный обязательный URL — настоящая ссылка `https://x.ai/bot/…`.",
        "license_h": "Лицензия",
        "license": "[CC0 1.0 Universal](LICENSE).",
        "empty": "*Приглашаем дополнения.*",
    },
}


def slugify(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^\w\s/-]", "", s).replace("/", "")
    return re.sub(r"-+", "-", re.sub(r"\s+", "-", s.strip()))


def switcher(current: str) -> str:
    parts = []
    for code, label, path in LANGS:
        parts.append(f"**{label}**" if code == current else f"[{label}]({path})")
    return " · ".join(parts)


def share_id(share_url: str) -> str:
    return share_url.removeprefix("https://x.ai/bot/")


def listing_line(item: dict) -> str:
    line = f"- [{item['name']}]({item['share_url']}) — {item['description']}"
    handle = item.get("twitter")
    if handle:
        handle = handle.lstrip("@")
        line += f" [@{handle}](https://x.com/{handle})"
    return line


def render(lang: str, items: list[dict]) -> str:
    t = COPY[lang]
    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        grouped[item["category"]].append(item)
    for cat in grouped:
        grouped[cat].sort(key=lambda x: (x["name"].casefold(), x["share_url"]))

    lines = [
        "# Awesome Grok Bot Templates [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)",
        "",
        f"> {t['tagline']}",
        "",
        switcher(lang),
        "",
        t["intro"],
        "",
        t["disclaimer"],
        "",
        f"## {t['howto_h']}",
        "",
        t["howto"],
        "",
        f"## {t['contents']}",
        "",
    ]
    labels = CATEGORY_LABELS[lang]
    for cat in CATEGORIES:
        label = labels[cat]
        n = len(grouped[cat])
        suffix = f" ({n})" if n else ""
        lines.append(f"- [{label}](#{slugify(label)}){suffix}")
    lines += [
        f"- [{t['related_h']}](#{slugify(t['related_h'])})",
        f"- [{t['contrib_h']}](#{slugify(t['contrib_h'])})",
        "",
    ]
    for cat in CATEGORIES:
        label = labels[cat]
        lines += [f"## {label}", ""]
        rows = grouped[cat]
        if not rows:
            lines += [t["empty"], ""]
            continue
        for item in rows:
            lines.append(listing_line(item))
        lines.append("")
    lines += [
        f"## {t['related_h']}",
        "",
        t["related"],
        "",
        f"## {t['contrib_h']}",
        "",
        t["contrib"],
        "",
        f"## {t['license_h']}",
        "",
        t["license"],
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    payload = json.loads((ROOT / "data" / "templates.json").read_text())
    items = payload.get("templates") or []
    for code, _label, filename in LANGS:
        (ROOT / filename).write_text(render(code, items))
    print(f"wrote {len(LANGS)} READMEs ({len(items)} listings)")


if __name__ == "__main__":
    main()
