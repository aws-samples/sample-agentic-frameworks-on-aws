import uuid
from typing import Any, Dict, List, Optional, Tuple
from agentic_memory.base import BaseEpisodicStore, BaseLongTermStore, BaseConsolidator
import boto3, botocore
import json

class Consolidator:
    def __init__(self, episodic_store: BaseEpisodicStore, long_term_store: BaseLongTermStore):
        self.episodic_store = episodic_store
        self.long_term_store = long_term_store
        self.bedrock_client = boto3.client('bedrock-runtime')

    def consolidate(self, key: Tuple) -> str:
        # Retrieve episodic events
        events = self.episodic_store.get(key)
        if not events:
            return "No episodic events to consolidate."

        # Prepare prompt with event details for LLM summarization
        prompt = self._build_prompt(events)
        #print(prompt)
        # Call LLM to summarize (user implements this)
        summary = self.call_bedrock_nova(prompt)

        vin = key[1] if len(key) > 1 else key[0]
        summary = summary.replace("```","").replace("json","")
        print(summary)
        summary = json.loads(summary)
        self.long_term_store.put(vin, summary)
        return f"Consolidated {len(events)} episodic events for {vin}."


    def format_cost(self,cost):
        if isinstance(cost, dict):
            return ", ".join([f"{k}: {v}" for k, v in cost.items()])
        elif isinstance(cost, (float, int)):
            return f"total: {cost}"
        else:
            return ""
    
    def _build_prompt(self, events: List[Dict]) -> str:
        prompt_lines = [
            "You are an expert automotive service assistant. Summarize the following vehicle service events into a concise, structured long-term memory record suitable for persistent storage.",
            "Remove duplicate items where necessary",
            "Each event contains detailed technician notes, issues observed, customer agreements, and a cost breakdown.",
            "",
            "Format your summary as a JSON object with the following fields:",
            "  - issue_summary: str",
            "  - resolution: str",
            "  - service_engineer: str",
            "  - service_date: str",
            "  - additional_notes: str",
            "  - cost: {parts: float, labor: float, tax: float, total: float}",
            "",
            "Here are the episodic events:"
        ]
        
        for idx, event in enumerate(events, 1):
            value = event.get("value", {})
            prompt_lines.append(f"\nEvent {idx}:")
            prompt_lines.append(f"  Service Type: {value.get('service_type', '')}")
            prompt_lines.append(f"  Mileage: {value.get('technician_checks', '')}")
            prompt_lines.append(f"  Dealer: {value.get('dealer', '')}")
            prompt_lines.append(f"  Technician Name: {value.get('technician_name', '')}")
            prompt_lines.append(f"  Technician Checks: {', '.join(value.get('technician_checks', []))}")
            prompt_lines.append(f"  Issues Observed: {', '.join(value.get('issues_observed', []))}")
            prompt_lines.append(f"  Customer Agreement: {value.get('customer_agreement', '')}")
            prompt_lines.append(f"  Service Notes: {value.get('service_notes', '')}")
            prompt_lines.append(f"  Service Date: {value.get('service_date', '')}")
            prompt_lines.append(f"  type: {value.get('type', '')}")
            prompt_lines.append(f"  Text: {value.get('text', '')}")
            prompt_lines.append(f"  Timestamp: {value.get('timestamp', '')}")
            cost_str = self.format_cost(value.get('cost'))
            prompt_lines.append(f"  Cost Breakdown: {cost_str}")
        prompt_lines.append("\nSummarize these events as described above.")
        return "\n".join(prompt_lines)
    

    def call_bedrock_nova(self, prompt: str, max_retries: int = 3) -> str:
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        retries = 0
        while retries < max_retries:
            try:
                response = self.bedrock_client.invoke_model(
                    modelId="us.amazon.nova-pro-v1:0",
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps(request_body)
                )
                result = json.loads(response['body'].read())
                # Adjust this line if Nova's output format changes
                return result.get('output', [{}]).get('message',{}).get('content',[])[0].get('text')
            except botocore.exceptions.ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == "ThrottlingException":
                    print(f"ThrottlingException encountered {retries}. Waiting 60 seconds before retrying...")
                    time.sleep(60)
                    retries += 1
                else:
                    raise
            except Exception as e:
                # Optionally handle other exceptions or re-raise
                raise
        raise RuntimeError("Max retries exceeded for Bedrock Nova call due to throttling.")