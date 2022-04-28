import re
import syntok.segmenter as segmenter
import mwparserfromhell


class Cutter:
    def __init__(self) -> None:
        pass

    def segmentation_auto(self, document, language_code):
        """Apply different segmentation methods for various languages.
        """
        if language_code in ['zh', 'zh-classical']:
            for sentence in self.segmentation_zh(document):
                yield sentence
        else:
            for sentence in self.segmentation_ie(document):
                yield sentence

    def segmentation_ie(self, document: 'str'):
        """Split a document into sentences.
        It works with Indo-European languages, mainly with English, German and Spanish.
        If there's sentence-ending punctuation and quotation marks appearing together, it will ignore the quotation.

        Parameters
        ----------
        document :
            The document to be segmented.
        Return : 
            Segmented sentence per yield.
        """
        for paragraph in segmenter.process(document):
            for sentence in paragraph:
                # sentence: List[Token]
                # str.join() only takes an iterable that elements are strings
                # Here the element are of Token class, so we have to convert them into strings during join() happens.
                # We can use map(func, iter), which will apply the func (here is str()) on every element of the iter during runtime.
                # BTW, tokens have a leading space by default, except the first token.
                # TODO: There are wierd 3-bar equal marks can't be strip in en/es documents.
                yield ''.join(map(
                    str,
                    sentence)).lstrip().strip('=').strip().strip('=').strip()
                yield '\n'  # Start a new line for the next sentence.
            # yield ('\n')  # Place an empty line between paragraphs.

    def segmentation_zh(self, document: 'str') -> 'list[str]':
        """Split a document into sentences.
        It works with simplified/traditional Chinese.

        Parameters
        ----------
        document :
            The document to be segmented.
        """
        #TODO: Update whole read, re.split, write using generator.
        pattern = '([﹒﹔﹖﹗．；。！？]["’”」』]{0,2}|：(?=["‘“「『]{1,2}|$)|={2,})'
        # is_not_punctuation = True
        # sentence_temp = ''
        # for sentence in re.split(pattern, document):
        #     sentence = sentence.strip('=').strip('\n').strip().strip('\n')
        #     if sentence == '\n': continue  # Skip empty lines.
        #     sentence_temp += sentence
        #     if is_not_punctuation:
        #         is_not_punctuation = not is_not_punctuation
        #         continue
        #     else:
        #         yield sentence_temp
        #         yield '\n'
        #     sentence_temp = ''
        #     is_not_punctuation = not is_not_punctuation
        sentences = re.split(pattern, document)
        sentences = ["".join(i) for i in zip(sentences[0::2], sentences[1::2])]
        # Push punctuations back to every sentence.
        # Here i is a tuple consisting of elements from sentences[0::2] and sentences[1::2].
        # join() will join those 2 elements inside each tuple.
        sentences = [
            re.sub('\\n|={2,}', '', sentence).strip() for sentence in sentences
        ]  # Remove \n and ==
        sentences = list(filter(('').__ne__,
                                sentences))  # Remove empty string ""
        for sentence in sentences:
            yield (sentence)
            yield ('\n')

    # def parse_and_tokenize(self, rawText) -> 'list[str]':
    #     """
    #     : rawText: String to be parsed and tokenized.
    #     """
    #     parseResult = str(mwparserfromhell.parse(rawText))

    #     pattern = '([﹒﹔﹖﹗．；。！？]["’”」』]{0,2}|：(?=["‘“「『]{1,2}|$)|={2,})'
    #     tokens = re.split(pattern, parseResult)
    #     tokens.append("")  # What is this?
    #     tokens = ["".join(i) for i in zip(tokens[0::2], tokens[1::2])]
    #     # Push punctuations back to every sentence.
    #     # Here i is a tuple consisting of elements from tokens[0::2] and tokens[1::2].
    #     # join() will join those 2 elements inside each tuple.
    #     tokens = [re.sub('\\n|={2,}', '', token).strip()
    #               for token in tokens]  # Remove \n and ==
    #     tokens = list(filter(('').__ne__, tokens))  # Remove empty string ""

    #     return tokens