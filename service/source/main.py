import tensorflow as tf
import unicodedata
import re
tf.random.set_seed(42)
from config.env import getenv

# Load model
from transformers import TFPegasusForConditionalGeneration, PegasusTokenizerFast
repo_name = getenv('MODEL_NAME')
model = TFPegasusForConditionalGeneration.from_pretrained(repo_name)
tokenizer = PegasusTokenizerFast.from_pretrained(repo_name)

# Model config
MODEL_MAX_LENGTH = 512
MODEL_MIN_LENGTH = 64
MIN_SUMMARY_LENGTH = 40
MAX_SUMMARY_LENGTH = 128
num_beams = 4

def remove_news_headline(text : str, delim : str):
    # Helper function to remove news headline (for example: JAKARTA, liputan6.com -- )
    x = text.split(delim)
    if len(x)>1: # dump the title
        return " ".join(x[1:])
    else:
        return x[0]

def text_cleaning(input_string : str, is_news : bool = True):
    # Main function to clean text, removes link, bullet point, non ASCII char, news headline, parantheses,
    # punctuation except "," and ".", numbers with dot (enumerating), extra whitespaces, too short sentences.
    lowercase = input_string.lower()
    # stripped_html = BeautifulSoup(lowercase, 'html.parser').get_text()
    remove_link = re.sub(r'(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w\.-]*)', '', lowercase).replace("&amp;","&")
    remove_bullet = "\n".join([T for T in remove_link.split('\n') if '•' not in T and "baca juga:" not in T])
    remove_accented = unicodedata.normalize('NFKD', remove_bullet).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    # remove news headline
    if is_news:
        y = remove_news_headline(remove_accented,'- ')
        y = remove_news_headline(y,'– ') 
        y = remove_news_headline(y,'- ') 
    else:
        y = remove_accented
    remove_parentheses = re.sub("([\(\|]).*?([\)\|])", "\g<1>\g<2>", y) 
    remove_punc = re.sub(r"[^\w\d.\s]+",' ', remove_parentheses)
    remove_num_dot = re.sub(r"(?<=\d)\.|\.(?=\d)|(?<=#)\.","",remove_punc)
    remove_extra_whitespace =  re.sub(r'^\s*|\s\s*', ' ', remove_num_dot).strip()
    return ".".join([s for s in remove_extra_whitespace.strip().split('.') if len(s.strip())>10]).replace("_","")

def process_input_eval(text : str, tokenizer = tokenizer):
    # Prepare text for generation
    t = text_cleaning(text)
    return tokenizer(t,
              return_tensors = "tf",
              padding = 'max_length',
              max_length = MODEL_MAX_LENGTH,
              truncation = True
              )

def abs_summary(request_data : dict):
    content = []
    for item in request_data['data']:
        t = process_input_eval(item['text'])
        x = model.generate(**t,
                            min_new_tokens = MIN_SUMMARY_LENGTH,
                            max_new_tokens = MAX_SUMMARY_LENGTH,
                            # early_stopping  = True, # want to explore full potential
                            num_beams = num_beams,
                            num_return_sequences = num_beams,
                            no_repeat_ngram_size = 1,
                            temperature = 0.7,
                            top_p = 0.75
                            #repetition_penalty = 2, # no need because no repeatings unigrams!
                            #encoder_repetition_penalty = 2,
                            #diversity_penalty = 0.1
                            )
    
        summary = tokenizer.batch_decode(x, skip_special_tokens=True)[0]
        
        result = {}
        result['article'] = item['text']
        result['summary'] = summary
        content.append(result)

    output = {'data' : content}
    return output