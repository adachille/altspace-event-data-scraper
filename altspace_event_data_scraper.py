from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import requests
import re
import sched
import time
import traceback

# Gets information related to all current events
def get_data_for_all_current_events():
    results = {}
    try:
        # Navigate to the main page
        main_events_page_url = base_url + "/events/main"
        main_events_result = requests.get(main_events_page_url)
        data = main_events_result.text
        main_events_page = BeautifulSoup(data, 'html.parser')

        # Get list of event links
        event_links = main_events_page.find_all("a", class_="block-link")
        for event_link in event_links:
            # Navigate to event page
            event_url = base_url + event_link['href']
            event_result = requests.get(event_url)
            event_data = event_result.text
            event_page = BeautifulSoup(event_data, 'html.parser')
            live_marker = event_page.find('div', class_="live-text") # used to check if event is live
            
            # Quit if no live marker because we've reached the end of the live events
            if live_marker is None:
                break
            
            # Get event id
            event_id = re.search('.*/([0-9]*)', event_url)[1]
            
            # Get title and tagline
            title_el = event_page.find('div', class_="title")
            title = title_el.find('h1', class_="name").text
            tagline = title_el.find('h2', class_="tagline").text
            
            # Get owner and url for ch
            owner_el = event_page.find('div', class_="owner")
            is_channel = owner_el.find('div', class_="favorite-button") is not None
            owner_name = ''
            owner_url = ''
            if is_channel:
                owner_name = owner_el.find('h2').text
                owner_url = base_url + owner_el.find('a')['href']
            else:
                owner_name = owner_el.find('h3').text
            
            # Get start and times
            time_el = event_page.find('div', class_="time-info-one-line-no-day-of-week")
            start_time_unix = time_el['data-unix-start-time']
            end_time_unix = time_el['data-unix-end-time']

            # Get number of people inside event
            num_people = int(event_page.find('div', class_="stat--value").text) # used to check if event is live
            
            # Add all the information to a data dictionary
            results[event_id] = {
                'url': event_url,
                'title': title,
                'tagline': tagline,
                'is_channel': is_channel,
                'owner_name': owner_name,
                'owner_url': owner_url,
                'start_time_unix': start_time_unix,
                'end_time_unix': end_time_unix,
                'num_people': num_people
            }
            
        return results

    except:
        print("Exception occured while attempting to collect data, returning None")
        traceback.print_exc()
        return None

def capture_data():
    call_time = datetime.now()
    data = get_data_for_all_current_events()
    retrieval_time = datetime.now()
    data_df = pd.DataFrame(data.values(), index=data.keys())
    data_df['retrieval_time'] = retrieval_time.strftime("%m-%d-%Y %H-%M-%S")
    data_df.index.set_names('event_id', inplace=True)
    data_df.to_csv(save_dir + retrieval_time.strftime("%m-%d-%Y %H-%M-%S") + '.csv')
    print(f"c_time: {call_time} | r_time: {retrieval_time} | f_time: {datetime.now()}")

if __name__ == '__main__':
    base_url = "https://account.altvr.com"
    save_dir = './result'
    # Run every 15 minutes
    start_time = time.time()
    delay_time = 900.0
    import pdb; pdb.set_trace()
    while True:
        capture_data()
        time.sleep(delay_time - ((time.time() - start_time) % delay_time))