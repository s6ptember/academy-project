from django import template
from django.utils.safestring import mark_safe
import re
import html

register = template.Library()

@register.filter
def format_text(text):
    """
    Форматирует текст, применяя Tailwind CSS стили к Markdown-подобному синтаксису.
    Адаптирован для мобильных устройств с отзывчивыми размерами шрифтов и отступов.
    Корректно обрабатывает многострочные блоки кода и добавляет кнопку копирования.
    """
    # Сначала находим и временно заменяем блоки кода плейсхолдерами
    code_blocks = []
    
    def store_code_block(match):
        lang = match.group(1) or 'plain'
        code = match.group(2).rstrip('\n').lstrip('\n')
        # Экранируем HTML-символы только для отображения
        display_code = html.escape(code)
        # Для копирования сохраняем исходный код без изменений
        encoded_code = html.escape(code).replace('"', '&quot;').replace('\n', '\\n')
        
        code_html = (
            f'<div class="relative fade-in visible transition-all duration-500">'
            f'<pre class="bg-gray-950 text-gray-200 border border-emerald-900 rounded-xl p-3 sm:p-4 mb-4 sm:mb-6 overflow-x-auto shadow-xl">'
            f'<code class="language-{lang}">{display_code}</code>'
            f'</pre>'
            f'<button class="absolute top-2 right-2 bg-emerald-600 text-white text-xs sm:text-sm px-1.5 sm:px-2 py-0.5 sm:py-1 rounded-md hover:bg-emerald-700 transition-colors duration-200 copy-code-btn" '
            f'data-code="{encoded_code}" title="Скопировать код">'
            f'<svg class="w-3 h-3 sm:w-4 sm:h-4 inline-block mr-0.5 sm:mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">'
            f'<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>'
            f'</svg>Копировать'
            f'</button>'
            f'</div>'
        )
        
        placeholder = f"__CODE_BLOCK_{len(code_blocks)}__"
        code_blocks.append(code_html)
        return placeholder

    # 1. Временно заменяем многострочные блоки кода
    text = re.sub(
        r'^```(\w+)?\s*\n([\s\S]*?)\n\s*```',
        store_code_block,
        text,
        flags=re.MULTILINE
    )

    # 2. Вложенные списки
    text = re.sub(
        r'^\s{2,4}-\s+\[(.+)\]\s*$',
        r'<li class="list-inside list-square ml-6 sm:ml-8 text-gray-300 mt-0.5 sm:mt-1 fade-in visible delay-250">\1</li>',
        text,
        flags=re.MULTILINE
    )
    text = re.sub(
        r'^-\s*(.+)$',
        r'<li class="list-disc ml-4 sm:ml-6 text-gray-200 font-medium mt-0.5 sm:mt-1 fade-in visible delay-200">\1</li>',
        text,
        flags=re.MULTILINE
    )
    text = re.sub(
        r'(<li class="list-(disc|square)[^>]*>.+?</li>\s*)+',
        r'<ul class="mb-4 sm:mb-6 pl-2 sm:pl-4 space-y-1 sm:space-y-2">\g<0></ul>',
        text,
        flags=re.DOTALL
    )

    # 3. Заголовок 1 (# Заголовок)
    text = re.sub(
        r'^# (.+)$',
        r'<h1 class="text-3xl sm:text-4xl md:text-5xl font-extrabold mb-4 sm:mb-6 bg-gradient-to-r from-emerald-400 to-cyan-600 bg-clip-text text-transparent transition-all duration-300 hover:scale-102 shadow-md fade-in visible">\1</h1>',
        text,
        flags=re.MULTILINE
    )

    # 4. Заголовок 2 (## Заголовок)
    text = re.sub(
        r'^## (.+)$',
        r'<h2 class="text-xl sm:text-2xl md:text-3xl font-bold mb-3 sm:mb-4 text-white border-l-4 border-emerald-500 pl-3 sm:pl-4 py-1 sm:py-2 transition-colors duration-300 hover:text-emerald-300 fade-in visible delay-100">\1</h2>',
        text,
        flags=re.MULTILINE
    )

    # 5. Заголовок 3 (### Заголовок)
    text = re.sub(
        r'^### (.+)$',
        r'<h3 class="text-lg sm:text-xl md:text-2xl font-semibold mb-2 sm:mb-3 text-gray-100 transition-all duration-300 hover:text-emerald-400 fade-in visible delay-150">\1</h3>',
        text,
        flags=re.MULTILINE
    )

    # 6. Жирный текст (**текст**)
    text = re.sub(
        r'\*\*(.+?)\*\*',
        r'<strong class="font-extrabold text-emerald-300 transition-colors duration-200">\1</strong>',
        text
    )

    # 7. Курсив (*текст*)
    text = re.sub(
        r'\*(.+?)\*',
        r'<em class="italic text-gray-300 transition-colors duration-200 hover:text-emerald-400">\1</em>',
        text
    )

    # 8. Аннотация (> текст)
    text = re.sub(
        r'^> (.+)$',
        r'<blockquote class="border-l-4 border-emerald-600 bg-gray-800/30 pl-4 sm:pl-6 py-2 sm:py-3 mb-4 sm:mb-6 text-gray-200 italic rounded-r-lg shadow-lg transition-transform duration-300 hover:scale-102 fade-in visible delay-200">\1</blockquote>',
        text,
        flags=re.MULTILINE
    )

    # 9. Однострочный код (`код`)
    text = re.sub(
        r'`(.+?)`',
        r'<code class="bg-gray-800 text-emerald-200 rounded-md px-1.5 sm:px-2 py-0.5 sm:py-1 text-sm sm:text-base shadow-sm transition-transform duration-200 hover:scale-105">\1</code>',
        text
    )

    # 10. Ссылка ([текст](url))
    text = re.sub(
        r'\[(.+?)\]\((.+?)\)',
        r'<a href="\2" class="bg-gradient-to-r from-emerald-400 to-cyan-600 text-transparent bg-clip-text font-medium relative after:absolute after:bottom-0 after:left-0 after:w-0 after:h-0.5 after:bg-emerald-400 after:transition-all after:duration-300 hover:after:w-full">\1</a>',
        text
    )

    # 11. Абзац (любой текст, не начинающийся с #, >, -, *, ``` и не являющийся плейсхолдером)
    text = re.sub(
        r'^(?!#|>|-\s|\*|```|__CODE_BLOCK_).+?$',
        r'<p class="mb-4 sm:mb-6 text-gray-200 text-sm sm:text-base leading-relaxed transition-opacity duration-300 fade-in visible delay-100">\g<0></p>',
        text,
        flags=re.MULTILINE
    )

    # 12. Возвращаем блоки кода на место
    for i, code_html in enumerate(code_blocks):
        text = text.replace(f"__CODE_BLOCK_{i}__", code_html)

    return mark_safe(text)