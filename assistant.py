from typing import cast
import os
from dotenv import load_dotenv
import chainlit  as cl
from agents import Agent , Runner , AsyncOpenAI , OpenAIChatCompletionsModel
from agents.run import RunConfig
from agents.tool import function_tool

from tools import add_product, get_product_details  , remove_product , update_product , list_all_products
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI API KEY is not set .Please ensure it is defined in your .env file")
@cl.on_chat_start
async def starting():
        
    external_client = AsyncOpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",

    )

    model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=external_client
    )

    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True

    )


    @function_tool
    def get_product_info(name: str) -> str:
        """Get product details, including name, price, and description."""
        return get_product_details(name)

    @function_tool
    def add_new_product(name: str, price: float, description: str) -> str:
        """Add a new product to the store."""
        return add_product(name, price, description)

    @function_tool
    def remove_products(name: str) -> str:
        """Remove a specific product from the inventory."""
        return remove_product(name)

    @function_tool
    def updates_product(name: str, new_name: str , new_price: float , new_description: str ) -> str:
        """Update a product's name, description, or price.  
        If the admin wants to update only a single value (e.g., just the description),  
        update it while keeping the remaining values unchanged."""
        return update_product(name, new_name, new_price, new_description)
    
    @function_tool
    def all_products() -> str:
        """Retrieve the names of all available products in the inventory."""
        return list_all_products()
    


    product_info_agent: Agent = Agent(
        name="Product Information Agent",
        instructions="You provide product details, including name, price, and description. When a user requests product details, you are responsible for displaying the information.",
        model=model,
        tools=[get_product_info]
    )

    add_new_product_agent: Agent = Agent(
        name="Product Addition Agent",
        instructions="You add new products using the add_new_product tool when the user provides a name, price, and description.",
        model=model,
        tools=[add_new_product]
    )

    product_delete_agent: Agent = Agent(
        name="Product Removal Agent",
        instructions="You are responsible for removing products from the inventory using the remove_products tool by their name.",
        model=model,
        tools=[remove_products]
    )

    update_product_agent: Agent = Agent(
        name="Product Update Agent",
        instructions="""You update products in the inventory by taking their name, new name, new price, and new description.  
        If a user wants to update only a single value, you take the name and update only the specified attribute while keeping others unchanged.""",
        model=model,
        tools=[updates_product]
    )
    list_products_agent: Agent = Agent(
    name="Product Listing Agent",
    instructions="You provide the names of all available products in the inventory when a user requests  which products are you selling .",
    model=model,
    tools=[all_products]
)

    agent: Agent = Agent(
        name="Shopping Agent",
        instructions="""You are a shopping agent responsible for delegating tasks to specific agents.
        - If a user requests to add a new product, delegate the task to the Product Addition Agent.
        - If a user requests product details, delegate the task to the Product Information Agent.
        - If a user requests to remove a product, delegate the task to the Product Removal Agent.
        - If a user requests to update a product, delegate the task to the Product Update Agent.
        """,
        model=model,
        handoffs=[add_new_product_agent, product_info_agent, product_delete_agent, update_product_agent, list_products_agent]
    )
    cl.user_session.set("chat_history", [])
    cl.user_session.set("agent", agent)
    cl.user_session.set("config", config)


    await cl.Message(content="I am your Shopping Assistant.How can i assist you today? ").send()


@cl.on_message
async def main(message : cl.Message):
    msg = cl.Message("Thinking...")
    await msg.send()

    
    agent : Agent = cast(Agent , cl.user_session.get("agent"))
    config : RunConfig = cast(RunConfig , cl.user_session.get("config"))
    history = cl.user_session.get("chat_history") or []

    history.append({"role": "user", "content": message.content})

    result = Runner.run_sync(agent , history , run_config=config)
    output = result.final_output
    msg.content = output
    await msg.update()

    history.append({"role": "developer", "content": output})

    cl.user_session.set("chat_history", history)



# async def main():
#     admin = input("How can i halp you: ")
#     result = await Runner.run(agent , admin, run_config=config)
#     print(f"Response : {result.final_output}")

# if __name__ == "__main__":
#     asyncio.run(main())

