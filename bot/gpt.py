import os

from llama_index import LLMPredictor, GPTSimpleVectorIndex, PromptHelper, ServiceContext, SimpleDirectoryReader
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.indices.query.schema import QueryConfig, QueryMode
from llama_index.indices.query.query_runner import QueryRunner
from langchain.chat_models import ChatOpenAI

VECTOR_INDEX_FILE_LIST = os.environ.get("VECTOR_INDEX_FILE_LIST", 'file_not_found')
TOP_K = 5

prompt_helper = PromptHelper(max_input_size=4096, num_output=2048, max_chunk_overlap=20)
llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo", model_kwargs={'engine':'gpt-35-turbo'}))
service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper, embed_model=OpenAIEmbedding(embed_batch_size=1))
vector_index_list = []

def build_index(input_dir, output_file, ext=['.md', '.txt']):
    print("Building new index... It will take a long time.")
    documents = SimpleDirectoryReader(input_dir, recursive=True, required_exts=ext).load_data()
    nodes = service_context.node_parser.get_nodes_from_documents(documents)
    print(f'Documents: {len(documents)}, Chunkes: {len(nodes)}')
    index = GPTSimpleVectorIndex.from_documents(documents, service_context=service_context)
    index.save_to_disk(output_file)


def load_index():
    global vector_index_list
    for file in VECTOR_INDEX_FILE_LIST.split(';'):
        if os.path.exists(file):
            index = GPTSimpleVectorIndex.load_from_disk(file)
            vector_index_list.append(index)
        else:
            raise Exception("Index not found. Please run build_index() first.")
    print("Index loaded from disk.", flush=True)


def ask(query):
    response = multiple_index_query(
        vector_index_list,
        query, 
        service_context=service_context,
        similarity_top_k=TOP_K,
        mode='embedding',
        response_mode='compact'
    )
    return str(response)


async def ask_async(query):
    response = await multiple_index_query_async(
        vector_index_list,
        query, 
        service_context=service_context,
        similarity_top_k=TOP_K,
        mode='embedding',
        response_mode='compact'
    )
    return str(response)


def multiple_index_query(
        vector_index_list,
        query_str,
        mode = QueryMode.DEFAULT,
        query_transform = None,
        use_async = False,
        **query_kwargs,
    ):
    query_obj, query_bundle, node_candidates = _prepare_query_objects(
        vector_index_list, query_str, mode, query_transform, use_async, **query_kwargs)
    response = query_obj.synthesize(query_bundle, node_candidates)
    return response


async def multiple_index_query_async(
        vector_index_list,
        query_str,
        mode = QueryMode.DEFAULT,
        query_transform = None,
        use_async = False,
        **query_kwargs,
    ):
    query_obj, query_bundle, node_candidates = _prepare_query_objects(
        vector_index_list, query_str, mode, query_transform, use_async, **query_kwargs)
    response = await query_obj.asynthesize(query_bundle, node_candidates)
    return response


def _prepare_query_objects(
        vector_index_list,
        query_str,
        mode,
        query_transform,
        use_async,
        **query_kwargs,
    ):
    mode_enum = QueryMode(mode)
    node_candidates = []
    for index in vector_index_list:
        index._preprocess_query(mode_enum, query_kwargs)
        query_config = QueryConfig(
            index_struct_type=index._index_struct.get_type(),
            query_mode=mode_enum,
            query_kwargs=query_kwargs,
        )
        query_runner = QueryRunner(
            index_struct=index._index_struct,
            service_context=index._service_context,
            query_context={index._index_struct.index_id: index.query_context},
            docstore=index._docstore,
            query_configs=[query_config],
            query_transform=query_transform,
            recursive=False,
            use_async=use_async,
        )
        query_combiner, query_bundle = query_runner._prepare_query_objects(query_str)
        query_bundle = query_combiner._prepare_update(query_bundle)
        query_obj = query_runner._get_query_obj(query_combiner._index_struct)
        nodes = query_obj.retrieve(query_bundle)
        node_candidates.extend(nodes)
    node_candidates.sort(key=lambda node: node.score)
    node_candidates = node_candidates[-TOP_K:]
    return query_obj, query_bundle, node_candidates
