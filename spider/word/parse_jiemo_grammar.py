import re

from u_base import u_log
from u_base import u_file
from db import Grammar, save_grammar


def parse_grammar_json(file_path: str):
    grammar_categories = u_file.load_json_from_file(file_path)
    if not grammar_categories or not 'data' in grammar_categories:
        u_log.warn('The grammar json is invalid: {}'.format(str))
        return

    u_log.info('load grammar json success. category size: {}'.format(len(grammar_categories)))
    grammar_categories = grammar_categories.get('data')
    for grammar_category in grammar_categories:
        u_log.info('parse grammar category: {}'.format(grammar_category.get('title')))
        if grammar_category.get('title') != grammar_category.get('label'):
            u_log.warn('The grammar title and label is not same.')
        grammars = grammar_category.get('grammerList')
        u_log.info('parse grammar category sub grammar. category: {}, grammar size: {}'
                   .format(grammar_category.get('title'), len(grammars)))
        for grammar in grammars:
            if grammar.get('explain') != grammar.get('comment') or grammar.get('type') != grammar.get('category') \
                    or grammar.get('category') != grammar_category.get('title'):
                u_log.warn('The grammar category is special. grammar: {}'.format(grammar.get('grammar')))
            u_log.info('get grammar: {}'.format(grammar.get('grammar')))
            db_grammar = Grammar(id=grammar.get('id'), content=grammar.get('content'))
            db_grammar.level = grammar.get('level')
            db_grammar.category = grammar.get('category')
            db_grammar.type = grammar.get('category')
            db_grammar.link = grammar.get('link')
            db_grammar.explain = grammar.get('explain')
            db_grammar.example = re.sub('[#@][0-9]*', '', grammar.get('exmple'))
            db_grammar.postscript = grammar.get('ps')
            save_grammar(db_grammar)


if __name__ == '__main__':
    grammar_json_file_path = r'./data/grammar-n5.json'
    parse_grammar_json(grammar_json_file_path)
