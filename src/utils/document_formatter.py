from typing import Dict, List, Any
from bs4 import BeautifulSoup
import json

class DocumentFormatter:
    """Class for document formatting and conversion"""
    
    @staticmethod
    def to_html(data: Dict[str, Any], include_styles: bool = True) -> str:
        """Convert processed document data to HTML format"""
        # Basic CSS styles
        styles = """
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #2C3E50; }
            table { border-collapse: collapse; margin: 10px 0; width: 100%; }
            th, td { border: 1px solid #BDC3C7; padding: 8px; text-align: left; }
            th { background-color: #F5F6FA; }
            .term { background-color: #E8F0FE; padding: 2px 4px; border-radius: 3px; }
            .measurement { color: #2980B9; }
            .date { color: #27AE60; }
            .abbreviation { font-weight: bold; }
            .metadata { color: #7F8C8D; font-size: 0.9em; }
        </style>
        """ if include_styles else ""
        
        # Start HTML document
        html = f"""<html>
        <head>
            <meta charset="utf-8">
            {styles}
        </head>
        <body>"""
        
        # Add metadata if available
        if 'metadata' in data:
            html += '<div class="metadata">'
            for key, value in data['metadata'].items():
                html += f'<p><strong>{key}:</strong> {value}</p>'
            html += '</div>'
        
        # Add main text with highlighted terms
        if 'text' in data:
            text = data['text']
            
            # Highlight terms
            if 'terms' in data:
                for term in data['terms']:
                    text = text.replace(
                        term['term'],
                        f'<span class="term" title="{term.get("definition", "")}">{term["term"]}</span>'
                    )
            
            html += f'<div class="content">{text}</div>'
        
        # Add tables if present
        if 'tables' in data and data['tables']:
            html += '<h2>Таблицы:</h2>'
            for table in data['tables']:
                html += '<table>'
                for i, row in enumerate(table):
                    html += '<tr>'
                    cell_tag = 'th' if i == 0 else 'td'
                    for cell in row:
                        html += f'<{cell_tag}>{cell}</{cell_tag}>'
                    html += '</tr>'
                html += '</table>'
        
        # Close HTML document
        html += '</body></html>'
        
        return html
    
    @staticmethod
    def to_json(data: Dict[str, Any], pretty: bool = True) -> str:
        """Convert processed document data to JSON format"""
        return json.dumps(data, ensure_ascii=False, indent=2 if pretty else None)
    
    @staticmethod
    def to_plain_text(data: Dict[str, Any], include_metadata: bool = True) -> str:
        """Convert processed document data to plain text format"""
        text_parts = []
        
        # Add metadata if requested
        if include_metadata and 'metadata' in data:
            text_parts.append('МЕТАДАННЫЕ:')
            for key, value in data['metadata'].items():
                text_parts.append(f'{key}: {value}')
            text_parts.append('\n')
        
        # Add main text
        if 'text' in data:
            text_parts.append('ТЕКСТ:')
            text_parts.append(data['text'])
            text_parts.append('\n')
        
        # Add tables
        if 'tables' in data and data['tables']:
            text_parts.append('ТАБЛИЦЫ:')
            for i, table in enumerate(data['tables'], 1):
                text_parts.append(f'\nТаблица {i}:')
                for row in table:
                    text_parts.append('\t'.join(str(cell) for cell in row))
                text_parts.append('')
        
        # Add terms
        if 'terms' in data and data['terms']:
            text_parts.append('МЕДИЦИНСКИЕ ТЕРМИНЫ:')
            for term in data['terms']:
                text_parts.append(f"- {term['term']}")
                if 'definition' in term and term['definition']:
                    text_parts.append(f"  Определение: {term['definition']}")
                if 'context' in term and term['context']:
                    text_parts.append(f"  Контекст: {term['context']}")
                text_parts.append('')
        
        return '\n'.join(text_parts)
    
    @staticmethod
    def to_markdown(data: Dict[str, Any]) -> str:
        """Convert processed document data to Markdown format"""
        md_parts = []
        
        # Add metadata
        if 'metadata' in data:
            md_parts.append('# Метаданные\n')
            for key, value in data['metadata'].items():
                md_parts.append(f'**{key}:** {value}  ')
            md_parts.append('\n')
        
        # Add main text
        if 'text' in data:
            md_parts.append('# Текст\n')
            md_parts.append(data['text'])
            md_parts.append('\n')
        
        # Add tables
        if 'tables' in data and data['tables']:
            md_parts.append('# Таблицы\n')
            for table in data['tables']:
                # Add header row
                md_parts.append('| ' + ' | '.join(str(cell) for cell in table[0]) + ' |')
                # Add separator
                md_parts.append('| ' + ' | '.join(['---' for _ in table[0]]) + ' |')
                # Add data rows
                for row in table[1:]:
                    md_parts.append('| ' + ' | '.join(str(cell) for cell in row) + ' |')
                md_parts.append('\n')
        
        # Add terms
        if 'terms' in data and data['terms']:
            md_parts.append('# Медицинские термины\n')
            for term in data['terms']:
                md_parts.append(f"* **{term['term']}**")
                if 'definition' in term and term['definition']:
                    md_parts.append(f"  * Определение: {term['definition']}")
                if 'context' in term and term['context']:
                    md_parts.append(f"  * Контекст: ```{term['context']}```")
                md_parts.append('')
        
        return '\n'.join(md_parts)