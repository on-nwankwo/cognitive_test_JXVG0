from IPython.display import display, Image, clear_output, HTML
import time
import random
random.seed(1)
import ipywidgets as widgets
from jupyter_ui_poll import ui_events
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json

# ----------------------------------------------------------------------------

"""
Defining the images into a dictionary to be used later.

The image titles have the number of dots for each side
    Picture18.21 has 18 dots on blue and 20 dots on yellow
The value in the dictionary is the correct answer to be used later
"""

image_data = {
        "Picture09.10.png": "YELLOW",
        "Picture09.12.png": "YELLOW",
        "Picture10.09.png": "BLUE",
        "Picture12.09.png": "BLUE",
        "Picture12.14.png": "YELLOW",
        "Picture12.16.png": "YELLOW",
        "Picture14.12.png": "BLUE",
        "Picture15.20.png": "YELLOW",
        "Picture16.12.png": "BLUE",
        "Picture16.18.png": "YELLOW",
        "Picture18.16.png": "BLUE",
        "Picture18.20.png": "YELLOW",
        "Picture18.21.png": "YELLOW",
        "Picture20.15.png": "BLUE",
        "Picture20.18.png": "BLUE",
        "Picture21.18.png": "BLUE",
        "Picture09.10.big.png": "YELLOW",
        "Picture09.12.big.png": "YELLOW",
        "Picture10.09.big.png": "BLUE",
        "Picture12.09.big.png": "BLUE",
        "Picture12.14.big.png": "YELLOW",
        "Picture12.16.big.png": "YELLOW",
        "Picture14.12.big.png": "BLUE",
        "Picture15.20.big.png": "YELLOW",
        "Picture16.12.big.png": "BLUE",
        "Picture16.18.big.png": "YELLOW",
        "Picture18.16.big.png": "BLUE",
        "Picture18.20.big.png": "YELLOW",
        "Picture18.21.big.png": "YELLOW",
        "Picture20.15.big.png": "BLUE",
        "Picture20.18.big.png": "BLUE",
        "Picture21.18.big.png": "BLUE",
    }

# ----------------------------------------------------------------------------

results_dict = {
    'filename': [],
    'nL': [],
    'nR': [],
    'ratio': [],
    'time': [],
    'correct': []
}
    
# ----------------------------------------------------------------------------

def display_img(img_file):
    """
    Function to display the images provided above
    """
    style_str = f'width: 500px;'
    html_out = HTML(f"<img style='{style_str}' src={img_file}></img>")
    display(html_out)

# ----------------------------------------------------------------------------

# function below lets buttons register events when clicked

event_info = {
    'type': '',
    'description': '',
    'time': -1
}

def register_btn_event(btn):
    """
    Function updates the event info dictionary with the details of the button click

    The button "type" and "description" will be used to register
    if the participant made the correct choice.
    """
    event_info['type'] = "button click"
    event_info['description'] = btn.description
    event_info['time'] = time.time()
    return

# ----------------------------------------------------------------------------

# function that waits for an event or specified timeout duration
# while checking for UI events (User Interface)

def wait_for_event(timeout=-1, interval=0.001, max_rate=20, allow_interupt=True):
    '''
    The function waits for an event or a specified timeout duration

    - Processes user interface (UI) events
    - Ends the loop if we have waited more than the timeout period or if the button is clicked
    - If the button is clicked, returns the description (colour chosen by the user)
    - If the button is not clicked, the event ends and the description is an empty string
        This is because no event occurred
    '''
    start_wait = time.time()

    event_info['type'] = ""
    event_info['description'] = ""
    event_info['time'] = -1

    n_proc = int(max_rate*interval)+1
    
    with ui_events() as ui_poll:
        keep_looping = True
        while keep_looping==True:
            # process UI events
            ui_poll(n_proc)

            # end loop if we have waited more than the timeout period
            if (timeout != -1) and (time.time() > start_wait + timeout):
                keep_looping = False
                
            # end loop if event has occured
            if allow_interupt==True and event_info['description']!="":
                keep_looping = False
                
            # add pause before looping
            # to check events again
            time.sleep(interval)
    
    # return event description after wait ends
    # will be set to empty string '' if no event occured
    return event_info

# ----------------------------------------------------------------------------

def send_to_google_form(data_dict, form_url):
    ''' Helper function to upload information to a corresponding Google form 
        You are not expected to follow the code within this function!
    '''
    form_id = form_url[34:90]
    view_form_url = f'https://docs.google.com/forms/d/e/{form_id}/viewform'
    post_form_url = f'https://docs.google.com/forms/d/e/{form_id}/formResponse'

    page = requests.get(view_form_url)
    content = BeautifulSoup(page.content, "html.parser").find('script', type='text/javascript')
    content = content.text[27:-1]
    result = json.loads(content)[1][1]
    form_dict = {}
    
    loaded_all = True
    for item in result:
        if item[1] not in data_dict:
            print(f"Form item {item[1]} not found. Data not uploaded.")
            loaded_all = False
            return False
        form_dict[f'entry.{item[4][0][0]}'] = data_dict[item[1]]
    
    post_result = requests.post(post_form_url, data=form_dict)
    return post_result.ok

# ----------------------------------------------------------------------------

def ans_single_test(img_file, right_answer):
    '''
    Runs a single ANS test.
 
    Args:
        img_file (str): the image to be displayed
        right_answer (str): the correct answer for the corresponding image

    - Displays the images
    - Tracks time
    - If the button description (i.e. colour) matches the right_answer
        right_answer is given as the value for each image in the image_data dict
    - Data is stored for the Google form    
 
    Returns:
        float: the score for one question (1 if correct, 0 if incorrect)
    '''
    
    display_img(img_file)
    time.sleep(0.75)
    clear_output(wait=True)
    
    display_img("Picture0.png")
    
    start_time_trial = time.time()

    print("Which side had the most circles?")
    print("You have 3 seconds!")

    btn_blue = widgets.Button(description = "BLUE")
    btn_yellow = widgets.Button(description = "YELLOW")
    panel = widgets.HBox([btn_blue, btn_yellow])
    
    btn_blue.on_click(register_btn_event)
    btn_yellow.on_click(register_btn_event)
    
    display(panel)
    result = wait_for_event(timeout=3)
    clear_output(wait=True)

    end_time_trial = time.time()
    time_trial = end_time_trial - start_time_trial

    if result['description'] == 'BLUE':
        print("Blue was chosen")
    elif result['description'] == 'YELLOW':
        print("Yellow was chosen")
    elif result['description'] == '':
        print("No choice was made!")
    
    time.sleep(1.5)
    clear_output(wait=True)
    
    if result['description']==right_answer:
        score = 1
    else:
        score = 0

    results_dict['filename'].append(img_file)
    results_dict['nR'].append(img_file[7:9])
    results_dict['nL'].append(img_file[10:12])
    nR = int(img_file[7:9])
    nL = int(img_file[10:12])
    
    nR_str = str(nR)
    if nR_str[0] == '0':
        nR_str = nR_str[1:]
    nR = int(nR_str)
    
    nL_str = str(nL)
    if nL_str[0] == '0':
        nL_str = nL_str[1:]
    nL = int(nL_str)
    
    results_dict['ratio'].append(nR / nL)

    results_dict['time'].append(time_trial)

    if result['description']==right_answer:
        results_dict['correct'].append('yes')
    else:
        results_dict['correct'].append('no')
   
    return score
    
# ----------------------------------------------------------------------------

def run_quiz():
    '''
    Runs a set of ANS tests for the images given in the image_data dict

    - Displays instructions and gathers user data to be stored in Google sheet
    - Tracks time for the entire test
    - Shuffles images in image_data dict and iterates through them for 64 trials
    - Assigns the keys and values to the img_file and right_answer arguments
        of the single ANS test function
    - Runs the single ANS for each image
    - Stores data for google form and json
 
    Returns:
        the total score for the test
    '''

    score = []    
    
    title = HTML("<h3>The Approximate Number System Test</h3>")
    display(title)
    time.sleep(2)
    print("Hello there! Welcome to the Approximate Number System Test!")
    time.sleep(2)
    print("Before we begin, there is some information to go through.")
    time.sleep(2)
    print("")

    # -----------------------------------------------------------------------

    data_consent_info = """DATA CONSENT INFORMATION:

    Please read:
    
    We wish to record your response data
    to an anonymised public data repository.
    Your data will be used for educational teaching purposes
    practising data analysis and visualisation.
    
    Please type 'yes' in the box below if you consent to the upload."""
    
    print(data_consent_info)
    result = input("> ")
    
    if result == "yes":
        print("Thanks for your participation!")
        print("Please contact 'philip.lewis@ucl.ac.uk'")
        print("if you have any questions or concerns")
        print("regarding the test or the stored results.")
    
    else: # end code execution by raising an exception
        raise(Exception("You did not consent to continue test."))

    clear_output(wait=False)

    # -----------------------------------------------------------------------

    display(title)
    time.sleep(2)
    
    print("The Approximate Number System (ANS) refers to")
    print("a part of our cognition that allows a rapid,")
    print("intuitive sense of numerosities.")
    time.sleep(3)
    print("")
    print("The following test will measure your individual ANS ability.")
    time.sleep(2)
    print("")
    print("For each trial, blue and yellow dots will flash")
    print("on the screen for a brief second.")
    time.sleep(2)
    
    print("")
    print("The images shown will appear similar to this.")
    time.sleep(1)
    display_img("Picture21.18.png")
    time.sleep(2)
    
    print("You will then be asked whether there were more")
    print("blue dots or more yellow dots on the screen.")
    print("Click on the button that corresponds with your answer.")
    time.sleep(4)
    print("")
    print("For each trial, you will have only 3 seconds")
    print("to respond before the next set of images are shown.")
    print("")
    print("The test will last under 5 minutes.")
    time.sleep(5)
    
    clear_output(wait=False)

    display(title)
    time.sleep(2)

    print("Before the test begins, we need some more information about you.")
    print("")
    print("If you would like to proceed, please answer the")
    print("following questions. The information you provide")
    print("and your results may be used for further data analysis.")
    time.sleep(2)

    id_instructions = """
    
    Enter your anonymised ID
    
    To generate a unique, anonymous 4-letter unique user identifier, please enter:
    
      - two letters based on the initials (first and last name) of a childhood friend
      - two letters based on the initials (first and last name) of a favourite actor/actress
    
    e.g. if your friend was called April Snow and the film star was Nicholas Cage
    then your unique identifier would be ASNC
    
    """
    
    print(id_instructions)
    print("What is your User ID?")
    user_id = input(">> ")
    print("Your User ID is:", user_id)
    ans1 = user_id

    clear_output(wait=False)
    time.sleep(1)

    print("")
    print("How old are you? (Please type your age in numbers)")
    ans2 = input(">> ")
    
    clear_output(wait=False)
    time.sleep(1)
    
    print("What gender do you identify with?")
    print("Please choose from the options below:")
    gender_options="""
    f - female
    m - male
    nb - non-binary
    o - other
    na - prefer not to say
    """
    gender_options_list = ["f", "m", "nb", "o", "na"]
    print(gender_options)
    print("For example, if you identify as female, input 'f'")

    while True:
        ans3 = input(">> ").lower()
        if ans3 in gender_options_list:
            break
        else:
            print("Please input one of the options given above.")

    clear_output(wait=False)
    time.sleep(1)
    
    print("Thank you for answering the previous questions.")
    input("If you would like to proceed with the test, press the enter.")
    time.sleep(1)
    clear_output(wait=False)

    start_message = HTML("<h3>The test will now start.</h3>")
    display(start_message)
    time.sleep(2)
    clear_output(wait=False)

    # -----------------------------------------------------------------------
    
    total = 0
    start_time_test = time.time()

    for i in range(4): #iterate four times (16 images x 4 = 64 trials)
        keys = list(image_data.keys())
        random.shuffle(keys)
        shuffled_image_data = {key: image_data[key] for key in keys}

        for key in shuffled_image_data.keys():
            file = key
            right_answer = image_data[key]
   
            score = ans_single_test(file, right_answer)
            total += score

        results_df = pd.DataFrame(results_dict)

    end_time_test = time.time()
    time_test = end_time_test - start_time_test

    data_dict = {
        'id': ans1,
        'age': ans2,
        'gender': ans3,
        'score': total,
        'time': time_test,
        'results_json': results_df.to_json()
    }
    
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfjWt43SiPVOJBCXJIzcKEW4ADPuPJgHnhipwBt4K-I-ZVXng/viewform?usp=sf_link"
    send_to_google_form(data_dict, form_url)
        
    print("You scored", total)
    print("Thank you, once again, for your participation!")
    print("Please contact 'ogo.nwankwo.20@ucl.ac.uk' or 'philip.lewis@ucl.ac.uk'")
    print("if you have any questions further or concerns")
    print("regarding the test or the stored results.")
    
    return total

# ----------------------------------------------------------------------------

run_quiz()