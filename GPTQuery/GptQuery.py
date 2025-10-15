import asyncio
import aiohttp
import json

class Query:
    def __init__(self, requestJSON : bool):
        self.query = {
                "messages": [],
                "RequestJSON": requestJSON
            }

    def AddSystemMessage(self, message):
        self.query["messages"].append({"role": "system", "content": message})

    def AddAssistantMessage(self, message):
        self.query["messages"].append({"role": "assistant", "content": message})

    def AddUserMessage(self, message):
        self.query["messages"].append({"role": "user", "content": message})


    def getJSON(self):
        """Returns the JSON string representation of the query."""
        return json.dumps(self.query, indent=4)

class Gpt:

    def __init__(self, batch_size: int = 10):
        self.api_endpoint = "https://legoresearch.econlabs.org/gpt/rungptquery"
        self.batch_size = batch_size
        self.total_tasks = 0
        self.completed_tasks = 0
        self.errors = 0
        self.results = []

    async def _send_task_to_api(self, session, task_data):
        headers = {"Content-Type": "application/json"}
        try:
            async with session.post(self.api_endpoint,
                                    data=task_data.getJSON(),
                                    headers=headers) as response:
                response.raise_for_status()
                js = json.loads(await response.text())
                if js.get("error"):
                    self.errors += 1
                else:
                    self.completed_tasks += 1
                return js
        except aiohttp.ClientError as e:
            self.errors += 1
            return {"answer": None, "error": str(e)}

    async def execute_queries_async(self, tasks: list):
        """
        Launch all tasks immediately but never allow more than
        self.batch_size concurrent HTTP requests.
        """
        self.total_tasks = len(tasks)
        self.completed_tasks = 0
        self.errors = 0
        self.results = [None] * self.total_tasks

        sem = asyncio.Semaphore(self.batch_size)

        async def worker(idx, task_data, session):
            async with sem:
                result = await self._send_task_to_api(session, task_data)
                self.results[idx] = result
                print(
                    f"Status: {self.completed_tasks}/{self.total_tasks} tasks done "
                    f"[errors: {self.errors}].",
                    end="\r",
                    flush=True,
                )

        async with aiohttp.ClientSession() as session:
            # create and schedule all tasks at once
            coros = [worker(i, t, session) for i, t in enumerate(tasks)]
            await asyncio.gather(*coros)

        print()  # move to a new line after progress output
        return self.results

    def execute_queries(self, tasks: list):
        return asyncio.run(self.execute_queries_async(tasks))

