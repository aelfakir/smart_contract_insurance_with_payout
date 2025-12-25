import streamlit as st
import hashlib
import json
from time import time

# --- BLOCKCHAIN LOGIC ---
class InsuranceBlockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        # Create Genesis Block
        self.create_block(proof=100, previous_hash='1')

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.pending_transactions,
            'proof': proof,
            'previous_hash': previous_hash,
        }
        self.pending_transactions = []
        self.chain.append(block)
        return block

    def add_transaction(self, sender, receiver, amount, policy_details):
        self.pending_transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount,
            'policy_details': policy_details
        })
        return self.get_last_block()['index'] + 1

    @staticmethod
    def hash(block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def get_last_block(self):
        return self.chain[-1]

# --- STREAMLIT UI ---
st.set_page_config(page_title="InsurTech Blockchain v4", layout="wide", page_icon="🛡️")

# Initialize blockchain in session state
if 'blockchain' not in st.session_state:
    st.session_state.blockchain = InsuranceBlockchain()

st.title("🛡️ Parametric Insurance Blockchain (app4)")
st.markdown("---")

# Navigation Sidebar
menu = st.sidebar.radio("Navigation", ["Policy Issuance", "Immutable Ledger", "Smart Contract Payout"])

# --- SECTION 1: POLICY ISSUANCE ---
if menu == "Policy Issuance":
    st.header("✍️ Issue New Insurance Contract")
    with st.form("issuance_form"):
        col1, col2 = st.columns(2)
        with col1:
            recipient = st.text_input("Recipient Name")
            p_type = st.selectbox("Insurance Type", ["Crop Protection", "Flight Delay", "Cyber Breach"])
        with col2:
            premium = st.number_input("Premium Paid ($)", min_value=50.0, value=100.0)
            coverage_limit = premium * 10
        
        if st.form_submit_button("Seal Contract & Mine Block"):
            if recipient:
                st.session_state.blockchain.add_transaction(
                    sender="Insurance_Pool",
                    receiver=recipient,
                    amount=premium,
                    policy_details={
                        "type": p_type, 
                        "status": "Active", 
                        "limit": coverage_limit
                    }
                )
                last_block = st.session_state.blockchain.get_last_block()
                new_hash = st.session_state.blockchain.hash(last_block)
                st.session_state.blockchain.create_block(proof=200, previous_hash=new_hash)
                st.success(f"Policy for {recipient} added to Block #{len(st.session_state.blockchain.chain)}")
            else:
                st.error("Recipient name is required.")

# --- SECTION 2: VIEW LEDGER ---
elif menu == "Immutable Ledger":
    st.header("📑 Public Transaction History")
    for block in reversed(st.session_state.blockchain.chain):
        with st.expander(f"📦 Block #{block['index']} | Hash: {st.session_state.blockchain.hash(block)[:16]}..."):
            st.write(f"**Previous Hash:** `{block['previous_hash']}`")
            st.table(block['transactions'])

# --- SECTION 3: SMART CONTRACT PAYOUT (FIXED LOGIC) ---
elif menu == "Smart Contract Payout":
    st.header("🤖 Smart Contract Execution")
    st.write("Validation Engine: Matches Recipient + Policy Type + Oracle Event.")
    
    # Logic: Mapping events to the required policy type
    event_mapping = {
        "Major Drought": "Crop Protection",
        "Flight Cancelled": "Flight Delay",
        "Data Leak": "Cyber Breach"
    }
    
    event = st.selectbox("Oracle Event Trigger", list(event_mapping.keys()))
    target = st.text_input("Recipient to Audit")
    
    if st.button("Execute Verification"):
        required_policy = event_mapping[event]
        found_and_matched = False
        payout_val = 0
        
        # Search chain for matching parameters
        for block in st.session_state.blockchain.chain:
            for tx in block['transactions']:
                if (tx['receiver'] == target and 
                    tx['policy_details'].get('status') == 'Active' and 
                    tx['policy_details'].get('type') == required_policy):
                    
                    found_and_matched = True
                    payout_val = tx['policy_details'].get('limit', 1000)
                    break
        
        if found_and_matched:
            st.balloons()
            st.success(f"VERIFIED: {target} holds a {required_policy} policy. Condition met.")
            
            # Record the payout on the chain
            st.session_state.blockchain.add_transaction(
                sender="Insurance_Pool",
                receiver=target,
                amount=payout_val,
                policy_details={"type": "CLAIM_PAYOUT", "event": event, "status": "Paid"}
            )
            
            last_block = st.session_state.blockchain.get_last_block()
            st.session_state.blockchain.create_block(proof=300, previous_hash=st.session_state.blockchain.hash(last_block))
            st.info(f"Payout of ${payout_val} recorded in the new block.")
        else:
            st.error(f"CLAIM REJECTED: {target} does not have an active '{required_policy}' policy for this '{event}'.")

# Sidebar reset
if st.sidebar.button("Hard Reset System"):
    st.session_state.blockchain = InsuranceBlockchain()
    st.rerun()
