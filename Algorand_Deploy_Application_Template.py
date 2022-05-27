import base64
from algosdk.future import *
from pyteal import *
from algosdk import *
from algosdk.v2client import *



# user declared account mnemonics
creator_mnemonic = "YOUR_MNEMONIC"

# for deployment with sandbox, here are the required parameters to instantiate a client
algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


# helper function to compile program source
def compile_program(algod_client, source_code):
    compile_response = algod_client.compile(source_code)
    return base64.b64decode(compile_response['result'])

# helper function that converts a mnemonic passphrase into a private signing key
def get_private_key_from_mnemonic(mn) :
    private_key = mnemonic.to_private_key(mn)
    return private_key

# Either import all required definitions for the smart contract's Approval Program and Clear Program or write them here


def Approval_Program():
    #include all pyteal approval code here, with the condition or sequence defined under the variable "program"
    program=Cond(
    
                )

    return compileTeal(
                        program, 
                        Mode.Application , # Mode can either be Application or Signature - here we set Mode to Application
                        version=6 # Your desired Teal Assembly Version for your Smart Contract - here we set the most recent: 6
                     )


def Clear_Program():
    #include all clear code here, with the condition or sequence defined under the variable "program"
    program = Seq(
    
                 )

    return compileTeal(
                        program,
                        Mode.Application , # Mode can either be Application or Signature
                        version=6 # Your desired Teal Assembly Version for your Smart Contract - here we set the most recent: 6
                     )


# use the provided mnemonic to generate the users private key
sender = get_private_key_from_mnemonic(creator_mnemonic)

# instantiate an algod client using the parameters provided earlier
algod_client = algod.AlgodClient(algod_token, algod_address)

# use the suggested fee parameters for a transaction
params = algod_client.suggested_params()


# compile approval program to TEAL assembly
with open("./approval.teal", "w") as f:
    approval_program_teal = Approval_Program()
    f.write(approval_program_teal)


# compile clear program to TEAL assembly
with open("./clear.teal", "w") as f:
    clear_state_program_teal = Clear_Program()
    f.write(clear_state_program_teal)

# compile approval_program_teal to binary
approval_program_compiled = compile_program(algod_client, approval_program_teal)

# compile clear_state_program_teal to binary
clear_state_program_compiled = compile_program(algod_client, clear_state_program_teal)


# dictate the quantity of Global int's and byteslices within the variable globalSchema
globalSchema = transaction.StateSchema(
                                     num_uints="Your Contracts # of Global Uints", # ex. num_uints=3
                                     num_byte_slices="Your Contracts # of Global Byteslices" # ex. num_byteslices=5
                                     )

# dictate the quantity of Local int's and byteslices within the variable localSchema
localSchema = transaction.StateSchema(
                                     num_uints="Your Contracts # of Local Uints",  # ex. num_uints=3
                                     num_byte_slices="Your Contracts # of Local Byteslices" # ex. num_byteslices=7
                                     )

# using the information provided above, we instantiate an application create transaction as the variable "createAppTxn"
createAppTxn = transaction.ApplicationCreateTxn(

                                                sender="SENDER_ADDRESS", # the Address of the planned Creator Account of the Smart Contract

                                                sp=params, # sp = suggested parameters, we bind it to the params variable we made earlier

                                                on_complete=transaction.OnComplete.NoOpOC, # Here we define the action to take once the Smart Contract is created, options are:
                                                                                           # OptIn, CloseOut, ClearState, UpdateApplication, DeleteApplication
                                                                                           # in this example, NoOp is set

                                                approval_program=approval_program_compiled, # We set the desired Approval Program included in the Application Creation Transaction to the
                                                                                            # compiled version we created earlier

                                                clear_program=clear_state_program_compiled, # We set the desired Clear Program included in the Application Creation Transaction to the
                                                                                            # compiled version we created earlier

                                                global_schema=globalSchema, # We set the Global variables included in the Application Creation Transaction to the globalSchema we set earlier

                                                local_schema=localSchema, # We set the Local variables included in the Application Creation Transaction to the lcoalSchema we set earlier

                                                foreign_assets=["FOREIGN_ASSET_ID's"], # Identify any Assets that need to be accessible by the Smart Contract by their ID here

                                                foreign_Apps= ["FOREIGN_APP_ID's"], # Identify any Applications (Other Smart Contracts) that need to be accessible by this Smart Contract by their ID here

                                                app_args=["ARGUMENTS_TO_INCLUDE_DURING_APPLICATION_CREATION"], # Include all arguments that need to be included in the Application Creation Transaction
                                                                                                               # are included here

                                                accounts= ["ACCOUNT_ADDRESSES_ACCESSIBLE_BY_THE_SMART_CONTRACT"], #Include all Account Addresses that are accessed by the Smart Contract here

                                                )


# Sign the Application Creation Transaction using the Private Key we generated from the mnemonic provided above
stxn = createAppTxn.sign(sender)

# Generate the transaction ID to be submitted to the network
print(f"{stxn.get_txid()} is the transaction ID. Will it work?")

# Attempt to send the Application Create Transaction to the Algorand Network
Transaction_ID = algod_client.send_transaction(stxn)

# If successful, prints the Application ID
print(Transaction_ID)