"""
situation:  list of strings containing the situation descriptions
utterances: list of dictionaries, each of which has two keys which are lists of strings.
    candidates: [next_utterance_candidate_1, ..., next_utterance_candidate_19]
        The last candidate is the ground truth response observed in the conversational data
    history: [dialog_turn_0, ... dialog_turn N], where N is an odd number since the other user starts every conversation.
Preprocessing:
    - Spaces before periods at end of sentences
    - everything lowercase
"""
EXAMPLE_ENTRY = {
        "situation": [
            "i work , so i am not free during the day .",
            "we promised to go to the sea .",
            "i don't like to make a itinerary ."
        ],
        "utterances": [
            {
                "candidates": [
                    "i want to know if there will be any problems if i can't make it to school today .",
                    "they need to put it in the place where it\u2019s visible .",
                    "oh man , i got an interview next week so there's a lot to prepare for .",
                    "it is made of pvc coated fabric our company mainly uses .",
                    "isn't the shuttle bus stop to the hotel in front of the airport ?",
                    "you cannot get your ticket issued without your passport .",
                    "i heard that it has become a trend to exercise at home recently . that is why i plan to buy a yoga mat .",
                    "i thought it was about 10 minutes , but i don't exactly know .",
                    "it depends on the area , but there is a basic charge of 2,000 won for delivery .",
                    "did you come to our after-sales service center because of that vacuum cleaner ?",
                    "shipping starts within about 2 days from the completion of the payment .",
                    "i am sorry but you cannot use this card for payment .",
                    "i'm going to use it only in the city but is it correct that the pass is for unlimited usage ?",
                    "you have to bear a certain level of discomfort staying in a multiple-person room .",
                    "this program was also planned by the most well-known producer in the country .",
                    "college students are already on vacation , but we are going to school at 8 .",
                    "how many hours will it take to get to prague ?",
                    "the fee is 5,000 won and it seems i've wrongly charged 3,000 won .",
                    "i am in the caf\u00e9 in front , can you come here ?"
                ],
                "history": [
                    "i have arrived in front of the office but the door is locked ."
                ]
            },
            {
                "candidates": [
                    "i'm going to fast intermittently starting today .",
                    "can you tell me how many of you there are first ?",
                    "can you move me to the seat in front of me ?",
                    "it smells good and i'd love to try it , but unfortunately , i have an allergy to peaches .",
                    "yes , take this ticket and you can get on in 10 minutes .",
                    "that's why . no wonder i saw many bouquets today .",
                    "i guess the application proceeded the latest updates .",
                    "reservation are possible the day after tomorrow , i will help you if you tell me your name and number .",
                    "why don't you take leave mid-day , go home and rest ?",
                    "ok . i'll exchange currencies and call you back .",
                    "everyone has their beginner days .",
                    "i see i didn't know the detailed regulations were different by country .",
                    "yes , but the inflight duty-free has an event for pre-payment .",
                    "this lead breaks too easy , do you have anything else ?",
                    "they're so talented that they go on outside performances .",
                    "today's deadline for delivery requests was 6 o'clock , and it's possible if you to make a request for a delivery tomorrow .",
                    "yes , the traffic will probably be heavy tomorrow since it's the weekend and the weather is nice .",
                    "excuse me , i am the person who got a refund after canceling the hotel yesterday .",
                    "i will do that , what is the exact location of the caf\u00e9 ?"
                ],
                "history": [
                    "i have arrived in front of the office but the door is locked .",
                    "i am in the caf\u00e9 in front , can you come here ?"
                ]
            },
            {
                "candidates": [
                    "i need to smoke to deal with your incessant nagging .",
                    "there is various food , so do you have any favorite food ?",
                    "please tell us a few things that we need to keep in mind as spectators before the performance starts .",
                    "didn't you say in confidence that you studied really hard yesterday ?",
                    "sorry , i'm not feeling well , so i will send it by tomorrow .",
                    "since it was released as a short dress , it would be very short for you .",
                    "when will you be back home , can i change the delivery date ?",
                    "why did you change so much money ? you've exchange twice more than what i've exchanged .",
                    "you can see the gate by looking at the screen over there .",
                    "it doesn't matter which line we take , but i prefer line 6 .",
                    "the breeze is cool and the floor is also softer than i thought .",
                    "check the color on your hand and you'll see right away .",
                    "the potatoes at the bottom of the box are all moldy .",
                    "how can i get a taxi as soon as possible after the game against that team ?",
                    "the true tour begins when we enter the cathedral .",
                    "surgery is done , and all i have left is physical therapy .",
                    "i would like the laptop case and a cordless mouse .",
                    "these new running shoes are very comfortable so they're very popular .",
                    "if you look opposite , it is next to the bank building ."
                ],
                "history": [
                    "i have arrived in front of the office but the door is locked .",
                    "i am in the caf\u00e9 in front , can you come here ?",
                    "i will do that , what is the exact location of the caf\u00e9 ?"
                ]
            }
        ]
}
