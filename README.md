# Superbench tech assessment note

## cases tested:

1. multi-turn conversation
   
user: I want to book a general cleaning service.
Response content: {'message': "It looks like you didn't mention the type of cleaning services. Can you please specify whether you're looking for a 3-hour or 4-hour cleaning?", 'thread_id': '22', 'requires_more_info': True}

user: 4-hour

{'message': "The next available slot is on 2025-01-01 00:00, and the price is $100 for 3 hours. Would you like to confirm this booking? (Please respond with 'yes' if you'd like to confirm)", 'thread_id': '22', 'requires_more_info': False}

user: yes

Response content: {'message': 'Booking confirmed.', 'thread_id': '22', 'requires_more_info': False}

3. single-turn with type specified
user: I want to book a 3-hour general cleaning service.
Response content: {'message': "The next available slot is on 2025-01-01 00:00, and the price is $120 for 4 hours. Would you like to confirm this booking? (Please respond with 'yes' if you'd like to confirm)", 'thread_id': '22', 'requires_more_info': False}
user: yes.
Response content: {'message': 'Booking confirmed.', 'thread_id': '22', 'requires_more_info': False}

4. post-renovation
   Response content: {'message': "We're connecting you with a human agent.", 'thread_id': '22', 'requires_more_info': False}

   
