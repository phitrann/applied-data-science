import json
import random
import logging
from spacy.gold import GoldParse
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import accuracy_score
def convert_dataturks_to_spacy(dataturks_JSON_FilePath):
    try:
        training_data = []
        lines=[]
        with open(dataturks_JSON_FilePath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines:
            data = json.loads(line)
            text = data['content']
            entities = []
            for annotation in data['annotation']:
                #only a single point in text annotation.
                point = annotation['points'][0]
                labels = annotation['label']
                # handle both list of labels or a single label.
                if not isinstance(labels, list):
                    labels = [labels]

                for label in labels:
                    #dataturks indices are both inclusive [start, end] but spacy is not [start, end)
                    entities.append((point['start'], point['end'] + 1 ,label))


            training_data.append((text, {"entities" : entities}))

        return training_data
    except Exception as e:
        logging.exception("Unable to process " + dataturks_JSON_FilePath + "\n" + "error = " + str(e))
        return None
    
    
def clean_entities(training_data):
  clean_data = []
  for text, annotation in training_data:
        
    entities = annotation.get('entities')
    entities_copy = entities.copy()
        
    # append entity only if it is longer than its overlapping entity
    i = 0
    for entity in entities_copy:
      j = 0
      for overlapping_entity in entities_copy:
        # Skip self
        if i != j:
          e_start, e_end, oe_start, oe_end = entity[0], entity[1], overlapping_entity[0], overlapping_entity[1]
          # Delete any entity that overlaps, keep if longer
          if ((e_start >= oe_start and e_start <= oe_end) \
          or (e_end <= oe_end and e_end >= oe_start)) \
          and ((e_end - e_start) <= (oe_end - oe_start)):
            entities.remove(entity)
        j += 1
      i += 1
    clean_data.append((text, {'entities': entities}))
                
  return clean_data

import spacy
################### Train Spacy NER.###########
def train_spacy():

    TRAIN_DATA = clean_entities(convert_dataturks_to_spacy("/space/hotel/phit/personal/applied-data-science/data/ner/traindata.json"))
    nlp = spacy.blank('en')  # create blank Language class
    # create the built-in pipeline components and add them to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner, last=True)
       

    # add labels
    for _, annotations in TRAIN_DATA:
         for ent in annotations.get('entities'):
            ner.add_label(ent[2])

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes):  # only train NER
        optimizer = nlp.begin_training()
        for itn in range(10):
            print("Starting iteration " + str(itn))
            random.shuffle(TRAIN_DATA)
            losses = {}
            for text, annotations in TRAIN_DATA:
                try:
                    nlp.update(
                        [text],  # batch of texts
                        [annotations],  # batch of annotations
                        drop=0.2,  # dropout - make it harder to memorise data
                        sgd=optimizer,  # callable to update weights
                        losses=losses)
                except Exception as e:
                    pass
            print(losses)
    nlp.to_disk("nlp_ner_model")
    #test the model and evaluate it
    examples = clean_entities(convert_dataturks_to_spacy("/space/hotel/phit/personal/applied-data-science/data/ner/testdata.json"))
    c=0        
    for text,annot in examples:

        f=open("resumes/resume"+str(c)+".txt","w")
        doc_to_test=nlp(text)
        d={}
        for ent in doc_to_test.ents:
            d[ent.label_]=[]
        for ent in doc_to_test.ents:
            d[ent.label_].append(ent.text)

        for i in set(d.keys()):

            f.write("\n\n")
            f.write(i +":"+"\n")
            for j in set(d[i]):
                f.write(j.replace('\n','')+"\n")
        d={}
        for ent in doc_to_test.ents:
            d[ent.label_]=[0,0,0,0,0,0]
        for ent in doc_to_test.ents:
            doc_gold_text= nlp.make_doc(text)
            gold = GoldParse(doc_gold_text, entities=annot.get("entities"))
            y_true = [ent.label_ if ent.label_ in x else 'Not '+ent.label_ for x in gold.ner]
            y_pred = [x.ent_type_ if x.ent_type_ ==ent.label_ else 'Not '+ent.label_ for x in doc_to_test]  
            if(d[ent.label_][0]==0):
                (p,r,f,s)= precision_recall_fscore_support(y_true,y_pred,average='weighted')
                a=accuracy_score(y_true,y_pred)
                d[ent.label_][0]=1
                d[ent.label_][1]+=p
                d[ent.label_][2]+=r
                d[ent.label_][3]+=f
                d[ent.label_][4]+=a
                d[ent.label_][5]+=1
        c+=1
    for i in d:
        print("\n For Entity "+i+"\n")
        print("Accuracy : "+str((d[i][4]/d[i][5])*100)+"%")
        print("Precision : "+str(d[i][1]/d[i][5]))
        print("Recall : "+str(d[i][2]/d[i][5]))
        print("F-score : "+str(d[i][3]/d[i][5]))
train_spacy()