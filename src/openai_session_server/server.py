import asyncio
#from openai_session_handler.models.genericassistant import GenericAssistant

from openai_session_handler import list_assistants_by_type

from openai_session_handler.models.assistants.baseassistant import BaseAssistant
from openai_session_handler.models.stream_thread import StreamThread

REGISTERED_ASSISTANTS = {

}

def _add_registered_assistant( registered_assistant_class ):
    REGISTERED_ASSISTANTS[registered_assistant_class.__name__] = registered_assistant_class

def _rm_registered_assistant(registered_assistant_class_name):
    del REGISTERED_ASSISTANTS[registered_assistant_class_name]

def _list_registered_assistants():
    return [registered_assistant for registered_assistant in REGISTERED_ASSISTANTS.keys()]


async def monitor_assistant(Assistant, assistant_id):

    def process_in_seq(assistant, st_msgs) :
        for x in st_msgs:
            sqlish = x.content[0]['value']
            assistant.process_sqlish(sqlish)
    try:
        while True:
            assistant = Assistant.retrieve(assistant_id=assistant_id)
            sthread_id = assistant.pub_thread
            st = StreamThread.retrieve(thread_id=sthread_id)
            print(f"High Water Mark = {st.hwm}")

            limit = 3

            process_from_begin = False

            if st.hwm == "":
                process_from_begin = True

            if process_from_begin == True:
                st_msgs = st.list_messages(limit=limit, order="asc")

                while len(st_msgs) > 0:
                    print("batch")
                    after = st_msgs[-1].id
                    process_in_seq(assistant, st_msgs)
                    st.set_hwm(after)

                    st_msgs = st.list_messages(limit=3, order="asc", after=after)

            else:
                process_st_msgs = []
                conti = True
                st_msgs = st.list_messages(limit=limit)
                
                while len(st_msgs) > 0 and conti == True :
                    for st_msg in st_msgs :
                        if (st_msg.id != st.hwm) : 
                            process_st_msgs.append(st_msg)
                        else:
                            conti = False
                            break
                    after = st_msgs[-1].id
                    st_msgs = st.list_messages(limit=limit, after=after)
                    
                
                if len(process_st_msgs) != 0:
                    process_st_msgs = process_st_msgs[::-1]
                    process_in_seq(assistant, process_st_msgs)
                    hwm = process_st_msgs[-1].id
                    st.set_hwm(hwm=hwm)
                else: 
                    print("No event on thread")
                    
            await asyncio.sleep(5)  # Interval between checks
    except Exception as e:
        log_error(assistant_id, e)


def check_assistant_for_cud_and_take_action(assistant_id, sthread_id, hwmthread_id):
    st = StreamThread.retrieve(thread_id=sthread_id)
    st_msgs = st.list_messages()
    for x in st_msgs:
        pass



async def check_for_entity (entity_list) -> BaseAssistant:
    for assistant_type_name, assistant_type in REGISTERED_ASSISTANTS.items():    
        for (assistant_id, _, _)  in list_assistants_by_type(assistant_type=assistant_type_name) : 
        
            if assistant_id in entity_list:
                return None, None
            else:
                return assistant_type, assistant_id
        else:
            return None, None


async def resource_watcher(task_queue, entity_list):
    try:
        while True:
            assistant_type, assistant_id = await check_for_entity(entity_list)
            if assistant_id != None:
                task = asyncio.create_task(monitor_assistant(assistant_type, assistant_id))
                task_queue.append(task)
                entity_list.append(assistant_id)                
            else:
                pass
            await asyncio.sleep(5)  # Interval between checks for new entities
    except Exception as e:
        log_error('ResourceWatcher', e)


def log_error(source, error):
    # Implement real logging here
    print(source, error)

async def main() :
    task_queue = []
    entity_list = []

    watcher_task = asyncio.create_task(resource_watcher(task_queue, entity_list))
    task_queue.append(watcher_task)

    await asyncio.gather(*task_queue)

def run_main() : 
    asyncio.run(main())

if __name__ == "__main__":
    print("in main")
    run_main()

