# Imports
import os
import json
from eth_typing import ContractName
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# load .env file
load_dotenv()

# Load a new Web3 Provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

# Load contract into Streamlit using cache decorator
@st.cache(allow_output_mutation=True)
def load_contract():
    with open(Path('./contracts/compiled/ArtToken_abi.json')) as f:
        artwork_abi = json.load(f)

    contract_address = os.getenv("SMART_CONTRACT_ADDRESS")

    contract = w3.eth.contract(
        address = contract_address,
        abi = artwork_abi
    )

    return contract

# Load contract and assign it to a variable
contract = load_contract()

# Build Streamlit Application
st.title("Register New Artwork")
accounts = w3.eth.accounts
address = st.selectbox("Select Artwork Owner", options=accounts)
artwork_uri = st.text_input("The URI to the artwork")

# Button for registering Artwork
if st.button("Register Artwork"):
    tx_hash = contract.functions.registerArtwork(address, artwork_uri).transact({
    "from": address,
    "gas": 1000000 #Note that this value depends on ETH Oracle for real-world
    })
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.write("Transaction receipt mined:")
    st.write(dict(receipt))

st.markdown("---")

# Display a token
st.markdown("## Display an Art Token")

selected_address = st.selectbox("Select Account", options=accounts)

tokens = contract.functions.balanceOf(selected_address).call()

st.write(f"This address owns {tokens} tokens.")

token_id = st.selectbox("Artwork Tokens", list(range(tokens)))

if st.button("Display"):

    # Use the contract's "OwnerOf" function to get the art tokens owner
    owner = contract.functions.ownerOf(token_id).call()

    st.write(f"The token is registered to {owner}")

    # Use the contract's "tokenURI" function to get the art token's URI
    token_uri = contract.functions.tokenURI(token_id).call()

    st.write(f"The tokenURI is {token_uri}")
    st.image(token_uri)
    