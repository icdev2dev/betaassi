from threads.basethread import BaseThread
from typing import Optional
from pydantic import Field
from messages.basemessage import BaseMessage
from runs.baserun import BaseRun


class RunThread(BaseThread):

    current_run_id: Optional[str] = Field(default="")

    def request_response(self, assistant_id, content:str): 

        _ = BaseMessage.create(thread_id=self.id, role='user', content=content)
        base_run = BaseRun.create(thread_id=self.id, assistant_id=assistant_id)
        self.set_current_run_id(base_run.id)

    def response_to_request(self): 

        if self.current_run_id != None:
            base_run = BaseRun.retrieve(thread_id=self.id, run_id=self.current_run_id)
            if base_run.status == 'completed': 
                base_msgs = BaseMessage.list(thread_id=self.id)
                return ('completed', base_msgs[0].content[0]['text']['value'])    
            else:
                return ('pending', '')
            
        return ('no_current_run', '')
