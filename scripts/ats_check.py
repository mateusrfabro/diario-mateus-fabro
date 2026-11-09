"""Confere se um currículo em PDF ou DOCX passa num ATS (Gupy, Workday, Greenhouse, LinkedIn) e mede a aderência a uma vaga.

O ATS não vê o desenho: lê o texto que sai do PDF. Este script lê o PDF do mesmo jeito (pypdf) e confere o que
costuma derrubar a triagem: texto não extraível, contato faltando, seção com nome fora do padrão, data ambígua,
palavras coladas por tabela/coluna, e (com --vaga) as palavras-chave da vaga que o currículo não tem.

Uso:
  python scripts/ats_check.py public/curriculo/mateus-fabro-pt.pdf
  python scripts/ats_check.py CV.pdf --vaga vaga.txt          # vaga.txt = texto da vaga colado
Saída: relatório + exit 0 (ok), 1 (problema de leitura). Palavra-chave faltando não é erro: é lista para decidir.
Regra: só acrescente ao currículo palavra-chave que você USOU de verdade.
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

SECOES = {
    "pt": ["resumo", "experiencia", "formacao", "competencias", "idiomas"],
    "en": ["summary", "experience", "education", "skills", "languages"],
}
# Termos de vaga de dados/tecnologia que o ATS costuma filtrar. Comparação sem acento e sem caixa.
TERMOS = [
    "python", "sql", "typescript", "javascript", "r", "scala", "java", "spark", "pyspark", "databricks", "airflow",
    "prefect", "dbt", "kafka", "etl", "elt", "data lake", "data warehouse", "lakehouse", "iceberg", "delta lake",
    "aws", "azure", "gcp", "bigquery", "redshift", "snowflake", "athena", "s3", "glue", "lambda", "ec2", "postgresql",
    "mysql", "mongodb", "redis", "docker", "kubernetes", "terraform", "git", "ci/cd", "power bi", "tableau",
    "looker", "metabase", "excel", "pandas", "numpy", "scikit-learn", "machine learning", "deep learning", "llm",
    "ia generativa", "generative ai", "nlp", "estatistica", "statistics", "modelagem de dados", "data modeling",
    "modelagem dimensional", "dimensional modeling", "api", "rest", "fastapi", "flask", "django", "next.js", "react",
    "node.js", "nestjs", "linux", "bash", "dashboards", "kpi", "a/b", "antifraude", "fraud", "credito", "credit",
    "atribuicao", "attribution", "marketing", "crm", "lgpd", "gdpr", "governanca de dados", "data governance",
    "qualidade de dados", "data quality", "pipeline", "pipelines", "streaming", "batch", "observabilidade",
    "agile", "scrum", "ingles", "english", "espanhol", "spanish",
]


def norm(t: str) -> str:
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", t)


def tem(termo: str, texto: str) -> bool:
    return re.search(rf"(?<![a-z0-9]){re.escape(termo)}(?![a-z0-9])", texto) is not None


def texto_pdf(caminho: Path) -> tuple[str, int]:
    """Texto como o ATS vê. .docx: parágrafos (páginas estimadas por ~4.000 caracteres)."""
    if caminho.suffix.lower() == ".docx":
        from docx import Document
        t = "\n".join(x.text for x in Document(str(caminho)).paragraphs)
        return t, max(1, -(-len(t) // 4000))
    import pypdf
    r = pypdf.PdfReader(str(caminho))
    return "\n".join(p.extract_text() or "" for p in r.pages), len(r.pages)


def checar(caminho: Path, vaga: str | None = None) -> tuple[list[str], list[str], list[str]]:
    """Devolve (erros, avisos, linhas do relatório)."""
    bruto, paginas = texto_pdf(caminho)
    t = norm(bruto)
    lang = "pt" if sum(tem(s, t) for s in SECOES["pt"]) >= sum(tem(s, t) for s in SECOES["en"]) else "en"
    erros, avisos, rel = [], [], [f"{caminho.name}: {paginas} página(s), {len(bruto)} caracteres, idioma {lang}"]
    if len(bruto.strip()) < 800:
        erros.append("pouco ou nenhum texto extraível: PDF de imagem/escaneado, o ATS lê vazio")
    if paginas > 2:
        avisos.append(f"{paginas} páginas: o recrutador lê 2; corte")
    if not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", bruto):
        erros.append("e-mail não encontrado no texto")
    if not re.search(r"\+?\d[\d ()-]{8,}\d", bruto):
        avisos.append("telefone não encontrado (normal só na versão pública)")
    if "linkedin.com/in/" not in t:
        avisos.append("URL do LinkedIn não aparece como texto (link escondido atrás de palavra não é lido)")
    faltam = [s for s in SECOES[lang] if not tem(s, t)]
    if faltam:
        erros.append(f"seções padrão ausentes: {', '.join(faltam)}")
    if not re.search(r"\b(0[1-9]|1[0-2])/(19|20)\d\d\b", bruto):
        avisos.append("nenhuma data MM/AAAA: o ATS pode não calcular o tempo de experiência")
    colados = sorted({m for m in re.findall(r"\b[a-zà-ú]{3,}[A-ZÀ-Ú][a-zà-ú]+\b", bruto)} - {"iGaming", "eSports"})
    if colados:
        avisos.append(f"palavras coladas (tabela/coluna?): {', '.join(colados[:6])}")
    if vaga:
        v = norm(vaga)
        pedidos = [k for k in TERMOS if tem(k, v)]
        ok = [k for k in pedidos if tem(k, t)]
        falta = [k for k in pedidos if not tem(k, t)]
        if pedidos:
            rel.append(f"aderência à vaga: {len(ok)}/{len(pedidos)} termos ({100 * len(ok) // len(pedidos)}%)")
            rel.append("  tem: " + ", ".join(ok))
            rel.append("  falta (acrescente SÓ se você usou): " + (", ".join(falta) or "nada"))
        else:
            rel.append("aderência à vaga: nenhum termo conhecido na vaga; compare manualmente")
    return erros, avisos, rel


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pdfs", nargs="+", type=Path)
    ap.add_argument("--vaga", type=Path, help="arquivo .txt com o texto da vaga")
    a = ap.parse_args(argv)
    vaga = a.vaga.read_text(encoding="utf-8") if a.vaga else None
    falhou = False
    for p in a.pdfs:
        erros, avisos, rel = checar(p, vaga)
        print("\n".join(rel))
        for x in erros:
            print(f"  ERRO  {x}")
        for x in avisos:
            print(f"  aviso {x}")
        if not erros and not avisos:
            print("  ok: leitura limpa")
        falhou |= bool(erros)
    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(main())
