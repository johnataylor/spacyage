# spacyage
Experiments with building Bots with [SpaCy](https://spacy.io/)

You will need Python and Node. And you will need the [Bot Framework Emulator](https://github.com/Microsoft/BotFramework-Emulator)

This is an application of the [Bot Builder Framework](https://github.com/Microsoft/botbuilder-python).

## Install Spacy

There are full instructions on the SpaCy web site, but for a quick start on windows:

Create and activate a Python Virtual Environment:

```cmd
python -m venv c:\env\spacyage
c:\env\spaceage\scripts\activate
```

And when inside this environment install SpaCy:

```cmd
pip install spacy
```

Then as administrator (because it needs permissions to creates a link):

```cmd
python -m spacy download en
```

## Install Bot Builder for Python

When in the virtual environment:

```cmd
pip install botbuilder-core
```

## Run the State Service

The simple state service is written in Node and naturally serves up a REST interface:

```cmd
cd StateService
npm install
node index.js
```

This is the most basic of services. Perhaps in the future we can reduce the round trip calls by batching up our assertions into a JSON-LD document and that would maintain the correct semantics. However, for now, we'll do fine with PUT, DELETE and GET even if it is a little chatty.

## Running the Bot

Back in the Python virtual environment:

```cmd
cd PythonBot
python Bot.py
```

## Testing

Start the Bot Framework Emulator and connect to http://localhost:9000 which is the endpoint served up by our Python Bot.

You should see the connect in the emulator window and the console you are running the Bot from.

Try typing:

```
add cheese
```

and you will see a PUT received at the State Service running under Node. You can add multiple items at a time:

```
add bacon and eggs
```

you can also remove items, and because we are using an idempotent PUT operation no harm is done if we accidently repeat something:

```
add bacon and remove the cheese
```

if we send an incomplete utterance the bot will realize that and attempt to resolves the semantics by concatenating it onto what it had just heard previously, as we are resolving everything down to idempotent operations this works out fine, so try this next:

```
and eggs
```

SpaCy is very fast and you won't notice the extra processing.

you might like to try other verbs, when you do you'll see this bot only understands how to do a limited number of things:

```
add anchoives and then jump in the air
```

but interestingly even in this case our bot realized what action we were asking it to perform.

Overall the resulting behavior is very natural for a multi-turn bot conversation. It is interestring to contrast the behavior you are seeing here with the bot-driven prompting behavior we commonly see. In the typical prompted case the bot asks a question and the user answers. In that case the context for understanding the utterance from the user is the question that was asked, there is little flexibility and little opportunity for any natural language at that point. 

## How it Works

We are using SpaCy to give us a parse tree of the English language text. SpaCy has a pretrained model of a number of different languages, here we are using the small English model. We did no additional training ourselves for this scenario. There are no specially trained intents here, although, of course, SpaCy can be trained to recognize intents that is not what we were interested in here because we wanted to explore the implications of multi-turn conversations. In this code the logic works directly against the statistically produced parse tree.

Once we have the parse tree we look for any verbs and then, if it is a verb we know how to work with, we pick up the dependent objects of that particular verb and for each according to our mapping we execute a call to our StateService. SpaCy gives us a rich object model and the code to traverse the structure it gives us is very straight forward.

SpaCy provides tools to visualize the underlying data structures, for example, [add bacon and remove the cheese](https://explosion.ai/demos/displacy?text=add%20bacon%20and%20remove%20the%20cheese&model=en_core_web_sm&cpu=1&cph=1) 

When the bot sees the verb "add" it executes a PUT and for "remove" it executes a DELETE. The mapping is easily extended in many different ways, for example, we could extend the number of verbs we understand, we could limit the number of nouns we accept, we could make our travsersal of the tree more forgiving, we could use lemmas, we could use similarity, and of course we could train our language model beyond what we have out of the box.

If the Bot does not find any verbs it concludes that the utterance is just a continuation of the previous utterance, that is reasonable given the nature of natural language, and so it just concatenates the text and reprocesses. If we were connecting this logic to a speech channel it would make sense to add a timeout to our willingness to concatenate, after all we are attempting to capture natural language and natural language, especially when spoken, has a strong time component.

## Conclusion

We have effectively modeled our bot as a protocol bridge between the protocol humans use to talk to each other, that of natural language verbs and their dependent objects, and the protocol computers use to talk to each other, that of network friendly assertions and retractions.

There is lots more fun to be had. The next steps include improving the mapping and optimizing our network protocols.

As we make the mapping of verbs and nouns more flexible it would be a good implementation choice to introduce some more data driven logic. For the network, RDF and specifically JSON-LD would be a natural choice for representing batches of assertions and retractions.

It should be pointed out that the fact that we are using English as our model is not particularly fundamental. Just about every language in common usage share the same univeral core. In other words the code didn't actually depend on English it depended on the universal language concepts of noun and verb.

Another area of investigation is training. So far the off the shelf model worked surprisingly well, however, the parse tree is statistically generated and can contain mistakes. For example, try "add mushroom and jump in the air" SpaCy gets confused and thinks "jump" was another noun and therefore somethng to add to our pizza. Adding the word "_then_ jump in the air" fixed things. But clearly the model could have been more appropriate to our domain, this is where addionitional, domain specific, training would help. And once we are in the business of training it turns out we might not actually care that much about traditional language structure, in other words, all we are trying to do is map langauge to rest calls. We could train to produce a dependency tree closer to the traditional bot model of of intent, of course we would naturally extend this to multi-intent, and all this with the assumption that those intents corresponded more directly to our rest calls.

