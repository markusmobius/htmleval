from LlmLib import Chat, Llm
import json

#define the chats
chats=[]
chat = Chat(requestJSON=False) 
chat.AddSystemMessage("You are a helpful assistant. You will talk like a pirate.")
chat.AddUserMessage("What's the best way to train a parrot?")
chats.append(chat)

chat = Chat(requestJSON=True) 
chat.AddSystemMessage("You are a helpful assistant.")
chat.AddUserMessage("Is Sarah usually a male name? Answer with as JSON of the form ['answer':'yes_or_no']")
chats.append(chat)

chat = Chat(requestJSON=True) 
chat.AddSystemMessage("You are a helpful assistant.")
chat.AddUserMessage("Name the 10 largest countries in the world (by landmass) from largest to smallest as a JSON list.")
chats.append(chat)

chat = Chat(requestJSON=False) 
chat.AddSystemMessage("You are a helpful assistant.")
chat.AddUserMessage("What is 2+2?")
chats.append(chat)

chat = Chat(requestJSON=True) 
chat.AddSystemMessage("You are a helpful assistant.")
chat.AddUserMessage("What is the square root of 121? Output as a JSON of the form {'value':}")
chats.append(chat)

chat = Chat(requestJSON=True) 
chat.AddSystemMessage("You are a helpful assistant.")
chat.AddUserMessage("What is the square root of 101? Output as a JSON of the form {'value':}")
chats.append(chat)

chat = Chat(requestJSON=True) 
chat.AddSystemMessage("You are a helpful assistant.")
chat.AddUserMessage("How many letters are in the word 'Rhythm'? Output as a JSON of the form {'value':}")
chats.append(chat)

chat = Chat(requestJSON=True) 
chat.AddSystemMessage("You are a helpful assistant.")
chat.AddUserMessage("How many letters are in the word 'totalitarian'? Output as a JSON of the form {'value':}")
chats.append(chat)

chat = Chat(requestJSON=True) 
chat.AddSystemMessage("You are a helpful assistant.")
chat.AddUserMessage("When was Barack Obama born? Output as a JSON of the form {'value':}")
chats.append(chat)

chat = Chat(requestJSON=False) 
chat.AddSystemMessage("You are a helpful assistant.")
chat.AddUserMessage("Summarize this text in one sentence of not more than 15 words: Jimmy Kimmel broke his silence on Tuesday night in an emotional return to ABC’s airwaves, addressing the controversy that temporarily sidelined his late-night show amid a still-swirling storm of political and corporate standoffs. 'This show is not important,' Mr. Kimmel said in his opening monologue. 'What’s important is that we get to live in a country that allows us to have a show like this.' ABC and Disney executives pulled 'Jimmy Kimmel Live!' off the air last week after an uproar over the host's comments about the suspected shooter of right-wing activist Charlie Kirk. On Tuesday night, Mr. Kimmel, choking up, said it 'was never my intention' to make light of the murder of a young man.?")
chats.append(chat)

chat = Chat(requestJSON=False) 
chat.AddSystemMessage("You are a helpful assistant.")
chat.AddUserMessage("Summarize this text: Abstractive summarization methods generate new text that did not exist in the original text. This has been applied mainly for text. Abstractive methods build an internal semantic representation of the original content (often called a language model), and then use this representation to create a summary that is closer to what a human might express. Abstraction may transform the extracted content by paraphrasing sections of the source document, to condense a text more strongly than extraction. Such transformation, however, is computationally much more challenging than extraction, involving both natural language processing and often a deep understanding of the domain of the original text in cases where the original document relates to a special field of knowledge. 'Paraphrasing' is even more difficult to apply to images and videos, which is why most summarization systems are extractive.")
chats.append(chat)

chat = Chat(requestJSON=False) 
chat.AddSystemMessage("You are a helpful assistant.")
chat.AddUserMessage("Who is older - god or the universe?")
chats.append(chat)

chat = Chat(requestJSON=False) 
chat.AddSystemMessage("You are a helpful assistant.")
chat.AddUserMessage("Who invented the light bulb?")
chats.append(chat)

chat = Chat(requestJSON=False) 
chat.AddSystemMessage("You are a helpful assistant.")
chat.AddUserMessage("What is an opera in one sentence?")
chats.append(chat)

chat = Chat(requestJSON=False) 
chat.AddSystemMessage("You are a helpful assistant.")
chat.AddUserMessage("Why can birds fly in one sentence?")
chats.append(chat)

chat = Chat(requestJSON=True) 
chat.AddSystemMessage("You are a helpful assistant.")
chat.AddUserMessage("Name the 5th and the 10th US president in a JSON array.")
chats.append(chat)

chat = Chat(requestJSON=True) 
chat.AddSystemMessage("You are a helpful assistant.")
chat.AddUserMessage("Name the 44th and the 45th US president in a JSON array.")
chats.append(chat)

chat = Chat(requestJSON=False) 
chat.AddSystemMessage("You are a helpful assistant.")
chat.AddUserMessage("Name all German chancellors after 1945 in a JSON array.")
chats.append(chat)

chat = Chat(requestJSON=False) 
chat.AddSystemMessage("You are a helpful assistant.")
chat.AddUserMessage("Name all Iranian presidents after 1945 in a JSON array.")
chats.append(chat)

chat = Chat(requestJSON=False) 
chat.AddSystemMessage("You are a helpful assistant.")
chat.AddUserMessage("Write a limerick on the beauty of trash incinerators.")
chats.append(chat)

chat = Chat(requestJSON=False) 
chat.AddSystemMessage("You are a helpful assistant.")
chat.AddUserMessage("Write a limerick on the beauty of garden chairs.")
chats.append(chat)

llm = Llm()
responses=llm.execute_chats(chats,["example"])
exit

for i,response in enumerate(responses):
    print(f"Task {i}")
    print("chat:")
    print(chats[i].getJSON())
    if response["error"]!=None:
        print("ERROR:")    
        print(response["error"])
    else:
        print("RESPONSE:")    
        print(response["answer"])
        print(f"Usage: {json.dumps(response["usage"])}")
    print("________________________________________________________")
    print("")

