from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper

app = FastAPI()

inprogress_orders = {}


@app.post("/")
async def handle_request(request: Request):
    # Retrieve the JSON data from the request
    payload = await request.json()

    # Extract the necessary information from the payload
    # based on the structure of the WebhookRequest from Dialogflow
    intent = payload["queryResult"]["intent"]["displayName"]
    parameters = payload["queryResult"]["parameters"]
    output_contexts = payload["queryResult"]["outputContexts"]
    session_id = generic_helper.extract_session_id(output_contexts[0]['name'])

    intent_handler_dict = {
        'new.appointment': new_order,
        'appointment.add - context: ongoing-appointment': add_to_order,
        # 'order.remove - context: ongoing-order': remove_from_order,
        'appointment.complete - context: ongoing-appointment': complete_order,
        'check.status - context: ongoing-check': track_order,
    }

    # Call the appropriate intent handler function
    return intent_handler_dict[intent](parameters, session_id)


def new_order(parameters: dict, session_id: str):
    del inprogress_orders[session_id]
    return JSONResponse(content={
        "fulfillmentText": 'Starting new appointment. Specify doctor names. For '
                           'example, you can say, "I would like to book an '
                           'appointment with Dr. D. N. Banerjee".'})


def add_to_order(parameters: dict, session_id: str):
    food_items = parameters["doctor-name"]
    quantities = [1,]

    if len(quantities) != len(food_items):
        fulfillment_text = ("Sorry I didn't understand. Can you please specify "
                            "doctor names clearly?")
    else:
        new_food_dict = dict(zip(food_items, quantities))

        if session_id in inprogress_orders:
            current_food_dict = inprogress_orders[session_id]
            current_food_dict.update(new_food_dict)
            inprogress_orders[session_id] = current_food_dict
        else:
            inprogress_orders[session_id] = new_food_dict

        order_str = generic_helper.get_str_from_food_dict(
            inprogress_orders[session_id])
        fulfillment_text = (f"So far you have an appointment with {order_str}. Do "
                            f"you want to confirm the appointment? Say 'Yes' to "
                            f"confirm otherwise say 'New Appointment'.")

    # Generate the response
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        fulfillment_text = ("I am having trouble finding your appointment. Can you "
                            "place a new appointment again?")
    else:
        order = inprogress_orders[session_id]
        order_id = save_to_db(order)

        if order_id == -1:
            fulfillment_text = "Sorry, I couldn't process your appointment due to a " \
                                "backend error. " \
                               "Please place a new appointment again."

        else:
            order_total = db_helper.get_total_order_price(order_id)
            fulfillment_text = f"Awesome. We have placed your appointment. " \
                               f"Here is your appointment id # {order_id}. " \
                               f"Your appointment fees is Rs. {order_total} which you " \
                               "can pay at the hospital while visiting the doctor."

        del inprogress_orders[session_id]

        return JSONResponse(content={
            "fulfillmentText": fulfillment_text
        })


def save_to_db(order: dict):
    # order = {"pizza": 2, "chole": 1}
    next_order_id = db_helper.get_next_order_id()

    for food_item, quantity in order.items():
        rcode = db_helper.insert_order_item(
            food_item,
            quantity,
            next_order_id
        )

        if rcode == -1:
            return -1

    db_helper.insert_order_tracking(next_order_id, "waiting")

    return next_order_id


def remove_from_order(parameters: dict, session_id: str):
    fulfillment_text = ""
    if session_id not in inprogress_orders:
        return JSONResponse(content={
            'fulfillment_text': "I am having trouble finding your appointment. Can you "
                                "place a new appointment again?"})

    current_order = inprogress_orders[session_id]
    food_items = parameters["doctor-item"]

    removed_items = []
    no_such_items = []

    for item in food_items:
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]

    if len(removed_items) > 0:
        fulfillment_text = f'Removed {",".join(removed_items)} from your appointment.'

    if len(no_such_items) > 0:
        fulfillment_text += (f' Your current appointment does not have '
                             f'{",".join(no_such_items)}.')

    if len(current_order.keys()) == 0:
        fulfillment_text += ' Your appointment is empty.'
    else:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        fulfillment_text += f' Here is what is in your appointment: {order_str}.'

    return JSONResponse(content={
        'fulfillmentText': fulfillment_text
    })


def track_order(parameters: dict, session_id: str):
    # Extract the necessary parameters
    order_id = int(parameters["appointment_id"])
    order_status = db_helper.get_order_status(order_id)

    if order_status:
        fulfillment_text = (f"The appointment status for appointment id: {order_id} "
                            f"is: {order_status}")
    else:
        fulfillment_text = f"No appointment found with appointment id: {order_id}"

    # Generate the response
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })
