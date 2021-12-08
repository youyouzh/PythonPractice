import json
import re
import requests
import hashlib
import gzip
from Crypto.Cipher import AES
from Crypto import Random
from binascii import b2a_hex, a2b_hex
import base64
from u_base import u_log as log
from u_base import u_file
from spider.word.database.db import Grammar, save_grammar


def parse_and_save_jiemo_grammar_json(file_path: str):
    grammar_categories = u_file.load_json_from_file(file_path)
    if not grammar_categories or not 'data' in grammar_categories:
        log.warn('The grammar json is invalid: {}'.format(str))
        return

    log.info('load grammar json success. category size: {}'.format(len(grammar_categories)))
    grammar_categories = grammar_categories.get('data')
    for grammar_category in grammar_categories:
        log.info('parse grammar category: {}'.format(grammar_category.get('title')))
        if grammar_category.get('title') != grammar_category.get('label'):
            log.warn('The grammar title and label is not same.')
        grammars = grammar_category.get('grammerList')
        log.info('parse grammar category sub grammar. category: {}, grammar size: {}'
                   .format(grammar_category.get('title'), len(grammars)))
        for grammar in grammars:
            if grammar.get('explain') != grammar.get('comment') or grammar.get('type') != grammar.get('category') \
                    or grammar.get('category') != grammar_category.get('title'):
                log.warn('The grammar category is special. grammar: {}'.format(grammar.get('grammar')))
            log.info('get grammar: {}'.format(grammar.get('grammar')))
            db_grammar = Grammar(id=grammar.get('id'), content=grammar.get('content'))
            db_grammar.level = grammar.get('level')
            db_grammar.category = grammar.get('category')
            db_grammar.type = grammar.get('category')
            db_grammar.link = grammar.get('link')
            db_grammar.explain = grammar.get('explain')
            db_grammar.example = re.sub('[#@][0-9]*', '', grammar.get('exmple'))
            db_grammar.postscript = grammar.get('ps')
            save_grammar(db_grammar)


def query_hujiang_word(word: str, from_lang='cn', to_lang='jp') -> dict:
    api_url = 'http://dict.hjapi.com/v10/quick/{}/{}'.format(from_lang, to_lang)
    sign_str = 'FromLang={}&ToLang={}&Word={}&Word_Ext=3be65a6f99e98524e21e5dd8f85e2a9b'\
        .format(from_lang, to_lang, word).encode(encoding='UTF-8')
    response = requests.post(
        api_url,
        data={
            "word": word,
            "word_ext": None
        },
        headers={
            "User-Agent": u_file.COMMON_USER_AGENT,
            "hujiang-appkey": "b458dd683e237054f9a7302235dee675",
            "hujiang-appsign": hashlib.md5(sign_str).hexdigest()
        },
    )
    log.info('end get info from web url: ' + api_url)
    if not (400 <= response.status_code < 500):
        response.raise_for_status()
    if response.text is None or response.text == '':
        log.error('The response text is empty.')
    query_result = json.loads(response.text)
    if 'data' not in query_result or query_result.get('status', -1) != 0:
        log.error('The response is not valid: {}'.format(response.text))
        return {}
    return query_result['data']


def hujiang_des_cbc():
    encode_data = '6DzM+js3y1hEpVVP0YSz5SslWCiMqYlTTf8G3LJlnJh1fQQVYkdBcajsWAf+rE0v/S3HHqjaXzyp\nKIefaU1EbnzTAveYrO5Xk5+uXH3GEjbNOqE/G6tsREBGNs7o0OyVUU52p/Ir4+q4nfgpK/dqoCfW\n2lVrq9zLQyKDLIe5UMoVWY8PD0YkZuP8Kc1BDNQvC5dmEJoixFxqnYuMT/YkzKshH+8mRa1o5xmv\nWyl3rD65kZlGEsuse0XXuGcnH67XIOTvSj55XxSJE6Bbx93K33lZexGieKvUAHCooTD6WuJabw87\nU1yHWbUtKou5cPD3gPM6ybq9cNnAEo49vVHPxiV47ZmUt+soiz3x7KoEQSol4BK9RaV6pVT/cIxj\nUuFd7ry3K/ua2nVbondMhYhwRKeIsvUH+bIIHL3588weZaNnPBWrfBWA/2BmZ7w5mLcGROYwMhr5\njWlC1i2kiulK2U3Je3mbWguVj8LS0aOE10tzdObMrAbA0pzLQQrVHOBeLfuRaW/HGcThT0yxyq1I\nX+A8zk2rtg+QAWnOEio+ud+IWrPKdxLxBET+L7hAi83wqJjbMlYdAgOYt6lZTVhyb4d9d56ZxWCw\nv93rRGtbU7TsaFVT0LM/o2elptSBiu3ehcsD3I4HxMdhon+cTViag2LDhOPA/wjj8gf+xdOiLOar\np/FfrSg384y5qFYM/zeF7Q3oWE3D8OBXrft0c/GrPd6icSqMhWRbQzvakjr7LcKItS1PKEJ9qsGZ\n5qKtH3EI9guL8aCnSd8zkHz0oULlELaQd6XHSlOXxNgSkAGOASr/YuOmgWBBwxlORgEgsdf0qlSR\nZOlYI46kbE/LdfNjubmW6e24ltO+5FtLhcLegXHSxUw6IBg5esi1Xsr1IAvIP/f22C3AwVOVy4bU\nVdIigc+fRubB25+gZeuWcxot8rcOU8xYiToLrwgrN8WJeCsSe7AQmEiD9edpPvcq3+OMVLCD0bCx\nlDcH4n35QrR+BHd52Gu0JUVOWaiA5daXx5jb4RJkSUCmiZjPBvKuhM0z4zK26QtnjlDORpqFxfXx\nrPlY/kTWGGvLMuCxgdsrH+gyRQS5VwjW5aqBrMTpBnm5fit94f92ewnaME0BBomTZi36jcpNZ/Wx\n50zlW/2ORQf0h8t+FHA+7+iF0RnJfDpAxl9X+I7Psp2tL14Bfo+NTGL5toQLaIA6KcA+oMGDP1Bm\nTHkktiyiFGZXiCMueWS/x/AlUlDnQgiHnB6GS18Q8lIs+SBE+bqgOn57AlIWPccKrMTuJ5SjDBkE\nnmW0TvbT4PMk3RyBX5CcloqO3SfsEdma7EGr2DlkTnwT8nGZoy/ny5JJBm3sCPvkjipIQj0rQ5DW\nPy7WxJiS1BtKtOU9wXOgehsHE58pFln+PYJnI2hyqcDO4Pk4BcjgNiejJfytGrjeP+eJT8SO1jiO\nvuM57DzQ1N9fIxJLqH5lw2aIoeV+FeKtK5SzQk9Sp+aZ3SsKLQilXEnNEGMq9KeVirrcuDcz+Kek\n6+mjNTsuFsIMLXFvrvrIedOyye0ceJ0E2AjwYG3a2CSHJiJhTcFefyJApddlCZRKn1KKTaZ+A5Fg\nmW38nc0oB+SxV7lYwIrY4wjyttb4OnuYElazouZXVD61uwM+xZynqcDAKpEx8IDPIPzmgXOYnoCk\nm/SpJbHCM1YriMlyWIIDBePr6GdW2x54bW/L6KHFsBAuEdH/PBjHFoRIXKaO59h/mEV9JGkG3WBI\nfYoDsT91h/nfbcFl/AC1zmRcLlk67f3zJr4AUJQ6O/X+w1NNLfW9m7/n97vtVxvm8XidT/46DDv/\nnLXfiDzEAgax14v7xYn4V8YnTCGB2a/NGTjpkNektMG3T78IP0S7LtHWDVqBW7GA/7eVdDkygklh\nyLgJDqZ40pFS0c3glTUiJqOjsvV1go1HTVXsVH8hT0rhy/yNmuwJZ+t2NWuTtzbJ5sv7nAnamS6C\nO1DIo7cACU1PpJL1C/rdhjve+xjt6Hgb3R2tyV93Ym3WvtKfi92yXNtFwOqgws6bW1YkDv0o7fVv\nVH6yNk7CG8em/lpfVmW2Yz21SVdx1jxdaOAFQay/OqPvw08/sm/LAr9BrfW2N0Ev8FmHNQ8UWXCR\n0l5879fHv5lkjLshFMVM+8hfLHeYDeKBcAGgDCCPUrfjYXVzAFTU64lTEOrvLVSr7pOdz+P6TaZ2\n4pa4Rm6LJrz2gyr8rM4xM/T++WP13Gs3NIdVHGT4CJJj7JmsAYatWk+TagUp3QAgXDD3NVHFbFXH\n2RA9GIEN9uBM8UuWLjmEGcowvI4T7dKE8rAFeRLx7HQKppWsWYsJZuxCzoDqZLOkSluzXisFBCKq\n6aRGBEjX1WP8RxIqUfT4op42b9k2LOmfoBtTA/XWEW/dIPkw9IEFMwqwWIhadSkqEFdU0+883dZp\n09ZeAEi6vFfWXXWbcAt1Li2HbXtgsCHFlEFbt+FILDrSdKcnf7w6kwuwb7LGnx9A7pqhBkqCilZC\nPGtVnqQG+HdAyKgkMWtebxDUrgdoFqKOuS0NQWxjdHdgLFyDIWBb8vZ3M0plVCzwAPz5xdXj/tAK\nbBrPgpqSA01i2lwwWE59/EcDUsXYHddUynFZbws4XHFBSA1Bwoldg5NHvZ2BleR6eHPWjjqaBZ1a\ntjayHgamsfbobTZXarJp6+pygtH0Xjf4FiGF0lS+NwUnjDwU5jvvS1PBbSIi30f0oHPH99yp+4bz\nbuTDkQRjnZBj5VvmIjdstjNX9H9LXy4uWrezI6TfrzbeBrTz18RdkEK1sRmx1HXb/LqgIW2uDqwS\nQ7Ih8qxpuvY5beHCJk7gbCtulbYbOCF5m0zWz4PStaWIwWaMvaiFtyoTg84O6/wDAea9ECeH9n3c\nTtp+jPJI9mV5c0FlkZm0vbZ6F87CefhF/0Ohr6gFXVKYX4M4CG7AD9UIYvJOnuyq5X625W+xqd2X\nHvTK9uNeMlSZUcByRdXSxEI0l31//gn6r3E+H4pTUbP29EsqD94lGDoxnpFht7JQFyMzySlF+Pxq\neQ5PFN5j5Hu5QxhGmon2d9DtBlVgPJ+hjKbNX7KYIAPYrahbglwr5H3Mp0aRSNgZzrxrusQVHaQU\nLmO3e87VzrUdtW9W3MyVCs93OWHOwHzgu3k3kuh8vDJRji0n6qHAjFzVe7X/7YfmLRR9Y6z94Xek\nOavpiaK1TU2Gd571IA836RJEVDDxOY+5jCfqBNuX5aJHnr8MtUNRjxQ3U2D5eg4NOENUzpWFqhdL\nNmMKSLlU+euujIk98ZFzx8FBiY0NzEZKcfQBzxRQ1SYUHe5M8TzhjDzqYF8A+A6M0+XHAXqvO1mi\n7awSBsGah26bGpPVVyh6c35T8seeKwllw/1Ssq2gYB5jXT9dfCUwnlgOUUu0TVYxgUEdB4EuF82r\nAsrarqrxrUiPfoQEBVJx1hkueY1nNWavNJgGBdxw6ky2qOfGs91CGAo8Vcm+Os/siHN432r95g+y\nriHLv2/Jv5M3rxdLfm+o3gyUUs3RqKq6xIb4VfQQ+6VBtgMgq5HUMldKTBPny6sWL5P0lWbppQUA\n5UYogXoUcFXJf5OsOaG2HxC2c501wfCtbJVjnk66kritJiKFkiFE8JHgwffXvGwWXyjCm4hb1TtG\nJIFGpIznAtnTpBDP9tO2mL+KnEZSdw7XsYf08JnfbTOuLVpZ31LW5ZMZX+xxtW25v2HrN7nP3gGT\ndRKpj50ju9oMqV5tb6UhGSpcLJcad3kMW6UH1xa693PZm3vnPxKep8FFqQWC1EOWvXr19Zse8Kco\nNwGEIVOazgwMSkLf1oF+aIHFmC3MNWYA9P500nYrStSAKWxuykY7LIwzNR5stXec5L51//JuY1q3\nESRmrBd8ffu74VvbiQ5naoAnJjC9Fd/dIC7NmY8VebKc52q9w7QJkOqe2EDeHs1DdrD1SjJLV3Md\n4K19HZUrkGkjWov/X6JQbM3hhjq1visZ1Mxnj7Njc4ZpgYNvMH2NOo1FsGRF1d72ZjegNnJw4IN3\nGgN45hICrSvVss4+VKLvLub1amQQ+DvGAMQ+I1peLguHfi1t30fAw16997Z4TiJAqez5T1uyYkgF\nfFzlZDPqdNzRkhEO0+ME2ZnDKMZvd9jHEIZ1XvwKlej40ESYhSykfk8Tn5VH4/UT012vuhk7ShgW\nrJZj+MdGA6NLDwuRi3WeLAVrV3cBF0d4/sfJhIqr2HYLO/sr4v+3s91UwpipUGgLs62hn3t4S+S2\nQj4Kn51yyPfH64sZMFVLerQXrK6qIfLbB3c6jokywzoASg3YbKzCU/rHFh1MkNYxGuqHvivxmX6L\nIRBv6vkUh/8AjhkgcvEPqxeYeJ8ZsAcJDwgz0bcCb57qYJwc6fQ2+xDAVqfVUdimDBNgMH6AAewY\nSBhl5Nr9TJJ6yqqeh0CBAaEE7P9IoLClgGa5dw6Gg48Sz+0leUKVebSEJNnFcEUxWwgrWvKc8Rg3\nTKRJFGeW3mJveNTkLrk5dflt8sy6Q/SKXqVcWK3UeNSNb6K2qceTv71Rw/BqkLlVGj+iInxvdfcw\nO3divyaAkU0HrMLossGd1bL5I8wUoaU2lfvx7dsVWDGlnKnNtwYhqHBpHeFgl0pv2dyMDBHVdiKU\noURldnEsY0S+r/NEIdQ9x/TC/K1xI4Mn8t+l87ArgF4/PLUTJ+0krfxTYzl8rBh9c86z21y1iAH2\n/nQoXqL1oyXOVcfmD0+IhOz4nUN7vUXX4RIx3o05WDM18jDArfiPIK/ZN1a811VD6fncJeh+yI0K\nfq4BcIqcgm1pTf4QHP20r3ScmO3JwmqgDjqD2wQ1xW9MK7QYmXsL9XQ8U0QIRCdZFp05gboRuQA/\nhunyJue5+9XGpu8AwZv3E92uy8Mukg3AjeT3UxiNxwJcPRWth9kO4x6QY1lvngxdfWs7PL237wys\nvGvKnTNjzDmFhOHaPtPsI0Zi0gqzfi8Z2CSoKGyA1yV1mpxH04QVG1c1DcCOVpA7vf76d5Fr1rMj\nYd904moZbmninsKHMQoPlgaTPmuCcFI3lYpBmdZiTy6gBRGmFPdHUHgGQvP5YK2gnYlBwF9AtiJ4\nHuSSvx60xNhCyzETAGr1zYVrRxsuJfMyVZPIBCdJdP8Gdnfr0q7pjiNZ/AsXHbw3cHSJw/jtkCiD\nljEsNc3AwYaWrkvTpQCi4mjME1qTMpk4omAw7HhVdnqlMkwyGQ3/EUAsV4w62FInNijKtP4ttL/E\nx2QlKptWpT8ipZY1jwTgWReEf/tHgDMyIedPtWrZ+fR4VVXthIFdQmNFHjKhwsi8zA5x+3CvPBb3\nq4KZMrhDRTmc5IMF/Qia1ukT0pFcxB4qDWRtzFBZd6NyJiFF/8uJLym6JYjl+m01mM9389yuq1rL\nUhSWGsROEqH+IOE/zZ1pvSkZQcGBdnzDewR+W9XgkxGFynFeQpZrbg8kVLz+ZdDbiOrIFxpo+BE6\nAks5ZNgfIZEaFcWVSL6of6j4ff3MxL1e2UkC7augCUO1CKuZJI/b7YrhlPBD4pT0eSRZZ5XwsSN6\nYBJp8kGe1F+zRkclpKArSbFK8nnu66tsbVrwbyK7d/0BNFVQ1cqlnMcjvKAFx+KMiV0jwy/kk6R0\niJFjiEPkttM04VUe8CYK/OUwwPiHdzR33MvJjb8c2qk/reWwNEFgm01UdfX4tQuF7zsFMfdMGDnf\nvv7aokDM9yWDdLYkskSQZrMZO9DflRrIimjhAqvBgtaLGwNqlXDhR8uLeDVmeNPrqB1Gau4NPKsp\nrOmftLi8xvnVHddqnC4t/MZ699jin78m2hlHeo/eiWny53QHqWnOYaP6Jmv5S1IBw4gvDxiOGqU2\nazg/mBJkXLbnJGqFoQxrZdoPzIr0yo0tM7mmreaeCkqJzTOZZHapaLlSpRa9p9EIi23l3kIc3FeK\nFXSdLY3s13TLRf18gafUteb2nmfXKiYjLjTSMEXEgURKulWUeRq4E2h1flvGJtcqq8g+XRak/2Lc\nVNRh7shsZVxgfZv3wFwjDd2F4VX5zUSWx1YwmtrF2REAlsIPahuw07i1VCiD/439u8AmTgGw9Q7q\nSKAmEqa7YnNwMf1DtiYd0as4XUvQr0HAtRq2aahLDvRNQvAFTS1uXbss1fyfa+7ePN6TC+t8isqt\n2vZhWY4jy4jMv4D9l1D232LUcT7OVjmcJisG+wmKrNIPncE16dwj9X/s2I4n30qQTCfKes/4ja7W\nzvKPFUfhVsfYB1+jn33mTCe9M9Y9xw67DwIsA2A9W3WU59cKcOHGje1IlcC4IF3RDyVI9PHxXXxL\n234rtz4WDN6hgQ3YBVcg3k1TP3oIbgWscpxpAeu4rl8ZZvkYbmjeIwphFhQdhhWRuBDQKgy/KQlO\nLlP7avTR27Rm5wQQgubJn/GaXHBJ45ZvYtyK71FqvHLqB7jVyIpuogvMm7q5XMjLByLcFKS2bVmd\niXzylUQjQLqLJ6Sf7nRtmJtH2b9/s4X2G8QL5M20kb/gkuMLyYoAagN3XD5zksJb0VJSVtgdjbws\nZmK5/N3tXMFXnLTGUIQwGAmEpmeJWb/YO+xVsLw7sbVSO0yX75ZP2p+R8GW/mxZK96clbXgqPwrk\n0Q=='
    key = 'ceh[Een,3d3o9neg}fH+Jx4XiA0,D1cT'.encode('UTF-8')
    iv = 'K+\\~d4,Ir)b$=paf'.encode('UTF-8')
    cipher = AES.new(key, AES.MODE_CBC, iv)

    decode_data = base64.decodebytes(encode_data.encode('UTF-8'))
    print(decode_data)

    decode_data = cipher.decrypt(decode_data)
    print(decode_data)
    decode_data = decode_data.replace(b'\x0f\x0f\x0f\x0f\x0f\x0f\x0f\x0f\x0f\x0f\x0f\x0f\x0f\x0f\x0f', b'')
    print(decode_data)
    decode_data = gzip.decompress(decode_data)
    print(decode_data)


if __name__ == '__main__':
    # grammar_json_file_path = r'./result/grammar-n5.json'
    # parse_and_save_jiemo_grammar_json(grammar_json_file_path)
    # query_hujiang_word("上")
    # query_hujiang_word("一人当たり", 'jp', 'cn')
    hujiang_des_cbc()
