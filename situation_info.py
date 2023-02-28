anno_to_situ = {
    "Workplace": ("i don't want to talk to my boss .", "i don't understand this situation .", "i have to copy the report ."),
    "Customer service (refunds/cancellations)": (
        "i need to talk to the customer on the phone .",
        "the customer wants to cancel the payment .",
        "the customer wants to return it because of the product defect .",
    ),
    "CS/Customer Service ": (
        "i'm using a duty-free shop .",
        "i'm curious about using the duty-free shop .",
        "i'm at the duty-free shop .",
    ),
    "Debate for and against": ("i'm in a meeting .", "i am talking about pros and cons ."),
    "Job interview": ("i'm unemployed .", "i'm looking for a job .", "i'm having a job interview ."),
    "School life": ("i just took a quiz .", "i have a test .", "i have a family road trip planned for the western u.s."),
    "Talking to a salesperson or friend about the style": (
        "i came to the hair salon .",
        "i want to change my hairstyle .",
        "i'm talking to the clerk about the style i want .",
    ),
    "Making suggestions and negotiating": (
        "i am worried that our company's mobile phone sales are declining .",
        "i have a business conversation .",
        "i'm negotiating with business customers .",
    ),
    "Packaging/Delivery": ("i want to wrap the leftovers .", "i wonder if there is a delivery .", "i don't want to eat here ."),
    "Marketing/Promotion ": (
        "the project proposal is due tomorrow ,",
        "a new product was released last week .",
        "i want to negotiate the price .",
    ),
    "Introducing products": (
        "i am confident in selling the product .",
        "i think the product is pretty .",
        "i think i'll sell out soon .",
    ),
    "Finding and selecting items": (
        "i'm going to ask the staff where this is .",
        "there's nothing i'm looking for .",
        "i don't know what to choose .",
    ),
    "Talking about symptoms": (
        "i came to the hospital because i was sick .",
        "i'm talking to a doctor about symptoms .",
        "i'm talking to a doctor at the hospital .",
    ),
    "Cosmetics shop": (
        "i want to buy eyeliner .",
        "i want to get a lipstick color recommendation .",
        "i'm in a new cosmetics store .",
    ),
    "IT/computer (repair)": (
        "there is a problem with computers and it devices .",
        "i am a pc repair engineer .",
        "i'm talking about pc repair .",
    ),
    "Arrival/Departure (Immigration, Baggage, Security)": (
        "i'm traveling to another country .",
        "i want to send my baggage to the plane .",
        "i'm at the airport .",
        "i'm nervous about immigration .",
    ),
    "Scheduling a meeting": ("i'd like to schedule a meeting .", "i coordinate the schedule .", "i have a meeting ."),
    "Eating and evaluating food": ("i am eating food .", "i am evaluating after eating food .", "i am a food critic ."),
    "Special products/deliveries": (
        "i'm making a special request for product and delivery .",
        "i'm trying to get a product .",
        "it is asking the seller .",
        "i want gift wrapping .",
    ),
    "Bookstores, stationery stores": (
        "i'm in the book store",
        "i'm at the stationery store .",
        "i'm trying to buy stationery .",
    ),
    "Inquiring/responding to the delivery status of an ordered item": (
        "i orderd the product .",
        "i am inquiring about the delivery status .",
    ),
    "Talking about medication instructions": (
        "i'm talking about how to take medicine .",
        "i'm talking to the pharmacist .",
        "i'm curious about the dosage .",
    ),
    "Making business arrangements for traveling for work": (
        "i'm going on a business trip .",
        "i have to prepare for a business trip .",
    ),
    "Travel expenses": (
        "i have to pay for the business trip expenses .",
        "a few days ago went on a business trip .",
        "i'm talking to the accounting staff .",
    ),
    "Hospitalization/discharge": ("i have been hospitalized .", "i am leaving the hospital .", "i'm talking to the patients ."),
    "Making corrections to your order history": (
        "the order details need to be revised .",
        "i ordered the product .",
        "i'm talking to custormer service agent .",
    ),
    "Taking an exercise lesson": ("i'm taking exercise lessons .", "i'm working out ."),
    "At an art gallery or museum": ("i'm talking at art galleries and museums .", "i'm a museum ."),
    "Having a problem with a product": (
        "i bought something .",
        "there is a problem with the product .",
        "i'm talking to a counselor .",
    ),
    "At a theater or performance venue": ("i'm in the theater .", "i'm talking at the theater .", "i'm watching a play ."),
}


situ_to_anno = {v: k for k, v in anno_to_situ.items()}
