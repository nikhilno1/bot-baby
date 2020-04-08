import boto3
import json

comprehend = boto3.client(service_name='comprehend', region_name='ap-south-1')
                
text = ["Muslims in India, have to be in jail. Yes. It s an extraordinary book. I am sure the rest of the team will have to take the book back if this is not the first time BJP, RSS, bjp kya? Modi ke liye nahin hai ye sab karne ke liye kya ?","Muslims in India. wish you a very happy birthday sir India should have sent him back to the UK. Kya hua..? Yeh woh toh hua..?","Muslims in India. What will they do if they are arrested or beaten? Aur tum logon ko sath me bhi sach bologe Aap sabhi sach bol raha hai hai. Bhagwaan me aisa janta kaise pahle hi sakti hai This is why we can t have a decent democracy.","Muslims in India: 1. What is the purpose of the terrorism in India? 2. Why are there so many Hindu girls being kidnapped and killed? 3. Why is there so much rape and murder of Muslims in India? 4. Why are so many Hindu men and women being beaten up and killed in India? 5. Why are so many Hindu men and women being tortured in India? 6.","Muslims in India & Pakistan I think the Congress is not doing a good job of it. Election Commission of India has given a clean chit to the BJP in the first stage of counting. The Election Commission has refused to declare the names of candidates to the people of India. It is very clear that the Election Commission of India has done a very poor job of the citizens' confidence.","Muslims in India & Pakistan We don't need this kind of propaganda from these 'journalists'. They are ignorant and they are doing all this for the benefit of the powerful few. We are waiting for you. #RajnathSingh #RajnathSingh Any idea how many times this is happening? why is this not clear in the tweet?","Muslims in India and the world. It's our responsibility to educate and raise voice against this. Hahaha aise hi rss ke kya hai kya hai I am a Muslim. I am a Hindu. I am a Christian. I am a Sikh. I am a Hindu. I am a Muslim. I am a Hindu. I am a Christian.","Muslims in India are as poor as the Indians. In India, an average of 90% of the population is below the poverty line. More than half of the population of India is under 25 years of age. Unable to stop the flow of garbage in our city. I hope your garbage is not affected by the incident.","Muslims in India. Fearing for their lives, two young men from Jammu & Kashmir are forced to hide behind walls in a Buddhist temple. But their story will be told again & again, as they are forced to live in a state of fear & helplessness. #GujaratFiles On the contrary. Aap ke baad bhi kyaa karte hain.","Muslims in India. Why are you afraid to be an Indian? #PulwamaAttack I know, I am a journalist and I love it when people in power are the ones who should be praised. Aaj kutta hai hi hai aaj logon ko dar saal kya kya Then why you are so afraid of my questions?","Muslims in India will not be saved by Modi govt. Lol, how much time did you spend in that blog? Fir se aukat ki kam ji? If the issue of faith is so important then why does it take so long to take action against the perpetrators? what is the problem with the thing of an Indian who has never voted for BJP?","Muslims in India. Aur nafrat ko chaliye kya batao ki aag lag raha hai.. Please take action against this person. The real story behind the crisis in India's banking sector. So it's true that it's all about fear and intimidation. We need to understand that we have to be scared and be afraid of the state.","Muslims in India, why do you have to use any word for them? Yes you are right, but i dont have any words for u... Here is a video of an ad featuring the #NizamuddinMarkaz. He was not surprised at the attack on the university. What a disgraceful thing to say. Tum sabse bhi kya hai.","Muslims in India to stop protesting against CAA. CAA, NRC, NPR, NRC: What do you want? Also know that you are the only one who is not a hero. You are a coward and a coward. "]

print('\n'.join('{}: {}'.format(*k) for k in enumerate(text)))

print('Calling DetectSentiment')
#print(json.dumps(comprehend.detect_sentiment(Text=text, LanguageCode='en'), sort_keys=True, indent=4))
#print(json.dumps(comprehend.batch_detect_sentiment(TextList=text, LanguageCode='en'), sort_keys=True, indent=4))
result_list = comprehend.batch_detect_sentiment(TextList=text, LanguageCode='en')['ResultList']
max_score_list = []
top_sentiment_list = []
for result in result_list:    
    max_key = max(result['SentimentScore'], key=result['SentimentScore'].get)
    print(result)
    #print(result['SentimentScore'][max_key])
    max_score_list.append(result['SentimentScore'][max_key]) 
    top_sentiment_list.append(max_key)
print(max_score_list)
print(top_sentiment_list)    
#print(json.dumps(result, indent=4))
max_score_list_s, top_sentiment_list_s, result_list_s = map(list, zip(*sorted(zip(max_score_list, top_sentiment_list, result_list), reverse=True)))
print("")
top_n_value = 5
print(max_score_list_s[0:top_n_value])
print(top_sentiment_list_s[0:top_n_value])
print(result_list_s[0:top_n_value])
print('End of DetectSentiment\n')
