# ISSUES
I started with rasa pro 3.11, and updated to rasa 3.12 just yesterday. Some observations may be irrelevant now.

## EnterpriseSearch
- Unable to use (faiss)[https://pypi.org/project/faiss/]] due to necessity downgrade python version to 3.7
- This:
  ```python
  from rasa.utils.endpoints import EndpointConfig
  from rasa.core.information_retrieval import SearchResultList, InformationRetrieval
  
  class MyVectorStore(InformationRetrieval):
      def connect(self, config: EndpointConfig) -> None:
          # Create a connection to the search system
          pass
  
      async def search(
          self, query: Text, tracker_state: dict[Text, Any], threshold: float = 0.0
      ) -> SearchResultList:
          # Implement the search functionality to retrieve relevant results based on the query and top_n parameter.
          pass
  ```
  from [here](https://rasa.com/docs/reference/config/policies/custom-information-retrievers#creating-a-custom-information-retrieval-class)
  Did not work for me for several reasons
  - `query` paramter also contained message sent by assistant (something like 'Moment please..' that assistant utters before running search), not only user. Theese messages appeared to be concatenated somehow..
  - I was unable to set embedding model I needed. This `text-embedding-ada-002` remained unchanged whatever I tried.
  - The easiest approach was to implement a custom action, that does it all.

## Slots
- I had to use `reset_after_flow_ends: false` instead of `persistent_slots`, because, slots values set in one flow were unable in other flow, what was crucial for my case.

## Other
- triggers session_start action twice. Don't know why. Faced this problem, while implementing welcome phrase from `AI MOTO EXPERT`
- Look's like flow's names are not using anywhere. why do weee need it? I see flow_ids everywhere. even in default CMD generator's prompt template.
