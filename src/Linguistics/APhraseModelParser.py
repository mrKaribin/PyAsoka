from PyAsoka.src.Debug.Logs import Logs as Log
import pymorphy2


# начало, конец модели - []
# линейный тип модели - L
# нелинейный тип модели - N
# выборочный тип модели - C
#   p - part_of_speach
#   a - animacy
#   s - aspect
#   m - mood
#   i - involvement
#   r - transitivity
#   g - genders
#   n - numbers
#   c - cases
#   t - tenses

# Пример: '[N:[C:показать{t:} сказать напомнить] [L:текущий время]]'

analyzer = pymorphy2.MorphAnalyzer()


def parse(regex: str):
    if len(regex) > 2 and regex[0] == '[' and regex[len(regex) - 1] == ']':
        return _parse_phrase_(regex)
    else:
        exception_broken_regex('Не обнаружены стартовый и/или конечный символы ("[", "]")')


def _find_end_of_model_(regex: str, str_ind: int = 0, fin_ind: int = -1):
    level = 1
    index = str_ind
    if fin_ind == -1:
        fin_ind = len(regex) - 1
    substr = regex[str_ind: fin_ind + 1]
    substr = substr
    for sim in substr:
        if sim == '[':
            level += 1
        elif sim == ']':
            level -= 1
        if level == 0:
            return index
        index += 1
    return -1


def _wrap_phrase_(regex: str, phrases: list, str_ind: int = 0, fin_ind: int = -1):
    regex += ' '
    # changed = False
    substr2 = regex[str_ind:fin_ind]
    while (s_ind := regex.find('[', str_ind, fin_ind)) != -1:
        substr1 = regex[s_ind + 1:fin_ind]
        if (f_ind := _find_end_of_model_(regex, s_ind + 1, fin_ind)) != -1:
            substr = regex[s_ind + 1:f_ind]
            regex, phrases = _wrap_phrase_(regex, phrases, s_ind + 1, f_ind)
            f_ind = _find_end_of_model_(regex, s_ind + 1, fin_ind)
            phrase = regex[s_ind:f_ind + 1]
            regex = regex[:s_ind] + f'%phr{len(phrases)}' + regex[f_ind + 1:]
            fin_ind -= len(phrase)
            phrases.append(phrase)
            # changed = True

    return regex, phrases


def _parse_phrase_(regex: str, phrases: list = []):
    from PyAsoka.src.Linguistics.PhraseModel import PhraseModel
    lng = len(regex)
    regex = regex[1:lng - 1]

    reg_type = regex[0]
    regex = regex[1:]
    if reg_type == 'L':
        _type = PhraseModel.Type.LINEAR
    elif reg_type == 'N':
        _type = PhraseModel.Type.NON_LINEAR
    elif reg_type == 'C':
        _type = PhraseModel.Type.CHOICE
    else:
        exception_broken_regex(f'Неверный тип модели фразы ({reg_type})')
        return
    model = PhraseModel(_type)

    regex, phrases = _wrap_phrase_(regex, phrases)

    words = regex.split(' ')
    for scheme in words:
        if scheme.find('%phr') != -1:
            scheme = phrases[int(scheme[4])]
            model.add(_parse_phrase_(scheme, phrases))
        elif len(scheme) > 0:
            model.add(_parse_word_(scheme))

    return model


def _parse_word_(scheme: str):
    global analyzer
    from PyAsoka.src.Linguistics.PhraseModel import AWordModel, Word, Noun, Verb
    if scheme.find('{') != -1:
        word, args = scheme.split('{')
    else:
        word, args = scheme, ''

    if not word.isalpha():
        exception_broken_regex(f'Буквенная часть модели слова содержит некорректные символы: {word}')
    if 0 < len(args) < 6:
        exception_broken_regex(f'Аргументная часть модели слова содержит слишком мало символов: {args}')

    if word != '':
        params = analyzer.parse(word)[0]
        word = params.normal_form
    else:
        word = None

    word_model = AWordModel(word)
    fields = dict({
        'p': {
            'value': None,
            'states': {
                'verb': Word.PartOfSpeech.VERB,
                'noun': Word.PartOfSpeech.NOUN,
                'adj': Word.PartOfSpeech.ADJECTIVE,
                'pron': Word.PartOfSpeech.PRONOUN,
                'adv': Word.PartOfSpeech.ADVERB,
                'num': Word.PartOfSpeech.NUMERAL
            }
        },
        'c': {
            'value': [],
            'states': {
                'nom': Noun.Case.NOMINATIVE,
                'gen': Noun.Case.GENITIVE,
                'dat': Noun.Case.DATIVE,
                'acc': Noun.Case.ACCUSATIVE,
                'ins': Noun.Case.INSTRUMENTAL,
                'pre': Noun.Case.PREPOSITIONAL
            }
        },
        't': {
            'value': [],
            'states': {
                'pst': Verb.Tense.PAST,
                'prs': Verb.Tense.PRESENT,
                'ftr': Verb.Tense.FUTURE
            }
        }
    })

    if len(args) > 5:
        args = args[:len(args - 2)]
        for arg in args.split(' '):
            try:
                field_name, state_names = arg.split(':')
                field = fields[field_name]
                for state_name in state_names.split(','):
                    if isinstance(field['value'], list):
                        field['value'].append(field['states'][state_name])
                    else:
                        field['value'] = field['states'][state_name]
            except Exception as e:
                exception_broken_regex(f'Ошибка разбора аргументов модели слова: {arg} : {str(e)}')

    word_model.part_of_speach = fields['p']['value']
    word_model.cases = fields['c']['value']
    word_model.tenses = fields['t']['value']
    return word_model


def exception_broken_regex(text):
    text = f'Некорректное регулярное выражение модели фразы: {text}'
    Log.error(text)
    raise Exception(text)
