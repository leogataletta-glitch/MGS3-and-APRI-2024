"""Local display translations. Source labels, widget values and data stay intact.

Spanish and Haitian Creole packs are machine-assisted editorial drafts. No
network request is made when someone visits the site.
"""
import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent / 'data'


@lru_cache(maxsize=3)
def _load(name):
    path = ROOT / name
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding='utf8'))


def text(value, lang=None):
    if not isinstance(value, str) or not value:
        return value
    if lang is None:
        import i18n
        lang = i18n.get_lang()
    if lang not in ('es', 'ht'):
        return value
    table = _load(f'interface_{lang}.json')
    source = value if value in table else _load('translation_aliases.json').get(value, value)
    return table.get(source, value)


def display_tree(value, lang):
    """Translate public presentation values, preserving structure and all keys."""
    if isinstance(value, dict):
        return {key: display_tree(item, lang) for key, item in value.items()}
    if isinstance(value, list):
        return [display_tree(item, lang) for item in value]
    return text(value, lang)


def formatter(original):
    """Localize a widget's label without translating its stored option value."""
    import i18n
    lang = i18n.get_lang()
    labels = {}
    def label(value):
        key = repr(value)
        if key not in labels:
            labels[key] = text(original(value), lang)
        return labels[key]
    return label


def component_html(markup):
    """Translate labels inside our own map/game iframes, including dynamic labels."""
    import i18n
    lang = i18n.get_lang()
    if lang not in ('es', 'ht') or not isinstance(markup, str):
        return markup
    table = _load(f'interface_{lang}.json')
    words = {source: value for source, value in table.items()
             if source and (source in markup or (len(source) < 100 and source.split('${')[0] in markup))}
    for source, english in _load('translation_aliases.json').items():
        if source and source in markup and english in table:
            words[source] = table[english]
    payload = json.dumps(words, ensure_ascii=False).replace('<', '\\u003c')
    script = r'''<script>(function(){
const words=__WORDS__;
const translatedValues=new Set(Object.values(words).map(v=>v.trim())),lastValue=new WeakMap();
const esc=s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
const patterns=Object.entries(words).filter(([s])=>/\$\{[^{}]+\}/.test(s)).map(([s,v])=>{
 const pieces=s.split(/(\$\{[^{}]+\})/g),slots=pieces.filter(x=>/^\$\{/.test(x));
 return {rx:new RegExp('^'+pieces.map(x=>/^\$\{/.test(x)?'(.+?)':esc(x)).join('')+'$'),slots,value:v};
});
window.__apriText=function(value){
 if(typeof value!=='string')return value;
 if(Object.hasOwn(words,value))return words[value];
 const trimmed=value.trim();
 if(Object.hasOwn(words,trimmed))return value.replace(trimmed,words[trimmed]);
 for(const p of patterns){const m=value.match(p.rx);if(m){let out=p.value;p.slots.forEach((s,i)=>out=out.replace(s,m[i+1]));return out;}}
 return value;
};
const skip=new Set(['SCRIPT','STYLE','CODE','PRE','TEXTAREA']);
function visit(node){
 if(node.nodeType===3){if(node.parentElement&&!skip.has(node.parentElement.tagName)&&lastValue.get(node)!==node.data&&!translatedValues.has(node.data.trim())){const t=window.__apriText(node.data);if(t!==node.data){lastValue.set(node,t);node.data=t;}}return;}
 if(node.nodeType!==1||skip.has(node.tagName))return;
 for(const attr of ['title','aria-label','placeholder','alt']){if(node.hasAttribute(attr)){const old=node.getAttribute(attr),t=window.__apriText(old);if(t!==old)node.setAttribute(attr,t);}}
 for(const child of node.childNodes)visit(child);
}
const observer=new MutationObserver(records=>{for(const r of records){if(r.type==='characterData')visit(r.target);else for(const n of r.addedNodes)visit(n);}});
observer.observe(document.documentElement,{subtree:true,childList:true,characterData:true});
visit(document.documentElement);
})();</script>'''.replace('__WORDS__', payload)
    first = re.search(r'<script\b', markup, re.I)
    return markup[:first.start()] + script + markup[first.start():] if first else markup + script
